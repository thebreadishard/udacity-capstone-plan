#!/usr/bin/env bash
# 15c (19:5x): behind chain 17.
# 15b (18:1x): on the projected target (chain 13 read).
# Sherlock chain 15, 1 Oct 2026 (amendment 17:1x): the 20-epoch QM9-pretrained mean body under the hybrid head on the carried recipe — pattern f + ridge
# target — against a fresh mean body on the same recipe; 175, seeds 0–2, 300 epochs (decision 51: chain 5b's best epochs touched the cap of 200).
# Lane B, after chain 14. Design-check gate for the fresh mean body exists (design_check_sherlock_mean); the checkpoint's gate ran for chain 5b.
set -uo pipefail
# no-set-e: every cell records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
PRE=out/rungC_pretrained_mean_long_$D.pt
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 300 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
until grep -q "=== chain 17 finished\|17 not started" out/E7_rungC_sherlock17_$D.log 2>/dev/null; do sleep 120; done   # re-queued 19:5x behind chain 17
grep -q "verdict: \*\*PASS\*\*" out/design_check_sherlock_mean_$D.txt || { echo "=== chain 15 not started: no mean-body PASS $(date)"; exit 1; }
grep -q "verdict: \*\*PASS\*\*" out/design_check_sherlock_prelong_$D.txt || { echo "=== chain 15 not started: no checkpoint PASS $(date)"; exit 1; }
echo "=== chain 15 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever2b_fproj_fresh_mean_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation mean $REC \
  && echo "=== chain 15 fresh mean (f) done $(date)" || echo "=== CHAIN 15 FRESH FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever2b_fproj_pretrained_long_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation mean --pretrained $PRE $REC \
  && echo "=== chain 15 pretrained long (f) done $(date)" || echo "=== CHAIN 15 PRETRAINED FAILED $(date)"
echo "=== chain 15 finished $(date)"
