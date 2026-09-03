# Plan 05 — Δ-Probed IR Pipeline

**Status: draft, folder created 2026-09-03. Not complete as a plan. Nothing here is a result.**
Supersedes plan 04 (CC-Anchored IR Pipeline), whose folder **stays in the tree** until the
user decides to remove it (see [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md)).
Plans 01–03 are git history only.

**Promised deliverable (Module 08).** A pipeline: **any individual aromatic molecule in, an
infrared spectrum out** — plan 04's criterion, ladder, opponents, scoreboards and gates — with
the coupled-cluster anchor obtained as a **probed correction Δ to the force constants** rather
than a learned per-molecule surface, and with the number of coupled-cluster evaluations that
correction needed, **K**, measured per rung and printed as a cost record beside every spectrum.
Whether K stops growing with molecule size is a measured question (Q8) with a pre-registered
losing condition, not a promise.

The sequence **ends at Module 09**. There is no `Horizon/` and there are no Projects 10–12.

## Glossary (one line each; the Goal file defines them fully)

- **Δ** = local coupled cluster minus DFT, as force constants: **Δ₂** Hessian correction,
  **Δ₃** cubic, **Δ₄** semi-diagonal quartic.
- **Local CC** = DLPNO-CCSD(T) (domain-based local pair natural orbital) or LNO-CCSD(T) (local
  natural orbital): controlled locality truncations of CCSD(T).
- **Mode E / mode G** = Δ recovered from energies only / from analytic gradients.
- **Pattern** = one simultaneous multi-atom displacement geometry; **K** = the measured number
  of patterns a rung needed to reach the residual target **ρ\***; **K_cap** = the pilot-note cap.
- **Structural prior** = the fixed, parameter-free regulariser of the promised recovery;
  **learned prior** = the Module-05 Transformer, a bonus arm only.
- **GVPT2** = resonance-explicit second-order vibrational perturbation theory; **MD-ACF** =
  spectrum from the dipole autocorrelation of molecular dynamics; **QFF** = quartic force
  field; **PNO** = pair natural orbital; **TightPNO/NormalPNO** = DLPNO threshold presets.

## Reading order

1. This file — orientation. **Draft, not complete.**
2. [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md) — every
   change relative to plan 04, in one table
3. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — prime directive
4. [GoalGathering/Research_Note_2026-09-03_Delta_Probing.md](GoalGathering/Research_Note_2026-09-03_Delta_Probing.md)
   — the source document: what was found on 2026-09-03, with verify statuses and errata
5. [GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md) — opponents
   and scoreboards (carried from plan 04)
6. [GoalGathering/Frozen_Ladder_and_Tolerances.md](GoalGathering/Frozen_Ladder_and_Tolerances.md)
   — sentence types, rungs, what is frozen now vs at the pilot note, stop conditions
7. [GoalGathering/Compute_Budget_2026-09-03.md](GoalGathering/Compute_Budget_2026-09-03.md)
   — three budgets; the classification rule; the order of timed probes
8. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
   — the Δ-probing object, gates Q0–Q8 / P0–P5, fail-closed sentences
9. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md)
   — bibliography with per-item verify status (items 23–41 new)
10. [probes/README.md](probes/README.md) — conventions and the probes owed
11. `GoalGathering/Capstone_Mapping.md` — **not yet written**; owed after the Round-7 reviews
12. `GoalGathering/Project_Proposal_<date>.md` — **not yet written**; owed after the mapping

## Review record

