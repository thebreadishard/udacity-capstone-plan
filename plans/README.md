# Project plan versions

This project has been planned four times. Folders for plans 01 (voxel field PES) and 02
(coupled-cluster anharmonic IR) were **removed from the tree on 2026-09-01**: the documents from
version control, and plan 02's leftover psi4 run artifacts from disk. They remain in git history.
Plan 02's ten raw `.npz` frequency arrays were never committed, so they were force-added in `800f3aa`
immediately before the deletion — `git show 800f3aa:<path>` retrieves one.

None of plans 01–04 has been executed as a plan. Nothing in plans 03 or 04 is a result.
**Do not call plan 04 complete as a plan.** Completeness waits on a review of that folder.

**Plan 04 is the current plan** (decided 2026-09-02; folder created the same day). It replaces
plan 03, which was **removed from the tree on 2026-09-02**; git history keeps it.

| | Plan | Status |
|---|---|---|
| **03** | Presence-Update-Rule | Superseded by 04. **Removed from the tree on 2026-09-02**; git history keeps it. Draft; never complete as a plan; never executed. |
| **04** | [CC-Anchored-IR-Pipeline](04_cc-anchored-ir-pipeline/) | **Current.** Draft as of 2026-09-02. Module 08: any individual aromatic → IR spectrum, scored against frozen state-of-the-art lines. Ends at 09. No Projects 10–12. |

Historic comparison (the 01, 02 and 03 plan documents are gone; this table is not a set of links):

| | 01 — Voxel Field PES | 02 — Coupled-Cluster Anharmonic IR | 03 — Presence-Update-Rule |
|---|---|---|---|
| **Status** | Superseded 2026-08-23. Removed from the tree 2026-09-01. | Superseded 2026-08-29. Removed from the tree 2026-09-01. | Superseded by 04 on 2026-09-02 and removed from the tree the same day. Draft; never complete as a plan; never executed. |
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

Plan 03 was in turn superseded on 2026-09-02. Round-5 Pass B gave **no green light** for its frozen
scope: it tried to own light–matter interaction *and* an IR network on one frozen clock, with three
physical timescales in play, and the IR product — the reason for the work — sat outside the scored
modules entirely. Plan 04 returns the IR product to Module 08 and drops the co-owned light–matter
solver.

The argument of record for the 02→03 pivot was `Why_03_Supersedes_02.md` (git history, in the
removed plan-03 folder).
The deleted plan-02 restructure proposal (git history only) is the argument for why 01 died.

## What survives into 04

Method-agnostic, from 01–03:

- pre-registration, frozen splits with hashes, ≥3 seeds, tuning parity
- declared effect size; inconclusive is publishable
- escalation ladders declared in advance; stopping is a result
- fail-closed reporting; DOI-before-claim; measured-not-asserted probes

From plan 02 specifically: the measured lab-comparison machinery (PAHdb experimental band reads
with recorded uids, NIST JCAMP parsing) — git history, recomputable, and the quantitative floor
under plan 04's frozen lines. From plan 03: nothing method-specific survives; its Maxwell–TDDFT
scope is dropped, its governance was already shared. Itemised fates of the thirty plan-01/02
review findings: `Inheritance_of_Reviews.md` in the removed plan-03 folder (git history).

## Layout

Only plan 04 is in this tree (01, 02 and 03 are git history):

```
plans/04_cc-anchored-ir-pipeline/
  README.md          orientation and reading order
  GoalGathering/     prime directive, frozen lines, ladder + tolerances, compute budget,
                     capstone mapping, distilled plan + gates, bibliography, Round-6 briefs
                     and the Round-6 Pass A review
  probes/            conventions declared; no probes yet
```

`Uitleg/` is not started for plan 04.

Three folders sit at the repository root and are **shared dumps**, because no plan may claim them:

- `Rubrics/` — the Udacity module rubrics 01-09, treated as fixed (version 1.5.1). If Udacity ever
  revises them, add a sibling folder rather than overwriting; several decisions turn on exact wording.
- `Papers/` — reference PDFs. Literature is a dump; plan 04's bibliography is the index.
- `AI_Chats/` — the planning conversations. They predate the splits.

The **professor reviews of plans 01–03 are not in this tree.** They remain in git history.
Plan 03's review record (Round 5 Pass A, addressed; Round 5 Pass B, no green light, not
addressed) went with its folder. Plan 04's review record is in its own README: Round-6 Pass A
(2026-09-02) is in the tree and addressed; Pass B is not yet run. Copying old reviews into
04 would imply 04 had survived them.

## Version 04 (created 2026-09-02)

Plan 04 exists: [`04_cc-anchored-ir-pipeline/`](04_cc-anchored-ir-pipeline/). Plan 03 was **not**
edited in place; it was removed from the tree on 2026-09-02 and remains readable in git history.
Do not resurrect the deleted 01 or 02 folders.

**Product.** Module 08 is a pipeline: any individual aromatic molecule in, an infrared spectrum
out, scored against the frozen lines in
[04 Frozen_Lines_to_Beat.md](04_cc-anchored-ir-pipeline/GoalGathering/Frozen_Lines_to_Beat.md)
under pre-registered gates: "beat" unconditional only on the gas-phase rungs; larger accuracy
rungs decided — or pre-declared inconclusive — by a measured matrix–gas gate; the reach
demonstration conditional on cluster access, with no accuracy claim.
Module 09 is the defense. The degree **ends there**. Plan 04 has no `Horizon/` and no Projects
10–12. Plan 03's exile of IR / JWST / C₃₈₄H₄₈ to Horizon 10–12 did **not** carry forward.

Round-5 Pass B still binds the *architecture*: plan 03 tried to own light–matter interaction and
an IR network on one frozen clock, and that scope has no green light. Plan 04 answers it by doing
one thing — matter, nuclei, spectra; light enters only as an inherited emission post-processing
layer, never as a co-owned solver.
