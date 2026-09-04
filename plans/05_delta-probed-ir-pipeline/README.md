# Plan 05 — Δ-Probed IR Pipeline

**Status: draft, folder created 2026-09-03. Not complete as a plan. Nothing here is a result.**
Supersedes plan 04 (CC-Anchored IR Pipeline). All five plan folders are in the tree
(decision 2, 2026-09-04): 01–04 are superseded, read-only records; 05 is current.

**Promised deliverable (Module 08).** A pipeline: **any individual aromatic molecule in, an
infrared spectrum out** — plan 04's criterion, ladder, opponents, scoreboards and gates — with
the coupled-cluster anchor obtained as a **probed correction Δ₂ to the harmonic force
constants** rather than a learned per-molecule surface, from local-CC responses with frozen
spaces, and with the number of responses that correction needed measured per rung and printed
as a cost record beside every spectrum. Mode E (energies) is the guaranteed route; mode G
(gradients) is built in a pre-registered side project. Whether the probe count stops growing
with molecule size is a measured question (Q8) with a pre-registered losing condition, not a
promise. No coupled-cluster correction to anharmonic constants is promised. The largest
species is reached by fragment probing under a measured licence.

The sequence **ends at Module 09**. There is no `Horizon/` and there are no Projects 10–12.

## Glossary

Every symbol and term is defined once in the **Goal file's glossary** (reading-order item 3):
Δ₂; local CC and frozen spaces; mode E / mode G; pattern, q_s, response; ρ, ρ\*, f_h, K, K_off,
K_cap; structural prior, learned prior, the licence; τ, τ₇, d₇, r_c, r_max, ε₈, η₈, γ, σ_E, σ_g;
gates Q0–Q8 and P0–P5; rungs and claim types; budgets B1–B3; milestones M1–M5; reading 1 / 2;
the pilot note and the dated notes; CMA, CMA-0, CMA-2; GVPT2, MD-ACF, QFF, CPS, PNO/LNO. Read it
before anything else.

## Reading order

1. This file — orientation. **Draft, not complete.**
2. [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md) — every
   change relative to plan 04, in one table (27 rows)
3. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — glossary, prime
   directive, the two 2026-09-04 directives, the decision record
4. [GoalGathering/Research_Note_2026-09-03_Delta_Probing.md](GoalGathering/Research_Note_2026-09-03_Delta_Probing.md)
   — the source document as written that morning; §8 records what the Round-7 reviews
   corrected and §9 what the 2026-09-04 decisions changed; §§8–9 win over §§1–7
5. [GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md) — opponents
   and scoreboards (carried from plan 04)
6. [GoalGathering/Frozen_Ladder_and_Tolerances.md](GoalGathering/Frozen_Ladder_and_Tolerances.md)
   — sentence types, rungs, the two licences, what is frozen now vs at the pilot note, stops
7. [GoalGathering/Compute_Budget_2026-09-03.md](GoalGathering/Compute_Budget_2026-09-03.md)
   — three budgets; the classification rule; the order of timed probes
8. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
   — the Δ-probing object, gates Q0–Q8 / P0–P5, fail-closed sentences
9. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md)
   — bibliography with per-item verify status (items 23–49 new)
10. [probes/README.md](probes/README.md) — conventions and the probes owed
11. [GoalGathering/Capstone_Mapping.md](GoalGathering/Capstone_Mapping.md) — modules 02–09
    against Rubrics v1.5.1; Pass 6 (sign-off) not done
12. [GoalGathering/Project_Proposal_2026-09-03.md](GoalGathering/Project_Proposal_2026-09-03.md)
    — the supervisor proposal: the *why* of the major decisions, the review status, and what
    was decided by whom
13. [GoalGathering/Side_Project_2026-09-04_ModeG_Gradients.md](GoalGathering/Side_Project_2026-09-04_ModeG_Gradients.md)
    — the pre-registered side project that builds frozen-space local-CC gradients (mode G):
    milestones M2–M5, kill criterion, budget bucket, what changes on success or failure

## Review record

- **Round 7, Pass A** (cold read, 2026-09-03, fresh context):
  [Professor_Review_2026-09-03_Round7_PassA.md](GoalGathering/Professor_Review_2026-09-03_Round7_PassA.md)
  — not sound enough for Pass B until patched; 10 blocking + 11 non-blocking; **all 21
  addressed in spec the same day**. Brief: [Review_Brief_2026-09-03_Round7_PassA.md](GoalGathering/Review_Brief_2026-09-03_Round7_PassA.md).
- **Round 7, Pass B** (adversarial domain, 2026-09-03, fresh context, literature verified):
  [Professor_Review_2026-09-03_Round7_PassB.md](GoalGathering/Professor_Review_2026-09-03_Round7_PassB.md)
  — **conditional**: green light for the R0–R1 measurement programme once six blocking items
  were written in; no green light for the promised set *as then worded*. **All six written in
  the same day** (Q6 thresholds; banded prior; Δ₃/Δ₄ out; CMA cited; cost question re-anchored;
  Q8 on direct blocks) and non-blocking 7–13. Brief: [Review_Brief_2026-09-03_Round7_PassB.md](GoalGathering/Review_Brief_2026-09-03_Round7_PassB.md).
- **2026-09-04, user decisions 1–6 and two directives** (Goal, "Decisions of 2026-09-04";
  "The goal binds"; "Inheritance is not authority"); the side project opened.
