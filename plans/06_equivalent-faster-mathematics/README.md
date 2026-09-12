# Plan 06 — Equivalent, Faster Mathematics (idea plan)

**Status: idea plan, opened 2026-09-12 at the user's request. It does not supersede plan 05.** Plan 05
runs to its end; plan 06 is explored beside it, in conversation, and only what survives a
falsification test on data that already exists may later enter plan 05 — and then only through a
dated note or decision in plan 05's own documents. Nothing here is a promise, a rung, or a module.

**The target (the user, 2026-09-12): solving the Schrödinger equation.** Plan 05 pays for its
coupled-cluster anchor with local-CC ground-state energies at displaced geometries: measured 2,087 s per
benzene energy and 41,375 s (11.5 h) per naphthalene energy at cc-pVTZ tight thresholds, times a deck of
hundreds of energies per molecule. Is there a different mathematics that yields the *same* energies (in
a sense this plan makes precise: levels E1/E2/E3) at a fraction of that cost? For the general problem
the answer is known to be no (QMA-hardness; references in the orientation note); for the specific class
of molecules plan 05 treats — gapped, closed-shell, aromatic, near equilibrium — it is an open question
about the *structure of that class*. The user's premise is that it is worth trying again with today's
tools: large models as proposers and readers, and a proof assistant (Lean) as the referee for the parts
that are exact.

**Rules carried from plan 05 unchanged.** Measured, not asserted: every number is printed by a script
or derived in place. Never cite from recall: every reference is verified (Crossref/DataCite/full text)
before it is written. Dated notes. No laptop compute while an anchor job runs. A direction is alive
only while it has a stated falsification test; a direction that fails its test is recorded as failed,
not deleted.

## Reading order

1. [GoalGathering/Orientation_2026-09-12.md](GoalGathering/Orientation_2026-09-12.md) — what "equivalent"
   can mean, where plan 05's time actually goes, seven candidate directions each with its cheapest
   falsification, the Lean route assessed honestly, the exploration protocol, and the first three
   experiments (all on data already in the repository).
