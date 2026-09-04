# Udacity AI Mastery — Capstone Project Plan

> **This repository is a planning and coordination artifact.** It contains no pipeline results
> for the current plan: no rung of plan 04 or plan 05 has run. What has run is one **coverage probe**
> (which laboratory data exists where — a measurement about data availability, committed with
> its raw evidence). It also contains tooling — probe scripts, a scraper.
> Its purpose is to design a coherent research project and distribute it across the Udacity Master in AI
> capstone sequence (Modules 02–09), so that every module both advances the science *and* satisfies the
> school's rubric.

> **All five plan folders are in the tree (user decision, 2026-09-04).** Plans 01, 02 and 03 were
> removed from the tree on 2026-09-01/02 and were **restored on 2026-09-04** from the commits
> just before their deletion, so that a reader of the repository can open them without git.
> They are superseded, read-only records: nothing in them is current, and they are not edited.
> Plan 04 is superseded and kept; **plan 05 is current.** Sentences below that say a plan was
> "removed from the tree" describe history and are left as written.
>
> **Current: plan 05.** Plan 05 — [Δ-Probed IR Pipeline](plans/05_delta-probed-ir-pipeline/) —
> was created on 2026-09-03 and supersedes plan 04, keeping plan 04's product, criterion,
> ladder, opponents and gates and changing one thing: the coupled-cluster anchor is a
> **probed correction to the force constants** (probe count measured per rung, expected to
> stop growing with size) instead of a learned per-molecule surface. Plan 04's folder stays in
> the tree until the user decides on its removal. The paragraphs below describing plan 04 are
> kept as written on 2026-09-02/03; where they say "current", read plan 05.
>
> **Plan 04** — [CC-Anchored IR Pipeline](plans/04_cc-anchored-ir-pipeline/) —
> was created on 2026-09-02 and supersedes plan 03. Plan 03 was **removed from the tree on
> 2026-09-02**; git history keeps it. Round-5 Pass B gave **no green light** for plan
> 03's frozen scope, and that verdict binds plan 04's architecture (one scope, one clock).
>
> **Plan 04 product.** Module 08 ships a pipeline: any individual aromatic molecule in, an
> infrared spectrum out — scored against frozen state-of-the-art lines
> ([Frozen_Lines_to_Beat.md](plans/04_cc-anchored-ir-pipeline/GoalGathering/Frozen_Lines_to_Beat.md)),
> with pre-registered gates: "beat" claims are unconditional only on the gas-phase rungs
> (benzene, naphthalene); larger accuracy rungs are decided — or pre-declared inconclusive —
> by a measured matrix–gas gate, and the C₃₈₄H₄₈-class reach demonstration is conditional on
> cluster access and carries no accuracy claim.
> The sequence ends at Module 09. There are **no** Projects 10–12. Demonstrably-better IR of
> complex aromatics is the reason for the work, not a horizon item after the degree.

---

## Plan versions

The project was planned five times. Plans 01 (voxel field PES) and 02 (coupled-cluster anharmonic IR)
were **removed from the tree on 2026-09-01** — documents from version control, and plan 02's leftover run
artifacts from disk. They remain in git history. Plan 02's raw frequency arrays (ten `.npz` Hessians and
geometries, ~10 h of psi4) had never been committed, so they were force-added in `800f3aa` before the
deletion; retrieve one with `git show 800f3aa:<path>`. Plan 03 (presence-update rule) is superseded and
was **removed from the tree on 2026-09-02**; git history keeps it.

Plan **05 is the current plan** (created 2026-09-03). It keeps plan 04's product and criterion —
a per-molecule IR pipeline whose success criterion is **relative, measured and gated**: agree with
known truth on small PAHs, beat the best available prediction per band where the laboratory data
can decide it, and earn trust for the sizes where nothing can check anyone — and replaces plan
04's learned per-molecule surface with a **probed** coupled-cluster correction to the force
constants, at a probe count measured per rung.

| | Plan | Status |
|---|---|---|
| **03** | [Presence-Update-Rule](plans/03_presence-update-rule/) | Superseded by 04 (2026-09-02); removed from the tree the same day and **restored 2026-09-04** as a read-only record. Draft; never complete as a plan; never executed. |
| **04** | [CC-Anchored-IR-Pipeline](plans/04_cc-anchored-ir-pipeline/) | Superseded by 05 on 2026-09-03; kept in the tree pending the user's removal decision. Draft; Round-6 reviews run and addressed; never executed. |
| **05** | [Δ-Probed-IR-Pipeline](plans/05_delta-probed-ir-pipeline/) | **Current.** Draft as of 2026-09-03. Same product and criterion as 04; CC anchor by probing the CC−DFT force-constant correction. Round-7 reviews not yet run. |

Start at [`plans/README.md`](plans/README.md) for why the earlier plans were dropped and what 05
inherits.

