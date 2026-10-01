#!/usr/bin/env bash
# Re-queued 15:0x behind chain 10.
# Sherlock chain 12, 1 Oct 2026 (amendment 14:1x, after lever 4 at 175 read *hurts*: 0.44 against 0.40 on the projected target): is the ridge target
# learnable at a larger λ or a smaller weight? Three cells at 175, pattern d, hybrid head, carried recipe: λ_rel 1e-1 and 1e-2 at aux weight 1.0, and
# λ_rel 1e-3 at aux weight 0.3. Queued behind chain 9b; the missing λ caches are computed on the fly (seconds per molecule, cached afterwards).
set -uo pipefail
# no-set-e: every cell records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
BASE="--head hybrid --aux pattern --sqm-scale --pair-features --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d --aux-target ls"
until grep -q "=== chain 10 finished\|10 not started" out/E7_rungC_sherlock10_$D.log 2>/dev/null; do sleep 60; done   # re-queued 15:0x behind chain 10
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 12 not started: no sum-body PASS $(date)"; exit 1; }
echo "=== chain 12 start $(date)"
for CELL in "lam1e-1:--ls-lam 1e-1 --aux-weight 1.0" "lam1e-2:--ls-lam 1e-2 --aux-weight 1.0" "w0.3:--ls-lam 1e-3 --aux-weight 0.3"; do
  L=${CELL%%:*}; FLAGS=${CELL#*:}
  python m05/rungC_train.py corpus/molecules out/E7_rungC_lever4_${L}_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $BASE $FLAGS \
    && echo "=== chain 12 cell $L done $(date)" || echo "=== CHAIN 12 CELL $L FAILED $(date)"
done
echo "=== chain 12 finished $(date)"
