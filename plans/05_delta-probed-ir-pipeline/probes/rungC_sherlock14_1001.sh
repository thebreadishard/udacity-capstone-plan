#!/usr/bin/env bash
# 14b (18:1x): on the projected target (chain 13 read); the ridge run was stopped by pid one minute in.
# Sherlock chain 14, 1 Oct 2026 (amendment 15:5x): kring weight 0.1 and 0.3 inside `--aux both`, pattern f + ridge target, hybrid head, carried recipe,
# 300 epochs — 175 (A + A2), seeds 0–2. Lane B, after chain 13.
set -uo pipefail
# no-set-e: every cell records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
BASE="--head hybrid --aux both --sqm-scale --pair-features --aux-weight 1.0 --epochs 300 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 14 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 14 start $(date)"
for KW in 0.1 0.3; do
  python m05/rungC_train.py corpus/molecules out/E7_rungC_lever3b_fproj_kw${KW}_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $BASE --kring-weight $KW \
    && echo "=== chain 14 kring weight $KW done $(date)" || echo "=== CHAIN 14 KW $KW FAILED $(date)"
done
echo "=== chain 14 finished $(date)"
