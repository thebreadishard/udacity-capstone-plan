# Inheritance of reviews — Plan 03

Professor reviews of plans 01 and 02 are **not** copied here. Copying them would imply plan 03 had survived them. This file is a **map**, not a stamp.

Sources (do not paste):

- Plan 01 Round 1: blocking issues **1–6**
- Plan 01 Round 2: blocking issues **7–15** (continues the numbering)
- Plan 01 Round 3: blocking findings **R3-1 … R3-6** (separate list)
- Plan 02 Round 4 Pass A: documentation-status issues **R4A-1 … R4A-3**
- Plan 02 Round 4 Pass B: domain issues **R4B-1 … R4B-6**

Fate vocabulary (same as plan 02, so a reviewer can audit without a new glossary):

| Fate | Meaning here |
|---|---|
| **Superseded** | The object of the finding does not exist in plan 03. |
| **Re-scoped** | The *class* of finding still applies, to a different named object. |
| **Carried** | The same constraint is still live. Named file. |
| **Addressed in spec** | Plan 03’s written architecture owns the hole (not yet science). |

This table is the argument of record for “what happened to the old issues.” A summary sentence that does not match the named rows is a defect (lesson of R4A-3).

---

## Itemised tally (30 source findings)

Each of **1–15, R3-1…R3-6, R4A-1…R4A-3, R4B-1…R4B-6** has exactly one primary fate.

| Fate | Count | Issues |
|---|---:|---|
| Superseded | 8 | 2, 10, 11, 14, R3-2, R4B-1, R4B-3, R4B-4 |
| Re-scoped | 5 | 1, 7, 12, R3-1, R3-4 |
| Carried | 16 | 3, 4, 5, 8, 9, 13, 15, R3-3, R3-5, R3-6, R4A-1, R4A-2, R4A-3, R4B-2, R4B-5, R4B-6 |
| Addressed in spec | 1 | 6 |

Check: \(8+5+16+1=30\).

**Open in 03** is a flag on a subset, not a fifth fate: **3** (no teacher cube), **5 / R3-3** (voxel DOI + mentor approval; bibliography item 10 FAIL), **7** (Q1/Q2 on a real teacher), **14** (Module 03 dataset not yet pinned to an accepted source), **15 / R3-6** (T0 not a calendar date), **R4B-2** (`teacher_cost.py` prints `NOT_RUN`).

Closing a row in *spec* is not a green light. Plan 03's own review record is one pass deep:
[Round 5 Pass A](Professor_Review_2026-09-01_Round5_PassA.md), a cold read, 2026-09-01. The adversarial
domain pass (Pass B) has not run.

---

## Plan 01 Round 1 (issues 1–6)

| # | Finding | Fate in 03 | Where |
|---|---|---|---|
| 1 | Phase 1 / critical ML result has no owner | **Re-scoped.** The thesis stencil is Module 05 **Task B**, not an ungraded workstream between 04 and 07. Task A is the rubric shield. | [Capstone_Mapping.md](Capstone_Mapping.md) M05 |
| 2 | Energy is not yet a functional of the field | **Superseded** as a PES. Plan 03 does not learn \(E[\rho]\). Distilled §5 still requires an implementable 11-channel conv, not a slogan. | Distilled §5 |
| 3 | Data-generation claim is not a method | **Carried.** Teacher recipe is written (code, ALDA, Maxwell, \(\Delta t\), windows, stop). **Open as science** until Octopus prints a cube. | Distilled §3; [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md); `probes/teacher_cost.py` |
| 4 | Two governing documents disagree | **Carried as a class.** Contradiction pass 2026-09-01 closed the known ORs. A new Pass A must still hunt leftovers (README vs PATCH, Q0 vs M02, “complete”). | [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) |
| 5 | Rubric landmines (synthetic / accepted sources / CNN-family) | **Carried.** M02–M04 third-party tables; M05 CNN-family explicit. **Round 5 Pass A found the carry incomplete:** the closed accepted-sources list was recorded for M04 only, and Module 03 has the same list. Both are now in the matrix. **Open:** M05 Task A voxel DOI unpinned (item 10 FAIL), and the M03 dataset is unpinned. | Mapping; [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) |
| 6 | Thesis comparison sits in the wrong module | **Addressed in spec.** P4 (learned vs frozen linear stencil) is Distilled §5.3 / §7. Module 08 assembles; it does not invent the comparison. | Distilled §5.3, §7, §8 |

## Plan 01 Round 2 (issues 7–15)

