# Udacity AI Mastery — Capstone Project Plan

> **This repository is a planning and coordination artifact.** It contains no implementation and no
> results. Its purpose is to design a coherent research project and distribute it across the Udacity
> Master in AI capstone sequence (Modules 02–09), so that every module both advances the science
> *and* satisfies the school's rubric.

---

## Two plans, side by side

The project has been planned twice. **Both plans are kept in full**, in [`plans/`](plans/), rather
than one being overwritten by the other.

| | Plan | Status |
|---|---|---|
| **01** | [Voxel Field PES (FNO-NCA)](plans/01_voxel-field-pes/) | Superseded 2026-08-23 — complete, coherent, not in development |
| **02** | [Coupled-Cluster Anharmonic IR](plans/02_coupled-cluster-anharmonic-ir/) | **Current** — rewrite in progress |

Start at [`plans/README.md`](plans/README.md) for the comparison and for why the project turned.

## The current objective (plan 02)

**Anharmonic infrared band families and relative intensities for named PAH sizes and charge states**,
from a potential-energy surface anchored to a **measured** coupled-cluster reference, with quantum
nuclear motion (GVPT2-class) and a **four-term error budget** — ending in a **pre-registered,
fail-closed identification** against one frozen JWST/PAHdb product.

Precision is carried by the theory ladder and the nuclear-motion method, not by a novel neural
architecture. Established equivariant machine-learned potentials are fine-tuned and Δ-learned up to
the gold rung; the contribution is the anchor, the budget and the fail-closed rule.

**Not claimed:** rovibrational line lists, sub-wavenumber lines, or "any size" without the measured
stop rung attached. Classical MD + dipole-ACF FFT is a diagnostic, not the deliverable.

## Repository layout

```
CapstonePlan/
├── plans/
│   ├── README.md                          comparison of the two plans, and why 01 was superseded
│   ├── 01_voxel-field-pes/                superseded plan, complete
│   │   ├── GoalGathering/                 prime directive, technical plan, module mapping,
│   │   │   │                              bibliography, 3 professor reviews
│   │   │   └── Horizon/                   this plan's own projects 10–12
│   │   ├── probes/                        numerical probes that measure the plan's arithmetic
│   │   └── Uitleg/                        Dutch VWO-6 explanation, 21 chapters
│   └── 02_coupled-cluster-anharmonic-ir/  current plan
│       ├── GoalGathering/                 + the restructure proposal that argues the pivot
│       │   └── Horizon/                   projects 10–12, marked as absorbed provenance
│       └── probes/
│
├── Rubrics/                               SHARED — Udacity module rubrics 01–09, treated as fixed
├── Papers/                                SHARED — 36 reference PDFs, numbered to the bibliography
├── AI_Chats/                              SHARED — the planning conversations behind the project
├── scraper/                               tooling, and the raw scrapes it produced
├── requirements.txt
└── README.md                              ← you are here
```

**Shared** is anything neither plan may claim as its own. The Udacity rubrics are the constraint both
were designed against; the literature is not version-specific; and the planning conversations predate
the split — the original ambition recorded in `gemini_chat_1.md` is closer to plan 02's goal than to
plan 01's. Everything else is duplicated on purpose, so each plan reads without cross-references.

The **professor reviews are deliberately not shared.** They reviewed plan 01. Copying them into plan
02 would imply plan 02 had survived them, and Round 4 is still pending; plan 02 carries an
inheritance table instead, showing where each of the fifteen blocking issues landed.

Documents 10–12 are **not** rubrics — they are each plan's own horizon-planning documents, and they
differ between plans, which is why they sit inside `GoalGathering/Horizon/`.

## Conventions this repository tries to keep

These outlived the pivot and are the most portable thing here:

- **Measured, not asserted.** Arithmetic that matters is executed in
  [`probes/`](plans/01_voxel-field-pes/probes/), not written out by hand.
- **Never cite from recall.** Every identifier is fetched. Three bibliography entries turned out to
  be wrong under this rule, and one of them is what triggered the pivot.
- **Pre-register comparisons.** Frozen splits, ≥3 seeds, tuning parity, a declared effect size, and
  "inconclusive" pre-authorised as a publishable outcome.
- **Escalation ladders are declared in advance**, and the rung that fired is reported in every
  downstream claim.
- **Stopping is a result.** A ladder that halts at a measured limit is reported as that limit, not
  quietly extended.
