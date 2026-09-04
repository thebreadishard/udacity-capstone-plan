# Plan 05 — Δ-Probed IR Pipeline

**Status: draft, folder created 2026-09-03. Not complete as a plan. Nothing here is a result.**
Supersedes plan 04 (CC-Anchored IR Pipeline), whose folder **stays in the tree** until the
user decides to remove it (see [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md)).
Plans 01–03 are superseded, read-only records restored to the tree on 2026-09-04.

**Promised deliverable (Module 08).** A pipeline: **any individual aromatic molecule in, an
infrared spectrum out** — plan 04's criterion, ladder, opponents, scoreboards and gates — with
the coupled-cluster anchor obtained as a **probed correction Δ₂ to the harmonic force
constants** rather than a learned per-molecule surface, from local-CC energies with frozen
domains, and with the number of energies that correction needed, **K = 2M + K_off**, measured
per rung and printed as a cost record beside every spectrum. Whether the off-diagonal count
K_off stops growing with molecule size is a measured question (Q8) with a pre-registered
losing condition, not a promise. No coupled-cluster correction to anharmonic constants is
promised.

The sequence **ends at Module 09**. There is no `Horizon/` and there are no Projects 10–12.

## Glossary (one line each; the Goal file defines them fully)

- **Δ** = local coupled cluster minus DFT, as force constants: **Δ₂** Hessian correction,
  **Δ₃** cubic, **Δ₄** semi-diagonal quartic. Only Δ₂ is promised.
- **Local CC** = DLPNO-CCSD(T) (domain-based local pair natural orbital) or LNO-CCSD(T) (local
  natural orbital): controlled locality truncations of CCSD(T).
- **Mode E / mode G** = Δ₂ recovered from energies only (the promised route) / from analytic
  gradients (a bonus on the 2026-09-03 landscape).
- **Pattern** = one simultaneous multi-atom displacement geometry; **K** = the measured number
  of patterns a rung needed to reach the residual target **ρ\***; **K_off** = K − 2M;
  **K_cap** = the pilot-note cap.
- **Structural prior** = the fixed, parameter-free, frequency-banded regulariser of the promised
  recovery; **learned prior** = the Module-05 Transformer, a bonus arm only.
- **CMA** = Concordant Mode Approach (Lahm 2022; Kitzmiller 2024): prior art for the diagonal
  part of this plan's recovery.
- **GVPT2** = resonance-explicit second-order vibrational perturbation theory; **MD-ACF** =
  spectrum from the dipole autocorrelation of molecular dynamics; **QFF** = quartic force
  field; **PNO** = pair natural orbital; **TightPNO/NormalPNO** = DLPNO threshold presets;
  **CPS** = complete-PNO-space extrapolation.

## Reading order

1. This file — orientation. **Draft, not complete.**
2. [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md) — every
   change relative to plan 04, in one table (23 rows)
3. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — prime directive
4. [GoalGathering/Research_Note_2026-09-03_Delta_Probing.md](GoalGathering/Research_Note_2026-09-03_Delta_Probing.md)
   — the source document as written that morning, with §8 recording what both reviews corrected
5. [GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md) — opponents
   and scoreboards (carried from plan 04)
6. [GoalGathering/Frozen_Ladder_and_Tolerances.md](GoalGathering/Frozen_Ladder_and_Tolerances.md)
   — sentence types, rungs, what is frozen now vs at the pilot note, stop conditions
7. [GoalGathering/Compute_Budget_2026-09-03.md](GoalGathering/Compute_Budget_2026-09-03.md)
   — three budgets; the classification rule; the order of timed probes
8. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
   — the Δ-probing object, gates Q0–Q8 / P0–P5, fail-closed sentences
9. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md)
   — bibliography with per-item verify status (items 23–47 new)
10. [probes/README.md](probes/README.md) — conventions and the probes owed
11. [GoalGathering/Capstone_Mapping.md](GoalGathering/Capstone_Mapping.md) — modules 02–09
    against Rubrics v1.5.1 for the re-worded promised set; Pass 6 (sign-off) not done; M05's
    rule-0 escalation is open decision 4
12. [GoalGathering/Project_Proposal_2026-09-03.md](GoalGathering/Project_Proposal_2026-09-03.md)
    — the supervisor proposal: the *why* of the major decisions, the conditional review
    status, and the decisions the student has not yet made

## Review record

- **Round 7, Pass A** (cold read, 2026-09-03, fresh context):
  [Professor_Review_2026-09-03_Round7_PassA.md](GoalGathering/Professor_Review_2026-09-03_Round7_PassA.md)
  — verdict: not sound enough for Pass B until patched; 10 blocking + 11 non-blocking.
  Brief: [Review_Brief_2026-09-03_Round7_PassA.md](GoalGathering/Review_Brief_2026-09-03_Round7_PassA.md).
  **All 21 addressed in spec the same day** (complete change table; K as a measurement with
  ρ\* and K_cap; Q8 in fixed form; cost record vs size sentence; learned prior barred from
  every promised rung; R2 re-read against the coverage probe; snippet items upgraded; P4
  sentences; glossary; stale text). Pass B confirmed the patches held.