| # | Finding | Fate in 03 | Where |
|---|---|---|---|
| 7 | Grid cannot carry the supervised all-electron density; Phase 0 validates the wrong object | **Re-scoped.** Plan 03 **refuses** 01’s spend: grid frozen at Q0 (\(0.20\,a_0\), nuclear \(h\sim 0.20\,a_0/Z\)) and audited (Q1/Q2), not redesigned for a CC 1-RDM PES. **Open as science** if teacher Q1/Q2 blow up — Distilled §7.3, not a silent coarsening. | Frozen ladder; `probes/grid_hash.py`, `electron_count.py` |
| 8 | Gates self-loosen (artifact folded into the noise floor) | **Carried.** P0–P2 numbers Module 08 may quote now; the 8 h P1 pilot may only **tighten**. Conservation penalty off so P0 is not trained into a tautology. | Frozen ladder; Distilled §6.1, §7.2 |
| 9 | Novelty check missed the field that already owns the idea | **Carried as prior-art duty.** Neighbours: Octopus, Maxwell–TDDFT, 1-D neural TDDFT (Shah & Cangi + RODARE 3995), FNO, NCA. What is scored is the P0–P4 contract, not “we ran TDDFT.” | Distilled §2.1; bibliography items 1–5, 13 |
| 10 | \(\Phi\) is a bypass channel | **Superseded.** No energy head. Poisson reconstruction of \(\mathbf{E}\) from \(\rho\) is forbidden unless Distilled §4. | Distilled §3.1, §4 |
| 11 | IR observable never trained / gated | **Superseded as a product.** IR is not Module 08. Dipole identity remains as **Q2**, a diagnostic, not a spectrum. | Overarching forbidden quotes; `probes/dipole_identity.py` |
| 12 | No invariance budget | **Re-scoped.** Translation equivariance is the shared conv. Rotation is **not** a numbered gate. Do not claim rotational invariance. | Distilled §5.2 |
| 13 | Central comparison is not yet an experiment | **Carried.** Frozen splits, \(\ge 3\) seeds, tuning parity (linear stencil has none), effect size after the 8 h pilot. | Distilled §6.2, §7 |
| 14 | Module 03 row-count arithmetic / noise model | **Superseded** as that egg-box factorial. **Open in 03**: the RODARE flatten was withdrawn on 2026-09-01 (not an accepted source), so M03's dataset is unpinned and no row count has been printed. | Mapping M03; bibliography item 3 |
| 15 | No calendar; hardest work behind a graded submission | **Carried as structure.** 840 h buckets exist; **T0 is not a calendar date** in the mapping draft. Wall-clock 168 h is a **cap**, not a measurement. | Mapping §6; Compute budget |

## Plan 01 Round 3 (R3-1 … R3-6)

| # | Finding | Fate in 03 | Where |
|---|---|---|---|
| R3-1 | Central experiment does not isolate representation | **Re-scoped.** Equal-label analogue: learned stencil vs **frozen linear** stencil on the **same** teacher cubes, same grid, same windows. Field-vs-MACE unequal labels are gone. | Distilled §5.3, P4 |
| R3-2 | Energy and force labels mutually inconsistent | **Superseded.** No PES labels. One teacher trajectory per hashed deck. | Distilled §3 |
| R3-3 | Modules 04–06 dataset eligibility / synthetic | **Carried, still open.** Same mentor-approval hole. Self-run Octopus cubes are **computational experiments** (Task B), not the graded Task A set. Task A now runs an A1/A2/A3 ladder that no longer depends on the FAIL'd item 10 as its own fallback. | Mapping M04–M06; bibliography item 10 FAIL |
| R3-4 | Dipole supervision post-hoc | **Re-scoped.** \(\boldsymbol{\mu}\) is not in the training loss. Q2 prints a residual. No post-hoc \(L_\mu\) rescue. | Distilled §6.1; Q2 |
| R3-5 | “Chemically precise” asserted | **Carried as claim-language.** Teacher is named **ALDA RT-TDDFT**, not chemical accuracy. Forbidden-quotes list. | [Overarching_Goal.md](Overarching_Goal.md) |
| R3-6 | Calendar non-operational | **Carried.** Same as issue 15. | Mapping §6 |

## Plan 02 Round 4 Pass A (documentation)

| # | Finding | Fate in 03 | Where |
|---|---|---|---|
| R4A-1 | Stale README / reading-order vs rewrite-status | **Carried as a class.** Plan 03 README, root README, and `plans/README.md` say **draft, not complete** (index patch applied 2026-09-01). [PATCH_plans_README.md](../PATCH_plans_README.md) is the argument of that apply; it must **not** say “complete as a plan.” | [README.md](../README.md) |
| R4A-2 | Adopted-vs-draft status drift | **Carried.** This folder is **draft as of 2026-09-01.** Plans 01/02 were removed from the tree on 2026-09-01 — documents from version control, and plan 02's leftover psi4 artifacts from disk, after Round 5 Pass A issue 1 found them still there. Plan 02's raw `.npz` arrays were committed (`800f3aa`) before deletion, so the claim “in git history” is now true of everything. | README status banner |
| R4A-3 | Inheritance tally unauditable | **This file.** Named rows. If a later README summary disagrees with the 30-finding table, the README is wrong. | this file |

