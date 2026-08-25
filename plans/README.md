# Project plan versions

This project has been planned twice. Both plans are kept here, complete and internally consistent,
so that the reasoning is legible without reading git history.

Neither has been executed. Nothing in this repository is a result.

| | [01 — Voxel Field PES](01_voxel-field-pes/) | [02 — Coupled-Cluster Anharmonic IR](02_coupled-cluster-anharmonic-ir/) |
|---|---|---|
| **Status** | Superseded 2026-08-23. Complete and coherent; not being developed. | **Current.** Rewrite in progress. |
| **Deliverable** | Vibrational band positions and relative IR envelopes for H₂O, D₂O, CO₂, benzene, within 10–15 cm⁻¹ | Anharmonic IR band families and relative intensities for named PAH sizes and charge states, with a four-term error budget, ending in a fail-closed identification |
| **Where precision comes from** | Own CCSD(T)/cc-pVTZ labels | A **measured** coupled-cluster rung — canonical vs local CC, error published per band family and charge state |
| **The model** | Bespoke: energy as a functional of a voxel electron-density field, \(E=\mathcal{E}[\rho,R]\), hybrid FNO-NCA encoder, forces by autograd | Borrowed: a fine-tuned equivariant MLIP, lifted to the gold rung by Δ-learning / transfer learning |
| **Nuclear motion** | Classical MD + dipole-ACF FFT | GVPT2 from a quartic force field, escalating to selected VCI |
| **Central question** | Does a continuous 3D field representation transfer better to unseen vibrational modes than an equivariant GNN? | Does a measured coupled-cluster anchor buy accuracy that DFT-anchored anharmonic PAH IR does not have? |
| **Horizon** | Post-master's Projects 10 → 11 → 12 | None. Projects 10–12 are absorbed into Modules 03–08. |
| **Reviews survived** | 3 professor rounds, 15 blocking issues | Round 4 pending |

---

## Why there are two

Plan 01 was not abandoned because it was wrong. It was reviewed three times, and every blocking
issue raised against it was closed. It was abandoned because of two things measured **after** it was
finished:

1. **Its deliverable had been overtaken.** Mai et al. (2025) computed anharmonic IR spectra by
   machine-learning MD for 1,704 PAHdb species up to 216 carbon atoms. Plan 01's Module 08 exit was
   the same class of result on H₂O and benzene, arriving in 2028.
2. **Its budget went to the wrong place.** Roughly two thirds of plan 01's fixed 840-hour baseline
   was spent making a voxel grid behave — validating discretization, not producing spectra. That
   spend was the reason it could not reach further.

Meanwhile the obstacles that plan 01 had described as post-master's walls turned out to be partly
gone: near-linear-scaling local coupled cluster reaches PAH-sized open-shell systems on one
workstation, transfer learning to CCSD(T) needs on the order of 100 points, and VPT2 can now be run
from a machine-learned potential for a 21-atom molecule in about a minute.

The full argument, six weighed alternatives and the effort arithmetic are in
[02's restructure proposal](02_coupled-cluster-anharmonic-ir/GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md).

## What survives from 01 into 02

- **The governance system**, which is the most valuable thing either plan contains and is entirely
  method-agnostic: pre-registration, frozen split files with hashes, ≥3 seeds, tuning parity,
  declared effect sizes, "inconclusive is publishable", claim ladders, escalation ladders,
  fail-closed reporting, error decomposition, DOI-before-claim, measured-not-guessed budgets.
- **The exact dipole identity** \(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho\,dV\) and the grid
  artifact budget, which move from the energy surface to the **dipole** surface.
- **The field model itself**, demoted to one of three legs in 02's pre-registered dipole-surface
  comparison. If it loses there, it is dropped and 02's spectra ship regardless.
- **The three professor reviews**, which are the record of how the discipline was built.

## Layout

Each version is self-contained and mirrors the same internal structure, so its relative links work
without rewriting:

```
plans/<version>/
  GoalGathering/     prime directive, technical plan, module mapping, bibliography
    Horizon/         this plan's projects 10-12 (they differ between plans)
  probes/            numerical probes that measure, rather than assert, the plan's arithmetic
  Uitleg/            Dutch VWO-6 explanation (version 01 only)
```

Three folders sit at the repository root and are **shared**, because neither plan may claim them:

- `Rubrics/` — the Udacity module rubrics 01-09, the constraint both plans were designed against,
  treated as fixed (version 1.5.1). If Udacity ever revises them, add a sibling folder rather than
  overwriting; several decisions turn on exact wording.
- `Papers/` — 36 reference PDFs. Literature is not version-specific, and duplicating it would add
  ~85 MB per plan.
- `AI_Chats/` — the planning conversations. They predate the split, and the original ambition
  recorded in them is closer to plan 02's goal than to plan 01's.

The **professor reviews are not shared.** They reviewed plan 01 and live there. Plan 02 carries an
inheritance table instead, showing where each of the fifteen blocking issues landed — because
copying the reviews across would imply plan 02 had survived them, and Round 4 is still pending.

## Adding a version 03

Copy the current version's folder, rename it, and add a row to the table above. The point of this
layout is that a superseded plan stays readable instead of becoming a diff.