- **Round 7, Pass B** (adversarial domain, 2026-09-03, fresh context, literature verified):
  [Professor_Review_2026-09-03_Round7_PassB.md](GoalGathering/Professor_Review_2026-09-03_Round7_PassB.md)
  — verdict: **conditional** — green light for the R0–R1 measurement programme once the six
  blocking items are written in; no green light for the promised set *as then worded*
  (Δ₃/Δ₄ on the promised path, mode G as the primary cost question, R6 as a whole-molecule
  object). Brief: [Review_Brief_2026-09-03_Round7_PassB.md](GoalGathering/Review_Brief_2026-09-03_Round7_PassB.md).
  **All six blocking items written in the same day, and the promised set re-worded as the
  review specified:** (1) Q6 given frozen threshold formulas (noise line σ_E ≤ 0.82·τ·q_s²,
  bias line, threshold line; pilot-note item 13), the R1 smoothness probe moved before the
  pilot note, pattern amplitude taken from its grid, Madriaga & Crawford's fixed-dimension
  result and Psi4's lack of domain reuse recorded; (2) the structural prior made
  frequency-banded, the dry-run pair fixed to bracket exact exchange, dry-run-flagged blocks
  given explicit two-mode patterns, K_off made the mode-E cost quantity, Q7 printed for
  diagonal-only and full recovery; (3) **Δ₃/Δ₄ removed from the promised set and from Q7**,
  a diagonal-cubic bonus probe kept, the DFT family set closed under the resonance search;
  (4) CMA cited (items 42–43), mode-tracking and gradient-based compressed sensing named,
  the novelty sentence rewritten and "never done" added to the forbidden quotes; (5) the
  cost question re-anchored on K_off in mode E with mode G as bonus, the gradient+(T) fallback
  withdrawn, **open decision 1 (fragment probing) moved before the pilot note and made the
  determinant of R6's promised form, whole-molecule R6 not promised in any branch**; (6) Q8
  computed on direct blocks (reference Hessian at R0–R1; a prior-free direct-block probe at
  R2–R3), reference-vs-recovered agreement made a Q7-class check, the anthracene locality
  probe added as a dated bonus. Non-blocking items 7–13 also written in (expected-effect
  line; CPS deck field and the pyrene canonical diagonal check; M05 corpus = Hessian QM9 +
  recomputed B3LYP with the Δ₂ support as target; R6 DFT Hessian as B3; R0 licence cell
  wording; Mulas functional B97-1; O1NumHess polyene note; item 30 full text; research-note
  section order).
- **Green light.** Pass B's green light for the **R0–R1 measurement programme** stands as
  written in the review. The promised set beyond R1, as re-worded above, is the set Pass B
  described as "not a mistake relative to plan 04"; whether that re-worded set is adopted is
  the **user's decision**, together with open decisions 1, 3 and 4 below. The mapping and the
  proposal (reading-order items 11–12) are written for the re-worded set and say so.

Plan 04's Round-6 Pass A and Pass B findings and their closures bind plan 05 and are not
re-litigated.

## Open decisions for the user

1. **Fragment probing — before the pilot note; decides R6's form.** In → R6 promised as
   fragment-probed Δ₂ conditional on Q8 at R2–R3 and B3. Out → R6 leaves the promised set.
   Whole-molecule R6 is not promised either way (Goal, Ladder §2 dated note).
2. ~~Removal of the plan-04 folder~~ — **decided 2026-09-04: all plan folders stay in the tree**; plans 01–03 were restored as read-only records.
3. **The R2 A-scored set** as re-read against the coverage probe (triphenylene in on gas
   families; tetracene fully gated) — veto by dated note restores plan 04's set.
4. **The Module-05 target** (Δ₂ support on a DFT-vs-DFT corpus from Hessian QM9) — veto makes
   M05 a demonstration, defended as one.
5. **Adoption of the Pass-B re-worded promised set** (Δ₂ only; mode E primary; R6 per
   decision 1) — the default this folder is written to.
6. **Machine**: whether the replacement laptop carries a GPU (a B2 fact either way).

## Not yet done (owed, in order)

- The user's decisions 1–6 above (the proposal's §10 puts them to the supervisor as well).
- Capstone mapping Pass 6 (module-by-module sign-off) once decisions 1, 3 and 4 are made.
- **The pilot note** (after the R0 pilot, the zero-CC dry run, the gradient-availability probe
  with memory, the R1 smoothness probe and the scoreboard re-read; before any local-CC Δ₂
  recovery exists; with open decision 1 recorded): band lists, margins and the
  expected-effect line, P-gate numbers, matrix tolerance, P3 effect size, M04 recipe,
  resonance route and resonance-closed family set, ρ\*, K_cap, f_h and seed, τ₇ and d₇, Q8
  numbers and direct-block pairs, Q6 numbers and the pattern amplitude.

## Provenance

Plan 05 is based on the research note of 2026-09-03 (item 4 above), which answered the user's
question *what single idea would make the plan-04 pipeline fast enough for super-large PAHs
without losing accuracy*. The answer — probe the local CC−DFT correction to the force constants
with a hashed pattern set instead of learning a surface — rests on published O(1)-gradient and
compressed-sensing Hessian recovery (bibliography items 23–24) and, as Round-7 Pass B
established, on the Concordant Mode Approach (items 42–43) for its diagonal part. What remains
proposed is stated in the research note's §8: local CC with frozen domains at PAH sizes, the
off-diagonal block by banded sparse recovery from multi-mode patterns, the recovery licensed
against direct references, and locality and K_off measured against size. The plan-04 source
conversation (`AI_Chats/grok_chat_4.md`) remains the provenance for the CC-anchor idea itself.

## What survives from plans 01–04

Method-agnostic governance, carried verbatim: measured-not-asserted arithmetic in `probes/`;
never cite from recall; pre-registration, frozen splits with hashes, ≥3 seeds, tuning parity;
declared effect size, **inconclusive is publishable**; escalation ladders declared in advance,
stopping is a result; fail-closed reporting; deviations only as dated notes committed before
the number is known. From plan 04 specifically: everything except the learned surface.
