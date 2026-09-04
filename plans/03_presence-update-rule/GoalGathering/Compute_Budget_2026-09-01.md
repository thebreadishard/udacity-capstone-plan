# Compute budget — Plan 03

**Date:** 2026-09-01 · **Status:** freeze lock, **not measured** · **Supersedes** the asserted “hours-to-days” sentence in `Why_03_Supersedes_02.md`

No wall-clock in this file is a result. A probe must print it. Until `probes/teacher_cost.py` exists and has been run, every time below is a **cap or a stop rule**, not an estimate dressed as a measurement.

This lock sits on the 2026-09-01 contradiction pass in
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md):
Octopus RT-TDDFT (ALDA), Maxwell–TDDFT \(\mathbf{E},\mathbf{B}\), frozen point nuclei, outer spacing \(0.20\,a_0\).

---

## 1. Two budgets, not one

Plan 02 mixed a human week with a machine week. Plan 03 does not.

| Resource | Amount | What it limits |
|---|---:|---|
| **Human attention** | 840 h across Modules 02–09 | decks, hashes, training choices, writing, gates |
| **Wall-clock compute** | 168 h total for the promised teacher set | how long Octopus and one conv-stencil may run unattended |

168 h is **one calendar week** (\(7\times24\)) of an unattended laptop. It is a **total budget for the promised set, not a weekly allowance**, and it is not a claim that the machine is idle 100 % of the time — the same laptop carries the 840 h of human work. If the set needs a second unattended week, that is a §4 note, not a second helping of the same cap.

The 80 h **grid + teacher I/O** cap in `Overarching_Goal.md` is **human**. It is the time spent writing hashed decks, converting cubes, and refusing to redesign the grid. It is not Octopus’s wall-clock.

If human I/O on grid + teacher exceeds 80 h, **stop**. Write a Distilled §4 note. Do not silently become plan 01.

---

## 2. Wall-clock cap for the promised teacher set

Promised teacher set = H-atom diagnostic + H₂ (train and held-out windows) + H₂O (transfer windows only). Same grid family. Maxwell–TDDFT on.

| Cap | Rule |
|---|---|
| **168 h wall-clock** | One unattended week for the whole promised set. |
| First H₂ Maxwell window | If it cannot be produced inside this cap, **stop**. Do not coarsen the grid, drop Maxwell, or switch codes to keep the brand. |
| Bonus hydrides / 1 fs extra window | Only after the promised set has printed inside the cap. |

A later probe may replace 168 h with a measured number. It may not raise the cap without a §4 note.

---

## 3. What is frozen (no remaining OR)

| Item | Freeze |
|---|---|
| Teacher code | **Octopus**. Input decks hashed. NWChem is not the teacher. |
| Functional | **ALDA** |
| H₂ / H₂O physics | Real-time TDDFT + **Maxwell–TDDFT** fields |
| Exact 2-e H₂ | Horizon 10 only |
| Nuclei | Frozen **point charges** on the scored window |
| Outer spacing | \(0.20\,a_0\) |
| Nuclear refinement | \(h(r)\sim 0.20\,a_0/Z\) near nuclei, capped at the outer spacing. *Corrected 2026-09-01: the old \(a_0/Z\) gave \(1.0\,a_0\) at hydrogen, coarser than the outer grid on every promised rung.* |
| Teacher \(\Delta t\) | \(0.05\) au |
| Learner \(k\) | **1** (one learner step = one teacher step) |
| State channels | **11**: \(\rho_+,\rho_-,j_{x,y,z},E_{x,y,z},B_{x,y,z}\) — the count is `len(grid_spec.CHANNEL_ORDER)`. \(\rho_+\) is bookkeeping (zeros / diagnostic); nuclei are not a second dynamical fluid. |
| Boundaries | Finite box, **non-periodic**. Learner padding and the P4 baseline must match the teacher rim. |
| Baseline integrator | Leapfrog Maxwell, CFL sub-cycled (119 sub-steps at the frozen \(h,\Delta t\)); see Distilled §5.3 |
| Drop \(\mathbf{B}\) | Forbidden until a probe prints that \(\mathbf{B}\) is numerically zero on the ladder |
| Kernel | Default **3×3×3**. **5×5×5** is the single Module 05 comparison axis. |
| Conservation penalty | **Off** by default. Turning it on is a dated note **before** training, with the weight frozen then. |
| Grid hash (Q0) | Module 05 scientific corpus, not Module 02 |
| Install | Octopus+Maxwell on this Windows laptop is **unmeasured**. If it cannot be installed and run inside the human 80 h + wall-clock 168 h caps, **stop**. Switching to Poisson or to another code is a §4 deviation, not a silent fallback. |

