# Plan 04 — CC-Anchored IR Pipeline

**Status: draft, folder created 2026-09-02. Not complete as a plan. Nothing here is a result.**  
Supersedes plan 03 (Presence-Update-Rule), which was **removed from the tree on 2026-09-02**.
Plans 01–03 are git history only.

**Promised deliverable (Module 08).** A pipeline: **any individual aromatic molecule in, an
infrared spectrum out** — with a per-size method ladder and a pre-registered, **gated**
comparison against the frozen state-of-the-art lines in
[GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md): "beat" claims
unconditional only on the gas-phase rungs (R0–R1); R2–R3 decided — or pre-declared
inconclusive — by the M03 matrix–gas gate; the C₃₈₄H₄₈-class reach demonstration conditional
on cluster access and carrying no accuracy claim.

The sequence **ends at Module 09**. There is no `Horizon/` and there are no Projects 10–12.
Chemically better IR of complex aromatics is the reason for the work, not a post-degree item.

## Reading order

1. This file — orientation. **Draft, not complete.**
2. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — prime directive
3. [GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md) — the named,
   versioned opponents and the laboratory scoreboards
4. [GoalGathering/Frozen_Ladder_and_Tolerances.md](GoalGathering/Frozen_Ladder_and_Tolerances.md)
   — rungs R0–R6, accuracy vs reach claims, stop conditions
5. [GoalGathering/Compute_Budget_2026-09-03.md](GoalGathering/Compute_Budget_2026-09-03.md) —
   human hours uncapped (logged, never limited); machine checkpoints as honesty devices; the
   timed-probe protocol. Supersedes the 2026-09-02 budget
6. [GoalGathering/Capstone_Mapping.md](GoalGathering/Capstone_Mapping.md) — modules 02–09
   against Rubrics v1.5.1; every artifact load-bearing; the three 2026-09-02 user decisions
7. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
   — levels and anchors, the Δ-vs-direct axis, Q/P gates with mandatory null rows
8. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md)
   — working bibliography with per-item verify status and named debts
9. [probes/README.md](probes/README.md) — probe conventions and the probes that exist

## Review record

- **Round 6, Pass A** (cold read, 2026-09-02):
  [Professor_Review_2026-09-02_Round6_PassA.md](GoalGathering/Professor_Review_2026-09-02_Round6_PassA.md)
  — verdict: not sound enough for Pass B until patched; 8 blocking + 11 non-blocking findings.
  **All 19 addressed in spec the same day** (banner/tree fix; Goal question split per claim
  type; Q4/M04 exception declared; R1 license made conditional; matrix tolerance moved to one
  bin; C₃₈₄H₄₈ hedged to class + debt; debt lists made identical; pilot-note inputs restricted
  to lab+opponent side and the R0 pilot stripped of its lab comparison; MAE-use removed; both
  M04 readings on the page; M04 recipe + promised families frozen in the pilot note; P4 bound
  to P2's bands/seeds/script with one fail-closed sentence; positions-scored/intensities-
  reported split; R2 A-set separated from unscored triphenylene + charge-state rule; stale
  layout/links/acronyms fixed; P3 effect size binned; booking rule added; ~1 cm⁻¹ bind
  carried).
- **Round 6, Pass B** (adversarial domain, 2026-09-02, run by the user in a fresh chat):
  [Professor_Review_2026-09-02_Round6_PassB.md](GoalGathering/Professor_Review_2026-09-02_Round6_PassB.md)
  — verdict: **no green light for the promised set as then worded**; 5 blocking + 6
  non-blocking. Addressed the same day in two steps. *Factual fixes* (commit `040371f`):
  resonance-explicit machinery (raw VPT2 forbidden on promised families), Q6 anchor-license
  probes as the stop-4 trigger, mechanical N_min × wall-clock kill rule, positions-only
  criterion sentences, Tang demoted to context, tier-2 blocked on debt 4, Sylvetsky pinned.
  *Scope decisions* (user, same day): R2–R3 stay promised **behind the M03 matrix–gas
  decidability gate** (matrix-limited families pre-declared inconclusive); R6 stays promised
  **conditional on B3**, its certificate an explicitly-labelled extrapolation with no accuracy
  claim (Distilled §9.5 rewritten); the M04 reading-2 fallback is now **named and verified**
  (NIST CCCBDB, DOI 10.18434/T47C7Z; VIBFREQ1295 as second option — bibliography items 21–22).

## Not yet done (owed, in order)

- **The pilot note** (after the R0 pilot and the scoreboard re-read probe: band lists, beat
  margins, P-gate numbers, matrix tolerance as measured, P3 effect size, M04 baseline recipe,
  resonance route per rung, N_min per rung — frozen before any pipeline-vs-lab number exists).

## Provenance

Plan 04 is based on the planning conversation [`AI_Chats/grok_chat_4.md`](../../AI_Chats/grok_chat_4.md)
(read in full, 360 lines): one CC run yields one energy (optionally analytic forces); a full CC
surface is feasible for water and impossible for coronene's 102 vibrational coordinates; the
workable recipe for large aromatics is an accurate equilibrium Hessian plus a machine-learned /
reduced-dimensional anharmonic correction trained on self-generated **DLPNO-CCSD(T)** points
(DLPNO = domain-based local pair natural orbital: a controlled locality truncation of coupled
cluster, usable at sizes where canonical CC is not), built **per molecule** — and that
per-molecule computation *is* the pipeline.

Round-5 Pass B (plan 03) still binds the architecture: no double-scope on one frozen clock.
Plan 04 does one thing — matter, nuclei, spectra. Light enters only as the emission
post-processing layer (tier 1, inherited cascade model), never as a co-owned Maxwell solver.

## What survives from plans 01–03

Method-agnostic governance, carried verbatim:

- measured-not-asserted arithmetic in `probes/`; missing inputs print `NOT_RUN`
- never cite from recall; verify-on-use; DOI before claim
- pre-registration; frozen splits with hashes; ≥3 seeds; tuning parity
- declared effect size; **inconclusive is publishable**
- escalation ladders declared in advance; stopping is a result
- fail-closed reporting; deviations only as dated notes committed before the number is known
