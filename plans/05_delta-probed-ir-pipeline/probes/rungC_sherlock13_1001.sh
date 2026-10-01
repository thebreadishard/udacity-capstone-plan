#!/usr/bin/env bash
# Lane B after chain 5b.
# Re-queued 12:3x as chain 9b behind chain 7c (its 12:26 start hit the exploded f cache files; repaired).
# Sherlock chain 13, 1 Oct 2026 (amendment 15:1x): pattern f with the registered projected target — is the ridge needed once the support is wide? Derived from chain 9 (which used the ridge-anchored LS target
# (λ_rel 1e-3), hybrid head, carried recipe, sum body — 175 (A + A2), seeds 0–2. Waits for chain 7 (pattern d, same target) and the pattern-f cache copy.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
until grep -q "=== chain 5b finished\|5 not started" out/E7_rungC_sherlock5_$D.log 2>/dev/null; do sleep 60; done   # lane B, after chain 5b
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 9 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 13 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever1b_f_proj_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== pattern f + projected target (175) done $(date)" || echo "=== CHAIN 13 FAILED $(date)"
echo "=== chain 13 finished $(date)"
