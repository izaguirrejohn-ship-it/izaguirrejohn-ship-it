# Signal Atlas Data Quality

**Review event data before it becomes a recommendation.**

A small Python tool that checks a supplied event feed for stale source records, missing details and conflicting dates. It produces a readable review report or structured JSON, with a precise field location for each finding.

Built for [John Izaguirre's portfolio](../../README.md), from a practical [Signal Atlas](https://signalatlas.guide) product question: how can editors see which event records need attention before people rely on them?

This is a standalone public demonstration. Its original fixtures use fictional Lisbon events and `.example` source URLs; a separate [Lisbon case study](case-study/README.md) uses dated public listings. It is not connected to Signal Atlas's production feed.

[Browser demo and launch setup](../../demo/README.md) · [Real-source case study](case-study/README.md) · [Automated test results](https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it/actions/workflows/portfolio.yml)

## Run it

Requires **Python 3.10 or newer**. Uses only the standard library; no package installation or API key is needed.

```bash
git clone https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it.git
cd izaguirrejohn-ship-it/projects/signal-atlas-data-quality
python3 check_events.py examples/clean-events.json --as-of 2026-09-15T12:00:00Z
```

The clean fixture returns `pass` with no findings and exit code `0`. The fixed reference time keeps the example reproducible when run later.

Try the fixture with deliberate problems:

```bash
python3 check_events.py examples/review-events.json --as-of 2026-09-15T12:00:00Z --format markdown
```

This returns **7 errors and 1 warning**, with exit code `1`. That exit code means the checker completed and found records needing review. The fixture includes a missing venue, an old source check, contradictory event dates, a missing UTC offset and a source check dated in the future.

Inspect the committed reports: [clean report](examples/reports/clean.md) · [review report](examples/reports/review.md) · [review JSON](examples/reports/review.json).

## What it checks

| Check | What an editor learns |
| --- | --- |
| Required metadata | Which event or source is missing a usable ID, title, city, venue, URL or required timestamp |
| Source freshness | Which recorded source checks exceed the chosen age limit, or occur after the reference time |
| Date consistency | Whether the event and its sources describe different start or end instants |
| Time ranges | Whether an end precedes or equals its start |
| Record identity | Whether event IDs repeat, or source IDs repeat within an event |
| Input quality | Whether URLs have an invalid structure, fields are unrecognized, or the feed is empty |

Findings include a stable code, severity, event ID, field path and review action. Errors produce `fail`; warnings alone produce `review`; no findings produce `pass`. Both `fail` and `review` return exit code `1`.

The default source-age limit is **7 days**, a configurable example policy. It is not an approved Signal Atlas production freshness standard. A source exactly at the limit is accepted; one beyond it is flagged.

## Use your own feed

Prepare a UTF-8 JSON file following the [input contract and rule reference](docs/input-contract.md). Each event represents one occurrence, and its source records describe that same occurrence.

```bash
python3 check_events.py your-events.json --max-source-age-days 2 --format markdown
```

Without `--as-of`, the checker uses the current UTC time. Use an explicit timestamp when you need reproducible results.

To save a report:

```bash
mkdir -p local-reports
python3 check_events.py examples/review-events.json --as-of 2026-09-15T12:00:00Z --output local-reports/review.json
```

`--output` creates a new file and refuses to overwrite an existing one, including the input file. Choose a new filename for each saved run. `local-reports/` is ignored by git.

| Exit code | Meaning |
| --- | --- |
| `0` | Completed; no findings |
| `1` | Completed; errors or warnings require review; report is available |
| `2` | Could not complete because of invalid input, arguments or a file error; read stderr |

## Design decisions

- **Compare instants, not strings.** `19:00+01:00` and `18:00Z` agree. Timestamps must include a known UTC offset; the tool does not guess one from a city or resolve daylight-saving ambiguity.
- **Keep disagreement visible.** A conflict does not make the newest source correct. The checker reports conflicting evidence and leaves the decision to an editor.
- **Preserve the supplied records.** The checker does not rewrite events or merge records based on similar titles. Each recurring occurrence needs its own event ID.
- **Make policy explicit.** The report records the reference time, source-age limit and tool version. Unknown fields produce warnings so misspellings do not disappear silently.

## Validation

```bash
python3 -m unittest -v
```

**32 checker tests passed locally on Python 3.12 on 15 September 2026.** They exercise freshness boundaries, time-zone equivalence, malformed records, date conflicts, duplicate identifiers, report escaping, CLI exit codes and protection against overwriting files. Four additional repository-level tests cover the case study and public build. The [Portfolio checks workflow](https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it/actions/workflows/portfolio.yml) runs the Python suites and checks worker-engine parity; consult the actual run for its current result.

## Limits

The tool checks the structure and consistency of supplied data. It does not fetch URLs, authenticate source claims, establish when a human actually checked a source, detect cancellations or verify ticket availability. A passing report is not proof that an event is real or still scheduled.

Source selection, provenance quality and the accuracy of event-to-source matching remain the input author's responsibility. Production feed adapters, editorial approval and live source retrieval are outside this demonstration.

[Source](check_events.py) · [Tests](test_check_events.py) · [Selected work](../../SELECTED_WORK.md#signal-atlas)
