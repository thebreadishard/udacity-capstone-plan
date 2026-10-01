#!/usr/bin/env bash
# Sherlock chain 19, 2 Oct 2026 (amendment 01:3x): the wide body (3 blocks × 128) on the carried recipe — pattern f, projected target, pattern + 0.3 × kring —
# 175, seeds 0–2, 300 epochs (decision 51: the wide body's best epochs touched the cap of 200 on pattern d). Lane B, after chain 18. Design-check gate
# for the wide sum body exists (design_check_sherlock_wide, PASS).
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux both --kring-weight 0.3 --sqm-scale --pair-features --aux-weight 1.0 --epochs 300 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --body-blocks 3 --body-width 128"
until grep -q "=== chain 18 finished\|18 not started" out/E7_rungC_sherlock18_$D.log 2>/dev/null; do sleep 120; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_sherlock_wide_$D.txt || { echo "=== chain 19 not started: no wide-body PASS $(date)"; exit 1; }
echo "=== chain 19 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_carried_wide_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== chain 19 (wide, 175) done $(date)" || echo "=== CHAIN 19 FAILED $(date)"
echo "=== chain 19 finished $(date)"
