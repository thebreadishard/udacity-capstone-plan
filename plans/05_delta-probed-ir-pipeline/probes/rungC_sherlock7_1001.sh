#!/usr/bin/env bash
# Sherlock chain 7, 1 Oct 2026 (lever 4, amendment 09:4x): the pattern term's target replaced by the pattern-consistent least-squares ΔF
# (`--aux-target ls`), hybrid head, pattern d, carried recipe, sum body — 175 (A + A2), seeds 0–2. Waits for chain 2 and for the A + A2 target cache.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d --aux-target ls"
until grep -q "=== chain 2 finished\|not started" out/E7_rungC_sherlock2_$D.log 2>/dev/null; do sleep 60; done
until grep -q "^median residual" out/ls_targets_build_d_AA2_$D.log 2>/dev/null; do sleep 60; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 7 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 7 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever4_ls_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== lever 4 LS target (175) done $(date)" || echo "=== LEVER 4 175 FAILED $(date)"
echo "=== chain 7 finished $(date)"
