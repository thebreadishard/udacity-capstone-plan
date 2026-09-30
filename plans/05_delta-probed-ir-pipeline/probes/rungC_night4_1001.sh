#!/usr/bin/env bash
# Rung C night chain 4, 1 Oct 2026 (amendment 00:5x): the data-scaling test on the hybrid + SQM head (175 / 449 / 750 of the mixed pool, 3 seeds),
# then the hybrid's zeroed-H_low control at 175 (A,A2). Design-check gate on the fresh sum body first.
set -uo pipefail
# no-set-e: the control must record even if the scaling run fails
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
WIN=$(python -c "import json;print(json.load(open('out/E7_rungC_s2_pick_2026-09-27.json'))['flags'])") || exit 1
python m05/design_check.py corpus/molecules --out out/design_check_night4_$D --aggregation sum > out/design_check_night4_$D.txt 2>&1 \
  && grep -q "verdict: \*\*PASS\*\*" out/design_check_night4_$D.txt || { echo "=== DESIGN CHECK FAILED — chain 4 not started $(date)"; exit 1; }
echo "=== night chain 4 start $(date) flags: $WIN"
python m05/rungC_train.py corpus/molecules out/E7_rungC_hybrid_scale_$D --use-analytic --pool-layers A,A2,B --sizes 175,449,750 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --head hybrid --aux pattern --sqm-scale $WIN \
  && echo "=== hybrid scaling done $(date)" || echo "=== HYBRID SCALING FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_hybrid_zerohlow_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0 --inner-val 0.15 --threads 8 --aggregation sum --head hybrid --aux pattern --sqm-scale --zero-hlow $WIN \
  && echo "=== hybrid zeroed-H_low control done $(date)" || echo "=== HYBRID CONTROL FAILED $(date)"
echo "=== night chain 4 finished $(date)"
