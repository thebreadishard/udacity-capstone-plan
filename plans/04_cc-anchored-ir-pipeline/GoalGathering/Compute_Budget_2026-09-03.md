# Compute budget — Plan 04 (2026-09-03)

**Supersedes [Compute_Budget_2026-09-02.md](Compute_Budget_2026-09-02.md)** under that file's
own supersede-only rule, after the user directive of 2026-09-03: **no cap on human hours.**
The project spends the hours it needs, even if that is a few years. Everything else the old
file froze is carried unchanged unless restated here.

---

## 1. What changed and what did not

| Budget | Old | Now |
|---|---|---|
| B1 human | 840 h cap + bucket caps | **uncapped.** Hours are *logged*, never limited. Time pressure is not a stop condition anywhere in this plan |
| B2 laptop | 168 h cap per rung pilot | **checkpoint, not a kill.** Crossing it forces a dated decision note (continue knowingly / reroute to B3 / stop) — never a silent overrun and never an automatic abandonment |
| B3 cluster | no number until access + timed probe + dated cap | **unchanged** — these are honesty preconditions, not time pressure |

## 2. B1 — human hours, uncapped

- The user directive (2026-09-03) is explicit: the hours that are needed will be spent, even
  if the project takes years. No document may reintroduce an hour cap, a weekly quota, or a
  deadline as a gate.
- **Logging stays.** Hours are booked to one bucket per entry (the 2026-09-02 booking rule),
  so where the time goes remains visible.
- **The plan-01 alarm survives as a signal, not a stop:** if plumbing/infrastructure hours
  dominate the log for a sustained period, that triggers a written review of *what* the time
  is buying — plan 01 died of two-thirds-on-the-grid, and the lesson is watchfulness, not a
  ceiling.

## 3. B2 and B3 — machine discipline, unchanged in spirit

- **B2 (laptop wall-clock):** the 168 h/rung-pilot figure is now a *checkpoint*. Its purpose
  was never speed — it was to prevent silent, unexamined spending. Crossing it requires a
  dated note choosing: continue on the laptop with eyes open, reroute the work to B3, or stop
  the rung. Coarsening the basis, loosening DLPNO thresholds, or shrinking sampling to duck
  under a checkpoint remains forbidden (that is a science decision, §4 of the distilled plan).
- **B3 (cluster node-hours):** unchanged. No cluster rung starts before (a) written access,
  (b) a timed probe printed by a script, (c) a dated per-rung cap note. The
  `wall_clock × N_min` rule is now a **classification** (is this factory B2 or B3 work?) and a
  decision point, not an automatic rung-kill: if it classifies as B3 and B3's preconditions
  are unmet, the rung waits or stops *by dated note*, and the wait is reported honestly.

## 4. Measured facts and protocol

Carried verbatim from the 2026-09-02 file: the old-laptop plan-02 timings (provenance only;
re-measure on the new machine), the timed-probe protocol (machine, date, settings, wall-clock
printed by a script or the timing is invalid), quiet-machine timing, and the
supersede-only-with-a-new-dated-doc rule, which this file itself obeys.
