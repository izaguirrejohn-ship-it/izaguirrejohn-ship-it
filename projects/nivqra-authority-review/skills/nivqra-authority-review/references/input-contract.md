# Input contract · version 1

Root keys: `schema_version` (integer 1), `mandate` (object), `evidence` (object). Each supplied field should have a supporting quote or source location keyed by field name in `evidence`. Missing provenance creates a finding. Unknowns stay null. Extra fields and runtime commands are rejected.

| Fields | Type |
|---|---|
| principal, agent_id, agent_name, purpose | string or null; never invent a registered identity |
| currency | EUR or null; no currency conversion |
| allowed_categories, blocked_categories, approved_counterparties | string arrays or null; [] is explicitly empty, null is unknown |
| allowed_tools, approved_resources | string arrays or null; design controls requiring runtime verification |
| per_action_limit_cents, period_limit_cents, approval_threshold_cents | nonnegative integers or null; EUR cents; period is calendar month; approval is strictly above threshold |
| require_new_counterparty_approval | boolean or null |
| approval_owner | supplied amount-threshold approver, string or null |
| new_counterparty_approval_owner | supplied new-counterparty approver, string or null; do not infer from another approval route |
| revocation_owner | supplied revocation human or role, string or null |
| valid_from, expires_at | timezone-aware ISO 8601 datetimes or null |
| max_uses | positive integer or null; null does not assert unlimited |
| notes | string or null |

Only agent_id, max_uses, notes, allowed_tools and approved_resources are optional for a basic document review. new_counterparty_approval_owner is required only when new-counterparty review is enabled. A missing registered identity still prevents runtime binding. Complete-for-review is not approved or active.

Zero boundaries and empty category allowlists need explicit interpretation; they are never inferred to grant unlimited authority. Supplied values are preserved for review.

[The fictional procurement fixture](../assets/procurement-input.json) demonstrates the input format. Never copy its invented identities or limits into a user's mandate.

Outputs are a normalized inactive proposal, a permission matrix, a readable review and acceptance-test specifications. They are not a drop-in API/database import. A future adapter must validate the current backend contract.
