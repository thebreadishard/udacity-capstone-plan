# Project plan versions

> **All five plan folders are in the tree (user decision, 2026-09-04).** Plans 01, 02 and 03 were
> removed from the tree on 2026-09-01/02 and were **restored on 2026-09-04** from the commits
> just before their deletion, so that a reader of the repository can open them without git.
> They are superseded, read-only records: nothing in them is current, and they are not edited.
> Plan 04 is superseded and kept; **plan 05 is current.** Sentences below that say a plan was
> "removed from the tree" describe history and are left as written.
>
> **Plan 05 is the current plan** (created 2026-09-03): [`05_delta-probed-ir-pipeline/`](05_delta-probed-ir-pipeline/)
> — the same criterion, ladder, opponents and gates as plan 04, with the coupled-cluster anchor
> obtained by **probing the CC−DFT force-constant correction** at a measured, size-saturating
> probe count instead of learning a per-molecule surface. Plan 04 is **superseded and kept in
> the tree** as a read-only record (user decision 2, 2026-09-04); see
> [`05_delta-probed-ir-pipeline/GoalGathering/Why_05_Supersedes_04.md`](05_delta-probed-ir-pipeline/GoalGathering/Why_05_Supersedes_04.md).
> The paragraphs below this banner describe the state up to plan 04 and are unedited.

This project has been planned five times (01–05). Folders for plans 01 (voxel field PES) and 02
(coupled-cluster anharmonic IR) were **removed from the tree on 2026-09-01**: the documents from
version control, and plan 02's leftover psi4 run artifacts from disk. They remain in git history.
Plan 02's ten raw `.npz` frequency arrays were never committed, so they were force-added in `800f3aa`
immediately before the deletion — `git show 800f3aa:<path>` retrieves one.

None of plans 01–05 has been executed as a plan. Nothing in plans 03, 04 or 05 is a result.
**Do not call plan 04 or plan 05 complete as a plan.** Plan 05's completeness waits on its
Round-9 Pass B and on the mapping's Pass 6.

**Plan 04 was the current plan from 2026-09-02 to 2026-09-03** (it replaced plan 03, which was
**removed from the tree on 2026-09-02**; git history keeps it). **Plan 05 is current** as of
2026-09-03; all plan folders are in the tree since 2026-09-04 (user decision 2).

| | Plan | Status |
|---|---|---|
| **03** | [Presence-Update-Rule](03_presence-update-rule/) | Superseded by 04. Removed from the tree on 2026-09-02, **restored 2026-09-04** as a read-only record. Draft; never complete as a plan; never executed. |
| **04** | [CC-Anchored-IR-Pipeline](04_cc-anchored-ir-pipeline/) | Superseded by 05 (2026-09-03); kept as a read-only record (decision 2). Draft; Round-6 Pass A and B run and addressed; never executed. |
| **05** | [Δ-Probed-IR-Pipeline](05_delta-probed-ir-pipeline/) | **Current.** Draft as of 2026-09-03, amended 2026-09-04. Same product and criterion as 04; CC anchor obtained by probing the CC−DFT harmonic force-constant correction (probe count measured per rung). Round 7 (A, B) and Round 8 (A, B) and Round 9 Pass A run and addressed; Round 9 Pass B owed. |

Historic comparison (the 01, 02 and 03 folders were restored on 2026-09-04: [01](01_voxel-field-pes/), [02](02_coupled-cluster-anharmonic-ir/), [03](03_presence-update-rule/); their documents are read-only records):

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
review findings: `Inheritance_of_Reviews.md` in the removed plan-03 folder (git history).

## Layout

All five plans are in this tree since 2026-09-04: 01–04 superseded and read-only, 05 current
(01–03 restored from the commits just before their deletion; their own READMEs still describe
the tree as it was when they were written):

```
plans/04_cc-anchored-ir-pipeline/     superseded 2026-09-03
  README.md          orientation; Round-6 review record
  GoalGathering/     goal, frozen lines, ladder, budgets, mapping, distilled plan, bibliography,
                     Round-6 briefs and reviews, project proposal of 2026-09-03
  probes/            the NIST gas-coverage probe and its raw cache

plans/05_delta-probed-ir-pipeline/    current — draft, created 2026-09-03
  README.md          orientation and reading order; Round-7, Round-8 and Round-9 review record
  GoalGathering/     goal, why-05-supersedes-04, research note (source), frozen lines (carried),
                     ladder + tolerances, compute budget, distilled plan + gates, bibliography
  probes/            conventions declared; probes owed, none run
```

Three folders sit at the repository root and are **shared dumps**, because no plan may claim them:

- `Rubrics/` — the Udacity module rubrics 01-09, treated as fixed (version 1.5.1). If Udacity ever
  revises them, add a sibling folder rather than overwriting; several decisions turn on exact wording.
- `Papers/` — reference PDFs. Literature is a dump; the current plan's bibliography is the index.
- `AI_Chats/` — the planning conversations. They predate the splits.

The **professor reviews of plans 01–03 are back in this tree** since the 2026-09-04 restore (inside
their own folders); they are records of dead plans, not of plan 05.
Plan 03's review record (Round 5 Pass A, addressed; Round 5 Pass B, no green light, not
addressed) went with its folder. Plan 04's review record is in its own README: Round-6 Pass A
and Pass B (both 2026-09-02) are in the tree and addressed. Plan 05's review record is in its
own README: Rounds 7 and 8 (both passes) and Round 9 Pass A run and addressed, Round 9 Pass B owed.
Copying old reviews into a new plan folder would imply the new plan had survived them.

## Version 05 (created 2026-09-03)

Plan 05 exists: [`05_delta-probed-ir-pipeline/`](05_delta-probed-ir-pipeline/). Plan 04 was **not**
edited in place and stays in the tree as a read-only record (decision 2, 2026-09-04). Plan 05
keeps plan 04's product, criterion, ladder, opponents, scoreboards, gates and Round-6 closures,
and changes how the coupled-cluster anchor is obtained — a probed correction to the force
constants at a measured probe count K, instead of a learned per-molecule surface. The argument
of record is
[`05_delta-probed-ir-pipeline/GoalGathering/Why_05_Supersedes_04.md`](05_delta-probed-ir-pipeline/GoalGathering/Why_05_Supersedes_04.md).
Nothing in plan 05 is a result; its Round-7 and Round-8 reviews and Round-9 Pass A have run and been
addressed; Round-9 Pass B is owed.

## Version 04 (created 2026-09-02; superseded 2026-09-03)

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
