#!/usr/bin/env bash
# Re-queued 13:2x as chain 5b: second lane after chain 11, on the ridge target.
# Sherlock chain 5, 1 Oct 2026 (lever 2b, amendment 08:0x + 08:4x): the 20-epoch QM9-pretrained mean body (lr 3e-4) under the hybrid head, pattern d,
# 175, seeds 0–2 — the same cell as lever 2a (ii) with the converged body. Waits for chain 4 and for the checkpoint; design-check gate on the checkpoint.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
PRE=out/rungC_pretrained_mean_long_$D.pt
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d --aux-target ls --ls-lam 1e-3"   # re-read on the ridge target (amendment 09:4x)
until grep -q "=== chain 11 finished" out/E7_rungC_sherlock11_$D.log 2>/dev/null; do sleep 120; done   # re-queued 13:2x: second lane, after chain 11
until grep -q "^wrote .*rungC_pretrained_mean_long" out/rungC_pretrained_mean_long_$D.log 2>/dev/null; do
  grep -q "Traceback" out/rungC_pretrained_mean_long_$D.log 2>/dev/null && { echo "=== chain 5 not started: the pretraining aborted $(date)"; exit 1; }
  sleep 300
done
[ -f "$PRE" ] || { echo "=== chain 5 not started: no checkpoint $PRE $(date)"; exit 1; }
python m05/design_check.py corpus/molecules --out out/design_check_sherlock_prelong_$D --aggregation mean --checkpoint $PRE --as-finetune > out/design_check_sherlock_prelong_$D.txt 2>&1 \
  && grep -q "verdict: \*\*PASS\*\*" out/design_check_sherlock_prelong_$D.txt || { echo "=== DESIGN CHECK (pretrained long) FAILED — chain 5 not started $(date)"; exit 1; }
echo "=== chain 5 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever2b_pretrained_long_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation mean --pretrained $PRE $REC \
  && echo "=== lever 2b pretrained long (175) done $(date)" || echo "=== LEVER 2B FAILED $(date)"
echo "=== chain 5b finished $(date)"
