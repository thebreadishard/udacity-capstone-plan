# Udacity AI Mastery — Capstone Project Plan

> **This repository is a planning and coordination artifact.** It contains no scientific results for the
> current plan: nothing in plan 03 has been executed. It does contain tooling — probe scripts, a scraper.
> Its purpose is to design a coherent research project and distribute it across the Udacity Master in AI
> capstone sequence (Modules 02–09), so that every module both advances the science *and* satisfies the
> school's rubric.

---

## Current plan

The project was planned three times. Plans 01 (voxel field PES) and 02 (coupled-cluster anharmonic IR)
were **removed from the tree on 2026-09-01** — documents from version control, and plan 02's leftover run
artifacts from disk. They remain in git history. Plan 02's raw frequency arrays (ten `.npz` Hessians and
geometries, ~10 h of psi4) had never been committed, so they were force-added in `800f3aa` before the
deletion; retrieve one with `git show 800f3aa:<path>`.

| | Plan | Status |
|---|---|---|
| **03** | [Presence-Update-Rule](plans/03_presence-update-rule/) | **Current.** Draft as of 2026-09-01; **not** complete as a plan; not executed |

Start at [`plans/README.md`](plans/README.md) for why the earlier plans were dropped.

## The current objective (plan 03)

A **single** translation-equivariant local presence-update rule on a **frozen** real-space grid:
the neighbourhood of a cell \((\rho_+,\rho_-,\mathbf{j},\mathbf{E},\mathbf{B})\) maps to the same
quantities in that cell one electronic time step later. One 3-D conv stencil, trained on **H₂**
teacher windows (Octopus RT-TDDFT, ALDA, Maxwell–TDDFT fields), scored with pre-registered gates
P0–P4, including zero-shot transfer to **H₂O**.

Precision is named **mean-field / ALDA**, not chemical accuracy. The grid is a constant after the
Q0 hash (Module 05), not the scientific contribution. Infrared spectra, JWST identification, and
C₃₈₄H₄₈ are **not** Module 08 promises.

**Not claimed:** many-electron correlation, a voxel PES, anharmonic PAH bands, or “complete as a
plan” before a review of *this* folder has closed. Nothing here is a result.

## Repository layout

```
CapstonePlan/
├── plans/
│   ├── README.md                          why 01/02 were dropped; 03 is current
│   └── 03_presence-update-rule/           current — draft, not complete
│       ├── GoalGathering/                 prime directive, freeze, mapping, bibliography,
│       │   │                              inheritance map, Round-5 review briefs
│       │   └── Horizon/                   projects 10–12 (phase, pair density, scale)
│       ├── probes/                        scripts; missing teacher files print NOT_RUN
│       └── PATCH_plans_README.md          applied 2026-09-01; still forbids “complete”
│
├── Rubrics/                               Udacity module rubrics 01–09, treated as fixed
├── Papers/                                reference PDFs (dump; 03 bibliography is the index)
├── AI_Chats/                              planning conversations (primary sources, not a plan)
├── scraper/                               tooling, and the raw scrapes it produced
├── requirements.txt
└── README.md                              ← you are here
```

The Udacity rubrics are the constraint. Literature PDFs are a dump, not a second plan. Planning
conversations predate the splits and are not filed under plan 03.

Plan 03 has two reviews of its own: the
[Round-5 Pass A cold read](plans/03_presence-update-rule/GoalGathering/Professor_Review_2026-09-01_Round5_PassA.md)
(2026-09-01, findings addressed in spec the same day) and the
[Round-5 Pass B adversarial domain review](plans/03_presence-update-rule/GoalGathering/Professor_Review_2026-09-01_Round5_PassB.md)
(2026-09-01, **findings not addressed**: no green light for the scope as frozen).
It also carries an
[inheritance map](plans/03_presence-update-rule/GoalGathering/Inheritance_of_Reviews.md) of thirty
source findings from the deleted plans — because copying those reviews into this folder would imply
plan 03 had survived them. The review files themselves are in git history only.

Documents 10–12 are **not** rubrics — they are this plan's horizon and sit in
`GoalGathering/Horizon/`.

## Conventions this repository tries to keep

These outlived the pivot and are the most portable thing here:

- **Measured, not asserted.** Arithmetic that matters is executed in
  [`plans/03_presence-update-rule/probes/`](plans/03_presence-update-rule/probes/), not written out
  by hand. Missing teacher files print `NOT_RUN`.
- **Never cite from recall.** Every identifier is fetched. Three bibliography entries turned out to
  be wrong under this rule, and one of them is what triggered the pivot.
- **Pre-register comparisons.** Frozen splits, ≥3 seeds, tuning parity, a declared effect size, and
  "inconclusive" pre-authorised as a publishable outcome.
- **Escalation ladders are declared in advance**, and the rung that fired is reported in every
  downstream claim.
- **Stopping is a result.** A ladder that halts at a measured limit is reported as that limit, not
  quietly extended.
