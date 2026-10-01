#!/usr/bin/env bash
# Re-queued 12:3x as chain 9b behind chain 7c (its 12:26 start hit the exploded f cache files; repaired).
# Sherlock chain 9, 1 Oct 2026 (lever 1b + 4, amendment 12:2x): pattern f (disjoint pairs up to three bonds apart) with the ridge-anchored LS target
# (λ_rel 1e-3), hybrid head, carried recipe, sum body — 175 (A + A2), seeds 0–2. Waits for chain 7 (pattern d, same target) and the pattern-f cache copy.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --aux-target ls --ls-lam 1e-3"
until grep -q "=== chain 7c finished\|not started" out/E7_rungC_sherlock7_$D.log 2>/dev/null; do sleep 60; done   # re-queued 12:3x behind 7c
until [ -f out/ls_targets/f_lam0.001/COPIED_AA2 ]; do sleep 60; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 9 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 9 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever1b_f_ls_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== pattern f + LS target (175) done $(date)" || echo "=== CHAIN 9 175 FAILED $(date)"
echo "=== chain 9b finished $(date)"
