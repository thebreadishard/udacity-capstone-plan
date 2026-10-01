#!/usr/bin/env bash
# Sherlock chain 3, 1 Oct 2026 (amendment 08:1x, lever 3 / H8): the auxiliary term on the read-out quantity itself (`--aux kring`, the ring-mode block
# of K) under the hybrid head, pattern d, sum body, 175, seeds 0–2 — beside the pattern-term record of lever 1. Queued behind chain 2.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
until grep -q "=== chain 7 finished\|not started" out/E7_rungC_sherlock7_$D.log 2>/dev/null; do sleep 60; done   # re-queued 09:3x behind lever 4
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 3 not started: no sum-body PASS from lever 1 $(date)"; exit 1; }
echo "=== chain 3 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever3_kring_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum \
  --head hybrid --aux kring --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d \
  && echo "=== lever 3 kring (175) done $(date)" || echo "=== LEVER 3 KRING FAILED $(date)"
echo "=== chain 3 finished $(date)"
