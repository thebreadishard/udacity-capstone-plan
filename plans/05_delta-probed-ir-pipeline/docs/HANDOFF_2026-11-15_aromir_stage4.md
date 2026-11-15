# Handoff — aromir, stage 4 (the soft-mode repair), 15 November 2026

Follows `HANDOFF_2026-11-15_aromir_stage3.md` and `…_anharmonic_decision.md`. Written from the same cloud session. TASKS 73, 216, 201.

## What was added to `thebreadishard/aromir`

`src/aromir/repair.py` and three functions in `vibrations.py` (`displacement`, `column`, `with_measured_columns`): the low-mode repair
of `corpus/analytic_hessians.repair_low_modes` and `corpus/vibrations.py`, for the product's one functional. Modes below 20 cm⁻¹
(`LOW_MODE_CM`), step 0.01 bohr, displaced points at conv_tol 1e-9 / conv_tol_grad 1e-7 started from the previous point's density, the
second-order finish as the fallback — the label route's settings of 14 November.

`lowlevel.compute(..., repair_soft_modes=…)` is a required keyword. **`aromir baseline` always repairs; `aromir spectrum` repairs when
the release's `training.json` says `soft_mode_repair: true`** — a network gets the kind of Hessian it was trained on. `probes/
aromir_model_card.py training` now takes `--soft-mode-repair yes|no` and refuses to run without it: **v1.3 (chain 35) is `no`**, a
network trained on the corpus after the swap of 14 November (v1.4) is `yes`.

## Validation (number and counterpart)

- Water's bend with the threshold raised to 2000 cm⁻¹, as `probes/label_route_repair_check.py` does: the measured mass-weighted
  column against the analytic one 2.9e-9; the repaired frequency moves 0.0023 cm⁻¹ (1679.3616 → 1679.3593); the repaired Cartesian
  Hessian within 1e-4 of its largest element. (The label route's own check on 14 Nov: 2.04e-8 and 0.016 cm⁻¹, on pyscf 2.14.0;
  this is 2.15.0.)
- The arithmetic exactly, on a synthetic Hessian: exact columns leave it unchanged (1e-14); a column 1.21 times stiffer raises that
  mode's frequency by 1.1 and no other.
- **Not validated: a genuinely soft mode.** No molecule with a mode below 20 cm⁻¹ was run in the cloud. To do on the laptop: aromir's
  repair on D_ac28161d06 against the probe's patched lowest mode (0.04 cm⁻¹ from the gradient and energy routes, TASKS 49 option 3).

## Three deliberate differences from the label route

1. **The directions come from the B3LYP modes alone.** The label route merges the soft modes of both labels (B3LYP and ωB97X) by an
   SVD, so a molecule whose ωB97X Hessian alone has a mode below 20 cm⁻¹ was repaired along a direction aromir will not measure.
   How many of the 58 repaired molecules that concerns is a count on the corpus (`probes/low_mode_coverage.py`'s bands per label).
2. **pyscf's own grid-response gradient, not `grid_response_blocked`.** aromir calls `nuc_grad_method().set(grid_response=True)`
   (pyscf `grad/test/test_rks.py`) and refuses, before pyscf allocates, a gradient whose per-atom arrays exceed `max_memory` — the
   label route's own estimate, 8 · grid points per atom · (10 nao + 3 natm² + 5 natm) bytes — with the advice to raise
   `--max-memory-mb`. The blocked version patches pyscf's private functions; it belongs upstream (TASKS 202), and aromir takes it
   from a released pyscf.
3. **With a release trained on unrepaired Hessians (v1.3) nothing is repaired**, so a soft mode that the analytic Hessian shows as
   imaginary still refuses the molecule, as pipeline 0.9 does.

## Still to do for 0.1

The release itself (the laptop's steps of stage 3's note, now with `--soft-mode-repair no` for v1.3), the comparison on a real soft
mode above, and the model card's text.
