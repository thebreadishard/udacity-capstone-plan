# Project plan versions

> **Plan 05 is current.** Plans 01–04 are superseded, read-only records: nothing in them is
> current, and they are not edited.
>
> **Plan 05 is the current plan** (created 2026-09-03): [`05_delta-probed-ir-pipeline/`](05_delta-probed-ir-pipeline/)
> — the same criterion, ladder, opponents and gates as plan 04, with the coupled-cluster anchor
> obtained by **probing the CC−DFT force-constant correction** at a measured, size-saturating
> probe count instead of learning a per-molecule surface. Plan 04 is superseded and kept as a
> read-only record; see
> [`05_delta-probed-ir-pipeline/GoalGathering/Why_05_Supersedes_04.md`](05_delta-probed-ir-pipeline/GoalGathering/Why_05_Supersedes_04.md).

This project has been planned five times (01–05); all five folders are here. Plan 02's ten raw
`.npz` frequency arrays live in git history only — `git show 57a7910:<path>` retrieves one.

None of plans 01–05 has been executed as a plan: no rung has run and there is no pipeline result.
Plan 05 has **probe results** (measurements about the method — the DFT dry run, the anchor timings,
probe M1 — dated 2026-09-05/06 in its `probes/` and research notes); these are evidence for or
against the plan's assumptions, not spectra. **Do not call plan 04 or plan 05 complete as a
plan.** Plan 05's completeness waits on the mapping's Pass 6 and on the pilot note.

**Plan 05 is current** since 2026-09-03; plan 04 was current for the one day before it.

| | Plan | Status |
|---|---|---|
| **03** | [Presence-Update-Rule](03_presence-update-rule/) | Superseded by 04 (2026-09-02); read-only record. Draft; never complete as a plan; never executed. |
| **04** | [CC-Anchored-IR-Pipeline](04_cc-anchored-ir-pipeline/) | Superseded by 05 (2026-09-03); read-only record. Draft; Round-6 Pass A and B run and addressed; never executed. |
| **05** | [Δ-Probed-IR-Pipeline](05_delta-probed-ir-pipeline/) | **Current.** Created 2026-09-03; text frozen 2026-09-04 (dated notes only); decisions closed 2026-09-05/06; probe M1 measured at cc-pVDZ; proposal of 2026-09-06 awaiting the supervisor. Same product and criterion as 04; CC anchor obtained by probing the CC−DFT harmonic force-constant correction (probe count measured per rung). Round 7 (A, B) and Rounds 8, 9 and 10 (A, B) run and addressed. |

Historic comparison ([01](01_voxel-field-pes/), [02](02_coupled-cluster-anharmonic-ir/), [03](03_presence-update-rule/); read-only records):

| | 01 — Voxel Field PES | 02 — Coupled-Cluster Anharmonic IR | 03 — Presence-Update-Rule |
|---|---|---|---|
| **Status** | Superseded 2026-08-23. | Superseded 2026-08-29. | Superseded by 04 on 2026-09-02. Draft; never complete as a plan; never executed. |
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

The argument of record for the 02→03 pivot is
[`03_presence-update-rule/GoalGathering/Why_03_Supersedes_02.md`](03_presence-update-rule/GoalGathering/Why_03_Supersedes_02.md);
the plan-02 restructure proposal
([`02_coupled-cluster-anharmonic-ir/GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md`](02_coupled-cluster-anharmonic-ir/GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md))
is the argument for why 01 died.

## What survives into 04 (and, through it, into 05)

Method-agnostic, from 01–03:

- pre-registration, frozen splits with hashes, ≥3 seeds, tuning parity
- declared effect size; inconclusive is publishable
- escalation ladders declared in advance; stopping is a result
- fail-closed reporting; DOI-before-claim; measured-not-asserted probes

From plan 02 specifically: the measured lab-comparison machinery (PAHdb experimental band reads
with recorded uids, NIST JCAMP parsing) — git history, recomputable, and the quantitative floor
under plan 04's frozen lines. From plan 03: nothing method-specific survives; its Maxwell–TDDFT
scope is dropped, its governance was already shared. Itemised fates of the thirty plan-01/02
review findings: [`03_presence-update-rule/GoalGathering/Inheritance_of_Reviews.md`](03_presence-update-rule/GoalGathering/Inheritance_of_Reviews.md).

## Layout

All five plans are in this tree: 01–04 superseded and read-only, 05 current (the READMEs of
01–03 describe the tree as it was when they were written):

```
plans/04_cc-anchored-ir-pipeline/     superseded 2026-09-03
  README.md          orientation; Round-6 review record
  GoalGathering/     goal, frozen lines, ladder, budgets, mapping, distilled plan, bibliography,
                     Round-6 briefs and reviews, project proposal of 2026-09-03
  probes/            the NIST gas-coverage probe and its raw cache

plans/05_delta-probed-ir-pipeline/    current — created 2026-09-03, text frozen 2026-09-04
  README.md          orientation and reading order; Round-7 to Round-10 review record
  GoalGathering/     goal, why-05-supersedes-04, research note (source), frozen lines (carried),
                     ladder + tolerances, compute budget, distilled plan + gates, bibliography
  probes/            conventions; probes owed; the probes that ran (DFT dry run, anchor timings, M1)
```

Two tracked folders and one local folder sit at the repository root, because no plan may claim them:

- `Rubrics/` — the Udacity module rubrics 01-09, treated as fixed (version 1.5.1). If Udacity ever
  revises them, add a sibling folder rather than overwriting; several decisions turn on exact wording.
- `Papers/` — local only, **git-ignored since 2026-09-06**: the PDFs were removed from the repository and from its history (`Papers_Inventory_2026-09-06.md` at the root records how); the current plan's bibliography is the index of what is held and read.
- `AI_Chats/` — the planning conversations. They predate the splits.

The professor reviews of plans 01–03 sit inside their own folders; they are records of
superseded plans, not of plan 05. Plan 03's review record (Round 5 Pass A, addressed; Round 5
Pass B, no green light, not addressed) is in its folder. Plan 04's review record is in its own README: Round-6 Pass A
and Pass B (both 2026-09-02) are in the tree and addressed. Plan 05's review record is in its
own README: Rounds 7, 8, 9 and 10 (both passes each) run and addressed.
Copying old reviews into a new plan folder would imply the new plan had survived them.

## Version 05 (created 2026-09-03)

Plan 05 exists: [`05_delta-probed-ir-pipeline/`](05_delta-probed-ir-pipeline/). Plan 04 was **not**
edited in place and stays in the tree as a read-only record. Plan 05
keeps plan 04's product, criterion, ladder, opponents, scoreboards, gates and Round-6 closures,
and changes how the coupled-cluster anchor is obtained — a probed correction to the force
constants at a measured probe count K, instead of a learned per-molecule surface. The argument
of record is
[`05_delta-probed-ir-pipeline/GoalGathering/Why_05_Supersedes_04.md`](05_delta-probed-ir-pipeline/GoalGathering/Why_05_Supersedes_04.md).
Nothing in plan 05 is a result; its Round-7 to Round-10 reviews have run and been addressed.

## Version 04 (created 2026-09-02; superseded 2026-09-03)

Plan 04 exists: [`04_cc-anchored-ir-pipeline/`](04_cc-anchored-ir-pipeline/). Plan 03 was **not**
edited in place; it is kept as a read-only record.

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
