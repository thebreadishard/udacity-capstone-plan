#!/usr/bin/env bash
# Sherlock chain 18, 1 Oct 2026 (amendment 22:4x): the carried recipe (pattern f, projected target, pattern + 0.3 × kring) at 449 — the middle point of
# the T2 learning curve beside chain 14b (175) and chain 17 (750). Lane B, after chain 15c.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux both --kring-weight 0.3 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
until grep -q "=== chain 15 finished\|15 not started" out/E7_rungC_sherlock15_$D.log 2>/dev/null; do sleep 120; done   # 15c prints the chain-15 marker
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 18 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 18 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_carried_449_$D --use-analytic --pool-layers A,A2,B --sizes 449 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== chain 18 (449) done $(date)" || echo "=== CHAIN 18 FAILED $(date)"
echo "=== chain 18 finished $(date)"
