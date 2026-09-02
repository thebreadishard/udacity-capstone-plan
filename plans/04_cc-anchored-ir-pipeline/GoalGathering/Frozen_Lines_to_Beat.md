# Frozen lines to beat — Plan 04

**Status.** Frozen 2026-09-02 (survey pass of that date). This file names the opponents.
After a comparison against a line has been **scored**, that line may not be swapped,
re-versioned, or reweighted; before that, changes require a dated note. Verify-on-use still
applies: every identifier below is re-fetched before it enters a scored Module 03–09 document.

**The criterion (from [Overarching_Goal.md](Overarching_Goal.md)).** The pipeline's band
positions for a molecule must be demonstrably more accurate than the best prediction
currently available anywhere for that molecule, judged per band against laboratory data —
**where that data can decide the comparison**: gas-phase rungs unconditionally, matrix-scored
families only if the M03-measured matrix–gas delta is smaller than the beat margin (Ladder
§2, Promised), and never on reach rungs. "Best available" is what this file freezes.

---

## 1. The world map (as measured on 2026-09-02)

| Method front | Reaches | Keeper | Verified how |
|---|---|---|---|
| Scaled harmonic DFT | **C₃₈₆** (4-31G above 200 C) | PAHdb theoretical v4.00 | v4.00 paper full text, 2026-09-02 |
| MLMD anharmonic (DFT teacher) | **C₂₁₆** | Mai et al. 2025 | arXiv abstract v3, 2026-09-02 |
| QFF/VPT2 anharmonic | **C₁₈** (PAHdb) / **C₂₄** (Mulas) | PAHdb Anharmonic v1.00; Mulas 2018 | PAHdb versions page, 2026-09-02; Mulas identifiers from plan-02 bib |
| CC-quality vibrations | ~benzene/naphthalene | scattered literature | plan-02 record; no PAH-scale product exists |

Between C₁₈ and C₃₈₄ no anharmonic-beyond-DFT or CC-anchored prediction exists. For
C₃₈₄H₄₈-class species (the 101–386-carbon bin) the **only** predictions on Earth are scaled
harmonic B3LYP/4-31G. Whether C₃₈₄H₄₈ *itself* has a v4.00 entry is **not verified** — the
evidence on file is the size bin plus NASA's own fit parameter N_carbon,max = 384, and a fit
parameter is not a species entry (debt 6; an M02 atlas task). The R6 target species is chosen
from what the atlas actually contains.

## 2. Line A — PAHdb v4.00 scaled harmonic (the breadth line)

- **What.** NASA Ames PAH IR Spectroscopic Database, library of computed spectra
  **version 4.00** (2024-06-27): **10,749 species**, B3LYP, 6-31G* (4-31G above 200 carbons),
  harmonic, three scale factors — 0.964 (C–H stretch ~3 µm), 0.979 (4–9 µm), 0.975 (>9 µm) —
  fitted to 25 gas-phase laboratory bands. Size bins reach 101–386 C (774 species); NASA's own
  Orion Bar fit uses N_carbon,max = 384.
- **Version paper.** Ricca, Boersma, Maragkoudakis, Roser, Shannon, Allamandola,
  Bauschlicher, "The NASA Ames PAH IR Spectroscopic Database: Computational Version 4.00,
  Software Tools, Website, and Documentation", ApJS **282**, 7 (2026).
  DOI `10.3847/1538-4365/ae1c38`. **Verified 2026-09-02** (IOP full text, open access).
- **Scale-factor paper (v3.00).** Bauschlicher, Ricca, Boersma, Allamandola, ApJS **234**, 32
  (2018). DOI `10.3847/1538-4365/aaa019`. Verified via the PAHdb citations block, 2026-09-02.
- **Why it is beatable.** The v4.00 paper itself: systematic uncertainties of the PAHdb
  spectra "are currently unquantified." Plan-02 probes measured the class of error for the
  scaled-harmonic approach (see §6).
- **Role.** The default opponent for every molecule; the *only* opponent at C₃₈₄H₄₈-class
  sizes (the specific R6 species comes from the M02 atlas; see debt 6).

## 3. Line B — anharmonic small-molecule front (the accuracy line)

- **PAHdb Anharmonic library v1.00** (2026-07-01): **45 spectra, C₆H₆ to C₁₈H₁₂**, including
  N/CN/NC substitutions. Verified on the PAHdb versions page, 2026-09-02. Method papers
  (Mackie et al. 2015–2022; Esposito et al. 2024a–c, per the v4.00 outlook section) are
  **not yet individually verified** — fetch before any scored comparison.
- **Mulas, Falvo, Cassam-Chenaï, Joblin**, "Anharmonic vibrational spectroscopy of Polycyclic
  Aromatic Hydrocarbons", JCP **149**, 144102 (2018). DOI `10.1063/1.5050087`,
  arXiv:1809.05669. Identifiers from the plan-02 bibliography (git history, `375f4ab`);
  landing page **not re-fetched since 2026-08** — re-verify at first scored use. Anharmonic
  DFT-QFF for pyrene and coronene; its own stated main limitation is the accuracy of the
  underlying QFF — exactly the CC-anchor gap.
