#!/usr/bin/env bash
# Rung C search stage H1, 1 Oct 2026 (amendment 03:5x): the hybrid head's own recipe — lr {3e-4,1e-3,3e-3} × width {128,256}, hybrid + SQM + pair
# features, A + A2 (175), seeds 0–2, inner validation 15 %; pick by the inner term with rungC_stage_pick.py.
set -uo pipefail
# no-set-e: every cell must record; the pick runs on whatever landed
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
grep -q "verdict: \*\*PASS\*\*" out/design_check_night4_$D.txt || { echo "=== H1 not started: no design-check PASS from chain 4 $(date)"; exit 1; }
echo "=== search H1 start $(date)"
CELLS=()
for LR in 3e-4 1e-3 3e-3; do
  for W in 128 256; do
    L="lr${LR}_w${W}"
    python m05/rungC_train.py corpus/molecules out/E7_rungC_H1_${L}_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum \
      --head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr $LR --hybrid-hidden $W \
      && echo "=== H1 cell $L done $(date)" || echo "=== H1 CELL $L FAILED $(date)"
    CELLS+=("$L:--lr $LR --hybrid-hidden $W")
  done
done
python m05/rungC_stage_pick.py "out/E7_rungC_H1_{label}_$D" "${CELLS[@]}" 2>&1 | tail -n 12
echo "=== search H1 finished $(date)"
