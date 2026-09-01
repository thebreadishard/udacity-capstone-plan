# Udacity AI Mastery — Capstone Project Plan

> **This repository is a planning and coordination artifact.** It contains no implementation and no
> results. Its purpose is to design a coherent research project and distribute it across the Udacity
> Master in AI capstone sequence (Modules 02–09), so that every module both advances the science
> *and* satisfies the school's rubric.

---

## Three plans, side by side

The project has been planned three times. **All three plans are kept in full**, in [`plans/`](plans/),
rather than one being overwritten by the other. Plans 01 and 02 stay until a later deletion pass.

| | Plan | Status |
|---|---|---|
| **01** | [Voxel Field PES (FNO-NCA)](plans/01_voxel-field-pes/) | Superseded 2026-08-23 — complete as a plan; not in development |
| **02** | [Coupled-Cluster Anharmonic IR](plans/02_coupled-cluster-anharmonic-ir/) | Superseded 2026-08-29 — complete as a plan; blocked on measurement |
| **03** | [Presence-Update-Rule](plans/03_presence-update-rule/) | **Current.** Draft as of 2026-09-01; **not** complete as a plan; not executed |

Start at [`plans/README.md`](plans/README.md) for the comparison and for why the project turned.

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
│   ├── README.md                          comparison of the three plans
│   ├── 01_voxel-field-pes/                superseded 2026-08-23
│   ├── 02_coupled-cluster-anharmonic-ir/  superseded 2026-08-29
│   └── 03_presence-update-rule/           current — draft, not complete
│       ├── GoalGathering/                 prime directive, freeze, mapping, bibliography,
│       │   │                              inheritance map, Round-5 review briefs
│       │   └── Horizon/                   projects 10–12 (phase, pair density, scale)
│       ├── probes/                        scripts; missing teacher files print NOT_RUN
│       └── PATCH_plans_README.md          applied 2026-09-01; still forbids “complete”
│
├── Rubrics/                               SHARED — Udacity module rubrics 01–09, treated as fixed
├── Papers/                                SHARED — reference PDFs, numbered to each plan's bibliography
├── AI_Chats/                              SHARED — the planning conversations behind the project
├── scraper/                               tooling, and the raw scrapes it produced
├── requirements.txt
└── README.md                              ← you are here
```

**Shared** is anything no plan may claim as its own. The Udacity rubrics are the constraint all three
were designed against; the literature is not version-specific; and the planning conversations predate
the splits. Everything else is duplicated on purpose, so each plan reads without cross-references.

The **professor reviews are deliberately not shared.** Rounds 1–3 reviewed plan 01 and live there;
Round 4 reviewed plan 02 and lives there. Plan 03 has **no** `Professor_Review_*` yet. It carries an
[inheritance map](plans/03_presence-update-rule/GoalGathering/Inheritance_of_Reviews.md) of the
thirty source findings — because copying those reviews across would imply plan 03 had survived them.

Documents 10–12 are **not** rubrics — they are each plan's own horizon-planning documents, and they
differ between plans, which is why they sit inside `GoalGathering/Horizon/`.

## Conventions this repository tries to keep

These outlived the pivot and are the most portable thing here:

- **Measured, not asserted.** Arithmetic that matters is executed in
  [`plans/03_presence-update-rule/probes/`](plans/03_presence-update-rule/probes/), not written out
  by hand. Missing teacher files print `NOT_RUN`. Plan 01’s probes remain as the record of that plan.
- **Never cite from recall.** Every identifier is fetched. Three bibliography entries turned out to
  be wrong under this rule, and one of them is what triggered the pivot.
- **Pre-register comparisons.** Frozen splits, ≥3 seeds, tuning parity, a declared effect size, and
  "inconclusive" pre-authorised as a publishable outcome.
- **Escalation ladders are declared in advance**, and the rung that fired is reported in every
  downstream claim.
- **Stopping is a result.** A ladder that halts at a measured limit is reported as that limit, not
  quietly extended.
