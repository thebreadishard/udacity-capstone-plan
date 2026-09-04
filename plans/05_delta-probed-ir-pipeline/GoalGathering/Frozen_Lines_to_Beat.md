# Frozen lines to beat — Plan 05

**Status.** Carried from plan 04 **unchanged in substance** on 2026-09-03: the opponents,
scoreboards, measured floor and verification debts are plan 04's, frozen 2026-09-02 (survey
pass of that date). Plan 05 changes how the pipeline is built, not whom it is scored against.
After a comparison against a line has been **scored**, that line may not be swapped,
re-versioned, or reweighted; before that, changes require a dated note. Verify-on-use still
applies: every identifier below is re-fetched before it enters a scored Module 03–09 document.

**The criterion (from [Overarching_Goal.md](Overarching_Goal.md)).** The pipeline's band
positions for a molecule must be demonstrably more accurate than the best prediction
currently available anywhere for that molecule, judged per band against laboratory data —
**where that data can decide the comparison**: gas-phase rungs unconditionally, matrix-scored
families only if the M03-measured matrix–gas delta is smaller than the beat margin (Ladder
§2, Promised), and never on reach rungs.

---

## 1. The world map (as measured on 2026-09-02; no new fetch on 2026-09-03)

| Method front | Reaches | Keeper | Verified how |
|---|---|---|---|
| Scaled harmonic DFT | **C₃₈₆** (4-31G above 200 C) | PAHdb theoretical v4.00 | v4.00 paper full text, 2026-09-02 |
| MLMD anharmonic (DFT teacher) | **C₂₁₆** | Mai et al. 2025 | arXiv abstract v3, 2026-09-02 |
| QFF/VPT2 anharmonic | **C₁₈** (PAHdb) / **C₂₄** (Mulas) | PAHdb Anharmonic v1.00; Mulas 2018 | PAHdb versions page, 2026-09-02; Mulas identifiers from plan-02 bib |
| CC-quality vibrations | ~benzene/naphthalene | scattered literature | plan-02 record; no PAH-scale product exists |

Between C₁₈ and C₃₈₄ no anharmonic-beyond-DFT or CC-anchored prediction exists. For
C₃₈₄H₄₈-class species (the 101–386-carbon bin) the **only** predictions found are scaled
harmonic B3LYP/4-31G. Whether C₃₈₄H₄₈ *itself* has a v4.00 entry is **not verified** (debt 6;
an M02 atlas task). The 2026-09-03 search for plan 05 (Research note §6) found no new entry
in this table — no CC-anchored PAH spectrum above naphthalene size. What it *did* find, and
Round-7 Pass B added, is the Concordant Mode Approach (bibliography items 42–43): CCSD(T)
force constants in a DFT normal-mode basis from single-point energies, on small molecules —
prior art for plan 05's diagonal recovery, not an opponent line (it produces no PAH spectra).

## 2. Line A — PAHdb v4.00 scaled harmonic (the breadth line)

- **What.** NASA Ames PAH IR Spectroscopic Database, computed library **version 4.00**
  (2024-06-27): **10,749 species**, B3LYP, 6-31G* (4-31G above 200 carbons), harmonic, three
  scale factors — 0.964 (C–H stretch ~3 µm), 0.979 (4–9 µm), 0.975 (>9 µm) — fitted to 25
  gas-phase laboratory bands. Size bins reach 101–386 C (774 species); NASA's own Orion Bar fit
  uses N_carbon,max = 384.
- **Version paper.** Ricca, Boersma, Maragkoudakis, Roser, Shannon, Allamandola, Bauschlicher,
  ApJS **282**, 7 (2026). DOI `10.3847/1538-4365/ae1c38`. **Verified 2026-09-02** (IOP full
  text, open access).
- **Scale-factor paper (v3.00).** Bauschlicher, Ricca, Boersma, Allamandola, ApJS **234**, 32
  (2018). DOI `10.3847/1538-4365/aaa019`. Verified via the PAHdb citations block, 2026-09-02.
- **Why it is beatable.** The v4.00 paper itself: systematic uncertainties of the PAHdb spectra
  "are currently unquantified." Plan-02 probes measured the class of error (§6).
- **Role.** The default opponent for every molecule; the *only* opponent at C₃₈₄H₄₈-class
  sizes.

## 3. Line B — anharmonic small-molecule front (the accuracy line)

- **PAHdb Anharmonic library v1.00** (2026-07-01): **45 spectra, C₆H₆ to C₁₈H₁₂**, including
  N/CN/NC substitutions. Verified on the PAHdb versions page, 2026-09-02. Method papers
  (Mackie et al. 2015–2022; Esposito et al. 2024a–c) **not yet individually verified**.
