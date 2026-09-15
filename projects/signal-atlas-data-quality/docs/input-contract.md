# Input contract and rule reference

Input schema version: **1**. Tool version: **1.0.0**.

The file is UTF-8 JSON containing an object with `schema_version: 1` and an `events` array. Missing or unsupported schema versions, a non-array `events` value, malformed JSON, duplicate JSON keys and nonstandard constants such as `NaN` stop evaluation with exit code `2`.

An empty event array is a warning, not a passing validation. Invalid records inside an otherwise valid envelope produce findings, and checks continue for the other records.

## Event object

| Field | Requirement | Meaning |
| --- | --- | --- |
| `id` | Required, non-empty string | Unique ID for one event occurrence across the feed |
| `title` | Required, non-empty string | Event name |
| `city` | Required, non-empty string | City label; this does not determine a time zone |
| `venue` | Required, non-empty string | Venue name or an explicit location description |
| `starts_at` | Required timestamp | Start recorded in the event feed |
| `ends_at` | Optional timestamp | End recorded in the event feed; omit when unknown |
| `sources` | Required, non-empty array | Source objects describing this same event occurrence |

## Source object

| Field | Requirement | Meaning |
| --- | --- | --- |
| `id` | Required, non-empty string | Unique within this event; reuse across different events is allowed |
| `url` | Required, non-empty string | Absolute HTTP or HTTPS URL, without credentials or whitespace; structure is checked, availability is not |
| `checked_at` | Required timestamp | Supplied record of when the source was checked; the tool cannot authenticate this claim |
| `starts_at` | Required timestamp | Event start reported by this source |
| `ends_at` | Optional timestamp | Event end reported by this source; omit when unknown |

Leading and trailing whitespace is ignored when comparing identifiers. IDs are case-sensitive. Other strings are checked for a non-whitespace value. Unknown fields at the root, event or source level generate warnings; their values are not interpreted.

All timestamps use `YYYY-MM-DDTHH:MM:SS`, optionally followed by one to six fractional-second digits, then `Z` or an explicit `±HH:MM` offset. Example: `2026-09-18T19:00:00+01:00`. Date-only values, missing offsets, `-00:00` (unknown offset), leap seconds and impossible dates are rejected. The supplied offset must describe the intended instant; no geographic time-zone inference is performed.

See [the complete clean fixture](../examples/clean-events.json). All fixture events, venues and source websites are fictional.

## Comparison rules

Times are normalized to UTC before comparison. End times must be strictly later than starts, including across midnight. Valid source times are compared against valid corresponding event times. The checker also compares sources within an event, including source end times when the event end is omitted.

Different instants are a conflict; no rounding or tolerance is applied. Invalid timestamps are reported and excluded from comparisons that require them. Stale records remain visible in conflict checks: age alone does not settle which claim is correct.

If an event supplies an end but none of its sources supplies a valid end, the checker warns about missing support. It does not synthesize an end. Claims from different event objects are not compared; the checker does not infer event identity from names, cities or venues.

Freshness is `as_of - checked_at`, compared with the configured number of complete 24-hour days. A check exactly at the age limit passes; a check older by any amount is stale. Future checks are errors. The age policy accepts integers from `0` to `36500`; the default is `7`.

## Finding codes

| Code | Severity | Meaning |
| --- | --- | --- |
| `REQUIRED_TEXT` | Error | Required text is absent, blank or the wrong type |
| `MISSING_TIMESTAMP` | Error | A required timestamp field is absent |
| `INVALID_TIMESTAMP` | Error | A supplied timestamp is invalid, including `null` |
| `INVALID_EVENT` | Error | An event array item is not an object |
| `INVALID_SOURCE` | Error | A source array item is not an object |
| `MISSING_SOURCES` | Error | Sources are missing, empty or not an array |
| `DUPLICATE_EVENT_ID` | Error | An event ID repeats in the feed |
| `DUPLICATE_SOURCE_ID` | Error | A source ID repeats within an event |
| `INVALID_SOURCE_URL` | Error | A source URL fails the structural HTTP(S) check |
| `FUTURE_SOURCE_CHECK` | Error | A recorded source check occurs after `as_of` |
| `INVALID_EVENT_INTERVAL` | Error | Event end is at or before its start |
| `INVALID_SOURCE_INTERVAL` | Error | A source's end is at or before its start |
| `EVENT_DATE_MISMATCH` | Error | A source date differs from the corresponding event date |
| `SOURCE_DATE_CONFLICT` | Error | Sources within an event disagree on a start or end instant |
| `STALE_SOURCE` | Warning | Recorded check exceeds the chosen age limit |
| `UNSUPPORTED_EVENT_END` | Warning | Event end has no valid source end to compare against |
| `UNKNOWN_FIELD` | Warning | An unrecognized field may indicate a typo |
| `EMPTY_FEED` | Warning | No events were supplied |

One underlying problem can yield more than one finding: a conflicting source start can disagree with the event and with another source. Counts refer to findings, not to unique real-world problems.

## Report schema

Both output formats contain the same findings. JSON includes `tool`, `tool_version`, report `schema_version`, normalized `as_of`, `max_source_age_days`, `status`, `summary` and `issues`.

`summary.events` counts all supplied event-array items, including invalid items. `summary.sources` counts all source-array items encountered on valid event objects, including invalid source items. Error and warning counts refer to finding severities.

Every issue includes `code`, `severity`, `path`, `event_id` and `message`. The field path uses zero-based array indices, for example `$.events[0].sources[1].checked_at`. `event_id` is `null` when a usable ID is unavailable. Codes are intended for automated handling; messages are intended for people and may evolve.

The report is deterministic for identical input, tool version, reference time and policy. Findings follow input order; no confidence score or publication approval is calculated. Consult the [CLI exit codes](../README.md#use-your-own-feed) when calling the checker from a script.
