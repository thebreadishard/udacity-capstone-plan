#!/usr/bin/env bash
# Sherlock chain 20, 2 Oct 2026 (amendment 01:5x): composition control — the carried recipe at 175 molecules drawn from the mixed pool (A + A2 + B) instead
# of A + A2 only; seeds 0–2. Lane B, after chain 19.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux both --kring-weight 0.3 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
until grep -q "=== chain 19 finished\|19 not started" out/E7_rungC_sherlock19_$D.log 2>/dev/null; do sleep 120; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 20 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 20 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_carried_mixed175_$D --use-analytic --pool-layers A,A2,B --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== chain 20 (mixed 175) done $(date)" || echo "=== CHAIN 20 FAILED $(date)"
echo "=== chain 20 finished $(date)"
