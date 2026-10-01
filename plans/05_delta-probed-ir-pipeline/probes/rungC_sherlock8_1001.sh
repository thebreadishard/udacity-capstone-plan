#!/usr/bin/env bash
# Sherlock chain 8, 1 Oct 2026 (lever 4 at 750, amendment 09:4x): LS pattern target, hybrid head, pattern d, carried recipe, pool A + A2 + B, seeds 0–2.
# Waits for chain 7 (the 175 read) and for the layer-B target cache (the local build log ends with the median line once every file is in).
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d --aux-target ls"
until grep -q "=== chain 7 finished\|not started" out/E7_rungC_sherlock7_$D.log 2>/dev/null; do sleep 60; done
until grep -q "^median residual" out/ls_targets_build_d_B_$D.log 2>/dev/null; do sleep 60; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 8 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 8 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever4_ls_750_$D --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== lever 4 LS target (750) done $(date)" || echo "=== LEVER 4 750 FAILED $(date)"
echo "=== chain 8 finished $(date)"
