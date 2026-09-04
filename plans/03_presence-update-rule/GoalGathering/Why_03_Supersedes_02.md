# Why plan 03 supersedes plan 02

**Date.** 2026-08-29.

Plan 02 is no longer in this tree (removed 2026-09-01). It remains in git history. This file is the
argument of record for why 03 replaced it; it is not a pointer into a live 02 folder.

## The block that 02 cannot lift inside a master’s

Plan 02’s module map was deliberately unwritten until three measurements existed (CC computability, locality of anharmonic corrections, dipole-surface gate). Round 4 already recorded:

- an in-core memory wall between benzene and naphthalene
- a published band-family where a locality assumption fails by tens of cm⁻¹
- intensities gated on a dipole surface that is itself a research object

That is a *label-factory* block. Waiting on it spends the capstone on instrumentation that Udacity Modules 03–06 cannot grade.

## What 03 keeps from 02

- Governance (pre-registration, hashes, seeds, fail-closed, DOI-before-claim).
- The discipline of a frozen ladder with named rungs and named stop conditions.
- Honesty that “chemically precise IR” has three readings and only one of them was even a possible 02 promise. 03 does not revive any of the three.

## What 03 refuses from 01

- Spending the thesis on making a voxel grid “good enough for a spectrum.”
- Scoring Module 08 on band positions of H₂O / benzene.
- Treating discretisation as the scientific contribution.

## Six alternatives weighed (short)

| # | Alternative | Verdict |
|---|---|---|
| A | Stay on 02, measure the CC rung | Rejected — map cannot start |
| B | Revive 01 PES+IR | Rejected — deliverable overtaken; budget profile failed |
| C | Graph-CA on atoms | Rejected — contradicts the local-field premise (one E, one B per point) |
| D | Exact 6-D two-electron QCA | Rejected for Module 08; H₂ diagnostic only |
| E | Learn KS orbitals, not fields | Rejected — molecule-size feature count sneaks back in |
| F | Presence-update-rule on frozen 3-D fields | **Taken** |

## Effort arithmetic (asserted; probes must confirm)

Teacher generation for H₂ and H₂O is **Octopus RT-TDDFT (ALDA) with Maxwell–TDDFT fields** on the frozen grid, not a naphthalene-CC wall. Nuclei are frozen point charges on the scored window. Caps, not estimates, live in [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md): 80 h **human** grid+teacher I/O, 168 h **wall-clock** for the promised teacher set. Do not type a runtime into this file. Training a 3×3×3 conv-stencil (5×5×5 is the comparison axis) on those windows is a Module 05 object. The scarce resource is *evaluation honesty* (P0–P4), not integral evaluation.

Contradiction pass 2026-09-01: H₂ is not an exact two-electron teacher in Modules 02–09. That teacher is Horizon 10. \(\mathbf{E},\mathbf{B}\) are teacher Maxwell channels, not a Poisson reconstruction.
