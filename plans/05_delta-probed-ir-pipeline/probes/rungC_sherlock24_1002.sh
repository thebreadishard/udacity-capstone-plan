#!/usr/bin/env bash
# Chain 24, 2 Oct 2026 (lever 1 / T3, amendment 06:4x): the carried recipe at 750 with --save-model (pattern f, projected target, pattern + 0.3 × kring + 0.1 ×
# K-diagonal, 3 × 64 body), seeds 0–2 — the proxy-trained models the CC transfer fine-tunes. Lane A, after chain 8b.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --save-model"
until grep -q "=== chain 8b finished\|8b not started" out/E7_rungC_sherlock8_$D.log 2>/dev/null; do sleep 120; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 24 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 24 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_carried_kd_750_saved_2026-10-02 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== chain 24 (750, models saved) done $(date)" || echo "=== CHAIN 24 FAILED $(date)"
echo "=== chain 24 finished $(date)"
