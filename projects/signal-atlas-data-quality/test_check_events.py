"""Behavior and CLI regression checks; run with python3 -m unittest -v."""

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check_events import InputError, check_feed, parse_timestamp, render_markdown

ROOT = Path(__file__).resolve().parent
AS_OF = "2026-09-15T12:00:00Z"


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.feed = json.loads((ROOT / "examples/clean-events.json").read_text(encoding="utf-8"))
        self.event = self.feed["events"][0]
        self.source = self.event["sources"][0]

    def report(self, **kwargs):
        return check_feed(self.feed, as_of=parse_timestamp(AS_OF), **kwargs)

    def codes(self):
        return [issue["code"] for issue in self.report()["issues"]]

    def test_clean_feed_passes(self):
        report = self.report()
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"], {"events": 1, "sources": 2, "errors": 0, "warnings": 0})

    def test_exact_freshness_boundary_passes(self):
        self.source["checked_at"] = "2026-09-08T12:00:00Z"
        self.assertEqual(self.report()["status"], "pass")

    def test_one_microsecond_beyond_freshness_boundary_warns(self):
        self.source["checked_at"] = "2026-09-08T11:59:59.999999Z"
        self.assertEqual(self.codes(), ["STALE_SOURCE"])
        self.assertEqual(self.report()["status"], "review")

    def test_zero_day_policy_requires_current_check_time(self):
        for source in self.event["sources"]:
            source["checked_at"] = AS_OF
        self.assertEqual(self.report(max_source_age_days=0)["status"], "pass")
        self.source["checked_at"] = "2026-09-15T11:59:59Z"
        self.assertEqual(self.report(max_source_age_days=0)["summary"]["warnings"], 1)

    def test_future_check_is_error(self):
        self.source["checked_at"] = "2026-09-15T12:00:01Z"
        self.assertEqual(self.codes(), ["FUTURE_SOURCE_CHECK"])
        self.assertEqual(self.report()["status"], "fail")

    def test_offsets_compare_instants(self):
        self.source["starts_at"] = "2026-09-18T14:00:00-04:00"
        self.source["ends_at"] = "2026-09-18T22:00:00+02:00"
        self.source["checked_at"] = "2026-09-15T13:00:00+01:00"
        self.assertEqual(self.report()["status"], "pass")

    def test_timestamp_rejects_naive_impossible_and_unknown_offset(self):
        for value in (None, [], 1, "2026-09-18", "2026-09-18T18:00:00", "2026-02-30T18:00:00Z",
                      "2026-09-18T18:00:00+01:60", "2026-09-18T18:00:00-00:00",
                      "2026-09-18T18:00:00+24:00", "2026-09-18T18:00:60Z",
                      "0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_timestamp(value)

    def test_bad_timestamp_becomes_field_finding(self):
        self.event["starts_at"] = "2026-09-18T19:00:00"
        self.assertEqual(self.codes(), ["INVALID_TIMESTAMP"])
        self.assertEqual(self.report()["issues"][0]["path"], "$.events[0].starts_at")

    def test_event_interval_must_be_positive(self):
        for end in (self.event["starts_at"], "2026-09-18T17:00:00Z"):
            with self.subTest(end=end):
                self.event["ends_at"] = end
                self.assertIn("INVALID_EVENT_INTERVAL", self.codes())

    def test_overnight_event_is_valid(self):
        self.event["ends_at"] = "2026-09-19T01:00:00+01:00"
        for source in self.event["sources"]:
            source["ends_at"] = "2026-09-19T00:00:00Z"
        self.assertEqual(self.report()["status"], "pass")

    def test_source_interval_is_checked_independently(self):
        self.source["ends_at"] = self.source["starts_at"]
        self.assertIn("INVALID_SOURCE_INTERVAL", self.codes())

    def test_sources_disagree_even_without_event_end(self):
        del self.event["ends_at"]
        self.source["ends_at"] = "2026-09-18T22:00:00Z"
        self.assertEqual(self.codes(), ["SOURCE_DATE_CONFLICT"])

    def test_source_and_canonical_disagreement_are_reported(self):
        self.source["starts_at"] = "2026-09-18T17:00:00Z"
        self.assertEqual(self.codes(), ["EVENT_DATE_MISMATCH", "SOURCE_DATE_CONFLICT"])
        self.assertEqual(self.report()["issues"][0]["event_id"], "demo-lisbon-001")

    def test_end_times_are_optional_but_supplied_end_needs_evidence(self):
        for source in self.event["sources"]:
            del source["ends_at"]
        self.assertEqual(self.codes(), ["UNSUPPORTED_EVENT_END"])
        del self.event["ends_at"]
        self.assertEqual(self.report()["status"], "pass")
        self.event["ends_at"] = None
        self.assertIn("INVALID_TIMESTAMP", self.codes())

    def test_missing_or_mistyped_required_metadata(self):
        for value in (None, "", "  ", [], {}, False, 0):
            with self.subTest(value=value):
                self.event["venue"] = value
                self.assertEqual(self.codes(), ["REQUIRED_TEXT"])
        del self.event["venue"]
        del self.source["starts_at"]
        self.assertEqual(self.codes(), ["REQUIRED_TEXT", "MISSING_TIMESTAMP"])

    def test_malformed_records_do_not_stop_later_event_checks(self):
        self.feed["events"].insert(0, None)
        self.event["sources"].insert(0, 42)
        self.event["venue"] = ""
        self.assertEqual(self.codes(), ["INVALID_EVENT", "REQUIRED_TEXT", "INVALID_SOURCE"])

    def test_sources_must_be_nonempty_array(self):
        for sources in (None, [], {}, "source"):
            with self.subTest(sources=sources):
                self.event["sources"] = sources
                self.assertEqual(self.codes(), ["MISSING_SOURCES"])

    def test_duplicate_event_and_source_ids(self):
        self.feed["events"].append(deepcopy(self.event))
        self.event["sources"][1]["id"] = " organizer "
        self.assertEqual(self.codes(), ["DUPLICATE_SOURCE_ID", "DUPLICATE_EVENT_ID"])

    def test_same_source_id_on_different_events_is_allowed(self):
        second = deepcopy(self.event)
        second["id"] = "demo-lisbon-004"
        self.feed["events"].append(second)
        self.assertEqual(self.report()["status"], "pass")

    def test_empty_feed_is_review_not_pass(self):
        self.feed["events"] = []
        self.assertEqual(self.codes(), ["EMPTY_FEED"])
        self.assertEqual(self.report()["status"], "review")

    def test_invalid_envelope_is_input_error(self):
        for data in (None, [], {}, {"schema_version": True, "events": []},
                     {"schema_version": 1.0, "events": []}, {"schema_version": 2, "events": []},
                     {"schema_version": 1, "events": {}}):
            with self.subTest(data=data):
                with self.assertRaises(InputError):
                    check_feed(data, as_of=parse_timestamp(AS_OF))

    def test_unknown_fields_are_visible(self):
        self.source["checked_on"] = "2026-09-15"
        self.assertEqual(self.codes(), ["UNKNOWN_FIELD"])

    def test_invalid_source_url_structure(self):
        for url in ("ftp://venue.example/a", "events/a", "https:///a", "https://venue.example:99999/a",
                    "https://user:password@venue.example/a", "https://venue.example\n/a",
                    "https://venue.example /a", "https://[broken", "https://venue.example\\evil/a"):
            with self.subTest(url=url):
                self.source["url"] = url
                self.assertIn("INVALID_SOURCE_URL", self.codes())

    def test_configuration_must_be_valid(self):
        with self.assertRaises(InputError):
            check_feed(self.feed, as_of=datetime(2026, 9, 15))
        for days in (-1, 36501, True, "7", 1.5):
            with self.subTest(days=days), self.assertRaises(InputError):
                self.report(max_source_age_days=days)

    def test_deterministic_and_does_not_mutate_input(self):
        self.event["venue"] = ""
        before = deepcopy(self.feed)
        first = self.report()
        self.assertEqual(first, self.report())
        self.assertEqual(self.feed, before)

    def test_markdown_escapes_untrusted_content(self):
        self.event["id"] = "<script>x</script>|[link](https://evil.example)\nextra"
        self.event["venue"] = ""
        report = render_markdown(self.report())
        self.assertNotIn("<script>", report)
        self.assertNotIn("[link]", report)
        self.assertIn("&#124;", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertEqual(len([line for line in report.splitlines() if line.startswith("| ")]), 3)


class CLITests(unittest.TestCase):
    def run_cli(self, input_path, *args):
        return subprocess.run([sys.executable, str(ROOT / "check_events.py"), str(input_path),
                               "--as-of", AS_OF, *args], capture_output=True, text=True, check=False)

    def test_clean_sample_json_stdout(self):
        result = self.run_cli(ROOT / "examples/clean-events.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")
        self.assertEqual(result.stderr, "")

    def test_review_sample_has_expected_findings_and_nonzero_exit(self):
        result = self.run_cli(ROOT / "examples/review-events.json")
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["summary"], {"events": 2, "sources": 3, "errors": 7, "warnings": 1})
        self.assertEqual({issue["code"] for issue in report["issues"]},
                         {"REQUIRED_TEXT", "STALE_SOURCE", "EVENT_DATE_MISMATCH", "SOURCE_DATE_CONFLICT",
                          "INVALID_TIMESTAMP", "FUTURE_SOURCE_CHECK"})

    def test_malformed_and_ambiguous_json_have_no_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            for content in ("{broken", '{"schema_version":1,"schema_version":2,"events":[]}',
                            '{"schema_version":1,"events":[],"x":NaN}', '[]'):
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    result = self.run_cli(path)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("Input/output error:", result.stderr)

    def test_output_file_is_created_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.md"
            result = self.run_cli(ROOT / "examples/review-events.json", "--format", "markdown", "--output", str(output))
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(result.stdout, "")
            before = output.read_bytes()
            self.assertIn(b"Status: **FAIL**", before)
            again = self.run_cli(ROOT / "examples/clean-events.json", "--output", str(output))
            self.assertEqual(again.returncode, 2)
            self.assertEqual(output.read_bytes(), before)

    def test_input_cannot_be_overwritten_by_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.json"
            original = (ROOT / "examples/clean-events.json").read_bytes()
            path.write_bytes(original)
            result = self.run_cli(path, "--output", str(path))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(path.read_bytes(), original)

    def test_invalid_cli_configuration_and_missing_file(self):
        path = ROOT / "examples/clean-events.json"
        for args in (("--as-of", "yesterday"), ("--max-source-age-days", "-1"),
                     ("--max-source-age-days", "1.5")):
            with self.subTest(args=args):
                result = self.run_cli(path, *args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
        self.assertEqual(self.run_cli(ROOT / "examples/does-not-exist.json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
