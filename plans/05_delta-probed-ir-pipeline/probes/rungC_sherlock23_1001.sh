#!/usr/bin/env bash
# Sherlock chain 23, 2 Oct 2026 (amendment 05:3x): the carried recipe with the K-diagonal term at 750 — pattern f, projected target, pattern + 0.3 × kring
# + KD × K-diagonal, pool A + A2 + B, seeds 0–2, 200 epochs. Lane B, after chain 22. KD is read from kd_weight.txt next to this script if present (set
# before the start from the 0.3 cell's read, recorded in the registration), else 0.1.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
HERE=$(cd "$(dirname "$0")" && pwd)
until grep -q "=== chain 22 finished\|22 not started" out/E7_rungC_sherlock22_$D.log 2>/dev/null; do sleep 120; done
KD=0.1; [ -f "$HERE/kd_weight.txt" ] && KD=$(cat "$HERE/kd_weight.txt")
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight $KD --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 23 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 23 start (kdiag weight $KD) $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_carried_kd_750_$D --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== chain 23 (750) done $(date)" || echo "=== CHAIN 23 FAILED $(date)"
echo "=== chain 23 finished $(date)"