- **Cheap-line marker: Bos et al.**, "Ethereal AI: Infrared Spectra of Polycyclic Aromatic
  Hydrocarbons with Machine Learning DFT Scaling Factors", ACS Omega **10**(50), 62282–62290
  (2025-12-10). DOI `10.1021/acsomega.5c10225`. Bibliographic record **verified via Crossref
  2026-09-02**; the MAE value recorded in plan 02 (~5 cm⁻¹) is **not re-read** (ACS full text
  returned 403) — re-read before quoting a number. Whatever MAE the full text reports, the
  role is fixed: the cheap line defines the cost bar — an anharmonic method must beat
  **ML-corrected** scaling, not merely raw scaling, or it has not earned its cost. The figure
  itself is quoted nowhere in this plan until the re-read.
- **Role.** The bar for benzene-to-tetracene-size rungs, where the pipeline must beat *good*
  predictions, not just broad ones.

## 4. Line C — Mai 2025 MLMD (the scale + temperature line)

- **Mai, Wang, Pan, Schörghuber, Kovács, Carrete, Madsen**, "Computing Anharmonic Infrared
  Spectra of Polycyclic Aromatic Hydrocarbons Using Machine-Learning Molecular Dynamics",
  MNRAS **541**, 3073 (2025); arXiv:2503.05120 (v3, 2025-06-30). **arXiv abstract verified
  2026-09-02**; MNRAS landing page not re-fetched — re-verify at first scored use.
- **What it does.** Anharmonic IR via MLMD for **1,704 PAHdb species up to C₂₁₆, at several
  temperatures**, linear scaling. Its accuracy ceiling is its DFT teacher — the paper's own
  claim is accuracy "comparable to conventional quantum chemical calculations."
- **Role.** The opponent for large rungs and for every temperature-dependent (tier-2) claim.
  On **accuracy rungs** (where its coverage and lab data overlap), beating it means beating
  its *teacher* — which is what the CC anchor is for. On **reach rungs** (R4–R5 sit inside
  its C₂₁₆ coverage) comparisons against it are theory-vs-theory and labelled as such; no
  "beat" is claimed there (Ladder §1).

## 5. Scoreboards (laboratory truth)

Predictions are scored against measurements, never against other predictions, wherever
measurements exist:

| Source | Content | Status |
|---|---|---|
| PAHdb experimental library **v3.10** (2023-04-13) | 84 species, matrix isolation (Ar, ~5–15 K) | versions page verified 2026-09-02; band-read recipe with recorded uids in plan-02 probes (git history) |
| PAHdb gas-phase library **v1.00** (2026-07-01) | 5 spectra (Canadian Light Source), CN-substituted range | versions page verified 2026-09-02 |
| NIST WebBook gas-phase IR | JCAMP-DX per CAS number | working parser + cache recipe in plan-02 probes (git history) |
| IRMPD / jet-cooled literature | e.g. cationic pyrene (Tang et al. 2025, arXiv:2504.11898) | plan-02 record; verify per use |

Matrix data carries a matrix shift; gas-phase is preferred where both exist; the comparison
protocol (which window, which class, which tolerance) is pre-registered per rung in the
ladder freeze, not chosen after the numbers exist.

## 6. The measured floor under the lines (from plan-02 probes, 2026-08)

Recomputable from git history (raw `.npz` preserved in commit `800f3aa`; band-read script
`pahdb_experimental_2026-08-28.py`): scaled harmonic B3LYP/6-31G* with a benzene-only scale
factor vs Ar-matrix lab values — quartet CH-oop band mean |error| **7.1 cm⁻¹** (worst
15.6 cm⁻¹), solo **−36**, duo **−49 cm⁻¹**; lab quartet spread across five 2–4-ring species
**60.2 cm⁻¹**, wider than computed. These numbers set the scale of what "beating the
harmonic line" must mean per band class, and they are already measured, not asserted.

## 7. Open verification debts (before any scored use; identical to the bibliography's list)

1. ACS Omega full text — read the actual MAE (§3).
2. PAHdb Anharmonic v1.00 method papers (Mackie / Esposito) — fetch and pin.
3. MNRAS landing page for Mai 2025; Mulas 2018 landing page — re-fetch.
4. Temperature-dependence lab references for tier 2 (Joblin-era band-shift measurements) —
   identify and pin before any tier-2 pre-registration.
5. DLPNO-CCSD(T) / ORCA method citations — still unpaid; the Sylvetsky & Martin identifier was
   pinned 2026-09-02 (bibliography item 15, during the Pass B review) and needs re-verifying
   at scored use.
6. Whether C₃₈₄H₄₈ itself (vs. same-bin species) has a PAHdb v4.00 entry — check by
   boundary-edge/formula search before the top rung is worded.
