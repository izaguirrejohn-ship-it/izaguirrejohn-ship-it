# NIVQRA browser authority review

A guided authoring interface around the unchanged NIVQRA Authority Review 1.0.0 Python compiler. It prepares a review from supplied fields and produces the same four files as the native compiler: Markdown review, inactive mandate JSON, permission CSV and scenario JSON.

**[Open the live authority review](https://izaguirrejohn-ship-it.github.io/izaguirrejohn-ship-it/nivqra/)** — no account or installation needed.

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

## Live verification · 15 September 2026

The first [source publication](https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it/commit/6528da94d244d05562e5d72e5c3b18fad4f1c22e) passed [deployment run 34991267263](https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it/actions/runs/34991267263): 55 Python tests on each of Python 3.10, 3.12 and 3.14, plus 22 worker checks across both demos.

Desktop Chrome verification confirmed:

- Research purchases: 0 human-decision findings, 1 runtime-coverage finding, 15 unrun scenarios.
- Missing owner: exactly 1 human-decision finding for the new-counterparty approver. The amount approver remained separate.
- Conflicting boundaries: exactly 2 human-decision findings, for category conflict and unreachable amount review.
- Blank brief: all 21 fields remained null, with no evidence notes or inherited fictional values; 15 human-input findings and 12 unrun scenarios.
- An entered €25.35 was preserved as 2535 cents with an explicit supplied-statement source note. Invalid amount notation was rejected. Editing hid stale results and downloads.
- The four downloaded outputs matched the native compiler's bytes exactly for the same exported input: mandate JSON 3662 bytes, CSV 2690, scenario JSON 7740 and Markdown 5826. The saved input JSON matched the displayed brief.
- The permissions view and new-counterparty scenario preserved the separate approval owners. Signal Atlas remained reachable and usable.

The desktop layout was inspected with no horizontal overflow. Mobile browser interactions have not been independently verified. These checks verify document authoring, not a live authority backend.
