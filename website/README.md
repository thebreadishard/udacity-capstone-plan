# website/ — the public front door of the pipeline (design stage)

Created 23 September 2026 at the user's request: a public, well-designed website with a dashboard of the molecules whose spectra the
pipeline has predicted — "a bit like NASA's PAHdb, but more modern", with a molecule image per entry, options for a visitor to find out
whether a molecule has been through the pipeline, and later a button to start the pipeline for a molecule. Built in small steps on slow
moments.

- `DESIGN_2026-09-23.md` — the design: audiences, the status ladder, information architecture, the molecule page, visual and mobile design,
  accessibility, the request flow, architecture, evidence rules, open decisions, sources.
- `BACKLOG.md` — the build order; each step fits a quiet hour and leaves something working.
- `site/` — the Astro site (design §9): `npm install && npm run build` in `website/site/` after the export has run; `npm run preview` serves it on
  127.0.0.1:4321 (also the `atlas` entry of `.claude/launch.json`). Zero client JavaScript so far; islands come with steps 5–7.
- `export/` — the mechanical export from the pipeline repository to the site's JSON (`build_catalog.py`, `depict.py`, `SCHEMA.md`, `tests/`; output in
  `export/out/`, not committed). The only code that lives here. The site itself will be its own repository so that it can never touch the
  pipeline's run directories.

Published 24 September at <https://thebreadishard.github.io/spectrum-atlas/> from the public repository
`thebreadishard/spectrum-atlas` (built site only; `website/deploy.sh` publishes; the source stays here). Decisions of 23 September 22:1x (design §12): name Spectrum Atlas, scope "molecules" (broader than PAHs), uncomputed rows shown, GitHub Pages first,
CC BY 4.0 / MIT, English, sign-in only for feeding the pipeline. Nothing is built yet. Rules that apply here as everywhere in this repository: every number traces to a file; commit named paths only;
nothing here runs compute.
