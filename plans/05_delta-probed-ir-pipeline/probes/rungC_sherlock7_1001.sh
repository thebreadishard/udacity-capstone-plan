#!/usr/bin/env bash
# Sherlock chain 7b, 1 Oct 2026 (lever 4 at 175, amendment 09:4x + 12:1x): the ridge-anchored LS pattern target (λ_rel 1e-3) under the hybrid head,
# pattern d, carried recipe, sum body — 175 (A + A2), seeds 0–2. Replaces chain 7 (stopped 11:5x: the plain LS target exploded).
# Waits for the λ cache (copied from the server; the local marker file is written by the copy waiter).
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d --aux-target ls --ls-lam 1e-3"
until [ -f out/ls_targets/d_lam0.001/COPIED_AA2 ]; do sleep 60; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 7b not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 7b start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever4_ls_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== lever 4 LS target (175) done $(date)" || echo "=== LEVER 4 175 FAILED $(date)"
echo "=== chain 7 finished $(date)"
