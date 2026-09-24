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
| 5 | spectrum viewer: **first half done 24 Sep 07:2x** — `components/Spectrum.astro` renders a stick spectrum at build time as SVG (two series, Okabe–Ito colours, wavenumber axis below and micron axis above, accessible title/desc, table twin on the page; no client JS). Still to do as an island: zoom/pan, broadened lines, the uncertainty band once rung 3 exists, CSV/JSON download | the molecule page's centre | 4 |
| 6 | search: **first half done 24 Sep 07:3x** — `components/AtlasSearch.astro` (vanilla script, no dependency) searches all 11,321 rows by name, formula, SMILES or id with status and layer filters, URL state, results table with links to computed pages; the catalogue is a 715 kB build-time endpoint loaded on first use. Still to do: PAHdb composition syntax, substructure (RDKit.js), element and size filters as a rail / bottom sheet, cards for uncomputed rows | the atlas works | 4 |
| 7 | ~~3D island~~ **done 24 Sep 07:3x**: `components/Viewer3D.astro` — a "Show 3D" button; 3Dmol.js (npm 2.5.5) is imported only on tap (166 kB compressed chunk), the corpus geometry is shown as sticks, the canvas is aria-hidden and the 2D depiction stays the accessible form; verified in the browser pane | the public's toy | 4 |
| 8 | mobile pass on real phones (bottom nav, sheets, scrubber, targets) | the mobile variant | 5–7 |
| 9 | accessibility pass: axe in CI, keyboard walk, screen-reader session, contrast check of the tokens | WCAG 2.2 AA | 8 |
| 10 | ~~Status and Methods pages~~ **done 24 Sep 07:3x**: Status lists the ledger as a changelog (export `changelog.json`, 131 entries newest first); Methods reads six architecture sheets from the repository at build time, shows their sources and renders them on tap with a lazy mermaid island (601 kB on tap, sources stay readable without JavaScript). Still open: what-is-running from the run logs | the honest pages | 4 |
| 11 | deploy: **done 24 Sep 08:1x** — public repository github.com/thebreadishard/spectrum-atlas (the user: "Maak de publieke repo maar aan. De 0 euro opties zijn prima."), GitHub Pages from the `gh-pages` branch at https://thebreadishard.github.io/spectrum-atlas/, base path wired through `src/lib/base.ts`, `website/deploy.sh` builds and force-pushes `dist/` (with `.nojekyll`, README, LICENCE); the source stays in this monorepo. Still to do: a nightly/tag-triggered build; the footer already carries the freshness stamp | public | 0, 9 |
| 12 | "Notify me" card (phase 1 of requests) | the reserved space filled | 11 |
| 13 | phase 2: request queue (FastAPI, OAuth, worker on rented servers, budget cap), ledger writes | requests | the licensed layer |

Working rules: commit only named paths; the export script gets tests before promotion; the site's numbers come from the export, never
from templates; corrections are dated addenda on the Status page.
