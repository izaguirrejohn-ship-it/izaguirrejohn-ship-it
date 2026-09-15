# Signal Atlas browser demo

A static interface around the original Python checker. The user can select or edit a feed, choose a reference time and source-age limit, run the checker, inspect findings and download JSON or Markdown.

**[Open the live quality desk](https://izaguirrejohn-ship-it.github.io/izaguirrejohn-ship-it/)** — no account or installation needed.

The same site also hosts the **[NIVQRA browser authority review](https://izaguirrejohn-ship-it.github.io/izaguirrejohn-ship-it/nivqra/)**. Both tools share the bundled Python runtime; this build publishes both interfaces. See [NIVQRA's guide](nivqra/README.md) for its separate authoring scope.

The build copies the canonical `check_events.py` into the public site. A Web Worker runs that same file with **Pyodide 314.0.7**, bundled from its pinned npm package and served by this site. There is no second JavaScript implementation of the validation rules.

## Local preview

From the repository root:

```bash
npm install --no-save --package-lock=false --ignore-scripts --no-audit --no-fund pyodide@314.0.7
python3 scripts/build_demo.py
python3 -m http.server 8765 --directory _site
```

Open `http://localhost:8765` in a browser. Serve over HTTP; opening the HTML as a `file:` URL does not support the worker and source fetches reliably. An internet connection is required for the first Pyodide load.

The app downloads its runtime and bundled examples from the same site. Event data is processed in the worker's memory; there is no event-data upload, analytics endpoint, local-storage persistence or live source retrieval. The hosting provider receives ordinary requests for public assets; the checker has no runtime CDN dependency.

Input is limited to 250,000 UTF-8 bytes and 500 events. A check can be cancelled; a 90-second timeout terminates the worker. Editing data or review settings invalidates the displayed report. Downloads apply only to the latest completed check.

## GitHub Pages deployment

GitHub Pages was enabled and the demo was verified live on 15 September 2026. Live browser testing found a failed external CDN load and then established that Pyodide 314.0.7 requires a module worker. The corrected demo bundles the runtime, uses a module worker and versions its browser asset URLs. Pushes to `main` run the checks and publish the demo after they pass.

For another repository, complete this one-time setup:

1. Open this repository's **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Open **Actions → Portfolio checks → Run workflow**, choosing `main`.

The workflow runs both Python test suites, checks the case study and public build, and compares the browser worker's actual Pyodide results with the native Python reports. If these jobs pass and Pages is enabled, it deploys the built site. Until that initial setting is enabled, tests and the site artifact can still complete, and deployment is explicitly skipped.

Use the deployment's returned URL as the live address. A committed interface, passing tests or a generated artifact alone does not establish a published site.

## Verification

`tests/test_browser_engine.cjs` exercises the real worker handler and pinned Pyodide runtime under Node, with worker APIs supplied by the test harness. It substitutes the browser module import with the identical Node package, preserving the handler and Python execution path. Four fixtures must exactly match native Python JSON reports; six malformed or oversized inputs must be rejected. This verifies engine parity, not browser loading, layout or UI interactions.

The Python build test confirms that the public site includes the original checker and only reviewed public assets. The workflow also checks JavaScript syntax.

Live desktop Chrome checks on 15 September 2026 verified all four examples: A produced 7 errors and 1 warning; B passed; D produced 9 timestamp errors; C passed. Removing a venue produced its expected finding, malformed JSON was rejected, editing hid stale downloads, and setting the clean example's source-age limit to zero produced 2 warnings. JSON and Markdown downloads for the reviewed Lisbon example matched the committed reports exactly. The desktop layout was inspected; mobile browser interaction has not been independently verified.

Verified application revision: [0fae1b8](https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it/commit/0fae1b82313bc50c0ecd175306ba9d210a5e9770). Its [deployment and checks](https://github.com/izaguirrejohn-ship-it/izaguirrejohn-ship-it/actions/runs/34989949754) passed. Later documentation-only commits do not change the tested application files.

## Dependencies

The Python CLI still has no external dependencies. The browser demo adds Pyodide; the hosted worker-engine verification and site build install the same exact npm version. The site includes the runtime's source and license notices in `runtime/`. GitHub workflow actions are pinned to reviewed release commit SHAs. See [Pyodide's self-hosting documentation](https://pyodide.org/en/stable/usage/downloading-and-deploying.html), [runtime notices](RUNTIME-NOTICES.md) and [GitHub's Pages setup guide](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
