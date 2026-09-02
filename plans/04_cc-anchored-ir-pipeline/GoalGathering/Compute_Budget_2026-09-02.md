# Compute budget — Plan 04 (2026-09-02)

**Status.** Caps and protocol frozen 2026-09-02. Caps are **not estimates**: nothing below is a
predicted runtime, and no cap may be read as "this is how long it takes". Measured slots are
filled only by timed probes; until then they read NOT_RUN. Agrees with
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md); the ladder's stop
conditions bind.

---

## 1. Three budgets, not one

Plans 01–03 learned this twice (a human budget once bounded a machine cost; a wall-clock cap
once hid a 21× resource). Plan 04 has **three** currencies and never mixes them:

| Budget | Currency | Cap | Governs |
|---|---|---|---|
| B1 human | attention hours | **840 h** total, Modules 02–09 (accounting baseline carried from plans 01–03) | everything a person does |
| B2 laptop | wall-clock hours | **168 h per rung pilot** (one unattended calendar week), R0–R3 | electronic structure + training runs on own hardware |
| B3 cluster | node-hours | **no number exists yet** — see §3; a rung-specific cap is frozen per rung, before that rung starts | DLPNO point factories and reach rungs |

The laptop is being replaced (decided 2026-09-02). Every plan-02 timing below is from the old
machine and is **provenance, not budget**; the new machine is re-timed by the R0 pilot before
any B2-governed decision cites a number.

## 2. B1 — human hours (840 h baseline)

| Bucket | Cap | Modules |
|---|---|---|
| Public-rubric datasets | 160 h | 02, 03, 04 |
| Pipeline infrastructure (codes, geometries, Hessians, DLPNO point factories, lab-scoreboard probes) | 200 h | 05 groundwork, probes |
| Anharmonic ML correction + scoring vs frozen lines (the thesis) | 240 h | 05, 08 core |
| Generative + agentic + synthesis | 160 h | 06, 07, 08 |
| Contingency / reviews / defense | 80 h | 09 + drift |

If pipeline infrastructure exceeds 200 h, the plan is drifting toward plan 01's failure mode
(two-thirds of the budget on plumbing). Stop and write the deviation.

**Booking rule.** Each logged hour is booked to exactly one bucket. The module names in the
table are examples of where a bucket is typically spent, not exclusive owners — a module may
draw from more than one bucket, but an hour can never be counted twice, and the bucket, not
the module, is the cap.

## 3. B3 — cluster node-hours (the new budget)

Nothing is measured. What exists is one **assertion** from the source conversation
(grok_chat_4): one DLPNO-CCSD(T)/TZ point of coronene ≈ tens of minutes to hours on a cluster
node; 10⁴ points ≈ thousands of node-hours. An assertion is not a budget. Therefore:

1. **No cluster rung starts** before all three exist, in writing, dated:
   (a) formalized access (account + allocation at UvA — the collaboration is decided, the
   allocation is not yet a fact); (b) a **timed single-point probe** at that rung's size and
   settings, run and printed by a script in `probes/`; (c) a node-hour cap for the rung,
   frozen in a dated note derived from that probe.
2. The first timed DLPNO probe (any size) also runs **on the laptop** if ORCA installs there —
   the R1 DLPNO-vs-canonical check is a laptop job by intent, and its timing decides whether
   R2/R3 point factories are B2 or B3 work. **The kill rule is arithmetic:** with N_min for
   the rung frozen in the pilot note (Ladder §4.8), if `wall_clock_per_point × N_min > 168 h`
   the factory is a B3 object; if B3's preconditions (§3.1) are then not met, the rung does
   not run and is reported fail-closed. No judgement call sits between the probe and the stop.
3. Reach rungs (R4–R6) are B3-only by assumption and therefore blocked on §3.1 in full.

## 4. Measured facts on file (old laptop, plan-02 probes, git history)

Provenance for expectations only; every number is re-measured on the new machine before use:

- CCSD(T)/6-31G* benzene (102 bf) single point: **19.6 s**. CCSD/cc-pVDZ (114 bf): 14.6 s.
- Canonical (T) in-core wall: **fails at ~114 bf with 28 GB** — the R0/R1 boundary is a
  measured fact, not a literature claim.
- B3LYP/6-31G* Hessians: benzene 3.3 min, naphthalene 12.7 min; `frequency(return_wfn=True)`
  (intensities) ≈ 3× a bare Hessian; coronene frequency job 176 min.
- Full plan-02 batch machinery (queue runner, detached execution, STATUS files) exists in git
  history and is the starting point for the pipeline's job control.

Provenance pointers: raw plan-02 `.npz` arrays are preserved in commit `800f3aa`; the timing
and band-read scripts are plan-02 `probes/` files in git history (e.g.
`pahdb_experimental_2026-08-28.py`, `verify_oop_bands_2026-08-27.py`).

## 5. Protocol

- Timed slots are filled by `probes/` scripts that print machine, date, settings, and
  wall-clock; a timing quoted anywhere else is invalid.
- Time jobs on a quiet machine or time them twice (plan-02 lesson: machine load produced a
  spurious 2× "shape effect").
- Queue generously, order jobs by what they *decide*, spend human hours on judgement
  (plan-02 lesson, carried).
- Supersede this file only with a new dated compute-budget doc; do not edit caps in place.
