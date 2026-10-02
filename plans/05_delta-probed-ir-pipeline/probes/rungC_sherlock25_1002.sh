#!/usr/bin/env bash
# Chain 25, 2 Oct 2026 (lever 1 / T3, amendment 06:4x): the leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ with the three saved models of chain 24
# (carried recipe at 750, seeds 0–2): four folds each, 300 fine-tune epochs at lr 1e-3, columns zero rule / α scaling / untouched / α tuned / head tuned.
# Lane A, after chain 24. Line: the held-out anchor's ring-ip ω ≤ 3 cm⁻¹ rms.
set -uo pipefail
# no-set-e: every seed records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
R=../../probes/results_m1
until grep -q "=== chain 24 finished\|chain 24 not started" out/E7_rungC_sherlock24_2026-10-02.log 2>/dev/null; do sleep 120; done
grep -q "=== chain 24 (750, models saved) done" out/E7_rungC_sherlock24_2026-10-02.log || { echo "=== chain 25 not started: chain 24 did not finish cleanly $(date)"; exit 1; }
echo "=== chain 25 start $(date)"
for s in 0 1 2; do
  M=out/E7_rungC_carried_kd_750_saved_2026-10-02_model_n750_seed$s.pt
  [ -f "$M" ] || { echo "=== chain 25 seed $s: no model $M $(date)"; continue; }
  python m05/rungC_cc_transfer.py corpus/molecules "$M" out/T3_cc_transfer_seed${s}_2026-10-02 --threads 8 --epochs 300 --lr 1e-3 \
    --anchor A_8448043181=$R/e8_benzene_ccpvdz_tlambda/hessian_ccsd_t.npz \
    --anchor B_8b12a55d3a=$R/e8_fluorobenzene_ccpvdz_2026-09-30/hessian_ccsd_t.npz \
    --anchor A_6e858b26e5=$R/e8_pyridine_ccpvdz_2026-09-30/hessian_ccsd_t.npz \
    --anchor A_01f3186607=$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz \
    && echo "=== chain 25 seed $s done $(date)" || echo "=== CHAIN 25 seed $s FAILED $(date)"
done
echo "=== chain 25 finished $(date)"