## The current objective (plan 04 wording; plan 05 keeps it and changes the anchor method)

A **per-molecule infrared pipeline**: equilibrium geometry, a DFT Hessian, and a coupled-cluster
correction — in plan 04 a machine-learned anharmonic correction trained on self-generated
DLPNO-CCSD(T) points; in plan 05 a **probed correction Δ to the force constants** recovered from
a measured number K of local-CC evaluations
([plan 05 Goal](plans/05_delta-probed-ir-pipeline/GoalGathering/Overarching_Goal.md)) —
producing band positions with a stated, measured error budget (intensities reported). The success criterion is **relative and gated**: beat the best prediction currently
available anywhere for that molecule (PAHdb v4.00 scaled-harmonic DFT; Mai 2025 MLMD; the
small-molecule anharmonic front), judged per band against laboratory data **where that data
can decide it** — gas-phase rungs unconditionally, larger rungs via the measured matrix–gas
gate, never on reach rungs. Opponents are named and versioned in
[Frozen_Lines_to_Beat.md](plans/05_delta-probed-ir-pipeline/GoalGathering/Frozen_Lines_to_Beat.md)
(carried unchanged from plan 04).

Size must scale to **C₃₈₄H₄₈-class species and larger** — the 101–386-carbon PAHdb bin, where
the only existing predictions anywhere are scaled harmonic B3LYP/4-31G. Compute starts on a
laptop (benzene pilot) and escalates to UvA supercomputer access when a rung demands it.
Emission after UV heating (the astronomical use case) is a declared post-processing tier, not a
co-owned solver.

**Not claimed:** absolute "chemical precision"; JWST species identification; any rung that has
not actually run and been scored. Nothing here is a result.

## Repository layout

```
CapstonePlan/
├── plans/
│   ├── README.md                          why 01/02/03 were dropped; 05 is current, 01–04 superseded
│   ├── 01_voxel-field-pes/                superseded 2026-08-23 — restored to the tree 2026-09-04, read-only
│   ├── 02_coupled-cluster-anharmonic-ir/  superseded 2026-08-29 — restored 2026-09-04, read-only
│   ├── 03_presence-update-rule/           superseded 2026-09-02 — restored 2026-09-04, read-only
│   ├── 04_cc-anchored-ir-pipeline/        superseded 2026-09-03 — kept, read-only
│   │   ├── GoalGathering/                 prime directive, frozen lines, Round-6 reviews, proposal
│   │   └── probes/                        the NIST gas-coverage probe (evidence in-tree)
│   └── 05_delta-probed-ir-pipeline/       current — draft, created 2026-09-03
│       ├── GoalGathering/                 goal, research note, ladder, budget, gates, bibliography
│       └── probes/                        conventions; probes owed (none run yet)
│
├── Rubrics/                               Udacity module rubrics 01–09, treated as fixed
├── Papers/                                reference PDFs (dump; plan bibliographies are the index)
├── AI_Chats/                              planning conversations (primary sources, not a plan)
│                                          — grok_chat_4.md is plan 04's source conversation
├── scraper/                               tooling, and the raw scrapes it produced
├── requirements.txt
└── README.md                              ← you are here
```

The Udacity rubrics are the constraint. Literature PDFs are a dump, not a second plan. Planning
conversations predate the splits and belong to no plan folder.

Plan 03's review record — the Round-5 Pass A cold read (2026-09-01, findings addressed in spec
the same day), the Round-5 Pass B adversarial domain review (2026-09-01, **findings not
addressed**: no green light for the scope as frozen), and an inheritance map of thirty source
findings from the deleted plans — was removed from the tree with the plan-03 folder on
2026-09-02 and remains in **git history**. Pass B's architectural verdict (one scope, one
clock) binds plan 04 and is restated in its prime directive.

Documents 10–12 are **not** rubrics — they were plan 03's horizon and went with the plan-03
folder on 2026-09-02 (git history). Plans 04 and 05 have no horizon documents.

## Conventions this repository tries to keep

These outlived the pivot and are the most portable thing here:

- **Measured, not asserted.** Arithmetic that matters is executed in probes
  ([plan 05 conventions](plans/05_delta-probed-ir-pipeline/probes/README.md)), not written out
  by hand. Missing inputs print `NOT_RUN`.
- **Never cite from recall.** Every identifier is fetched. Three bibliography entries turned out to
  be wrong under this rule, and one of them is what triggered the pivot.
- **Pre-register comparisons.** Frozen splits, ≥3 seeds, tuning parity, a declared effect size, and
  "inconclusive" pre-authorised as a publishable outcome.
- **Escalation ladders are declared in advance**, and the rung that fired is reported in every
  downstream claim.
- **Stopping is a result.** A ladder that halts at a measured limit is reported as that limit, not
  quietly extended.
