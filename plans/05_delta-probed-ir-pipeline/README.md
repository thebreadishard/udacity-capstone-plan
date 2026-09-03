# Plan 05 — Δ-Probed IR Pipeline

**Status: draft, folder created 2026-09-03. Not complete as a plan. Nothing here is a result.**
Supersedes plan 04 (CC-Anchored IR Pipeline), whose folder **stays in the tree** until the
user decides to remove it (see [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md)).
Plans 01–03 are git history only.

**Promised deliverable (Module 08).** A pipeline: **any individual aromatic molecule in, an
infrared spectrum out** — the same criterion, ladder, opponents, scoreboards and gates as plan
04 — with one change of method: the coupled-cluster anchor is no longer a learned per-molecule
surface but a **probed correction Δ to the force constants**, recovered from a number of
local-CC evaluations K that the plan measures rung by rung and expects to stop growing with
molecule size. K is reported next to every spectrum; if it does not saturate, the size claim
is withdrawn, not softened.

The sequence **ends at Module 09**. There is no `Horizon/` and there are no Projects 10–12.

## Reading order

1. This file — orientation. **Draft, not complete.**
2. [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md) — what
   changed and what did not, in one table
3. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — prime directive
4. [GoalGathering/Research_Note_2026-09-03_Delta_Probing.md](GoalGathering/Research_Note_2026-09-03_Delta_Probing.md)
   — the source document: what was found on 2026-09-03, with verify statuses
5. [GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md) — opponents
   and scoreboards (carried from plan 04)
6. [GoalGathering/Frozen_Ladder_and_Tolerances.md](GoalGathering/Frozen_Ladder_and_Tolerances.md)
   — rungs, claim types, the new pilot-note numbers (K, r_c), stop conditions
7. [GoalGathering/Compute_Budget_2026-09-03.md](GoalGathering/Compute_Budget_2026-09-03.md)
   — three budgets; the classification rule `wall_clock_per_probe × K`
8. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
   — levels, the Δ-probing object, gates Q0–Q8 / P0–P5, fail-closed sentences
9. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md)
   — bibliography with per-item verify status (items 23–41 new)
10. [probes/README.md](probes/README.md) — conventions and the probes owed
11. `GoalGathering/Capstone_Mapping.md` — **not yet written**; owed after the Round-7 reviews
12. `GoalGathering/Project_Proposal_<date>.md` — **not yet written**; owed after the mapping

## Review record

- **Round 7, Pass A** (cold read): not yet run. Brief:
  `GoalGathering/Review_Brief_<date>_Round7_PassA.md` (to be written before the review).
- **Round 7, Pass B** (adversarial domain): not yet run.

Plan 04's Round-6 Pass A and Pass B findings and their closures bind plan 05 and are not
re-litigated; the plan-05 documents carry those closures in their text.

## Open decisions for the user

1. **Fragment probing** at R4–R6 (Goal, "Open decisions"): in or out of the promised set.
2. **Removal of the plan-04 folder** from the tree.
3. **Machine**: whether the replacement laptop carries a GPU (decides whether GPU DFT Hessians
   are B2 or B3 work).

## Not yet done (owed, in order)

- Round-7 Pass A brief and review; patches.
- Round-7 Pass B brief and review; patches; green-light decision.
- Capstone mapping (modules 02–09 against Rubrics v1.5.1).
- Project proposal for the supervisor.
- **The pilot note** (after the R0 pilot, the zero-CC dry run, the Q7 reference and the
  scoreboard re-read: band lists, margins, P-gate numbers, matrix tolerance, P3 effect size,
  M04 recipe, resonance route, K and r_c per rung, Q7 tolerance, f_h).

## Provenance

Plan 05 is based on the research note of 2026-09-03 (item 4 above), which answered the user's
question *what single idea would make the plan-04 pipeline fast enough for super-large PAHs
without losing accuracy*. The answer — probe the local CC−DFT correction with a
size-independent pattern set instead of learning a surface — rests on published O(1)-gradient
and compressed-sensing Hessian recovery (bibliography items 23–24) that no one had applied to a
CC−DFT difference or to anharmonic constants as of that search. The plan-04 source conversation
(`AI_Chats/grok_chat_4.md`) remains the provenance for the CC-anchor idea itself.

## What survives from plans 01–04

Method-agnostic governance, carried verbatim: measured-not-asserted arithmetic in `probes/`;
never cite from recall; pre-registration, frozen splits with hashes, ≥3 seeds, tuning parity;
declared effect size, **inconclusive is publishable**; escalation ladders declared in advance,
stopping is a result; fail-closed reporting; deviations only as dated notes committed before
the number is known. From plan 04 specifically: everything except the learned surface.
