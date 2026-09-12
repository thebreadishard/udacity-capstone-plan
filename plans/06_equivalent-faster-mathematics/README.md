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

## What this folder will and will not contain

- Will: orientation and reading notes, small numerical experiments on plan 05's sealed lines and dry-run
  tensors (`experiments/`), Lean files if the formal route is taken (`lean/`), and dated decisions.
- Will not: pipeline results, modules, rungs, or any claim about spectra. Those belong to plan 05.
