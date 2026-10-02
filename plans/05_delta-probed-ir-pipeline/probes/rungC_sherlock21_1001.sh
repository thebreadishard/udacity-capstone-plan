#!/usr/bin/env bash
# Sherlock chain 21, 2 Oct 2026 (amendment 03:1x): the carried recipe at fixed composition — pool A + A2, sizes 45 and 100 (175 = chain 14b), seeds 0–2 —
# the three-point T2 curve without the composition confound of the mixed pool. Lane B, at once.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux both --kring-weight 0.3 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 21 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 21 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_carried_AA2_45_100_$D --use-analytic --pool-layers A,A2 --sizes 45,100 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== chain 21 (45, 100) done $(date)" || echo "=== CHAIN 21 FAILED $(date)"
echo "=== chain 21 finished $(date)"
