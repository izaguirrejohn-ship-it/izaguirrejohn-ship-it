# NIVQRA browser authority review

A guided authoring interface around the unchanged NIVQRA Authority Review 1.0.0 Python compiler. It prepares a review from supplied fields and produces the same four files as the native compiler: Markdown review, inactive mandate JSON, permission CSV and scenario JSON.

## Experience

- Three explicitly fictional examples: research purchases, a missing counterparty approver, and conflicting boundaries.
- A blank brief starts every field unknown, with no invented identities, budgets or dates.
- Guided identity, spending, scope, approval and validity fields. EUR amounts become exact integer cents; unknown fields remain null. A blank list is unknown; `[]` is explicitly empty.
- User edits are recorded as supplied browser statements. Unchanged example fields retain their fictional source notes. Input JSON and provenance can be inspected and saved.
- Findings, permissions, scenario specifications and downloads have separate accessible views. Editing clears stale results and downloads. Checks can be cancelled and time out after 90 seconds. Browser inputs are capped at 250 KB.

## Scope

Every output is **DRAFT · NOT ACTIVE**. Scenario specifications remain `not_run`. There is no authority activation, request approval, live policy change, payment, account connection or lead collection. The interface does not convert other currencies or interpret a free-form description with an AI model.

The browser runs the published `compile_review.py` in a Pyodide 314.0.7 module worker. Both portfolio demos share the site's bundled runtime. Briefs are processed in memory, with no application upload, analytics or local-storage persistence. The hosting provider receives ordinary public-asset requests.

## Build and verification

Use the repository's [shared build instructions](../README.md). The site is assembled with NIVQRA under `/nivqra/` and Signal Atlas at its existing address. The canonical compiler, original fixture and package provenance are preserved.

`tests/test_nivqra_browser_engine.cjs` compares all four generated files exactly against the native compiler for the three examples and a blank brief. It checks the specific missing-owner and conflicting-boundary results, inactive output and eight invalid-input rejections. The harness substitutes the module import and worker/file APIs; it does not establish browser startup or UI behavior. Public build checks verify that the packaged compiler matches its canonical source byte for byte.

Live browser verification is performed after deployment. Source publication and passing engine tests alone do not establish a working browser experience.
