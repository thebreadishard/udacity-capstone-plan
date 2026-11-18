# Pre-registration: aromir's acceptance runs before the weights go to the Hugging Face Hub (TASKS 269), 18 November 2026

Written before any of these runs. The six criteria were agreed by the user on 18 Nov (TASKS 269); this note fixes what criteria
1–3 compute and when each passes. The runs wait until the laptop is free of the search `v14_stage1`, its stage 2 and final chain,
and the demo folders of TASKS 246 (the parent session's order, 18 Nov 15:0x). Everything below runs through `tools/runspec.py`.

## The release under test

aromir `main` at the commit that lands branch `acceptance-269` (TASKS 266 and the v1.4 audit's answers), installed from GitHub
into a fresh environment, with the bundled v1.4 release networks. The capstone pipeline (`m08.pipeline`) with the carried v1.4
release networks, at the master commit of the day the runs start. Both commits go into the record.

## Criterion 1: a clean install runs end to end

- Linux (WSL 2, Ubuntu 26.04): a fresh venv (`~/aromir_clean_269`, Python 3.12) with the README's two commands, then
  `aromir spectrum c1ccccc1`. Native Windows: a fresh venv (`C:\Users\thebr\aromir_win269`, Python 3.14) the same way. The
  install alone passed on 18 Nov for both, with `aromir check` and a water B3LYP/6-31G* Hessian equal on both to every printed
  digit (`probes/results_m1/aromir_clean_install_2026-11-18`).
- **Passes** when each exits 0 with a certificate of 30 bands, and the two certificates' corrected positions agree within
  0.5 cm⁻¹ band by band (the engine's noise between platforms at the printed 0.1 cm⁻¹, with geometry optimisation in between).
  Run time and peak memory are recorded for each.

## Criterion 2: aromir against the pipeline

**The set** (`probes/results_m1/aromir_acceptance_2026-11-18/select_set.py`, its rule written in the script before it ran;
`fixed_set.json`): benzene; the eight molecules of hold-out (a) as v1.4 reads it — benzene is one of them, so the set has **18
molecules**, not 19; the three smallest fluorene and the two smallest fluoranthene children of hold-out (b); five molecules the
corpus does not hold: 4-methylthioanisole, 2-chloro-4-fluoroanisole, 3-fluoro-4-methylbenzonitrile, 5-chlorothiophene-2-
carbonitrile, 5-fluoro-2-methylbenzothiazole (the first five of the script's candidate list that aromir admits and the corpus
lacks; the first pass found five of the eight first candidates in the corpus, and the list was extended before the second pass).

**The runs.** aromir: `aromir spectrum <SMILES>` in the clean WSL environment, 4 threads. The pipeline: `python -m m08.pipeline`
as it runs for a user, which for a corpus molecule takes the corpus's psi4 geometry and stored analytic Hessian (step 1's reuse)
and for the five new ones computes them (psi4 optimisation, pyscf Hessian). Run time and peak memory per molecule and per tool.

**Three comparisons, and when each passes:**

1. *Same input, two codes.* aromir's correction (`Release.corrections`) on the pipeline's own geometry and B3LYP Hessian, in the
   pipeline's atom order, against the pipeline's stored ΔH (`correction.npz`) and its corrected wavenumbers. **Passes** when every
   corrected wavenumber agrees within **0.01 cm⁻¹** for every molecule (the conversion check of v1.3 found 2.4e-7 over 76 molecules;
   aromir evaluate and product_error.py agree to 0.0048 cm⁻¹ on v1.4's hold-outs).
2. *End to end, B3LYP.* Each tool's B3LYP harmonic positions, band by band in order. **Passes** when, per molecule, the rms over all
   bands is ≤ **1.0 cm⁻¹** and every band above 200 cm⁻¹ is within **2.0 cm⁻¹**. Basis: the two chains optimise with different
   engines (psi4, density-fitted, grid (75, 302); pyscf, (99, 590)), and a geometry from another SMILES writing moved phenanthrene's
   B3LYP bands by 0.36 cm⁻¹ (30 Oct 2026); bands below 200 cm⁻¹ are reported, not judged.
3. *End to end, corrected.* The same rule on the corrected positions. Where comparison 3 fails and 1 and 2 pass, the excess is put
   down to the atom order (the network is not order-free) and is read against criterion 3's measured spread, not passed by it.

Beside them, for the 13 corpus molecules: aromir's corrected positions against the stored ωB97X reference, rms per family — the
first audit's K6 number, aromir's own chain at its own geometry.

## Criterion 3: the spread under a rotation, a mirror image and another atom order

v1.4's bundled release on the stored B3LYP geometries and Hessians of the molecules of v1.3's `invariance.json` (benzonitrile,
phenylacetylene, diphenylacetylene with a linear group; benzene, biphenyl, 2-methylnaphthalene, phenol without), the same trials
(8 random rotations, the mirror image, 12 shuffled xyz listings, seeded), and the atom-order spread of v1.3's evaluation (three
molecules, five SMILES-writing orders). The records go into v1.4's folder as `invariance.json` and the evaluation's
`atom_order_spread`, so the card and certificate state them. **Passes** when each spread is within the licence line aromir states
(3 cm⁻¹). v1.4 has v1.3's input settings, whose spreads were 5.34, 5.22 and 5.27 cm⁻¹ with a linear group and 10.73 between
SMILES orders; if v1.4's are alike, criterion 3 fails as written, and the report says so — the fix is a retrain with order-free
inputs (aromir's roadmap 1.0), not a number.
