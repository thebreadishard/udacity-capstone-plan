# Plan 01 — Voxel Field PES (FNO-NCA)

**Status: superseded 2026-08-23** by [plan 02](../02_coupled-cluster-anharmonic-ir/). Kept complete
and internally consistent, not as an archive of mistakes. See [../README.md](../README.md) for why
the project turned.

This plan is **coherent, reviewed and not currently being developed**. It is not frozen on
principle — if plan 02's gates fail in a way that makes a bespoke field representation attractive
again, this is a working starting point rather than a historical curiosity. Corrections to factual
errors are therefore allowed here (see *Errata* below).

---

## What this plan was

Learn the electronic energy as a **functional of a continuous 3D electron-density field** rather
than of atom-centred features:

$$E_\theta(\mathbf{R})=\sum_A E^{\mathrm{atom}}_{Z_A}+E_{\mathrm{es}}\big[\rho_{\mathrm{ref}}+\Delta\rho_\theta,\mathbf{R}\big]+\int\varepsilon_\theta\,dV$$

with the promolecular reference \(\rho_{\mathrm{ref}}\) integrated analytically, only the smooth
deformation density \(\Delta\rho_\theta\) on the voxel grid, a hybrid FNO-NCA encoder, and forces by
exact automatic differentiation so that the PES is conservative by construction. Train on own
CCSD(T)/cc-pVTZ labels; freeze the weights; run classical MD; read the IR envelope off the dipole
autocorrelation. No spectral quantity is ever a training target.

**Scored molecules:** H₂O, D₂O, CO₂, benzene.
**Central question:** under identical energy/force supervision, does a continuous 3D field
representation transfer better to unseen vibrational modes than an equivariant GNN, and what does
explicit density supervision add on top?
**Horizon:** post-master's Projects 10 → 11 → 12, in that order.

## Reading order

1. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — the prime directive
2. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md) — the technical plan, §1–§9
3. [GoalGathering/Capstone_Mapping.md](GoalGathering/Capstone_Mapping.md) — how it maps onto Udacity modules 02–09
4. [Uitleg/00_Leeswijzer.md](Uitleg/00_Leeswijzer.md) — Dutch, VWO-6 level, 21 chapters
5. The three professor reviews, in date order — the record of how the discipline was built

## What it got right, and what killed it

Three review rounds raised fifteen blocking issues; all were closed in spec. The reviews are worth
reading on their own merits — several of the findings are measured, not argued, and the probes in
[probes/](probes/) execute the arithmetic rather than asserting it.

Two of those findings are the reason the plan is superseded, and both are its own:

- **Issue 7** measured that a 0.20 Å grid cannot carry an all-electron density: 11 % electron-count
  error, 3.8 Ha per cell translation artifact. The fix — the promolecular reference split — worked,
  but it established that the representation needed defending rather than paying off.
- **Issue 12** measured the rotation residual at \(1.7\times10^{3}\) meV/Å for the full density
  against \(3\times10^{-5}\) meV/Å for the deformation-only scheme. An equivariant GNN gets exact
  rotational invariance for free.

Neither is a refutation. Together with a literature check the plan had not yet run, they made the
cost of the representation visible against what it bought.

## Errata

Known factual errors in this plan's documents, listed rather than silently patched:

| Document | Error | Status |
|---|---|---|
| `GoalGathering/Relevant_Scientific_Papers.md` item 4 | Attributed to "Nandi et al." with a paraphrased title. The stored PDF (`Papers/04_Kaser2021_TransferLearning_CCSDT.pdf`, arXiv:2103.05491) is Käser, Boittier, Upadhyay & Meuwly, *"MP2 Is Not Good Enough: Transfer Learning ML Models for Accurate VPT2 Frequencies"*, JCTC 2021. `Papers/README.md` always had it right; the bibliography prose did not. | **Corrected** |
| `GoalGathering/Relevant_Scientific_Papers.md` item 12 | Summarised as "brought MLMD methodology to aromatic systems". Understates it: Mai et al. computed 1,704 PAHdb species up to 216 carbon atoms. | **Corrected**, with the consequence noted |
| `GoalGathering/Relevant_Scientific_Papers.md` item 15, study 2 | Described as identifying "the isotopic makeup of deep space PAHs". It is size/charge classification (random forest, F1 = 0.963), not identification of named species. | **Corrected**; study 1 marked unverified |

These are bibliography errors, independent of the pivot. They were found while scoping plan 02 and
are fixed here too, because this plan is a plan and not a snapshot.

## Not shared with plan 02

`Uitleg/` exists only here — plan 02 has no Dutch explanation yet.

Two folders at the repository root are shared with plan 02 and may not be changed by either:
[`Papers/`](../../Papers/) (literature) and [`Rubrics/`](../../Rubrics/) (the Udacity module
requirements this plan was designed against, version 1.5.1). This plan's own horizon documents
10–12 are **not** rubrics and live in [`GoalGathering/Horizon/`](GoalGathering/Horizon/).
