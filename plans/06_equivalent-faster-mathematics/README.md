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
9. [lean/](lean/README.md) — the formal route: a Lake project on Mathlib `v4.34.0-rc2` (installed 2026-09-12); `Plan06/T1/MeasurementAlgebra.lean` holds T1 — T1a, T1b and T1c all proved (no `sorry`): exact recovery from colour-class probes, Δ + 1 probes suffice, and the symmetric one-sided scheme. Build with `lake exe cache get && lake build`; `.lake/` is git-ignored.
10. [Uitleg/](Uitleg/00_Leeswijzer.md) — the plan explained at vwo-6 level in Dutch: the question, what is proven impossible, why it can still work for this class, the directions and experiments, Lean as referee, glossary.

## What this folder will and will not contain

- Will: orientation and reading notes, small numerical experiments on plan 05's sealed lines and dry-run
  tensors (`experiments/`), Lean files of the formal route (`lean/`, since 2026-09-12), and dated decisions.
- Will not: pipeline results, modules, rungs, or any claim about spectra. Those belong to plan 05.
