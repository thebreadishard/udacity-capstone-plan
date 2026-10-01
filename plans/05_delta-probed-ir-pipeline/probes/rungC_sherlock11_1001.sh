#!/usr/bin/env bash
# Sherlock chain 11, 1 Oct 2026 (lever 3b, amendment 13:2x): pattern term on the ridge target + kring term (`--aux both`), hybrid head, pattern d, carried
# recipe, sum body — 175 (A + A2), seeds 0–2. Second lane: starts when the 20-epoch pretraining has written its checkpoint (its six cores are then free).
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux both --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d --aux-target ls --ls-lam 1e-3"
until grep -q "^wrote .*rungC_pretrained_mean_long" out/rungC_pretrained_mean_long_$D.log 2>/dev/null; do
  grep -q "Traceback" out/rungC_pretrained_mean_long_$D.log 2>/dev/null && break     # an aborted pretraining also frees the cores
  sleep 120
done
until [ -f out/ls_targets/d_lam0.001/COPIED_AA2 ]; do sleep 60; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 11 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 11 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever3b_both_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== lever 3b both terms (175) done $(date)" || echo "=== CHAIN 11 FAILED $(date)"
echo "=== chain 11 finished $(date)"
