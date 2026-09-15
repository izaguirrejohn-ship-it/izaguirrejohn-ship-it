# I.O.V portfolio

A static selected-work page for John Izaguirre, published at `/work/` alongside the existing Signal Atlas root demo and NIVQRA `/nivqra/` demo.

## Content and implementation

- Founder story and IOV's approved Strategic Intelligence Studio positioning.
- Two project entries with actual browser screenshots, role, product question, design decision, links to the working demo and original source.
- Expandable build notes describing the Lisbon normalization case and NIVQRA's separate approval responsibilities.
- Operator context and links to the existing IOV contact page and public business email.
- A participant guide and a downloadable plan for the first five usability reviews. Publication does not imply that invitations were sent or sessions took place.

This page is plain HTML and CSS. Core navigation and build notes work without JavaScript. System fonts, explicit image dimensions, lazy-loaded screenshots, visible keyboard focus, a skip link and reduced-motion support keep the page simple to use. No analytics, form endpoint, persistent browser storage or third-party script is added. The host receives ordinary public asset requests.

`scripts/build_demo.py` publishes an explicit allowlist into `_site/work/`. The existing Python build check covers the added assets; the original tools and worker code are unchanged. The two existing demo addresses stay valid.

## Sources and scope

Copy uses the public root README, SELECTED_WORK.md, each package's README, the Lisbon case study and the original NIVQRA authoring workflow. Founder and contact context links to https://iov.agency/operator and https://iov.agency/contact . No customer results, live authority integration or new partnership status is asserted.

Screenshots were captured from the working GitHub Pages demos on 15 September 2026, revision a101510fbbda1ba3c597ba4ee3d5ce8d0f5366b5. Signal Atlas uses the fictional flawed feed; NIVQRA uses the fictional research-purchasing brief. They are actual interface captures, not mockups. The navigation shown predates the new portfolio link. Full-size images can be opened from the page.

## Preview

Follow the root demo's [build instructions](../README.md). Open `/work/` on the resulting local HTTP server. The feedback guide is `/work/feedback.html`.

## Feedback

Use [feedback-guide.md](feedback-guide.md) to organize five initial reviews. Keep completed participant notes private and report only consented, non-identifying learnings publicly. A successful usability session is evidence about that task and participant; it is not a claim of product-market fit.