## Plan 02 Round 4 Pass B (domain)

| # | Finding | Fate in 03 | Where |
|---|---|---|---|
| R4B-1 | Core hypothesis oriented the wrong way (electronic vs nuclear IR error) | **Superseded** as that hypothesis. Plan 03 asks a different question (local stencil vs linear Maxwell+continuity on H₂ → H₂O). A *new* Pass B may still attack whether 3×3×3 is the wrong operator because Hartree/KS is nonlocal. | Overarching Goal; Distilled §2; Round-5 Pass B attack 1 |
| R4B-2 | Cost arithmetic missing / citation was a single point | **Carried.** Caps exist (80 h human I/O, 168 h wall-clock). `teacher_cost.py` prints **NOT_RUN** until a log exists. Do not type hours into markdown. | Compute budget; `probes/teacher_cost.py` |
| R4B-3 | GVPT2 / pyrene-scale congestion | **Superseded.** No QFF, no pyrene, no Module 08 IR. | Frozen ladder Horizon 10–12 |
| R4B-4 | MLIP cannot be assumed to carry CC-quality third derivatives | **Superseded.** No MLIP, no third derivatives. | — |
| R4B-5 | Residual contribution closer to a wrapper than a new method | **Carried as novelty-honesty.** Distilled §2.1: running TDDFT / storing cubes / training a CNN is not novel. The scored object is the frozen P0–P4 contract. Inconclusive is publishable. | Distilled §2.1 |
| R4B-6 | Effort table is unmeasured guesses; calendar does not close | **Carried.** Option-F lesson kept: the **promised** set is H / H₂ / H₂O, not C₃₈₄H₄₈. Stop if the first H₂ Maxwell window misses 168 h. | Mapping §6; Distilled §3.3 |

## Plan 02 approval conditions (not extra source issues)

| Condition | In 03 |
|---|---|
| Execute a cost pilot under production settings | **Open.** `teacher_cost.py` + first Octopus window. |
| Dated resonance-criterion amendment | **Superseded** (no GVPT2). Analogous: dated Distilled §4 notes only. |
| Front-loaded hypothesis pilot | **Re-scoped** to P0 on the linear stencil **before** training (Distilled §7.3). |
| Pass A status statements | **This draft** must keep saying draft. |
| Small-molecule excellence as primary | **Adopted in 03 from the start:** H₂ promised, H₂O transfer, horizon for the rest. |

---

## Class table (orientation only)

The class table is **not** a substitute for the named rows.

| Class of finding | Where it lives in 03 |
|---|---|
| Discretisation can eat the budget | Frozen grid; 80 h cap; Q0 hash |
| Deliverable overtaken by PAH ML-IR | IR is not a 03 product |
| Label factory blocked (CC memory, locality) | Teacher is Octopus RT-TDDFT; CC is not on the ladder |
| “Not synthetic” rubric clause | M02–M04 tables; cubes delayed to M05 with Task A fallback; **DOI still unpinned** |
| Forbidden precision language | Overarching Goal |
| Inconclusive must be publishable | P3/P4 |
| Dipole identity | Q2, diagnostic only |
| Governance worth more than the model | M07 agent |
| Scope creep via Horizon | Horizon 10–12 excluded from M08 |
| Status / tally drift | This file; README draft banner |
| Unmeasured cost | Caps + `teacher_cost.py` NOT_RUN |

---

## What a new review is for

Plan 03's review record is **one pass deep**. The briefs ask for a **new** Round 5 (Pass A cold, Pass B adversarial TDDFT / ML-propagator), not a copy of 01 or 02.

- [Professor_Review_2026-09-01_Round5_PassA.md](Professor_Review_2026-09-01_Round5_PassA.md) — **done** 2026-09-01; 9 blocking, 6 non-blocking, 8 loopholes; addressed in spec the same day
- [Review_Brief_2026-09-01_Round5_PassA.md](Review_Brief_2026-09-01_Round5_PassA.md) — the brief that produced it
- [Review_Brief_2026-09-01_Round5_PassB.md](Review_Brief_2026-09-01_Round5_PassB.md) — **not yet run.** Hand it Pass A's findings 2–4 with the brief.

**Status.** Draft map. Not complete as a plan.
