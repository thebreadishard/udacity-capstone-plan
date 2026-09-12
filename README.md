# Udacity AI Mastery — Capstone Project Plan

This repository is the planning and coordination record of one research project: a pipeline that turns any
individual aromatic molecule into an infrared spectrum with a coupled-cluster-anchored correction, scored
against laboratory data and against the best existing predictions, and built across the eight modules of the
Udacity AI Master capstone sequence (Modules 02–09) so that every module both advances the science and
satisfies the school's rubric. It contains **no pipeline results**: no rung of the plan has run. What has run
are *probes* (measurements about the data and about the method, each committed with its raw evidence), the
first versions of four course modules, and a sibling idea plan. A public, lay-level lab notebook in English
lives at <https://thebreadishard.github.io/> (separate repository, same evidence rules).

## Where things stand (12 September 2026)

- **Plan 05 is the current plan**, created 3 September 2026; its text has been frozen since 4 September and
  changes only by dated notes that name a measurement or a decision. Thirty-five numbered decisions have been
  taken under that rule. The project proposal goes to the academic supervisor on 14 September.
- **Probes that have run** (plan 05, `probes/`): the DFT dry run of the Δ-recovery at benzene; the anchor
  timing probes (benzene single points at cc-pVDZ and cc-pVTZ, one canonical CCSD(T) gradient, one naphthalene
  LNO-CCSD(T)/cc-pVTZ energy at 11.5 h on the laptop; the same at the anchor's tighter thresholds is running);
  probe M1, the frozen local-correlation spaces against a canonical truth line, at cc-pVDZ and cc-pVTZ and at
  two threshold settings; the cheap basis-set line (cc-pVQZ and cc-pV5Z) that put two basis terms into the
  anchor (decision 33); and the laboratory band-uncertainty columns of Module 03.
- **Course modules in rubric form** (`modules/`): 02 the opponent atlas (first version complete), 03 the
  laboratory scoreboard with a pre-registered matrix–gas test (six families reject a zero offset), 04 the
  calibrated-harmonic baseline with a committed-before-training recipe (no model beats the library; that
  baseline is what the pipeline must beat), 05 the Δ₂-support predictor (Hessian QM9 downloaded and inventoried,
  a resumable corpus factory prepared, notebook and report skeletons in place; nothing trained).
- **Plan 06** is an idea plan beside plan 05, not a successor: is there an equivalent but faster mathematics
  for the electronic problem plan 05 solves at its anchor? It has an orientation with six directions and their
  falsification tests, seven small experiments on plan 05's sealed data, verified reading notes, and a Lean 4 /
  Mathlib project in which the algebra of one direction (sparse recovery of the correction from colour-class
  probes) is proved. Anything it finds enters plan 05 only through plan 05's own dated notes; its first transfer
  is plan 05 decision 34.

Nothing above is a spectrum, an accuracy claim or a "beat". The plan's own rule: not claimed are absolute
"chemical precision", JWST species identification, and any rung that has not run and been scored.

## Plan versions

The project was planned five times before the current plan settled; all folders are in the tree, the earlier
ones as read-only records. Plan 02's raw frequency arrays (ten `.npz` Hessians, about ten hours of psi4) live
in git history only: `git show 57a7910:<path>` retrieves one.

| | Plan | Status |
|---|---|---|
| **01** | [Voxel-Field-PES](plans/01_voxel-field-pes/) | Superseded 2026-08-23; read-only record. |
| **02** | [Coupled-Cluster-Anharmonic-IR](plans/02_coupled-cluster-anharmonic-ir/) | Superseded 2026-08-29; read-only record. |
| **03** | [Presence-Update-Rule](plans/03_presence-update-rule/) | Superseded by 04 (2026-09-02); read-only record. Draft; never complete as a plan; never executed. |
| **04** | [CC-Anchored-IR-Pipeline](plans/04_cc-anchored-ir-pipeline/) | Superseded by 05 (2026-09-03); read-only record. Round-6 reviews run and addressed; never executed. |
| **05** | [Δ-Probed-IR-Pipeline](plans/05_delta-probed-ir-pipeline/) | **Current.** Created 2026-09-03; review rounds 7–10 addressed; text frozen 2026-09-04; decisions 1–35; probes and four modules run as listed above. |
| **06** | [Equivalent-Faster-Mathematics](plans/06_equivalent-faster-mathematics/) | **Idea plan beside 05** (opened 2026-09-12): no rungs, no modules, no results of its own; feeds plan 05 by dated notes only. |

[`plans/README.md`](plans/README.md) explains why the earlier plans were dropped and what plan 05 inherits.

## The objective

A **per-molecule infrared pipeline**: equilibrium geometry, a DFT Hessian, and a coupled-cluster correction
to the harmonic force constants, **probed** rather than computed in full — recovered from a measured number
of local coupled-cluster energies with frozen correlation spaces, the count printed beside every spectrum as a
cost record ([plan 05 Goal](plans/05_delta-probed-ir-pipeline/GoalGathering/Overarching_Goal.md)). The
success criterion is relative, measured and gated: agree with known truth on the small molecules; beat the
best prediction available anywhere for that molecule (PAHdb v4.00 scaled-harmonic DFT, the anharmonic
small-molecule front, a 2025 machine-learned line, and this project's own calibrated baseline) per band
against laboratory data **where the data can decide it**; and earn, rung by rung, the trust needed for the
sizes where nothing can check anyone. Opponents are named and versioned in
[Frozen_Lines_to_Beat.md](plans/05_delta-probed-ir-pipeline/GoalGathering/Frozen_Lines_to_Beat.md); the
rungs, tolerances and gates in [Frozen_Ladder_and_Tolerances.md](plans/05_delta-probed-ir-pipeline/GoalGathering/Frozen_Ladder_and_Tolerances.md).

Size must scale to the 101–386-carbon PAHdb bin, where the only existing predictions are scaled harmonic
B3LYP/4-31G. Compute starts on a laptop (the benzene rung) and moves to a cluster when a rung demands it;
the measured cost per naphthalene energy is what the cluster request will be sized on. Emission after UV
heating (the astronomical use case) is a declared post-processing tier, not a co-owned solver. The module
sequence ends at Module 09; a network trained on the pipeline's own output is named as follow-up work outside
the sequence, gated by measured conditions (decision 32).

## Repository layout

```
CapstonePlan/
├── plans/
│   ├── README.md                            why 01–04 were dropped; 05 current; 06 the idea plan
│   ├── 01_voxel-field-pes/                  superseded, read-only
│   ├── 02_coupled-cluster-anharmonic-ir/    superseded, read-only
│   ├── 03_presence-update-rule/             superseded, read-only
│   ├── 04_cc-anchored-ir-pipeline/          superseded, read-only (its NIST gas-coverage probe is evidence still used)
│   ├── 05_delta-probed-ir-pipeline/         CURRENT — created 2026-09-03, text frozen 2026-09-04
│   │   ├── README.md                        status, reading order, review record, decisions 1–35, dated notes, what is owed
│   │   ├── GoalGathering/                   goal, ladder, budget, gates, bibliography, the supervisor proposal;
│   │   │   ├── notes/                       research notes, decision memos, the software-changes ledger
│   │   │   └── reviews/                     review rounds 7–10, cold reads, seam checks
│   │   ├── modules/                         the course modules in rubric form
│   │   │   ├── 02_opponent_atlas/           PAHdb as served: the opponents (notebook, report, provenance)
│   │   │   ├── 03_lab_scoreboard/           laboratory bands with u_band; pre-registered matrix–gas test
│   │   │   ├── 04_calibrated_harmonic/      the calibrated baseline; recipe committed before training
│   │   │   └── 05_support_predictor/        Δ₂-support Transformer: corpus factory, skeletons (nothing trained)
│   │   ├── probes/                          probe scripts, engine patches, launcher, and the results:
│   │   │   ├── results_dryrun/              DFT Δ-recovery dry run (benzene; naphthalene geometry)
│   │   │   ├── results_timing/              anchor single points, canonical gradient, naphthalene timings
│   │   │   ├── results_m1/                  probe M1 runs, the sealed truth line, the basis line
│   │   │   └── results_m03/                 R0 scoreboard, Q10 readiness
│   │   └── Uitleg/                          Dutch lay explanation of plan 05, 18 chapters (not binding)
│   └── 06_equivalent-faster-mathematics/    IDEA PLAN beside 05 (opened 2026-09-12)
│       ├── GoalGathering/                   orientation, ledger of directions, reading and result notes
│       ├── experiments/                     X1–X5 on plan 05's sealed data (scripts and printed tables)
│       ├── lean/                            Lean 4 + Mathlib project: the recovery theorems (no `sorry`)
│       └── Uitleg/                          Dutch lay explanation of plan 06, 7 chapters
│
├── Rubrics/                                 Udacity module rubrics 01–09 and the APA template, treated as fixed
├── Papers_Inventory_2026-09-06.md           why the PDFs left the repository and how the history was rewritten
├── Papers/                                  local only, git-ignored: the working copies of the literature
├── AI_Chats/                                planning conversations (primary sources, not a plan)
├── scraper/                                 tooling, and the raw scrapes it produced
├── requirements.txt
└── README.md                                this file
```

Literature PDFs are not in the repository (37 were removed from the history on 6 September 2026; the plan
bibliographies hold the references, `Papers/` is a local working copy). The planning conversations predate the
plan folders and belong to none of them. Plan 03's review record, whose architectural verdict (one scope, one
clock) binds plans 04 and 05, is in the plan-03 folder.

## Conventions this repository tries to keep

These outlived every pivot and are the most portable thing here:

- **Measured, not asserted.** Every number in a plan document is printed by a script in `probes/` or
  `experiments/`, or its arithmetic is shown in place. Missing inputs print `NOT_RUN`.
- **Never cite from recall.** Every reference is fetched and verified (Crossref, DataCite, or the full text).
  Several bibliography entries turned out wrong under this rule, and one of them triggered a pivot.
- **Pre-register comparisons.** Recipes and tests are committed before the data they judge exist; frozen
  splits, several seeds, tuning parity, a declared effect size, and "inconclusive" pre-authorised as an outcome.
- **Frozen text, dated notes.** A frozen plan changes only by a dated note that names the measurement or
  decision behind the change; corrections are appended, never rewritten.
- **Stopping is a result.** A ladder that halts at a measured limit is reported as that limit, not quietly
  extended; long runs log their progress hourly and can be resumed.