- **Round 8, Pass A** (cold read of the patched set, 2026-09-04, fresh context):
  [Professor_Review_2026-09-04_Round8_PassA.md](GoalGathering/Professor_Review_2026-09-04_Round8_PassA.md)
  — "not yet": 11 blocking + 9 non-blocking, almost all seams left by the 2026-09-04
  find-and-replace edits plus three design holes. **All 20 addressed in spec the same day:**
  (1) the learned prior's rule made one rule everywhere — *earned on R2–R3 (both recoveries on
  the same responses, agreement within τ₇), spent on R4–R6*, R0–R3 scored spectra always
  structural, officer rule / claim ladder / M08 labels / glossaries aligned; (2) the licence's
  reference check made a full structural-vs-prior comparison per family, with η₈ as the block
  tolerance; (3) frozen-space code made main-project probe M1 under stop 1, so mode E is
  guaranteed *given M1* and the side project's failure (M2–M5) costs nothing; (4) the side
  project's engine hedged everywhere it is named ((T) snippet-grade; gradient code unlocated;
  §1.2 labelled reasoning); (5) K_cap(G) frozen from a gradient-mode DFT dry run for every
  rung, so licensing mode G never touches the pilot note; M5 added so a "run" exists at R3;
  (6) the pilot-note leak closed — smoothness scatter printed, means sealed; gradient probe
  run/no-run at equilibrium before the note; M2–M5 after it; M1 prints scatter without a
  verdict; (7) a mode-G noise line (σ_g ≤ 2.8·τ·q_s) and a "beat and noise" rule per mode;
  (8) the fragment licence given three parts — Q8 at R2–R3, the fragment-vs-whole comparison at
  R3 (and R4 where affordable), a direct-block probe on the R6 fragments — and the R6 sentences
  split into per-family withdrawal and all-families refusal; (9) "O(1)-class" removed and
  "-class" added to the forbidden list; (10) the M05 corpus size removed from frozen text
  (dated note after the B2 timing); (11) every decided-vs-open survivor swept, decisions 5–6
  added to the Goal's record, research note §9 appended; non-blocking 12–19 swept (stale
  banners; change table rows 9/10/16/17/18 rewritten and rows 25–27 added; debt lists; snippet
  labels; kill clock made calendar time with M1 booked to infrastructure; Q8-at-R0 as a Q7
  sub-item; Distilled §1/§2 for both modes; glossary moved into the Goal); (20) the QM9 /
  Foundations-module question raised as **open decision 7**. Brief:
  [Review_Brief_2026-09-04_Round8_PassA.md](GoalGathering/Review_Brief_2026-09-04_Round8_PassA.md).
- **Round 8, Pass B** (re-assessment): not yet run. Brief:
  [Review_Brief_2026-09-04_Round8_PassB.md](GoalGathering/Review_Brief_2026-09-04_Round8_PassB.md).

Plan 04's Round-6 findings and their closures bind plan 05 and are not re-litigated.

## Decisions

All six decisions of 2026-09-04 are closed and recorded in the Goal ("Decisions of
2026-09-04"): 1 fragment probing as a method under the fragment licence; 2 all plan folders
stay; 3 the R2 re-read stands; 4 Module 05 adopted; 5 the promised set — Δ₂ only, mode E
guaranteed, mode G built in the side project; 6 the B2 laptop named.

**Open:** 7. Has the Foundations module (02) already been submitted, and on which dataset?
(Round-8 Pass A issue 20: the scraped rubric page contains the student's words naming QM9 for
that project.) The mapping's M02 and M05 rows depend on the answer.

## Not yet done (owed, in order)

- **Round 8, Pass B** — the re-assessment that turns Round 7's "conditional" into a verdict on
  the set as it now stands.
- The user's answer to open decision 7.
- Capstone mapping Pass 6 (module-by-module sign-off).
- **Probe M1** (frozen LNO spaces reproduce the reference energy) — the first code of the
  project, main-project work.
- **The pilot note** (after the R0 pilot, the two-mode zero-CC dry run, the gradient
  run/no-run at equilibrium, probe M1 and the R1 smoothness probe's scatter; before any
  local-CC Δ₂ number is readable): band lists, margins and the expected-effect line, P-gate
  numbers, matrix tolerance, P3 effect size, M04 recipe, resonance route and resonance-closed
  family set, ρ\* and K_cap per mode, f_h and seed, τ₇ and d₇, Q8 numbers and direct-block
  pairs, Q6 numbers and the pattern amplitude.

## Provenance

Plan 05 is based on the research note of 2026-09-03 (item 4 above), which answered the user's
question *what single idea would make the plan-04 pipeline fast enough for super-large PAHs
without losing accuracy*. The answer — probe the local CC−DFT correction to the force constants
with a hashed pattern set instead of learning a surface — rests on published O(1)-gradient and
compressed-sensing Hessian recovery (bibliography items 23–24) and, as Round-7 Pass B
established, on the Concordant Mode Approach (items 42–43) for its diagonal part. What remains
proposed is stated in the research note's §8. The plan-04 source conversation
(`AI_Chats/grok_chat_4.md`) remains the provenance for the CC-anchor idea itself.

## What survives from plans 01–04

Method-agnostic governance, carried because each rule serves the goal: measured-not-asserted
arithmetic in `probes/`; never cite from recall; pre-registration, frozen splits with hashes,
≥3 seeds, tuning parity; declared effect size, **inconclusive is publishable**; escalation
ladders declared in advance, stopping is a result; fail-closed reporting; deviations only as
dated notes committed before the number is known. From plan 04 specifically: everything except
the learned surface.
