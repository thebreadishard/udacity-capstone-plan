#!/usr/bin/env bash
# Chain 27, 2 Oct 2026 (T3b, amendment 14:2x): the regularised head fine-tune (--head-l2 0.01 / 0.1 / 1) on the same folds with chain 24's three models. Lane A.
set -uo pipefail
# no-set-e: every cell records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
R=../../probes/results_m1
echo "=== chain 27 start $(date)"
for L in 0.01 0.1 1; do for s in 0 1 2; do
  python m05/rungC_cc_transfer.py corpus/molecules out/E7_rungC_carried_kd_750_saved_2026-10-02_model_n750_seed$s.pt out/T3b_l2${L}_seed${s}_2026-10-02 --threads 8 --epochs 300 --lr 1e-3 --head-l2 $L \
    --anchor A_8448043181=$R/e8_benzene_ccpvdz_tlambda/hessian_ccsd_t.npz --anchor B_8b12a55d3a=$R/e8_fluorobenzene_ccpvdz_2026-09-30/hessian_ccsd_t.npz \
    --anchor A_6e858b26e5=$R/e8_pyridine_ccpvdz_2026-09-30/hessian_ccsd_t.npz --anchor A_01f3186607=$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz \
    && echo "=== chain 27 l2 $L seed $s done $(date)" || echo "=== CHAIN 27 l2 $L seed $s FAILED $(date)"
done; done
echo "=== chain 27 finished $(date)"