---

## 4. Tests: what Module 08 may quote before any pilot

The 8 h P1 pilot is **human**. It runs on the H₂ train/validation slice only (Distilled §6.2). It may only **tighten** a number. It may not loosen one, and after it has printed, no P0–P4 number moves in either direction without a §4 note committed *before* the affected quantity is measured.

| Test | Frozen quantity | Gate Module 08 may quote now |
|---|---|---|
| P0 | \(T_0 = 200\) teacher steps, field-free | \(\lvert N(t)-N(0)\rvert / N(0) < 10^{-3}\) on H₂; on H₂O \(< 5\times10^{-3}\) **report only, not a gate** |
| P1 | one-step relative \(L^2\) on \(\rho_-\) | \(< 5\times 10^{-3}\) on held-out H₂; \(\ge 3\) seeds |
| P2 | same, after \(T = 200\) teacher steps (\(k=1\)) | \(< 5\times 10^{-2}\) or fail-closed |
| P3 | P1-style on H₂O, zero-shot | no absolute number; beat linear stencil or **inconclusive** |
| P4 | learned vs frozen linear Maxwell+continuity stencil | declared \(\Delta\) in relative \(L^2\), 3 seeds |

\(T = 200\) steps at \(\Delta t = 0.05\) au is \(10\) au \(\approx 0.24\) fs. A **1 fs** window is a bonus report if it fits the teacher cap. It is not a second P2 gate.

Energy drift is reported. It is not a hidden extra gate. If P0 fails, P2 is not interpreted.

P4 effect size (small / medium) is pre-registered after the 8 h pilot, not after the test.

---

## 5. Human 840 h (unchanged buckets)

At the ~10 h/week this project actually has, 840 h is ~84 weeks. That is the number the calendar has to close against, and it cannot be checked until T0 is a date (Mapping §6, plan-01 issue 15 / R3-6, still open).

| Bucket | Cap | Why |
|---|---|---|
| Frozen grid + teacher I/O | 80 h | Plan 01 **budgeted** ~560 h here. Forbidden. |
| Public-rubric datasets (M02–M04) | 160 h | Rubrics 02–04 demand third-party tables. |
| Learned stencil + tests P0–P4 | 320 h | The thesis. Includes the 8 h P1 pilot. |
| Generative + agentic + synthesis | 200 h | Rubrics 06–08. |
| Contingency / reviews | 80 h | |

---

## 6. Probe that must exist before anyone believes a cost

`probes/teacher_cost.py` must print, from a real run or an honest “not run” exit:

- wall-clock of one H-atom diagnostic window (this rung is analytic / grid-TDSE, so its line is a diagnostic cost, not an Octopus cost)
- wall-clock of one H₂ Maxwell window of 200 steps
- wall-clock of one H₂O Maxwell window of 200 steps
- whether the sum sits under 168 h

Do not type those numbers into this file by hand.

---

## 7. Escalation (declared in advance)

1. Octopus+Maxwell cannot be installed inside the caps → **stop**. Name the missing binary. Do not Poisson.
2. First H₂ window exceeds 168 h wall-clock → **stop**. Do not coarsen \(0.20\,a_0\).
3. Human grid+teacher I/O exceeds 80 h → **stop**. Do not redesign the grid.
4. P0 fails on the linear stencil already → the teacher or grid is wrong; do not train. Repairing the grid after Q0 still needs a dated §4 note (rungs 2 and 3 are not suspended by this rung).
5. P0 fails only on the learned rule → fail-closed; P2 is not interpreted.
6. P3 does not beat the linear stencil → report **inconclusive**. That is a result.
