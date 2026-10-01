#!/usr/bin/env bash
# Sherlock chain 6, 1 Oct 2026 (amendment 09:1x): the middle point of the pattern-d learning curve — 449 molecules of A + A2 + B, carried recipe,
# seeds 0–2 — so that 175 / 449 / 750 give the three points T2 needs. Queued behind chain 4 (chain 5 waits for the pretraining checkpoint beside it).
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d"
until grep -q "=== chain 4 finished" out/E7_rungC_sherlock4_$D.log 2>/dev/null; do sleep 120; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 6 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 6 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever1_d_449_$D --use-analytic --pool-layers A,A2,B --sizes 449 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== pattern d (449) done $(date)" || echo "=== PATTERN D 449 FAILED $(date)"
echo "=== chain 6 finished $(date)"
