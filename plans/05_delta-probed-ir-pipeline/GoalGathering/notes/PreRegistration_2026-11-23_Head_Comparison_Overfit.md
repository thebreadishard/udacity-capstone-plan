# Pre-registration: can each head fit benzene alone? (TASKS 296, step 1)

Registered 23 November 2026, 09:5x, before the run. The run is `probes/runspecs/head296_overfit.json` (chain
`probes/runs/head296_overfit.json`); it has not been launched. It loads the whole corpus, so it runs after `v14_stage2` has ended
and after the DFT batch has been written into the corpus, not beside either.

## Why

The design note on presentation dependence (`Design_2026-11-23_Presentation_Dependence_Repair.md`) keeps the Cartesian head as a
second route only, on the ground that the hybrid head is the better one. That ground is one comparison, of 1 October on 175
molecules, in which the Cartesian head was not learning: it could not fit benzene alone, and it gave the same error with the
low-level Hessian zeroed. A head that cannot fit one molecule needs a repair, not a comparison on the pool. So the comparison on the
pool is registered only after this test, and its design depends on the outcome below.

## The run

Three trainings of `m05/rungC_train.py --overfit-one A_8448043181` (benzene), 5,000 steps, sum aggregation, body 64 × 3 blocks,
seed 0, analytic labels (`--use-analytic`), no inner validation and no early stopping (the mode's documented recipe):

| arm | head | settings |
|---|---|---|
| cartesian_lr1e-3 | Cartesian | lr 1e-3, the registered loss |
| cartesian_lr3e-4 | Cartesian | lr 3e-4 |
| hybrid_carried | hybrid | the carried recipe of v1.4's control: `--aux both`, k-ring 0.3, k-diag 0.1 per family, SQM α, pair features, hidden 256, pattern f, lr 3e-4, weight decay 1e-4 |

Every arm's arguments passed the trainer's own config check on 23 November (`parse_config(...).resolved()`, no data loaded).

## What is read

From each arm's own report (`out/head296/overfit_<arm>.md`), the row of hold-out (a), which in this mode is benzene itself: the
column 'ΔH residual ratio' and the column 'corrected ω' (cm⁻¹). No new read script: three rows are read by eye and copied with the
file names into the ledger.

For reference, the same diagnostic of 1 October (old labels, files `out/E7_rungC_diag_overfit_benzene_*_2026-10-01.md`):
Cartesian lr 1e-3: 0.583 and 17.13 cm⁻¹ (uncorrected 25.01); hybrid, pattern term, lr 1e-3: 0.079 and 1.55 cm⁻¹.

## The rule

For the Cartesian head, over its two learning rates:

- **FITS**: at one of the two rates the ΔH residual ratio is ≤ 0.10 and the corrected ω is ≤ 2.0 cm⁻¹ — the level the hybrid head
  reached on 1 October. Then the comparison on the pool is registered next: the Cartesian head with its learning rate and schedule
  searched, at least two seeds, the v1.4 control's data, hold-outs and selection set, and the presentation test on both heads.
- **CANNOT FIT**: at both rates the ΔH residual ratio is ≥ 0.30. Then no pool run: the next step is to find why a head that can
  express any symmetric, translation-free ΔH does not reach it on one molecule (output scale, loss weights, the unused low-level
  input), with HIP's construction (Burger et al. 2025) as the reference design.
- **BETWEEN**: anything else. Then one more diagnostic before a decision: 20,000 steps at the better of the two rates.

The hybrid arm is the control of the test itself: it must again reach a ΔH residual ratio ≤ 0.10 and ω ≤ 2.0 cm⁻¹; if it does
not, the test is not read and the cause is looked for first (the labels changed from finite-difference to analytic since October).

## Expectation, written before the run

CANNOT FIT, near 0.58 and 17 cm⁻¹ as on 1 October: the Cartesian head's code has not changed in what it predicts. The labels have
(analytic now), so a different number would itself be information. The hybrid arm: fits, near 0.08 and 1.5 cm⁻¹.

## Not in this registration

The comparison on the pool, its read rule and its power; the repair of the hybrid head's inputs (TASKS 287), which goes on either way.
