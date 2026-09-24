# Udacity AI Mastery — Capstone Project Plan

This repository is the planning and coordination record of one research project: a pipeline that turns any
individual aromatic molecule into an infrared spectrum with a coupled-cluster-anchored correction, scored
against laboratory data and against the best existing predictions, and built across the eight modules of the
Udacity AI Master capstone sequence (Modules 02–09) so that every module both advances the science and
satisfies the school's rubric. It contains **no pipeline results**: no rung of the plan has run and been scored. What
has run are *probes* (measurements about the data and about the method, each committed with its raw evidence), the
first versions of four course modules, a corpus of cheap-level Hessians, and a sibling idea plan. A public, lay-level lab notebook in English
lives at <https://thebreadishard.github.io/> (separate repository, same evidence rules).

## Where things stand (24 September 2026)

- **Plan 05 is the current plan**, created 3 September 2026; its text has been frozen since 4 September and changes only
  by dated notes that name a measurement or a decision. Fifty numbered decisions have been taken under that rule. The
  conversation with the academic supervisor is on **28 September** (decision 44); the desk package (cover note, reading
  copy, plan 06 annex) is in `plans/05_delta-probed-ir-pipeline/GoalGathering/`.
- **The anchor run finished on 24 September** (21:02, after eight days on the laptop): probe M3's coupled-cluster-anchored decks for
  naphthalene at cc-pVTZ, read family by family against pre-registered criteria. Family 1 (out-of-plane, mode 12) lost — that
  family stays on the expensive basis; family 2 (in-plane C–H bend, mode 22) won on 23 September; family 3 (C–C stretch, mode 31)
  came out between the win and lose lines on 24 September (4.1 cm⁻¹ off the transferred benzene value) and stays on the expensive
  basis too. The R0 diagonal deck was read on 22 September (in-plane frequencies improve against CCSD(T), out-of-plane do not,
  C–H stretches need the geometry term). Since 24 September 21:24 the laptop runs the four densification points of decision 45
  (mode 12, for the error budget's σ), expected to finish around 26 September; nothing else runs locally until then.
- **A corpus exists** (module 05's factory, run on rented Hetzner servers): deck v1 — B3LYP and ωB97X 6-31G* geometries and
  Hessians — for 244 molecules (layers A and A2 of a 11,321-row manifest), frozen as releases on 22 and 23 September. Its
  quality is guarded by a second route: benzene's finite-difference Hessian was found wrong by 133 cm⁻¹ (psi4's default
  grid with a 0.005 bohr step), replaced by an analytic Hessian, and the guard is now policy (decision 50); the twenty
  molecules with an imaginary mode are on the same second route tonight.
- **Module 05 has run in full three times** and its two pre-registered experiments changed the design: E6 (a learning curve
  at 45, 100 and 175 molecules) showed that no mode-basis model learns the couplings of the correction matrix; E7 traced
  it to the target and showed that the same molecules teach the couplings once the target is written as pairwise local
  terms in primitive internal coordinates (ring coupling ratio 0.43 / 0.47 on two hold-outs, corrected frequencies within
  4.7 / 5.1 cm⁻¹ against 23 without correction). Decision 49: the couplings are learned in local coordinates. E8 — does the
  coupled-cluster correction live in the same local pattern — is running (benzene CCSD(T)/cc-pVDZ Hessian, read-out 24
  September; naphthalene pre-authorised on a win).
- **Course modules in rubric form** (`modules/`): 02 the opponent atlas (runs from the repository alone since 22 September),
  03 the laboratory scoreboard (report rebuilt with the 31-column dataset; a pre-registered matrix–gas test; shape-score
  columns against PAHdb), 04 the calibrated-harmonic baseline (unchanged since 12 September; no model beats the library),
  05 the support predictor (executed notebook and report, with the E6/E7 outcome as follow-up cells so the reviewer sees
  what was learned).
- **Own software and its policy**: `src/dpir` (quartic force fields and VPT2 from analytic Hessians, provenance) with tests
  and CI, promoted from probes under a two-tier quality policy with a mechanical gate (decision 47, `QUALITY_POLICY.md`);
  the noise principle of 21 September — every derived quantity gets a second route or a symmetry check — after the
  finite-difference quartics turned out to be noise.
- **Plan 06** stays an idea plan beside plan 05: experiments X1–X22 on plan 05's sealed data (X19, an IP-tuned functional,
  lost; X22 measured that the gradient count grows linearly at every symmetry of the layer-A molecules), theorems T1a–T1c
  proved in Lean 4 / Mathlib (no `sorry`). Anything it finds enters plan 05 only through plan 05's own dated notes.
