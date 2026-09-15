# NIVQRA · Agent Authority Review

**DRAFT · NOT ACTIVE**

Agent: Research Agent. Principal: Fictional Northstar operations lead.

An authoring review of supplied information. No live workspace was read and no authority was granted, changed or revoked.

Review state: **complete for human review**. Amounts are EUR cents; period is calendar month.

## Permission matrix

| Field | Proposed value | Evidence |
|---|---|---|
| principal | Fictional Northstar operations lead | Fictional test brief explicitly specifies "Fictional Northstar operations lead" |
| agent_id | fixture-research-01 | Fictional test brief explicitly specifies "fixture-research-01" |
| agent_name | Research Agent | Fictional test brief explicitly specifies "Research Agent" |
| purpose | Acquire research datasets from approved vendors | Fictional test brief explicitly specifies "Acquire research datasets from approved vendors" |
| currency | EUR | Fictional test brief explicitly specifies "EUR" |
| approval_owner | Fictional operations lead | Fictional test brief explicitly specifies "Fictional operations lead" |
| new_counterparty_approval_owner | Fictional vendor review lead | Fictional test brief: new counterparties require the vendor review lead. |
| revocation_owner | Fictional operations lead | Fictional test brief explicitly specifies "Fictional operations lead" |
| valid_from | 2026-09-10T00:00:00Z | Fictional test brief explicitly specifies "2026-09-10T00:00:00Z" |
| expires_at | 2026-10-10T00:00:00Z | Fictional test brief explicitly specifies "2026-10-10T00:00:00Z" |
| notes | Fictional acceptance fixture. No live account or authority. | Fictional test brief explicitly specifies "Fictional acceptance fixture. No live account or authority." |
| allowed_categories | data; research APIs | Fictional test brief explicitly specifies ["data", "research APIs"] |
| blocked_categories | marketing lists | Fictional test brief explicitly specifies ["marketing lists"] |
| approved_counterparties | Fictional Civic Data | Fictional test brief explicitly specifies ["Fictional Civic Data"] |
| allowed_tools | dataset.request | Fictional test brief explicitly specifies ["dataset.request"] |
| approved_resources | research catalogue | Fictional test brief explicitly specifies ["research catalogue"] |
| per_action_limit_cents | 2000 | Fictional test brief explicitly specifies 2000 |
| period_limit_cents | 50000 | Fictional test brief explicitly specifies 50000 |
| approval_threshold_cents | 1000 | Fictional test brief explicitly specifies 1000 |
| max_uses | 50 | Fictional test brief explicitly specifies 50 |
| require_new_counterparty_approval | Yes | Fictional test brief explicitly specifies true |

## Findings

- **verify_runtime_coverage**: Verify these design controls in the complete execution path; this package does not enforce them.

## Scenario specifications

All cases are **not run**. Expectations are test requirements, not observed policy decisions.

| Case | Test | Expected assertion | Missing inputs |
|---|---|---|---|
| S01 | Draft has no authority | Refuse execution under an inactive draft. | None for this specification |
| S02 | Within the stated boundary | After separate test activation, the canonical engine permits only if all applicable checks pass. Inspect its evidence. | None for this specification |
| S03 | Per-action hard ceiling | Refuse an over-limit request; routing to approval alone is insufficient. | None for this specification |
| S04 | Monthly cap exhausted | Refuse another one-cent action after a positive monthly cap is exhausted. Resolve zero-cap semantics first. | None for this specification |
| S05 | Human approval threshold | Inside hard limits and other rules, route to the named human without execution. Resolve an unreachable threshold first. | None for this specification |
| S06 | New counterparty | When review is required, route to the named new-counterparty approver. Otherwise verify the explicitly supplied counterparty scope. | None for this specification |
| S07 | Outside category scope | Refuse an out-of-scope category. Resolve empty-list semantics first. | None for this specification |
| S08 | Outside validity window | Refuse before valid_from and at/after expires_at in the complete execution path. This is an unverified coverage requirement. | None for this specification |
| S09 | Revocation | After an authorized human revokes the test mandate, later and retried actions cannot execute. | None for this specification |
| S10 | Replay and concurrency | No duplicate execution or double draw; aggregate authority cannot be overspent. Verify in the execution path. | None for this specification |
| S11 | Use cap | Refuse the next action after the use cap is exhausted. | None for this specification |
| S12 | Tool and resource boundaries | Verify refusal for an out-of-scope tool/resource in the actual control layer; record any missing implementation. | None for this specification |
| S13 | Exactly at the amount-review threshold | At a positive threshold, amount alone does not require review because the rule is strictly above. All other checks still apply. | None for this specification |
| S14 | Exactly at the per-action hard limit | A request equal to a positive ceiling does not exceed it. It may still need human review or refusal under other rules. | None for this specification |
| S15 | Explicitly blocked category | Refuse this explicitly blocked category even for one cent. If also allowlisted, resolve the document conflict and verify refusal precedence. | None for this specification |

## Human handoff

Resolve findings with the responsible principal. Validate scenarios against the canonical NIVQRA backend in an authorized test environment. Activation is a separate human action. These files are not a drop-in runtime import.
