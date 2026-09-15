#!/usr/bin/env python3
"""Offline checks for a supplied event feed. Python 3.10+, standard library only."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

VERSION = "1.0.0"
TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})",
    re.ASCII,
)
EVENT_FIELDS = {"id", "title", "city", "venue", "starts_at", "ends_at", "sources"}
SOURCE_FIELDS = {"id", "url", "checked_at", "starts_at", "ends_at"}


class InputError(ValueError):
    """The file or checker configuration cannot be evaluated."""


def parse_timestamp(value: object) -> datetime:
    """Parse the documented ISO 8601 subset, normalize to UTC, reject naive time."""
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        raise ValueError("Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset.")
    # datetime accepts noncanonical offset minutes such as +01:60; this schema does not.
    if value[-1] != "Z":
        hours, minutes = int(value[-5:-3]), int(value[-2:])
        if hours > 23 or minutes > 59 or value.endswith("-00:00"):
            raise ValueError("Use a known UTC offset; -00:00 is not supported.")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise ValueError("Timestamp has an invalid date, time or UTC range.") from exc


def utc_text(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def valid_url(value: str) -> bool:
    """Check structure only. This function makes no request."""
    if any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value):
        return False
    try:
        parsed = urlsplit(value)
        return bool(
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            and parsed.username is None
            and parsed.password is None
            and "\\" not in parsed.netloc
            and (parsed.port is None or 1 <= parsed.port <= 65535)
        )
    except ValueError:
        return False


def check_feed(data: object, *, as_of: datetime, max_source_age_days: int = 7) -> dict:
    """Return deterministic findings without mutating data or accessing the network."""
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise InputError("as_of must be a timezone-aware datetime.")
    try:
        as_of = as_of.astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise InputError("as_of is outside the supported UTC range.") from exc
    if type(max_source_age_days) is not int or not 0 <= max_source_age_days <= 36500:
        raise InputError("max_source_age_days must be an integer from 0 to 36500.")
    if not isinstance(data, dict):
        raise InputError("The feed must be a JSON object.")
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise InputError("schema_version must be the integer 1.")
    if not isinstance(data.get("events"), list):
        raise InputError("events must be a JSON array.")

    issues = []
    event_ids = set()
    source_count = 0

    def add(code, severity, path, message, event_id=None):
        issues.append({"code": code, "severity": severity, "path": path,
                       "event_id": event_id, "message": message})

    def unknown_fields(obj, allowed, path, event_id=None):
        for key in sorted(set(obj) - allowed):
            add("UNKNOWN_FIELD", "warning", path, f"Unrecognized field {key!r}; check for a typo.", event_id)

    def required_text(obj, field, path, event_id):
        value = obj.get(field)
        if not isinstance(value, str) or not value.strip():
            add("REQUIRED_TEXT", "error", f"{path}.{field}", "Supply a non-empty text value.", event_id)
            return None
        return value.strip()

    def timestamp(obj, field, path, event_id, required=True):
        if field not in obj:
            if required:
                add("MISSING_TIMESTAMP", "error", f"{path}.{field}", "Supply a timestamp with a UTC offset.", event_id)
            return None
        try:
            return parse_timestamp(obj[field])
        except ValueError as exc:
            add("INVALID_TIMESTAMP", "error", f"{path}.{field}", str(exc), event_id)
            return None

    unknown_fields(data, {"schema_version", "events"}, "$")
    if not data["events"]:
        add("EMPTY_FEED", "warning", "$.events", "No events were supplied; there is nothing to evaluate.")

    for index, event in enumerate(data["events"]):
        path = f"$.events[{index}]"
        if not isinstance(event, dict):
            add("INVALID_EVENT", "error", path, "Each event must be a JSON object.")
            continue
        event_id = required_text(event, "id", path, None)
        if event_id:
            if event_id in event_ids:
                add("DUPLICATE_EVENT_ID", "error", path + ".id", "Use a unique ID for each event occurrence.", event_id)
            event_ids.add(event_id)
        unknown_fields(event, EVENT_FIELDS, path, event_id)
        for field in ("title", "city", "venue"):
            required_text(event, field, path, event_id)
        start = timestamp(event, "starts_at", path, event_id)
        end = timestamp(event, "ends_at", path, event_id, required=False)
        if start is not None and end is not None and end <= start:
            add("INVALID_EVENT_INTERVAL", "error", path + ".ends_at", "Event end must be later than its start.", event_id)

        sources = event.get("sources")
        if not isinstance(sources, list) or not sources:
            add("MISSING_SOURCES", "error", path + ".sources", "Supply a non-empty array of source records.", event_id)
            continue
        source_ids = set()
        claims = {"starts_at": [], "ends_at": []}
        for source_index, source in enumerate(sources):
            source_count += 1
            source_path = f"{path}.sources[{source_index}]"
            if not isinstance(source, dict):
                add("INVALID_SOURCE", "error", source_path, "Each source must be a JSON object.", event_id)
                continue
            unknown_fields(source, SOURCE_FIELDS, source_path, event_id)
            source_id = required_text(source, "id", source_path, event_id)
            if source_id:
                if source_id in source_ids:
                    add("DUPLICATE_SOURCE_ID", "error", source_path + ".id", "Use unique source IDs within this event.", event_id)
                source_ids.add(source_id)
            url = required_text(source, "url", source_path, event_id)
            if url and not valid_url(source["url"]):
                add("INVALID_SOURCE_URL", "error", source_path + ".url", "Use an absolute HTTP(S) URL without credentials or whitespace.", event_id)
            checked = timestamp(source, "checked_at", source_path, event_id)
            if checked is not None:
                age = as_of - checked
                if age < timedelta(0):
                    add("FUTURE_SOURCE_CHECK", "error", source_path + ".checked_at", "The recorded check is later than as_of; verify its clock or provenance.", event_id)
                elif age > timedelta(days=max_source_age_days):
                    add("STALE_SOURCE", "warning", source_path + ".checked_at", f"Recorded check at {utc_text(checked)} is older than the limit of {max_source_age_days} days. Refresh it.", event_id)

            source_start = timestamp(source, "starts_at", source_path, event_id)
            source_end = timestamp(source, "ends_at", source_path, event_id, required=False)
            if source_start is not None and source_end is not None and source_end <= source_start:
                add("INVALID_SOURCE_INTERVAL", "error", source_path + ".ends_at", "Source end must be later than its start.", event_id)
            for field, observed, canonical in (("starts_at", source_start, start), ("ends_at", source_end, end)):
                if observed is None:
                    continue
                claims[field].append(observed)
                if canonical is not None and canonical != observed:
                    add("EVENT_DATE_MISMATCH", "error", source_path + "." + field, f"Source says {utc_text(observed)}; event says {utc_text(canonical)}. Review before publication.", event_id)

        for field, values in claims.items():
            distinct = sorted(set(values))
            if len(distinct) > 1:
                times = ", ".join(utc_text(value) for value in distinct)
                add("SOURCE_DATE_CONFLICT", "error", path + ".sources", f"Sources disagree on {field}: {times}. Resolve the evidence; do not pick a winner automatically.", event_id)
        if end is not None and not claims["ends_at"]:
            add("UNSUPPORTED_EVENT_END", "warning", path + ".ends_at", "No valid source end time supports this event end; check its provenance.", event_id)

    counts = Counter(issue["severity"] for issue in issues)
    status = "fail" if counts["error"] else "review" if counts["warning"] else "pass"
    return {
        "tool": "signal-atlas-data-quality", "tool_version": VERSION, "schema_version": 1,
        "as_of": utc_text(as_of), "max_source_age_days": max_source_age_days,
        "status": status,
        "summary": {"events": len(data["events"]), "sources": source_count,
                    "errors": counts["error"], "warnings": counts["warning"]},
        "issues": issues,
    }


def markdown_cell(value: object) -> str:
    value = html.escape(str(value), quote=False)
    for character in ("\\", "`", "*", "_", "[", "]"):
        value = value.replace(character, "\\" + character)
    return value.replace("|", "&#124;").replace("\r", " ").replace("\n", " ")


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = ["# Signal Atlas — Data Quality Report", "",
             f"Status: **{report['status'].upper()}** · As of: {report['as_of']}", "",
             f"{summary['events']} event(s) · {summary['sources']} source record(s) · "
             f"{summary['errors']} error(s) · {summary['warnings']} warning(s)", "",
             f"Source-age limit: {report['max_source_age_days']} days. Checks use supplied data only.", ""]
    if report["issues"]:
        lines.extend(["| Severity | Code | Event | Field | Review action |",
                      "| --- | --- | --- | --- | --- |"])
        for issue in report["issues"]:
            values = [issue["severity"], issue["code"], issue["event_id"] or "—", issue["path"], issue["message"]]
            lines.append("| " + " | ".join(markdown_cell(value) for value in values) + " |")
    else:
        lines.append("No issues found by the configured checks.")
    lines.extend(["", "A pass is not confirmation that an event is real, available or still scheduled. "
                  "URLs and source claims were not fetched or verified.", ""])
    return "\n".join(lines)


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise InputError(f"Duplicate JSON key: {key!r}.")
        obj[key] = value
    return obj


def reject_constant(value):
    raise InputError(f"Nonstandard JSON constant: {value}.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON event feed")
    parser.add_argument("--as-of", help="Reference time with offset; defaults to the current UTC time")
    parser.add_argument("--max-source-age-days", type=int, default=7, help="0–36500; default: 7 (demo policy)")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path, help="Create a new report file; refuses to overwrite an existing file")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args(argv)
    try:
        as_of = parse_timestamp(args.as_of) if args.as_of is not None else datetime.now(timezone.utc)
        data = json.loads(args.input.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object, parse_constant=reject_constant)
        report = check_feed(data, as_of=as_of, max_source_age_days=args.max_source_age_days)
        output = render_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2, ensure_ascii=True) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as destination:
                destination.write(output)
        else:
            sys.stdout.write(output)
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        print(f"Input/output error: {exc}", file=sys.stderr)
        return 2
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
