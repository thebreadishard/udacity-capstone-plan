#!/usr/bin/env bash
# Sherlock chain 17, 1 Oct 2026 (amendment 19:5x): pattern f, projected target, pattern + 0.3 × kring terms, hybrid head, carried recipe — the full pool
# (A + A2 + B, 750), seeds 0–2, 200 epochs. Lane B, at once (the pretraining cells follow it).
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux both --kring-weight 0.3 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 17 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 17 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever3b_fproj_kw0.3_750_$D --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== chain 17 (750) done $(date)" || echo "=== CHAIN 17 FAILED $(date)"
echo "=== chain 17 finished $(date)"
