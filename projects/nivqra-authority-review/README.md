# NIVQRA Authority Review

**Turn an agent workflow into an inactive mandate draft, a permission matrix and a scenario review pack.**

A Python authoring tool with a guided browser demonstration from I.O.V / John Izaguirre. This repository publishes the prepared **1.0.0** package with a worked example and reproducible tests.

The compiler uses the Python standard library. It requires no API key, external service or third-party Python package.

## Try it

**[Open the browser authority review](https://izaguirrejohn-ship-it.github.io/izaguirrejohn-ship-it/nivqra/)** to choose a fictional example or start a blank structured brief. Inspect findings, permissions and scenario specifications, then download all four authoring files. The browser uses the original compiler and keeps every result inactive. [Browser source and verification](../../demo/nivqra/README.md).

From a terminal with Python 3 installed:

```sh
git clone https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it.git
cd izaguirrejohn-ship-it/projects/nivqra-authority-review
python3 skills/nivqra-authority-review/scripts/compile_review.py \
  --input skills/nivqra-authority-review/assets/procurement-input.json \
  --out review-output
```

Use a new output directory for each run. The compiler refuses to overwrite an existing directory.

For your own review, make a copy of the [example input](skills/nivqra-authority-review/assets/procurement-input.json), replace it with your supplied facts and evidence, then pass that copy to `--input`. Unknown fields remain `null`; the example's fictional identities and budgets are not defaults for a real workflow.

## The example

A fictional Research Agent is given:

| Boundary | Fictional input |
| --- | --- |
| Purpose | Acquire research datasets from approved vendors |
| Currency and period | EUR; calendar month |
| Per-action ceiling | €20 |
| Monthly cap | €500 |
| Amount review | Strictly above €10 |
| Amount approver | Fictional operations lead |
| New-counterparty approver | Fictional vendor review lead |
| Blocked category | Marketing lists |

All values are fixtures. The validity dates in the fixture are also illustrative; the authoring tool does not grant current authority.

## Inspect the output

| File | What it provides |
| --- | --- |
| [authority-review.md](examples/output/authority-review.md) | A readable review, permission table, findings and scenario specifications |
| [mandate-draft.json](examples/output/mandate-draft.json) | Supplied design fields, provenance, findings and explicit inactive state |
| [permission-matrix.csv](examples/output/permission-matrix.csv) | A structured field/value/evidence matrix for review |
| [scenario-tests.json](examples/output/scenario-tests.json) | Fifteen scenario specifications for this fixture, each marked `not_run` |

**DRAFT · NOT ACTIVE.** These are authoring outputs. The tool does not activate mandates, approve requests, enforce a live policy, revoke authority or execute payments. Test specifications need separate execution against an authorized implementation.

## Run the tests

From this project's directory:

```sh
python3 -m unittest discover \
  -s skills/nivqra-authority-review/scripts \
  -p 'test_*.py' -v
```

**Local verification on 15 September 2026: 19 tests passed.** The CLI example also generated four output files successfully. These checks validate the authoring package; they do not establish runtime enforcement.

The [Portfolio checks workflow](https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it/actions/workflows/portfolio.yml) also runs this authoring suite on repository changes. The linked run records its actual result.

The checks cover inactive output, separate approval owners, missing data, invalid inputs, conflicting scope, exact-boundary scenario generation, deterministic output, CSV handling and refusal to overwrite output.

## Design decisions

- Keep an unknown decision visible instead of filling it with an invented answer.
- Keep amount approval and counterparty approval as separate responsibilities.
- Store money as integer cents and preserve the supplied boundaries.
- Distinguish a specification from an observed runtime result.
- Make the review runnable locally without a network dependency.

## Scope and package provenance

Version 1.0.0 supports EUR spending designs with calendar-month caps. Other currencies and periods require a different contract; this package does not convert them.

The original package's compiler, tests, fixture, skill instructions and manifest are preserved. The quickstart and generated example were added for GitHub. [PROVENANCE.json](PROVENANCE.json) records source-file hashes.

The prepared plugin manifest is included for inspection. No marketplace listing, host installation or plugin certification is asserted by this GitHub publication.

[Input contract](skills/nivqra-authority-review/references/input-contract.md) · [Product compatibility](skills/nivqra-authority-review/references/product-compatibility.md) · [Product overview](https://iov.agency/nivqra/authority-review)
