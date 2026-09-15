# Product compatibility

Reviewed 10 September 2026 against NIVQRA Main Hub revision `2eb0999b94fe47198c468648ee50b69947f16ff8`. This is dated source evidence, not a live connection.

Owning sources: docs/PRODUCT_DECISIONS.md, docs/DISTRIBUTION_LAYER_V0_3.md, docs/MACHINE_MANDATES.md, docs/AUTHORITY_ARCHITECTURE.md, src/lib/policy.ts and draft interfaces in src/lib/ai.server.ts.

Approved V0.3 direction: one authority-intelligence backend across assistant surfaces. Public assistants inspect, explain and draft. They never activate, approve, revoke, change policy or execute. The MCP surface remains described as planned. This authoring workflow adds no server or competing policy engine.

Canonical mandate vocabulary uses per_action_limit_cents and period_limit_cents. The inspected purchase engine uses per_transaction_limit_cents and monthly_budget_cents. A future adapter must map these explicitly, and map new-counterparty review to new-vendor review only when appropriate.

The inspected evaluatePolicy function checks revoked state, categories, per-transaction ceiling, monthly budget, approval threshold and new-vendor review. Zero numeric limits and an empty allowed-category list disable some checks in that function. This workflow flags these cases instead of interpreting them as unlimited authority.

Validity dates, max uses, exact tool/resource lists and principal/agent binding require verification in the complete server path. Their appearance in documents does not prove enforcement. Scenarios generated here are requirements for that verification and are not executed against a server.

Every draft stays DRAFT · NOT ACTIVE. Actual policy outcomes must come from the canonical backend with its evidence and context.
