# Project plan versions

This project has been planned three times. Folders for plans 01 (voxel field PES) and 02
(coupled-cluster anharmonic IR) were **removed from the tree on 2026-09-01**: the documents from
version control, and plan 02's leftover psi4 run artifacts from disk. They remain in git history.
Plan 02's ten raw `.npz` frequency arrays were never committed, so they were force-added in `800f3aa`
immediately before the deletion — `git show 800f3aa:<path>` retrieves one.

Neither 01, 02, nor 03 has been executed as a plan. Nothing in plan 03 is a result.
**Do not call plan 03 complete as a plan.** Completeness waits on a review of that folder.

**Plan 04 is incoming** (decided 2026-09-02; folder not yet created). It will replace plan 03.
Do not treat 03 as the destination of new work, and do not edit 03 in place to become 04.

| | Plan | Status |
|---|---|---|
| **03** | [Presence-Update-Rule](03_presence-update-rule/) | Last written. Draft as of 2026-09-01; not complete as a plan; not executed. **Will be replaced by 04.** |
| **04** | — | **Incoming.** Not yet a folder. Will supersede 03. Module 08: any individual aromatic → IR spectrum. Ends at 09. No Projects 10–12. |

Historic comparison (the 01 and 02 plan documents are gone; this table is not a set of links):

| | 01 — Voxel Field PES | 02 — Coupled-Cluster Anharmonic IR | 03 — Presence-Update-Rule |
|---|---|---|---|
| **Status** | Superseded 2026-08-23. Removed from the tree 2026-09-01. | Superseded 2026-08-29. Removed from the tree 2026-09-01. | Last written. Draft; not complete as a plan; not executed. **Will be replaced by 04.** |
| **Deliverable** | Vibrational band positions / IR envelopes, H₂O–benzene | Anharmonic IR families, benzene and naphthalene, four-term error budget | A shared local presence-update rule with P0–P4 gates on H₂ and H₂O |
| **Where precision comes from** | Own CCSD(T)/cc-pVTZ labels | A measured CC rung | Named Octopus RT-TDDFT (ALDA) on a **frozen** grid |
| **The model** | Hybrid FNO-NCA, \(E=\mathcal{E}[\rho,R]\) | Fine-tuned equivariant MLIP as cheap QFF half | 3-D conv stencil on \((\rho_\pm,\mathbf{j},\mathbf{E},\mathbf{B})\) |
| **Nuclear motion** | Classical MD + dipole-ACF | GVPT2 / hybrid QFF | Frozen nuclei on the scored window |
| **Central question** | Field vs GNN transfer on vibrations | Does a CC anchor beat DFT-anchored PAH IR? | Does one local field rule transfer H₂ → H₂O and stay a fixed point? |
| **Horizon** | Projects 10–12 | Absorbed / none | Projects 10–12 (phase, pair density, scale) |
| **Reviews survived** | Rounds 1–3 (git history) | Round 4 (git history) | Round 5 Pass A (cold read, 2026-09-01), addressed. Round 5 Pass B (domain, 2026-09-01): **no green light for the scope as frozen**, not addressed |

---

## Why the earlier plans were dropped

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
The deleted plan-02 restructure proposal (git history only) is the argument for why 01 died.

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

Only plan 03 is in this tree (04 is incoming and has no folder yet):

```
plans/03_presence-update-rule/
  GoalGathering/     prime directive, technical plan, module mapping, bibliography,
                     inheritance map, Round-5 briefs and the Round-5 Pass A review
    Horizon/         this plan's projects 10-12
  probes/            numerical probes that measure, rather than assert, the plan's arithmetic
  PATCH_plans_README.md
```

`Uitleg/` is not started for plan 03.

Three folders sit at the repository root and are **shared dumps**, because no plan may claim them:

- `Rubrics/` — the Udacity module rubrics 01-09, treated as fixed (version 1.5.1). If Udacity ever
  revises them, add a sibling folder rather than overwriting; several decisions turn on exact wording.
- `Papers/` — reference PDFs. Literature is a dump; plan 03's bibliography is the index.
- `AI_Chats/` — the planning conversations. They predate the splits.

The **professor reviews of plans 01 and 02 are not in this tree.** They remain in git history.
Plan 03's own review record starts with Round 5 Pass A (2026-09-01). Copying 01/02 reviews into 03
would imply 03 had survived them.

## Adding a version 04 (this is now the next action)

Plan 04 is **decided** (2026-09-02) and **not yet written**. When it is written: copy the last
written folder (`03_presence-update-rule/`), rename it, and turn the 04 row in the table above from
“incoming” into a link. Do **not** edit 03 in place. A superseded plan stays readable in **git
history** instead of becoming an unreadable diff. Do not resurrect the deleted 01 or 02 folders.

**Product, frozen as intent until the folder exists.** Module 08 is a pipeline: any individual
aromatic molecule in, an infrared spectrum out. Module 09 is the defense. The degree **ends there**.
Do not create a `Horizon/` or Projects 10–12 in plan 04. Plan 03's exile of IR / JWST / C₃₈₄H₄₈
to Horizon 10–12 does **not** carry forward.

Round-5 Pass B still binds the *architecture*: plan 03 tried to own light–matter interaction and
an IR network on one frozen clock, and that scope has no green light. Plan 04 does not get to
ignore that. It also does not get to “pick one” by dropping the IR product. The IR pipeline is the
Module 08 exit; how the clocks and the teacher are chosen is what 04 has to design.
