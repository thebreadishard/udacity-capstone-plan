# Udacity AI Mastery — Capstone Project Plan

> **This repository is a planning and coordination artifact.** It contains no pipeline results:
> no rung of plan 04 or plan 05 has run. What has run (state 2026-09-06) are **probes** —
> measurements about data and about the method, each committed with its raw evidence: plan 04's
> laboratory-coverage probe; plan 05's DFT dry run (benzene), the anchor timing probes (single
> points and one canonical CCSD(T) gradient at cc-pVDZ), and **probe M1** (frozen local-CC spaces
> against a canonical truth line, benzene, four runs at cc-pVDZ; the cc-pVTZ run is in progress).
> It also contains tooling — probe scripts, a scraper — and a Dutch lay explanation of plan 05.
> A public lay-level lab notebook in English lives at <https://thebreadishard.github.io/>
> (separate repository; same evidence rules).
> Its purpose is to design a coherent research project and distribute it across the Udacity Master in AI
> capstone sequence (Modules 02–09), so that every module both advances the science *and* satisfies the
> school's rubric.

> **Plan 05 is current.** Plans 01–04 are superseded and kept in the tree as read-only records:
> nothing in them is current, and they are not edited.
>
> **Current: plan 05.** Plan 05 — [Δ-Probed IR Pipeline](plans/05_delta-probed-ir-pipeline/) —
> was created on 2026-09-03 and supersedes plan 04, keeping plan 04's product, criterion,
> ladder, opponents and gates and changing one thing: the coupled-cluster anchor is a
> **probed correction to the force constants** (probe count measured per rung) instead of a learned per-molecule surface.
>
> **Plan 04** — [CC-Anchored IR Pipeline](plans/04_cc-anchored-ir-pipeline/) —
> was created on 2026-09-02 and superseded plan 03. Round-5 Pass B gave **no green light** for plan
> 03's frozen scope, and that verdict binds the architecture of plans 04 and 05 (one scope, one clock).
>
> **Plan 04 product.** Module 08 ships a pipeline: any individual aromatic molecule in, an
> infrared spectrum out — scored against frozen state-of-the-art lines
> ([Frozen_Lines_to_Beat.md](plans/04_cc-anchored-ir-pipeline/GoalGathering/Frozen_Lines_to_Beat.md)),
> with pre-registered gates: "beat" claims are unconditional only on the gas-phase rungs
> (benzene, naphthalene — plan 05: both expected unconditional on named room-temperature sources); larger accuracy rungs are decided — or pre-declared inconclusive —
> by a measured matrix–gas gate, and the C₃₈₄H₄₈-class reach demonstration is conditional on
> cluster access and carries no accuracy claim.
> The sequence ends at Module 09. There are **no** Projects 10–12. Demonstrably-better IR of
> complex aromatics is the reason for the work, not a horizon item after the degree.

---

## Plan versions

The project was planned five times. All five plans are in the tree: plan 05 is current, plans 01
(voxel field PES), 02 (coupled-cluster anharmonic IR), 03 (presence-update rule) and 04 (CC-anchored
IR pipeline) are superseded, read-only records. One thing lives in git history only: plan 02's raw
frequency arrays (ten `.npz` Hessians and geometries, ~10 h of psi4), committed in `57a7910` —
retrieve one with `git show 57a7910:<path>`.

Plan **05 is the current plan** (created 2026-09-03). It keeps plan 04's product and criterion —
a per-molecule IR pipeline whose success criterion is **relative, measured and gated**: agree with
known truth on small PAHs, beat the best available prediction per band where the laboratory data
can decide it, and earn trust for the sizes where nothing can check anyone — and replaces plan
04's learned per-molecule surface with a **probed** coupled-cluster correction to the force
constants, at a probe count measured per rung.

