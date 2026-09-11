# Module 03 — provenance and status (project notes; not part of the Udacity submission text)

**Required sentence.** These are laboratory measurements from the public PAHdb experimental libraries
and NIST WebBook. Not synthetic, not AI-generated, not the Module 02 dataset.

## Sources and how they were obtained

| side | source | file(s) | obtained how |
|---|---|---|---|
| matrix | PAHdb **experimental** library v3.10 (2023-04-13), 84 species, 3,896 bands; Ar matrix (Mattioda et al. 2020; the 1998 species: Hudgins & Sandford 1998, 10 K, 0.9 cm⁻¹) | Module 02's parse `../02_opponent_atlas/out/experimental_3.10/{bands.csv.gz,species.csv}` of the XML (sha256 `b8b48777…`) | PAHdb download form, filled by the student (2026-09-10) |
| gas, GC-IRD | NIST Chemistry WebBook, `$NIST SOURCE=MSDC-IR` (NIST/EPA gas-phase IR database, SRD 35): benzene, naphthalene, anthracene, pyrene, triphenylene, chrysene | `plans/04_cc-anchored-ir-pipeline/probes/nist_cache/*.jdx`, anthracene from `plans/02_…/probes/nist_cache/` | plan-02/plan-04 WebBook cache (JCAMP), already in git |
| gas, other | Coblentz naphthalene vapour (245 °C, 4 cm⁻¹) and benzene cell (2 cm⁻¹) records | same caches | same |
| gas, R0 | NIST Quantitative IR benzene record, 0.125 cm⁻¹ (Chu et al. 1999), as scored by probe 2a | `probes/results_m03/benzene/SCOREBOARD_benzene_quantir_0p125.json` | fetched 2026-09-10 with the user's permission |

Every input's sha256 is printed in `out/SUMMARY.md` by the builder. The dataset (`notebook/bands_lab.csv`,
0.6 MB) and the pairs are committed; nothing in `data/` (none needed here).

## What was fixed before the data were joined

`PRE_REGISTRATION.md` (commit 5d946d2, 2026-09-11): the four species, the primary record per species,
the peak rule (prominence ≥ 5 σ, S/N ≥ 10, parabolic apex), the ±20 cm⁻¹ largest-intensity one-to-one
match, Δ = ν_matrix − ν_gas, the Module 02 family rule on the gas position, n_min = 6, the Wilcoxon
signed-rank test, α = 0.05 with Holm, the declared secondary pooled test, the printed-not-tested
statistics. The builder and notebook implement it without change.

## Status

- 2026-09-11: module scaffolded in the Udacity rubric form (Rubrics/03) on branch
  `module-03-lab-scoreboard`: pre-registration → builder → dataset (4,218 × 21) and 74 pairs (63 primary)
  → `notebook/analysis.ipynb` (descriptive statistics, three figures, the test) → `module_summary.pdf`
  in the APA 7 template with Lusa et al. (2024) and a Crossref/DataCite-verified References list.
  **Result (printed by the notebook):** six families tested, all reject a zero matrix−gas offset after
  Holm (median +3.3 to +5.9 cm⁻¹, matrix above hot gas); C–H stretch (n = 4) and low/skeletal (n = 5)
  inconclusive by construction; pooled p = 1.6 × 10⁻¹⁰ (secondary); naphthalene's 245 °C column median
  +1.4 cm⁻¹ (n = 11).
- **What this is and is not for the plan.** It is the first measured matrix–gas number for the Ladder §2
  matrix gate (pilot-note item 4) — an *offset between the sources as they exist* (10 K matrix against a
  hot lightpipe vapour), not the matrix shift at equal temperature. The pilot note, not this module,
  fixes the beat margins and the verdicts.

## Owed (before submission, due per proposal §12, and for the plan)

- The student's own pass over notebook, README and summary.
- The u_band columns of the Ladder rule on these gas records (temperature term per decision 29 and the
  Ladder floor; the probe-2a script extended from benzene to the GC-IRD and Coblentz records) — the
  dataset carries u_res and u_c only.
- The PNNL/NWIR naphthalene record (items 57, 59; not held), the jet-cooled tetracene and coronene band
  lists (items 61–62) as labelled cold columns, the R2/R3 scoreboard columns, and the intensities of
  decision 18.
- Family labels by DFT mode vector (naphthalene dry-run mode table) in place of the frequency-range rule.
- Item 50's description PDF read in full (the 8.0 cm⁻¹ statement is snippet grade) and the lightpipe
  temperature; the Hudgins & Sandford conditions read for the non-1998 matrix species (Mattioda series).

## Files

- `build_lab_tables.py` — dataset + pairs + `out/SUMMARY.md`; imports the JCAMP reader of `probes/m03_band_uncertainty.py`.
- `notebook/make_notebook.py` → `notebook/analysis.ipynb`, `notebook/figures/fig1–3`, `notebook/test_results.json`.
- `make_summary.py` → `module_summary.docx/.pdf` (template `Rubrics/APA7_template.docx`).
- `README.md` (rubric form), `requirements.txt` (`pip freeze`).
