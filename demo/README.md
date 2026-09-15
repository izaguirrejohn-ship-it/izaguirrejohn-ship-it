# Signal Atlas browser demo

A static interface around the original Python checker. The user can select or edit a feed, choose a reference time and source-age limit, run the checker, inspect findings and download JSON or Markdown.

The build copies the canonical `check_events.py` into the public site. A Web Worker runs that same file with **Pyodide 314.0.7**, loaded from the version-pinned official jsDelivr distribution. There is no second JavaScript implementation of the validation rules.

## Local preview

From the repository root:

```bash
python3 scripts/build_demo.py
python3 -m http.server 8765 --directory _site
```

Open `http://localhost:8765` in a browser. Serve over HTTP; opening the HTML as a `file:` URL does not support the worker and source fetches reliably. An internet connection is required for the first Pyodide load.

The app downloads its runtime and bundled examples. Event data is processed in the worker's memory; there is no event-data upload, analytics endpoint, local-storage persistence or live source retrieval. The external runtime CDN and hosting provider still receive ordinary requests for their assets.

Input is limited to 250,000 UTF-8 bytes and 500 events. A check can be cancelled; a 90-second timeout terminates the worker. Editing data or review settings invalidates the displayed report. Downloads apply only to the latest completed check.

## GitHub Pages activation

The repository initially had Pages disabled. The connection can publish code and workflows but cannot change that account setting.

1. Open this repository's **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Open **Actions → Portfolio checks → Run workflow**, choosing `main`.

The workflow runs both Python test suites, checks the case study and public build, and compares the browser worker's actual Pyodide results with the native Python reports. If these jobs pass and Pages is enabled, it deploys the built site. Until that initial setting is enabled, tests and the site artifact can still complete, and deployment is explicitly skipped.

Use the deployment's returned URL as the live address. A committed interface, passing tests or a generated artifact alone does not establish a published site.

## Verification

`tests/test_browser_engine.cjs` exercises the real worker handler and pinned Pyodide runtime under Node, with worker APIs supplied by the test harness. Four fixtures must exactly match native Python JSON reports; six malformed or oversized inputs must be rejected. This verifies engine parity, not browser layout or UI interactions.

The Python build test confirms that the public site includes the original checker and only an explicit list of public assets. The workflow also checks JavaScript syntax. Browser UI verification is a separate step once a reachable preview or deployment is available.

## Dependencies

The Python CLI still has no external dependencies. The browser demo adds Pyodide; the hosted worker-engine verification installs the same exact npm version. GitHub workflow actions are pinned to reviewed release commit SHAs. See [Pyodide's documentation](https://pyodide.org/en/stable/usage/quickstart.html) and [GitHub's Pages setup guide](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
