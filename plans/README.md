# Project plan versions

This project has been planned three times. All three folders stay here so the reasoning is legible
without reading git history. Plans 01 and 02 remain until a later deletion pass.

Neither 01, 02, nor 03 has been executed. Nothing in this repository is a result.
**Do not call plan 03 complete as a plan.** Completeness waits on a review of that folder.

| | [01 — Voxel Field PES](01_voxel-field-pes/) | [02 — Coupled-Cluster Anharmonic IR](02_coupled-cluster-anharmonic-ir/) | [03 — Presence-Update-Rule](03_presence-update-rule/) |
|---|---|---|---|
| **Status** | Superseded 2026-08-23. Complete as a plan; not developed. | Superseded 2026-08-29. Complete as a plan; blocked on measurement. | **Current.** Draft as of 2026-09-01; not complete as a plan; not executed. |
| **Deliverable** | Vibrational band positions / IR envelopes, H₂O–benzene | Anharmonic IR families, benzene and naphthalene, four-term error budget | A shared local presence-update rule with P0–P4 gates on H₂ and H₂O |
| **Where precision comes from** | Own CCSD(T)/cc-pVTZ labels | A measured CC rung | Named Octopus RT-TDDFT (ALDA) on a **frozen** grid |
| **The model** | Hybrid FNO-NCA, \(E=\mathcal{E}[\rho,R]\) | Fine-tuned equivariant MLIP as cheap QFF half | 3-D conv stencil on \((\rho_\pm,\mathbf{j},\mathbf{E},\mathbf{B})\) |
| **Nuclear motion** | Classical MD + dipole-ACF | GVPT2 / hybrid QFF | Frozen nuclei on the scored window |
| **Central question** | Field vs GNN transfer on vibrations | Does a CC anchor beat DFT-anchored PAH IR? | Does one local field rule transfer H₂ → H₂O and stay a fixed point? |
| **Horizon** | Projects 10–12 | Absorbed / none | Projects 10–12 (phase, pair density, scale) |
| **Reviews survived** | Rounds 1–3 | Round 4 | None yet |

---

## Why there are three

Plan 01 was not abandoned because it was wrong. It was reviewed three times, and every blocking
issue raised against it was closed *in spec*. It was abandoned because of two things measured
**after** it was finished:

1. **Its deliverable had been overtaken.** Mai et al. (2025) computed anharmonic IR spectra by
   machine-learning MD for 1,704 PAHdb species up to 216 carbon atoms. Plan 01's Module 08 exit was
   the same class of result on H₂O and benzene, arriving in 2028.
2. **Its budget went to the wrong place.** Roughly two thirds of plan 01's fixed 840-hour baseline
   was spent making a voxel grid behave — validating discretization, not producing spectra.

Plan 02 was not abandoned because it was wrong. Round 4 accepted the governance and then **reduced
the scope**. It is superseded because it is **blocked on a label factory** the rubric sequence cannot
wait for: a coupled-cluster rung that must be measured before the module map can be written, plus a
locality assumption that already failed on a published PAH band family.

Plan 03 moves the scarce resource to a question Modules 03–06 can score: one local dynamical rule,
a frozen discretisation, public-or-generated-computational trajectories, and tests that do not wait
on in-core CCSD(T) naphthalene.

The argument of record is
[Why_03_Supersedes_02.md](03_presence-update-rule/GoalGathering/Why_03_Supersedes_02.md).
Plan 02's restructure proposal remains the argument for why 01 died.

## What survives into 03

Method-agnostic, from 01 and 02:

- pre-registration, frozen splits with hashes, ≥3 seeds, tuning parity
- declared effect size; inconclusive is publishable
- escalation ladders declared in advance; stopping is a result
- fail-closed reporting; DOI-before-claim; measured-not-asserted probes
- the dipole identity as a **diagnostic** of learned \(\rho_-\), not as a spectral product

The field representation survives. The PES-to-IR product does not. The CC-anharmonic product does
not. Itemised fates of the thirty source findings:
[03 inheritance map](03_presence-update-rule/GoalGathering/Inheritance_of_Reviews.md).

## Layout

Each version is self-contained and mirrors the same internal structure, so its relative links work
without rewriting:

```
plans/<version>/
  GoalGathering/     prime directive, technical plan, module mapping, bibliography
    Horizon/         this plan's projects 10-12 (they differ between plans)
  probes/            numerical probes that measure, rather than assert, the plan's arithmetic
  Uitleg/            Dutch VWO-6 explanation (version 01; 03 not started)
```

Three folders sit at the repository root and are **shared**, because no plan may claim them:

- `Rubrics/` — the Udacity module rubrics 01-09, treated as fixed (version 1.5.1). If Udacity ever
  revises them, add a sibling folder rather than overwriting; several decisions turn on exact wording.
- `Papers/` — reference PDFs. Literature is not version-specific, and duplicating it would add tens
  of MB per plan.
- `AI_Chats/` — the planning conversations. They predate the splits.

The **professor reviews are not shared.** Rounds 1–3 reviewed plan 01 and live there; Round 4
reviewed plan 02 and lives there. Plan 03 has no professor review yet. Copying 01/02 reviews into 03
would imply 03 had survived them.

## Adding a version 04

Copy the current version's folder, rename it, and add a row to the table above. The point of this
layout is that a superseded plan stays readable instead of becoming a diff.
