# Signal Atlas — Data Quality Report

Status: **FAIL** · As of: 2026-09-15T12:00:00Z

2 event(s) · 3 source record(s) · 7 error(s) · 1 warning(s)

Source-age limit: 7 days. Checks use supplied data only.

| Severity | Code | Event | Field | Review action |
| --- | --- | --- | --- | --- |
| error | REQUIRED\_TEXT | demo-lisbon-002 | $.events\[0\].venue | Supply a non-empty text value. |
| warning | STALE\_SOURCE | demo-lisbon-002 | $.events\[0\].sources\[0\].checked\_at | Recorded check at 2026-09-01T12:00:00Z is older than the limit of 7 days. Refresh it. |
| error | EVENT\_DATE\_MISMATCH | demo-lisbon-002 | $.events\[0\].sources\[1\].starts\_at | Source says 2026-09-20T19:00:00Z; event says 2026-09-19T19:00:00Z. Review before publication. |
| error | EVENT\_DATE\_MISMATCH | demo-lisbon-002 | $.events\[0\].sources\[1\].ends\_at | Source says 2026-09-20T21:00:00Z; event says 2026-09-19T21:00:00Z. Review before publication. |
| error | SOURCE\_DATE\_CONFLICT | demo-lisbon-002 | $.events\[0\].sources | Sources disagree on starts\_at: 2026-09-19T19:00:00Z, 2026-09-20T19:00:00Z. Resolve the evidence; do not pick a winner automatically. |
| error | SOURCE\_DATE\_CONFLICT | demo-lisbon-002 | $.events\[0\].sources | Sources disagree on ends\_at: 2026-09-19T21:00:00Z, 2026-09-20T21:00:00Z. Resolve the evidence; do not pick a winner automatically. |
| error | INVALID\_TIMESTAMP | demo-lisbon-003 | $.events\[1\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | FUTURE\_SOURCE\_CHECK | demo-lisbon-003 | $.events\[1\].sources\[0\].checked\_at | The recorded check is later than as\_of; verify its clock or provenance. |

A pass is not confirmation that an event is real, available or still scheduled. URLs and source claims were not fetched or verified.
