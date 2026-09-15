# Signal Atlas — Data Quality Report

Status: **FAIL** · As of: 2026-09-15T14:44:41Z

3 event(s) · 6 source record(s) · 9 error(s) · 0 warning(s)

Source-age limit: 7 days. Checks use supplied data only.

| Severity | Code | Event | Field | Review action |
| --- | --- | --- | --- | --- |
| error | INVALID\_TIMESTAMP | lisbon-gulbenkian-hard-days-night-20260919 | $.events\[0\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | INVALID\_TIMESTAMP | lisbon-gulbenkian-hard-days-night-20260919 | $.events\[0\].sources\[0\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | INVALID\_TIMESTAMP | lisbon-gulbenkian-hard-days-night-20260919 | $.events\[0\].sources\[1\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | INVALID\_TIMESTAMP | lisbon-gulbenkian-dont-look-back-20260919 | $.events\[1\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | INVALID\_TIMESTAMP | lisbon-gulbenkian-dont-look-back-20260919 | $.events\[1\].sources\[0\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | INVALID\_TIMESTAMP | lisbon-gulbenkian-dont-look-back-20260919 | $.events\[1\].sources\[1\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | INVALID\_TIMESTAMP | lisbon-ccb-beethoven-20260927 | $.events\[2\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | INVALID\_TIMESTAMP | lisbon-ccb-beethoven-20260927 | $.events\[2\].sources\[0\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |
| error | INVALID\_TIMESTAMP | lisbon-ccb-beethoven-20260927 | $.events\[2\].sources\[1\].starts\_at | Use YYYY-MM-DDTHH:MM:SS with Z or an explicit ±HH:MM offset. |

A pass is not confirmation that an event is real, available or still scheduled. URLs and source claims were not fetched or verified.
