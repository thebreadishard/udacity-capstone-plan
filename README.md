# Udacity AI Mastery — Capstone Project Plan

> **This repository is a planning and coordination artifact.** It contains no scientific results for the
> current plan: nothing in plan 04 has been executed. It does contain tooling — probe scripts, a scraper.
> Its purpose is to design a coherent research project and distribute it across the Udacity Master in AI
> capstone sequence (Modules 02–09), so that every module both advances the science *and* satisfies the
> school's rubric.

> **Current: plan 04.** Plan 04 — [CC-Anchored IR Pipeline](plans/04_cc-anchored-ir-pipeline/) —
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

The project was planned four times. Plans 01 (voxel field PES) and 02 (coupled-cluster anharmonic IR)
were **removed from the tree on 2026-09-01** — documents from version control, and plan 02's leftover run
artifacts from disk. They remain in git history. Plan 02's raw frequency arrays (ten `.npz` Hessians and
geometries, ~10 h of psi4) had never been committed, so they were force-added in `800f3aa` before the
deletion; retrieve one with `git show 800f3aa:<path>`. Plan 03 (presence-update rule) is superseded and
was **removed from the tree on 2026-09-02**; git history keeps it.

Plan **04 is the current plan** (created 2026-09-02): a per-molecule IR pipeline — geometry, best
affordable Hessian, machine-learned anharmonic correction on self-generated DLPNO-CCSD(T) points —
whose success criterion is **relative and measured**: beat the best prediction currently available
anywhere for that molecule, judged per band against laboratory data.

| | Plan | Status |
|---|---|---|
| **03** | Presence-Update-Rule | Superseded by 04 (2026-09-02); **removed from the tree the same day**, git history keeps it. Draft; never complete as a plan; never executed. |
| **04** | [CC-Anchored-IR-Pipeline](plans/04_cc-anchored-ir-pipeline/) | **Current.** Draft as of 2026-09-02. Module 08: any individual aromatic → IR spectrum vs frozen lines. Ends at 09. No Projects 10–12. |

Start at [`plans/README.md`](plans/README.md) for why the earlier plans were dropped and what 04 is
allowed to inherit.

## The current objective (plan 04)

A **per-molecule infrared pipeline**: equilibrium geometry, the best affordable Hessian, and a
machine-learned / reduced-dimensional anharmonic correction trained on self-generated
DLPNO-CCSD(T) points — producing band positions and intensities with a stated, measured error
budget. The success criterion is **relative**: beat the best prediction currently available
anywhere for that molecule (PAHdb v4.00 scaled-harmonic DFT; Mai 2025 MLMD; the small-molecule
anharmonic front), judged per band against laboratory data. Opponents are named and versioned in
[Frozen_Lines_to_Beat.md](plans/04_cc-anchored-ir-pipeline/GoalGathering/Frozen_Lines_to_Beat.md).

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
│   ├── README.md                          why 01/02/03 were dropped; 04 is current
│   └── 04_cc-anchored-ir-pipeline/        current — draft, created 2026-09-02
│       ├── GoalGathering/                 prime directive, frozen lines to beat
│       └── probes/                        conventions declared; no probes yet
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

Documents 10–12 are **not** rubrics — they were plan 03's horizon and sit in its
`GoalGathering/Horizon/` until that folder's removal. Plan 04 has no horizon documents.

## Conventions this repository tries to keep

These outlived the pivot and are the most portable thing here:

- **Measured, not asserted.** Arithmetic that matters is executed in probes
  ([plan 04 conventions](plans/04_cc-anchored-ir-pipeline/probes/README.md)), not written out
  by hand. Missing inputs print `NOT_RUN`.
- **Never cite from recall.** Every identifier is fetched. Three bibliography entries turned out to
  be wrong under this rule, and one of them is what triggered the pivot.
- **Pre-register comparisons.** Frozen splits, ≥3 seeds, tuning parity, a declared effect size, and
  "inconclusive" pre-authorised as a publishable outcome.
- **Escalation ladders are declared in advance**, and the rung that fired is reported in every
  downstream claim.
- **Stopping is a result.** A ladder that halts at a measured limit is reported as that limit, not
  quietly extended.
