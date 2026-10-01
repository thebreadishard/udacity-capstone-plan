#!/usr/bin/env bash
# Sherlock chain 4, 1 Oct 2026 (amendment 08:2x, lever 2c / H4): encoder capacity — 5 blocks × 64 and 3 blocks × 128 — under the hybrid head,
# pattern d, sum body, 175, seeds 0–2, against lever 1's 0.40. Design-check gate per body. Queued behind chain 3.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d"
until grep -q "=== chain 3 finished\|not started" out/E7_rungC_sherlock3_$D.log 2>/dev/null; do sleep 60; done
echo "=== chain 4 start $(date)"
for CELL in "deep:--body-blocks 5 --body-width 64" "wide:--body-blocks 3 --body-width 128"; do
  L=${CELL%%:*}; FLAGS=${CELL#*:}
  python m05/design_check.py corpus/molecules --out out/design_check_sherlock_${L}_$D --aggregation sum $FLAGS > out/design_check_sherlock_${L}_$D.txt 2>&1 \
    && grep -q "verdict: \*\*PASS\*\*" out/design_check_sherlock_${L}_$D.txt || { echo "=== DESIGN CHECK ($L) FAILED — cell skipped $(date)"; continue; }
  python m05/rungC_train.py corpus/molecules out/E7_rungC_lever2c_${L}_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC $FLAGS \
    && echo "=== lever 2c $L (175) done $(date)" || echo "=== LEVER 2C $L FAILED $(date)"
done
echo "=== chain 4 finished $(date)"