| | Plan | Status |
|---|---|---|
| **03** | [Presence-Update-Rule](plans/03_presence-update-rule/) | Superseded by 04 (2026-09-02); read-only record. Draft; never complete as a plan; never executed. |
| **01** | [Voxel-Field-PES](plans/01_voxel-field-pes/) | Superseded 2026-08-23; read-only record. |
| **02** | [Coupled-Cluster-Anharmonic-IR](plans/02_coupled-cluster-anharmonic-ir/) | Superseded 2026-08-29; read-only record. |
| **04** | [CC-Anchored-IR-Pipeline](plans/04_cc-anchored-ir-pipeline/) | Superseded by 05 (2026-09-03); read-only record. Draft; Round-6 reviews run and addressed; never executed. |
| **05** | [Δ-Probed-IR-Pipeline](plans/05_delta-probed-ir-pipeline/) | **Current.** Created 2026-09-03; Rounds 7–10 (A, B) run and addressed; **plan text frozen 2026-09-04** (changes only by dated notes naming a measurement or decision); the nineteen open decisions closed 2026-09-05/06; **probe M1 measured** (frozen spaces smooth to 0.002–0.06 µE_h and, with tight thresholds and the composite energy, biased by 0.015–0.18 cm⁻¹ against canonical CCSD(T) at cc-pVDZ — [research note](plans/05_delta-probed-ir-pipeline/GoalGathering/Research_Note_2026-09-05_Probe_M1.md)); the laboratory sources for module 03 read and recorded 2026-09-06; the [supervisor proposal](plans/05_delta-probed-ir-pipeline/GoalGathering/Project_Proposal_2026-09-06.md) rewritten as one document 2026-09-06 and awaiting her reading. Same product and criterion as 04; CC anchor by probing the CC−DFT harmonic force-constant correction. No rung has run. |

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
can decide it** — benzene and naphthalene unconditionally on room-temperature gas spectra (expected), the
larger accuracy rungs per family by the measured band-centre uncertainty and the matrix–gas
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
│   ├── 01_voxel-field-pes/                superseded 2026-08-23, read-only
│   ├── 02_coupled-cluster-anharmonic-ir/  superseded 2026-08-29, read-only
│   ├── 03_presence-update-rule/           superseded 2026-09-02, read-only
│   ├── 04_cc-anchored-ir-pipeline/        superseded 2026-09-03, read-only
│   │   ├── GoalGathering/                 prime directive, frozen lines, Round-6 reviews, proposal
│   │   └── probes/                        the NIST gas-coverage probe (evidence in-tree)
│   └── 05_delta-probed-ir-pipeline/       current — created 2026-09-03, text frozen 2026-09-04
│       ├── GoalGathering/                 goal, ladder, budget, gates, bibliography, research notes,
│       │                                  review rounds 7–10, the supervisor proposal (2026-09-06)
│       ├── Uitleg/                        Dutch lay explanation, 18 chapters (not binding)
│       └── probes/                        conventions, the probes owed, and the probes that ran:
│           ├── results_dryrun/            DFT Δ-recovery dry run (benzene)
│           ├── results_timing/            anchor single points and the cc-pVDZ canonical gradient
│           └── results_m1/                probe M1 runs and the sealed canonical truth line
│
├── Rubrics/                               Udacity module rubrics 01–09, treated as fixed
├── Papers/                                local only, git-ignored since 2026-09-06 — see Papers_Inventory
├── Papers_Inventory_2026-09-06.md         why the PDFs left the repository and how the history was rewritten
├── AI_Chats/                              planning conversations (primary sources, not a plan)
│                                          — grok_chat_4.md is plan 04's source conversation
├── scraper/                               tooling, and the raw scrapes it produced
├── requirements.txt
└── README.md                              ← you are here
```

The Udacity rubrics are the constraint. Literature PDFs are no longer in the repository: 37 of
them had been committed, were untracked on 2026-09-06 and removed from the history the same day
(git-filter-repo; record in `Papers_Inventory_2026-09-06.md`); the plan bibliographies hold the
references and the folder `Papers/` is a local, git-ignored working copy. Planning conversations
predate the splits and belong to no plan folder.

Plan 03's review record — the Round-5 Pass A cold read (2026-09-01, findings addressed in spec
the same day), the Round-5 Pass B adversarial domain review (2026-09-01, **findings not
addressed**: no green light for the scope as frozen), and an inheritance map of thirty source
findings from plans 01 and 02 — is in the plan-03 folder. Pass B's architectural verdict (one
scope, one clock) binds plans 04 and 05 and is restated in their prime directives.

Documents 10–12 in plan 03's `Horizon/` folder are **not** rubrics — they were plan 03's horizon.
Plans 04 and 05 have no horizon documents.

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