- **Mulas, Falvo, Cassam-Chenaï, Joblin**, JCP **149**, 144102 (2018). DOI `10.1063/1.5050087`,
  arXiv:1809.05669. Identifiers from the plan-02 bibliography; re-verified by plan 04's Pass B
  reviewer on 2026-09-02 (arXiv); full text read by plan 05's Pass B reviewer on 2026-09-03.
  Anharmonic **B97-1** QFF (TZ2P pyrene, 6-31G* coronene) for pyrene and coronene; its own
  stated limitation is the accuracy of the underlying QFF — exactly the CC gap. The P2
  comparison against this line is functional-specific.
- **Cheap-line marker: Bos et al.**, "Ethereal AI: Infrared Spectra of Polycyclic Aromatic
  Hydrocarbons with Machine Learning DFT Scaling Factors", ACS Omega **10**(50), 62282–62290
  (2025-12-10). DOI `10.1021/acsomega.5c10225`. Record **verified via Crossref 2026-09-02**;
  the MAE value **not re-read** (ACS 403) — the figure is quoted nowhere in this plan until the
  re-read. Role fixed: an anharmonic method must beat **ML-corrected** scaling, not merely raw
  scaling, or it has not earned its cost.
- **Role.** The bar for benzene-to-tetracene-size rungs.

## 4. Line C — Mai 2025 MLMD (the scale + temperature line)

- **Mai, Wang, Pan, Schörghuber, Kovács, Carrete, Madsen**, MNRAS **541**, 3073 (2025);
  arXiv:2503.05120 (v3). **arXiv abstract verified 2026-09-02**; MNRAS landing page not
  re-fetched (debt 3).
- **What it does.** Anharmonic IR via MLMD for **1,704 PAHdb species up to C₂₁₆, at several
  temperatures**, linear scaling; accuracy "comparable to conventional quantum chemical
  calculations" — its DFT teacher's ceiling.
- **Role.** Opponent for large rungs and every tier-2 claim; on accuracy rungs beating it means
  beating its teacher; on reach rungs comparisons are theory-vs-theory and labelled as such.

## 5. Scoreboards (laboratory truth)

| Source | Content | Status |
|---|---|---|
| PAHdb experimental library **v3.10** (2023-04-13) | 84 species, matrix isolation (Ar, ~5–15 K) | versions page verified 2026-09-02; band-read recipe with recorded uids in plan-02 probes (git history) |
| PAHdb gas-phase library **v1.00** (2026-07-01) | 5 spectra (Canadian Light Source), CN-substituted range | versions page verified 2026-09-02 |
| NIST WebBook gas-phase IR | JCAMP-DX per CAS number | working parser + cache recipe in plan-02 probes; **coverage probe run** under plan 04 (gas IR present for benzene, naphthalene, pyrene, chrysene, triphenylene; tetracene solid-only; coronene absent; the R2 gas grids are ~4 cm⁻¹) — raw evidence in plan 04's `probes/nist_cache/`, to be re-run under plan 05's hash; the R2 row of the Ladder was re-read against it (dated note there) |
| IRMPD / jet-cooled literature | e.g. cationic pyrene (Tang et al. 2025, arXiv:2504.11898) | context only for neutral rungs; verify per use |

Matrix data carries a matrix shift; gas-phase is preferred where both exist; the comparison
protocol is pre-registered per rung in the pilot note, not chosen after the numbers exist.

## 6. The measured floor under the lines (plan-02 probes, 2026-08)

Recomputable from git history (raw `.npz` preserved in commit `800f3aa`; band-read script
`pahdb_experimental_2026-08-28.py`): scaled harmonic B3LYP/6-31G* with a benzene-only scale
factor vs Ar-matrix lab values — quartet CH-oop band mean |error| **7.1 cm⁻¹** (worst
15.6 cm⁻¹), solo **−36**, duo **−49 cm⁻¹**; lab quartet spread across five 2–4-ring species
**60.2 cm⁻¹**, wider than computed. These numbers set the scale of what "beating the harmonic
line" must mean per band class.

## 7. Open verification debts (before any scored use; identical to the bibliography's "Named debts")

1. Bos 2025 full text → the actual MAE (item 7).
2. Mackie/Esposito anharmonic method papers (item 12).
3. MNRAS landing for Mai 2025 (item 5); Mulas 2018 landing re-fetch (item 6).
4. Joblin-era T-dependence references (item 20).
5. Local-CC method and software citations — the DLPNO-CCSD(T) method papers (item 17, NOT
   FETCHED) and the Mester et al. 2025 MRCC overview (item 34, second identifier); items 32,
   33 and 34's Nagy & Kállay are OK; Sylvetsky pinned.
6. C₃₈₄H₄₈ per-species presence in PAHdb v4.00 — an M02 task.

Debts that concern plan 05's *method* rather than its opponents (full texts of items 27, 28,
30, 37; the O1NumHess code version; the GPU Hessian timing) are listed only in the
bibliography under "Method debts" and are not part of this list.
