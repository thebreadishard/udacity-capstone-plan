#!/usr/bin/env bash
# Chain 16 (18:1x): the carried recipe (pattern f, projected target) at 750, right after chain 10.
# Promoted 15:0x (chain 9b read: pattern f + ridge works at 175, 0.33): starts at once; the lambda cells (12) and 8b follow.
# Re-queued 12:3x as chain 8b behind chain 9b (its 12:19 start failed on the exploded cache files).
# Sherlock chain 10, 1 Oct 2026 (lever 1b at 750, amendment 12:4x): pattern f with the ridge target, hybrid head, carried recipe, pool A + A2 + B, seeds 0–2.
# Waits for chain 7 (the 175 read) and for the layer-B target cache (the local build log ends with the median line once every file is in).
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
until grep -q "=== chain 10 finished\|10 not started" out/E7_rungC_sherlock10_$D.log 2>/dev/null; do sleep 60; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 8 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 16 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever1b_f_proj_750_$D --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== pattern f + projected target (750) done $(date)" || echo "=== CHAIN 16 FAILED $(date)"
echo "=== chain 16 finished $(date)"
