# Capstone mapping — Plan 03 Presence-Update-Rule

Rubrics are `Rubrics/` at repo root, version **1.5.1**, treated as fixed.  
This map is how plan 03 *uses* each rubric rather than fighting it.

The clause “must not be synthetic or AI-generated” in Modules 02–06 is treated as a **hard constraint**. Self-trained network samples are never a Module 02–06 dataset. Teacher cubes from PySCF/Octopus are computational experiments; they are used as the *scientific* corpus from Module 05 upward, and they are **not** offered as the Module 02–04 CSV.

## Module 02 — AI Programming Foundations

**Rubric need.** Public tabular CSV, \(\ge 200\) rows, \(\ge 5\) columns, not synthetic, no model training.

**Plan 03 use.** A public molecular table that is *about fields and response*, not a cube.

- Primary candidate: **QM9 on Kaggle / Figshare** (134k molecules; dipole, polarizability, HOMO/LUMO, ZPVE, geometry-derived columns).  
- Work: load, two documented cleaners (unit checks, impossible-dipole filter), EDA on dipole vs polarizability and on element counts.
- Why this is not a detour: Module 08’s dipole diagnostic \(\boldsymbol\mu=-\int\mathbf{r}\,\Delta\rho\,dV\) needs fluency with dipole as a column before it is an integral.

**Not used here.** Any Octopus cube. Any network output.

## Module 03 — Statistical analysis

**Rubric need.** Different public CSV, \(\ge 500\) rows, \(\ge 6\) columns, numeric + grouping, one hypothesis test, required PLOS ONE reproducibility paper + one more scholarly source.

**Plan 03 use.** Flatten a *published* time-dependent density corpus to a table.

- Primary candidate: HZDR RODARE “Dataset for Machine Learning Time Propagators for TDDFT” (2,048 1-D TDDFT trajectories). Flatten to rows = (system, time), columns = integrated density moments, dipole, laser amplitude, bin of intensity / wavelength as the **grouping** variable.
- Hypothesis test, pre-registered: dipole-response amplitude does not differ across two declared intensity bins (two-sample test on a frozen split). Inconclusive allowed.
- If RODARE packaging is awkward: QM7-X subset (\(\ge 500\) rows) with a grouping variable “contains oxygen / not”, testing a dipole or HOMO shift. Still on-theme. Still public.

**Required citations.** Huebner et al. PLOS ONE 2024 (longitudinal IDA) for the time-axis workflow; one TDDFT or density-statistics paper from `Relevant_Scientific_Papers.md`.

## Module 04 — Applied machine learning

**Rubric need.** Dataset from **Kaggle, UCI, Data.gov, or an open government portal only.** Tabular. Supervised or unsupervised. Not the M02 or M03 file.

**Plan 03 use.** Do not smuggle cubes into a CSV-only rubric.

- Dataset: a **Kaggle QM9 variant not used in M02** (e.g. a different target: polarizability or \(C_v\)), or another Kaggle molecular set (Mordred-featurised QM9 if that is a distinct Kaggle dump — verify before freezing).
- Model: scikit-learn baseline (ridge / RF) predicting the frozen target from composition + simple shape descriptors.
- This module scores *hygiene* (split, leakage, metrics, bias). It does not score the stencil.
- Report the limitation in one sentence: a bag-of-features dipole predictor is not a presence-update rule. That sentence is the bridge, not a failure.

## Module 05 — Deep learning systems

**Rubric need.** CNN for images *or* RNN for sequences *or* Transformer for text. PyTorch. One controlled comparison. Public, not-synthetic, not reused.

**Plan 03 use — this is the first module that is allowed to see a grid.**

- Treat a **published 3-D electron-density volume** as an image stack. Public sources: QM9 voxel densities from Jørgensen & Bhowmik / VASP QM9-density releases (document the exact Zenodo/Figshare DOI in the freeze file).
- Task A (rubric-shaped): CNN on 2-D slices through published densities, auxiliary target already in QM9 (e.g. dipole component from the slice statistics) — only if that target is in the public table and not computed by us.
- Task B (thesis-shaped, same notebook family): 3-D conv stencil trained on **teacher pairs** from H₂ (scientific corpus). The rubric write-up foregrounds Task A if a reviewer treats self-run TDDFT as “synthetic.” Task B is the paper. Both are implemented.
- Controlled comparison: kernel 3×3×3 vs 5×5×5, **or** local conv vs a small FNO block, exactly one axis changed.
- Metrics: P1 one-step error; loss curves; P0 as a pass/fail panel.

If a mentor rejects self-run cubes as data, Module 05 ships on published density voxels alone and P1 waits for Module 08’s scientific appendix. That fallback is pre-declared, not improvised.

## Module 06 — Generative AI

**Rubric need.** GAN, VAE, or Transformer. Public data. Ethics section grounded in *this* run.

**Plan 03 use.** VAE on local stencils or density slices from the **same published voxel source as M05 Task A**, not reused as the M05 training split (new hash).

- Generate neighbouring-cell fields / slices.
- Evaluate: reconstruction of \(\rho_-\); whether samples violate \(N\ge 0\) or produce a net plus in vacuum.
- Ethics: fabricated densities as fake laboratory fields; risk of a surrogate being read as a measurement; ownership of teacher trajectories from academic codes.

Forbidden: shipping the VAE samples as “new molecules.”

## Module 07 — Agentic workflows

**Plan 03 use.** A fail-closed **teacher-and-hash agent**, single agent, tools:

- `check_grid_hash`
- `load_split`
- `refuse_if_water_in_h2_train`
- `run_p0_probe`
- `write_claim_or_stop`

Persona: conservative lab officer. Memory: the frozen ladder file. Safeguard: if P0 fails, the agent may not emit a P2 claim. Observed failure case: deliberately poisoned hash → refuse.

This is the governance system of plans 01–02, executed rather than described.

## Module 08 — Industry synthesis

**Industry.** Scientific-software / digital-twin vendors (attosecond labs, radiation-chemistry codes, TCAD-adjacent EM-matter coupling). Problem: a full TDDFT step is too slow for interactive or ensemble work; an uncertified neural step is too dangerous.

**Integrate at least three prior modules.**

- M03: the pre-registered test language and the longitudinal-data discipline.
- M05: the conv-stencil.
- M07: the fail-closed agent that decides whether a rollout certificate may be printed.

Artifact: a small service that accepts a hashed grid state and returns either the next field **and** a certificate (P0 last-passed, seed, split hash) or a refusal.

Paper: 1,500–2,000 words, industry constraints, the mean-field limitation said in public language.

## Module 09 — Defense

Defend the *rule*, the *gates*, and the *refusal to spend the thesis on a grid or a PAH spectrum*. Be ready for the question “is this just TDDFT with extra steps?” Answer: the contribution is a certified local surrogate with a frozen evaluation contract, not a new functional.
