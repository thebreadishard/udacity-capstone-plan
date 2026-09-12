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
  `module-03-lab-scoreboard`: pre-registration → builder → dataset (4,218 × 21; × 31 since 2026-09-12) and 74 pairs (63 primary)
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

- **2026-09-12: u_band columns added (Ladder rule; the test is untouched — positions only).** For every gas peak
  the builder now prints the temperature term and u_band = √(u_res² + u_c² + u_T²) with, for the hot sources, the
  Ladder's floor form u_T = χ_F·(T_source − 296 K) + u_296: χ_F from Joblin et al. (1995, item 52, Table 1) — the
  molecule's own slope where measured (naphthalene and pyrene C–H stretch, pyrene 8.5 and 12 µm), pyrene's as a
  labelled stand-in, the 0.044 cm⁻¹ K⁻¹ floor elsewhere; u_296 by the Bose rule with ν_m = mean PAHdb theoretical
  v4.00 unscaled mode below 700 cm⁻¹ (417–441 cm⁻¹ for the four primary species; benzene 553.8 from probe 2a);
  T_source 523.15 K for the GC-IRD lightpipe (250 °C recalled default, item 50 owed), 518.15 K for the Coblentz
  245 °C column. **Printed result (`out/U_BAND.md`, 75 record × family rows):** on the four primary GC-IRD
  records u_band is 8.6 cm⁻¹ (C–H in-plane bend), 9.6 (C–H out-of-plane), 10.2–12.1 (C–H stretch) and
  15.9–16.2 cm⁻¹ (all floor-slope families); none of the 63 primary pairs is decidable at the candidate margins
  2 or 5 cm⁻¹, 17 at 10 (C–H bend families only); on the Coblentz 245 °C naphthalene column 5.1–14.1 cm⁻¹
  (3 pairs decidable at 10). The R0 benzene rows keep probe 2a's 2.55 cm⁻¹. This is the Ladder's "inconclusive
  by construction on the hot WebBook source" expectation, now measured; R1's decidability rests on the PNNL
  record as the Ladder already says. Not a verdict on any family — the pilot note fixes margins and chooses
  between the floor form and the ±30 % corrected form (δ_T is printed beside u_T for that).

## Owed (before submission, due per proposal §12, and for the plan)

- The student's own pass over notebook, README and summary.
- ~~The u_band columns of the Ladder rule on these gas records~~ — **done 2026-09-12** (see Status): the
  dataset carries `temperature_K`/`temperature_source`, `chi_F_cm_per_K`/`chi_F_source`, `nu_m_cm`/`nu_m_source`,
  `u_296_cm`, `delta_T_cm`, `u_T_cm`, `u_band_cm`, `u_band_without_T_cm`; the pairs carry `u_T_gas_cm`,
  `u_band_gas_cm` and `decidable_at_2/5/10`; per record and family in `out/U_BAND.md`. Still open inside it:
  the GC-IRD lightpipe temperature (250 °C recalled until item 50's PDF is read) and the ±30 % corrected
  form, which the pilot note may choose over the floor form.
- The PNNL/NWIR naphthalene record (items 57, 59; not held), the jet-cooled tetracene and coronene band
  lists (items 61–62) as labelled cold columns, the R2/R3 scoreboard columns, and the intensities of
  decision 18.
- Family labels by DFT mode vector (naphthalene dry-run mode table) in place of the frequency-range rule.
- ~~Item 50's description PDF read in full~~ — **done 2026-09-12 evening**: the 8.0 cm⁻¹ conversion is now read, not snippet grade; the guide gives **no temperature** for either subset ("analytical conditions are not given" for the EPA/Sadtler spectra), so the 250 °C stays an assumption, now labelled per record origin (EPA/Sadtler: naphthalene, anthracene, benzene GC-IRD; NIST HP 5965: pyrene, chrysene, triphenylene). Still open: the lightpipe
  temperature; the Hudgins & Sandford conditions read for the non-1998 matrix species (Mattioda series).

## Files

- `build_lab_tables.py` — dataset + pairs + `out/SUMMARY.md`; imports the JCAMP reader of `probes/m03_band_uncertainty.py`.
- `notebook/make_notebook.py` → `notebook/analysis.ipynb`, `notebook/figures/fig1–3`, `notebook/test_results.json`.
- `make_summary.py` → `module_summary.docx/.pdf` (template `Rubrics/APA7_template.docx`).
- `README.md` (rubric form), `requirements.txt` (`pip freeze`).
