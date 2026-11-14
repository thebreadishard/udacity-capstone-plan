# The low-mode repair moves into the label route

**Written 14 November 2026.** TASKS 216, from the user's rule of that morning: the pipeline carries every quality-raising lesson,
directly as a step or indirectly through the trained network (CLAUDE.md, *Improvements reach the end product*). Today the repair is a
probe that patches 58 corpus folders by hand; every molecule computed after today would carry the same error again.

## 1. What is wrong today

`modules/05_support_predictor/corpus/analytic_hessians.py` computes a molecule's two analytic label Hessians and writes them. pyscf's
CPU DFT Hessian carries no grid-weight derivatives (pyscf#3437), which moves a vibration below ≈ 20 cm⁻¹ by up to 6 cm⁻¹ and one above
it by under 0.5 (TASKS 201 step 2). The repair that removes it — recompute the Hessian's column along each soft direction from central
differences of grid-response gradients — lives in `probes/low_mode_patch.py` (the arithmetic), `probes/low_mode_patch_run.py` (the
driver) and `probes/hessian_grid_response_fd.py` (one displaced point). The label route knows nothing about it.

## 2. What the integration must not break

- A molecule with no mode below the threshold must come out **bit for bit** as it does today. This is the regression test that goes in
  first, on a branch in its own worktree, as CLAUDE.md requires of a refactor in a path a run uses.
- The file's reader contract: `H_raw`, `H_projected`, `freq_cm`, `energy`, `grid`, `charge`, `spin`, `reference`, `software` stay, with
  the same meanings. The trainer reads `H_projected` (`m05/rungC_equivariant.load_molecule`), the release builder reads `freq_cm`.
- `probes/low_mode_swap.py` and the 58 folders it swaps must keep working: the route's own repair and the swap must write the same
  thing, so that a repaired corpus folder cannot be told apart by where its repair came from.

## 3. The shape of the change

**One implementation, in the production folder.** A new module `modules/05_support_predictor/corpus/low_mode_repair.py` holds what is
now split over the three probe files: the projected vibrational modes, the merged low-mode directions, the displaced grid-response
gradient, and the patched column. `probes/low_mode_patch.py` and `probes/hessian_grid_response_fd.py` then import from it instead of
carrying their own copies, so the arithmetic exists once (CLAUDE.md, *One implementation of every constant and formula*). The corpus
folder keeps importing nothing outside itself.

**The trigger is measured, not chosen.** The repair runs when a projected vibrational mode of *either* label falls inside
|ω| < `LOW_MODE_CM` = 20.0 cm⁻¹. Above that the measured change stays under 0.5 cm⁻¹; below it reaches 6. TASKS 218 asks whether the
threshold should be higher — the dry run of 14 November saw a 62 cm⁻¹ mode move 6.72 cm⁻¹ — and that question is answered by its own
measurement, not here. The constant lives in the new module and both routes read it from there.

**The order of operations changes.** `process_molecule` loops over the functionals and writes each Hessian as it goes. The merged
direction set needs both Hessians, so the loop splits in two: compute both, then decide on the directions, then repair, project, write.
That is the one structural change, and it is why the regression test comes first.

**What a repaired file says about itself.** The repaired Hessian is written as `H_raw` and `H_projected`, exactly as an unrepaired one
is, so no reader has to know. Beside it go `H_raw_unrepaired` and a `low_mode_patch` JSON string with the registration, the threshold,
the step, the number of directions and the frequencies before and after — the same key `probes/low_mode_swap.py` writes, so the two
sources of a repair are indistinguishable to a reader and distinguishable to an auditor.

**Cost.** Two displaced points per direction and functional: minutes for a molecule of 8–40 atoms, hours at 60 (one point of
T_76dfc434db took 1,915 s after the solver fix of 14 November, 9,988 s before it). The route reports the extra points and their seconds
in `analytic_check.json`; a runspec that computes labels states them in its estimate. No budget guard: a molecule with a soft mode
costs what it costs, and a silent skip would put the error back.

## 4. What the tests pin

1. **No low mode, no change**: a molecule whose lowest vibration is above the threshold gives the same `H_raw`, `H_projected` and
   `freq_cm` as the current code, to the bit. Run on water and on one corpus molecule above the threshold.
2. **A low mode is repaired**: a folder with a mode below the threshold comes out with the repaired Hessian, the unrepaired one beside
   it, and the provenance string filled in.
3. **The two routes agree**: for one of the 58 folders, the route's own repair and `probes/low_mode_patch_run.py`'s patch give the same
   Hessian to 1e-10 hartree/bohr². This is the test that keeps the swap and the route from drifting apart.
4. **The arithmetic moved, not changed**: the probe modules' results before and after the move are identical on the stored point files
   of `probes/results_m1/low_mode_patch_2026-11-13/`, which need no new computation.

## 5. What this does not do

It does not change the threshold (TASKS 218), does not touch the 34 molecules whose imaginary mode is a geometry rather than
quadrature noise (TASKS 215), and makes no claim about modes between 20 and 30 cm⁻¹. It does not re-run the corpus: the 58 folders are
handled by the registered swap of 14 November, and this change is for every molecule computed after it.
