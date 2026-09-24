# Spectrum Atlas — build order for slow moments

Each step is small enough for a quiet hour, leaves something that works, and never touches the pipeline's run directories. Steps 1–3 need
no design decision from the user; step 4 onward benefits from the answers to `DESIGN_2026-09-23.md` §12. No step runs compute.

| # | step | result | depends on |
|---|---|---|---|
| 0 | ~~user reads the design; decisions §12~~ **done 23 Sep 22:1x** (name, scope, rows shown, GitHub Pages, licences, English, access policy) | a name, hosting, licence | — |
| 1 | ~~`export/build_catalog.py`~~ **done 24 Sep 07:0x**: manifest + ledger + results + releases + second route → `catalog.json` (11,321 rows), 244 per-molecule JSONs, `summary.json` with rung counts; invariants fail the build; six pytest tests on the real corpus | the data contract, mechanical | — |
| 2 | ~~`export/depict.py`~~ **done 24 Sep 07:1x**: RDKit SVGs with carbons in `currentColor` and heteroatoms in `var(--accent)`, alt text from name and formula; 244 computed + all 5,266 rows with a SMILES (≈ 10 kB each, 51 MB; layer C has no SMILES yet) | the depictions | 1 |
| 3 | ~~JSON schema~~ **done 24 Sep 07:0x**: `export/SCHEMA.md` (fields, sources, the ladder, flags, invariants, what is not yet in the contract) | a stable contract for the site | 1 |
| 4 | ~~the site skeleton~~ **done 24 Sep 07:2x** in `website/site/` (Astro 5.18, zero client JS): tokens in OKLCH with light/dark, Base layout with desktop top bar and mobile bottom nav (44 px targets), Home with the ladder from `summary.json`, Atlas with the 244 computed molecules as cards with inline SVG depictions, Molecule pages (header, depiction, ladder with dates and evidence links, frequency table, second route, provenance), Status, Methods, About; 249 pages build in 3 s; checked at 375 px and 1200 px (no horizontal overflow). Moves to its own repository at deploy (step 11) | a browsable static site, locally | 0, 3 |
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
