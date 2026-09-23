# Spectrum Atlas — build order for slow moments

Each step is small enough for a quiet hour, leaves something that works, and never touches the pipeline's run directories. Steps 1–3 need
no design decision from the user; step 4 onward benefits from the answers to `DESIGN_2026-09-23.md` §12. No step runs compute.

| # | step | result | depends on |
|---|---|---|---|
| 0 | ~~user reads the design; decisions §12~~ **done 23 Sep 22:1x** (name, scope, rows shown, GitHub Pages, licences, English, access policy) | a name, hosting, licence | — |
| 1 | `export/build_catalog.py` (Python, in this repository): manifest + ledger + results + releases + second route → `catalog.json`, per-molecule JSON, rung counts; a check that every exported number exists in a source; unit tests on three molecules | the data contract, mechanical | — |
| 2 | `export/depict.py`: RDKit SVG depictions for the computed molecules, themed via CSS variables; alt-text strings | 244 SVGs | 1 |
| 3 | JSON schema for `catalog.json` and `molecule.json` (documented in `export/SCHEMA.md`) | a stable contract for the site | 1 |
| 4 | the site repository: Astro 5 skeleton, tokens (light/dark), Home · Atlas · Molecule from static JSON; no islands yet | a browsable static site, locally | 0, 3 |
| 5 | spectrum viewer island (dual axis, sticks/broadened, band for uncertainty, CSV/JSON download, table twin) | the molecule page's centre | 4 |
| 6 | search island (MiniSearch over the catalogue; composition syntax; URL state) and filters (rail + bottom sheet) | the atlas works | 4 |
| 7 | 3D island (3Dmol.js, on tap, from corpus geometry) | the public's toy | 4 |
| 8 | mobile pass on real phones (bottom nav, sheets, scrubber, targets) | the mobile variant | 5–7 |
| 9 | accessibility pass: axe in CI, keyboard walk, screen-reader session, contrast check of the tokens | WCAG 2.2 AA | 8 |
| 10 | Status and Methods pages from the ledger and the architecture sheets | the honest pages | 4 |
| 11 | deploy (GitHub Pages or Cloudflare Pages), nightly build on the pipeline's release tags, footer freshness stamp | public | 0, 9 |
| 12 | "Notify me" card (phase 1 of requests) | the reserved space filled | 11 |
| 13 | phase 2: request queue (FastAPI, OAuth, worker on rented servers, budget cap), ledger writes | requests | the licensed layer |

Working rules: commit only named paths; the export script gets tests before promotion; the site's numbers come from the export, never
from templates; corrections are dated addenda on the Status page.