- **Round 7, Pass A** (cold read, 2026-09-03, fresh context):
  [GoalGathering/Professor_Review_2026-09-03_Round7_PassA.md](GoalGathering/Professor_Review_2026-09-03_Round7_PassA.md)
  — verdict: not sound enough for Pass B until patched; 10 blocking + 11 non-blocking
  findings. Brief: [GoalGathering/Review_Brief_2026-09-03_Round7_PassA.md](GoalGathering/Review_Brief_2026-09-03_Round7_PassA.md).
  **All 21 addressed in spec the same day:** complete change table in Why_05 (1); K made a
  measurement with a frozen residual target ρ\* and a separate cap K_cap, pilot inputs
  restricted to lab/opponent side + DFT-only dry run + timings, Q7 references and the R0 batch
  moved after the note (2, 21); Q8 given a fixed three-part form with its numbers as
  pilot-note item 12 (3, 20); the prime directive's cost sentence made conditional on mode G
  and the cost record separated from the size claim (4, 10); the learned prior barred from
  every promised rung including R6 (5); Δ₃/Δ₄ probed from R0 and licensed by Q7 (6); R2 row
  re-read against the coverage probe, with a per-family decidability rule (7); snippet-grade
  items upgraded by Crossref/arXiv or explicitly not relied on, locality written as the bet
  (8); P4 consequence sentences rewritten for the right arm and added for (b)/(c), with a
  discriminability clause in Q7 (9); MD-ACF's potential defined (11); hold-out seeded and
  residual defined (12); Q7's freezing limitation stated and Q6 given a bias column (13);
  debt lists made identical with a separate method-debt list (14); unmeasured "cannot afford"
  sentences removed (15); glossary and notation on first use (16); stale text swept (17); M05
  corpus widened to the dry-run tensors with distinctness deferred to the mapping (18);
  atom/mode counts, arXiv/JPCA dates and the Sanders sentence corrected in a research-note
  erratum (19).
- **Round 7, Pass B** (adversarial domain): not yet run. Brief:
  [GoalGathering/Review_Brief_2026-09-03_Round7_PassB.md](GoalGathering/Review_Brief_2026-09-03_Round7_PassB.md).

Plan 04's Round-6 Pass A and Pass B findings and their closures bind plan 05 and are not
re-litigated; the plan-05 documents carry those closures in their text.

## Open decisions for the user

1. **Fragment probing** at R4–R6 (Goal, "Open decisions"): in or out of the promised set.
2. **Removal of the plan-04 folder** from the tree.
3. **The R2 A-scored set** as re-read against the coverage probe (triphenylene in on gas
   families; tetracene fully gated) — veto by dated note restores plan 04's set.
4. **Machine**: whether the replacement laptop carries a GPU (a B2 fact either way).

## Not yet done (owed, in order)

- Round-7 Pass B review; patches; green-light decision.
- Capstone mapping (modules 02–09 against Rubrics v1.5.1), including the M05 corpus
  distinctness call.
- Project proposal for the supervisor.
- **The pilot note** (after the R0 pilot, the zero-CC dry run, the gradient-availability probe
  and the scoreboard re-read; before any local-CC Δ exists): band lists, margins, P-gate
  numbers, matrix tolerance, P3 effect size, M04 recipe, resonance route, ρ\*, K_cap, f_h and
  seed, Q7 tolerances and d₇, Q8 numbers.

## Provenance

Plan 05 is based on the research note of 2026-09-03 (item 4 above), which answered the user's
question *what single idea would make the plan-04 pipeline fast enough for super-large PAHs
without losing accuracy*. The answer — probe the local CC−DFT correction with a hashed pattern
set whose count is intended to saturate, instead of learning a surface — rests on published
O(1)-gradient and compressed-sensing Hessian recovery (bibliography items 23–24). The
2026-09-03 search found no application of that recovery to a CC−DFT difference or to
anharmonic constants; that absence is a search result, and Pass B is asked to try to falsify
it. The plan-04 source conversation (`AI_Chats/grok_chat_4.md`) remains the provenance for the
CC-anchor idea itself.

## What survives from plans 01–04

Method-agnostic governance, carried verbatim: measured-not-asserted arithmetic in `probes/`;
never cite from recall; pre-registration, frozen splits with hashes, ≥3 seeds, tuning parity;
declared effect size, **inconclusive is publishable**; escalation ladders declared in advance,
stopping is a result; fail-closed reporting; deviations only as dated notes committed before
the number is known. From plan 04 specifically: everything except the learned surface.
