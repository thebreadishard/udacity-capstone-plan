#!/usr/bin/env bash
# Sherlock chain 22, 2 Oct 2026 (lever 5, amendment 04:2x): the carried recipe (pattern f, projected target, pattern + 0.3 × kring) plus a K-diagonal term over
# all modes at weight 0.1 and 0.3 — 175, seeds 0–2. Lane B, at once.
set -uo pipefail
# no-set-e: every cell records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
BASE="--head hybrid --aux both --kring-weight 0.3 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 22 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 22 start $(date)"
for KD in 0.1 0.3; do
  python m05/rungC_train.py corpus/molecules out/E7_rungC_lever5_kd${KD}_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $BASE --kdiag-weight $KD \
    && echo "=== chain 22 kdiag $KD done $(date)" || echo "=== CHAIN 22 KD $KD FAILED $(date)"
done
echo "=== chain 22 finished $(date)"