- **Public face**: eleven lay-level posts on the blog; a public website ("Spectrum Atlas", a status ladder per molecule with
  provenance on every number) designed on 23 September in `website/`, nothing built.
- **Mandate (13 September)**: an affordable plan — a desktop plus a small Snellius allocation must suffice to train the
  network by 2027 — with the standing instruction to keep solving obstacles autonomously; the obstacle ledger is in
  `GoalGathering/notes/`.

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
| **05** | [Δ-Probed-IR-Pipeline](plans/05_delta-probed-ir-pipeline/) | **Current.** Created 2026-09-03; review rounds 7–10 addressed; text frozen 2026-09-04; decisions 1–50; the anchor running, a 244-molecule corpus, four modules, own software under a quality policy — as listed above. |
| **06** | [Equivalent-Faster-Mathematics](plans/06_equivalent-faster-mathematics/) | **Idea plan beside 05** (opened 2026-09-12): experiments X1–X22 on plan 05's sealed data, theorems T1a–T1c in Lean; no rungs, no modules; feeds plan 05 by dated notes only. |

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
│   │   ├── README.md                        status, reading order, review record, decisions 1–50, dated notes, what is owed
│   │   ├── QUALITY_POLICY.md                two-tier code policy with its mechanical gate (decision 47)
│   │   ├── GoalGathering/                   goal, ladder, budget, gates, bibliography, the supervisor proposal;
│   │   │   ├── notes/                       research notes, decision memos, pre-registrations, the obstacle and software ledgers
│   │   │   ├── architecture/                the architecture sheets (mermaid) and ARCHITECTURE.md
│   │   │   └── reviews/                     review rounds 7–10, cold reads, seam checks
│   │   ├── modules/                         the course modules in rubric form
│   │   │   ├── 02_opponent_atlas/           PAHdb as served: the opponents (notebook, report, provenance)
│   │   │   ├── 03_lab_scoreboard/           laboratory bands with u_band; pre-registered matrix–gas test
│   │   │   ├── 04_calibrated_harmonic/      the calibrated baseline; recipe committed before training
│   │   │   └── 05_support_predictor/        the support predictor: corpus factory (244 molecules done), E6/E7 scripts, executed notebook and report
│   │   ├── probes/                          probe scripts, engine patches, launcher, and the results:
│   │   │   ├── results_dryrun/              DFT Δ-recovery dry run (benzene; naphthalene geometry)
│   │   │   ├── results_timing/              anchor single points, canonical gradient, naphthalene timings
│   │   │   ├── results_m1/                  probe M1 and M3 runs, the sealed truth line, the basis line, the R0 deck read
│   │   │   ├── results_m2a/ results_m2b/ results_m4/   later probe families
│   │   │   ├── results_vpt2/                the VPT2 runs and the finite-difference noise demonstration
│   │   │   └── results_m03/                 R0 scoreboard, Q10 readiness
│   │   ├── src/dpir/                        own software (QFF, VPT2, provenance) — promoted code only
│   │   ├── tests/  tools/                   its tests; the stamp, staged-path and architecture-sync tools
│   │   └── Uitleg/                          Dutch lay explanation of plan 05, 18 chapters (not binding)
│   └── 06_equivalent-faster-mathematics/    IDEA PLAN beside 05 (opened 2026-09-12)
│       ├── GoalGathering/                   orientation, ledger of directions, reading and result notes
│       ├── experiments/                     X1–X5 on plan 05's sealed data (scripts and printed tables)
│       ├── lean/                            Lean 4 + Mathlib project: the recovery theorems (no `sorry`)
│       └── Uitleg/                          Dutch lay explanation of plan 06, 7 chapters
│
├── website/                                 the public Spectrum Atlas: design and backlog (nothing built)
├── Rubrics/                                 Udacity module rubrics 01–09 and the APA template, treated as fixed
├── docs/                                    repository-level records (the PDF inventory and history rewrite of 6 September)
├── Papers/                                  local only, git-ignored: the working copies of the literature
├── AI_Chats/                                planning conversations (primary sources, not a plan)
├── scraper/                                 tooling, and the raw scrapes it produced
├── requirements.txt
└── README.md                                this file
```

Literature PDFs are not in the repository (37 were removed from the history on 6 September 2026 — record in
[`docs/Papers_Inventory_2026-09-06.md`](docs/Papers_Inventory_2026-09-06.md); the plan bibliographies hold the references,
`Papers/` is a local working copy). The planning conversations predate the
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