2. The ledger of directions at the end of that file — the only place where a direction's status lives.
3. [GoalGathering/Reading_Note_2026-09-12_X0_Complexity_and_Locality.md](GoalGathering/Reading_Note_2026-09-12_X0_Complexity_and_Locality.md) — X0 and X3a.
4. [GoalGathering/Reading_Note_2026-09-12_X4_Mathlib_Survey.md](GoalGathering/Reading_Note_2026-09-12_X4_Mathlib_Survey.md) — X4: what Mathlib holds for the Lean route (present / absent, per need; the three formal targets assessed).
5. [GoalGathering/Note_2026-09-12_T1b_Symmetric_Readability_and_X1_Correction.md](GoalGathering/Note_2026-09-12_T1b_Symmetric_Readability_and_X1_Correction.md) — the mathematics of T1b (one-sided readability is not a graph colouring; Theorem A is the Lean statement) and the **X1 correction**: verified product counts 8–18 (CPR) / 7–14 (symmetric) at benzene, not 4–5 (`experiments/x1b_symmetric_colouring.py`).
6. [GoalGathering/Reading_Note_2026-09-12_Coleman_More_1984_Symmetric_Colouring.md](GoalGathering/Reading_Note_2026-09-12_Coleman_More_1984_Symmetric_Colouring.md) — Coleman & Moré 1984 read in full: our `SymmValid` is their symmetrically consistent partition; symmetric colouring = no 2-coloured P₄; NP-complete; **triangular substitution is the scheme that pays** — X1c: 6–7 products at benzene (`experiments/x1c_triangular_substitution.py`).
7. [GoalGathering/Result_Note_2026-09-12_X1d_Noise_Propagation.md](GoalGathering/Result_Note_2026-09-12_X1d_Noise_Propagation.md) — X1d: plan 05's noise through the recovery schemes; substitution with 6 products stays within the noise budget (0.10 cm⁻¹ vs 0.07 for the deck), (`experiments/x1d_noise_propagation.py`); cost convention corrected the same evening: with energies only a second-order product costs 4M, so 6 products ≈ 720 > 448 — the route pays only with gradients (M2). Transferred to plan 05 as proposal P24.
8. [GoalGathering/Result_Note_2026-09-12_X5_Atom_Pair_Structure.md](GoalGathering/Result_Note_2026-09-12_X5_Atom_Pair_Structure.md) — X5: the correction in real space — 93.5 % on atoms and bonds, all 78 atom-pair blocks above the noise floor, the carbon ring flat (meta/para ≈ bonded), rank full again: S2 unlikely, S1 E2/E3, first motivation for S3 (`experiments/x5_atom_pair_structure.py`).
9. [GoalGathering/Reading_Note_2026-09-12_S3_DMRG_Pi_Systems.md](GoalGathering/Reading_Note_2026-09-12_S3_DMRG_Pi_Systems.md) — S3 reading (verified records; Hachmann et al. 2007 open text): the honest form of S3 is E2 (the ring-confined π part); X6 defined (π-CAS share at benzene, compute later).
10. [GoalGathering/Reading_Note_2026-09-12_S1_Decay_Theorems_Benzi.md](GoalGathering/Reading_Note_2026-09-12_S1_Decay_Theorems_Benzi.md) — S1's rigorous side: Benzi–Boito–Razouk's decay theorems (gap ⇒ exponential decay in graph distance, rate ∝ gap) as the template for T3; graph distance is the right variable for X5's "flat ring"; X7 defined (λ vs gap along the ladder). Conjecture T3 is now stated in the Orientation §5 (dated addition), with the Lean prerequisite check: Mathlib lacks Bernstein's ellipse theorem.
11. [lean/](lean/README.md) — the formal route: a Lake project on Mathlib `v4.34.0-rc2` (installed 2026-09-12); `Plan06/T1/MeasurementAlgebra.lean` holds T1 — T1a, T1b and T1c all proved (no `sorry`): exact recovery from colour-class probes, Δ + 1 probes suffice, and the symmetric one-sided scheme. Build with `lake exe cache get && lake build`; `.lake/` is git-ignored.
12. [GoalGathering/Result_Note_2026-09-12_X8_Size_Scaling_Substitution.md](GoalGathering/Result_Note_2026-09-12_X8_Size_Scaling_Substitution.md) — X8: the substitution count against the element count from benzene to C₃₈₄H₄₈ under connectivity patterns; the benzene calibration shows norm-based sparsity is not band-based sparsity (no pattern licensed at benzene); the size brackets wait for the naphthalene tensor.
13. [GoalGathering/Note_2026-09-12_T3_Proof_Plan.md](GoalGathering/Note_2026-09-12_T3_Proof_Plan.md) — Conjecture T3 as a proof plan: hypothesis audit (the gap hypothesis fails asymptotically on plan 05's size sequence), layers L0–L3 with their status, the sharper conjecture T3′ (the correction decays faster than either Hessian) with its test X9, and the buildable Lean lemmas T3a–T3c.
14. [GoalGathering/Result_Note_2026-09-12_X9_Correction_Longer_Ranged_Than_Hessian.md](GoalGathering/Result_Note_2026-09-12_X9_Correction_Longer_Ranged_Than_Hessian.md) — X9: T3′ falsified at benzene — the correction is longer-ranged than the DFT Hessian (its share rises with bond-graph distance; C–C meta/para 19–26 %).
15. [GoalGathering/Result_Note_2026-09-12_X10_DFT_Predictable_Pairs.md](GoalGathering/Result_Note_2026-09-12_X10_DFT_Predictable_Pairs.md) — X10: a free DFT-only rule (resonance denominators within an irrep) picks the 19 of 47 off-diagonal pairs that matter at 0.5 cm⁻¹ at benzene; candidate proposal for plan 05 after naphthalene; §5 (X11): on that pattern the substitution count is 4 products = 8 gradients, so the two savings stack.
16. [GoalGathering/Cost_Ladder_2026-09-12_Network_Data.md](GoalGathering/Cost_Ladder_2026-09-12_Network_Data.md) — the cost ladder: what it would take to run plan 05 many times (the network's data), lever by lever — thresholds, X10's pair rule, substitution or full Hessians with gradients, engine levers, locality — each with its measured or estimated factor and the order in which the missing numbers arrive.
17. [GoalGathering/Draft_P25_2026-09-12_DFT_Pair_Rule.md](GoalGathering/Draft_P25_2026-09-12_DFT_Pair_Rule.md) — draft P25 (not submitted): the free DFT ordering of off-diagonal pairs inside plan 05's symmetry prior, as an ordering (never a truncation), with the naphthalene repeat of X10 as its pre-registered licence test; waits for the user's decision and for the tensor.
18. [Uitleg/](Uitleg/00_Leeswijzer.md) — the plan explained at vwo-6 level in Dutch: the question, what is proven impossible, why it can still work for this class, the directions and experiments, Lean as referee, glossary.

## What this folder will and will not contain

- Will: orientation and reading notes, small numerical experiments on plan 05's sealed lines and dry-run
  tensors (`experiments/`), Lean files of the formal route (`lean/`, since 2026-09-12), and dated decisions.
- Will not: pipeline results, modules, rungs, or any claim about spectra. Those belong to plan 05.
