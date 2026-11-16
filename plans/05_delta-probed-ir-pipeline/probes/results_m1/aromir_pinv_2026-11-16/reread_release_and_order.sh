#!/usr/bin/env bash
# reread_release_and_order.sh — in WSL, from the plan folder, with ~/aromir_dev holding the fixed aromir (TASKS 236, 230):
#  1. the release check of 15 Nov again (probes/aromir_release_compare.py, same three molecules and checkpoints): aromir with the
#     rank-based B+ against the trainer's inference path, tolerance 1e-6 hartree/bohr2;
#  2. TASKS 230's atom-order read (probes/network_invariance_check.py --what smiles --seeds 5, the three molecules of 15 Nov) as it
#     was measured, and again with the rank-based B+ in place of np.linalg.pinv(B) inside the process.
set -uo pipefail
# no-set-e: each step's exit code is printed and the next step still runs
OUT=probes/results_m1/aromir_pinv_2026-11-16
PY=$HOME/aromir_dev/bin/python
export OMP_NUM_THREADS=4 PYTHONUNBUFFERED=1 PYTHONUTF8=1
MODELS="E7_rungC_chain35_analytic_model_n750_seed0.pt E7_rungC_chain35_analytic_model_n750_seed1.pt E7_rungC_chain35_analytic_model_n750_seed2.pt"
ORDER_IDS="A_541c53d1a5 A_fdc27f1bd1 A_ea73419366"
# shellcheck disable=SC2086  # the model and id lists are word lists
$PY probes/aromir_release_compare.py "$HOME/aromir-src/src/aromir/releases/v1.3" $OUT/delta_h_compare_fixed.json --models $MODELS \
  --ids A_3100da3761 A_541c53d1a5 B_0da4a5aea1
echo "(REREAD) release compare exit $?"
# shellcheck disable=SC2086
$PY probes/network_invariance_check.py $ORDER_IDS --what smiles --seeds 5 --out $OUT/order_spread_smiles_before.json
echo "(REREAD) order read as measured: exit $?"
# shellcheck disable=SC2086
$PY $OUT/run_with_rank_pinv.py probes/network_invariance_check.py $ORDER_IDS --what smiles --seeds 5 --out $OUT/order_spread_smiles_rank_pinv.json
echo "(REREAD) order read with the rank-based B+: exit $?"
