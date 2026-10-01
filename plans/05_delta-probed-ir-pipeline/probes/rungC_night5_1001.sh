#!/usr/bin/env bash
# Rung C night chain 5, 1 Oct 2026 (amendment 02:4x): the hybrid + SQM head with rung B's pair features, at A+A2 (175) and A+A2+B (750), 3 seeds.
set -uo pipefail
# no-set-e: the 750 run must record even if the 175 run fails
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
WIN=$(python -c "import json;print(json.load(open('out/E7_rungC_s2_pick_2026-09-27.json'))['flags'])") || exit 1
grep -q "verdict: \*\*PASS\*\*" out/design_check_night4_$D.txt || { echo "=== NIGHT CHAIN 5 not started: no design-check PASS from chain 4 $(date)"; exit 1; }
echo "=== night chain 5 start $(date) flags: $WIN"
python m05/rungC_train.py corpus/molecules out/E7_rungC_hybrid_pf_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --head hybrid --aux pattern --sqm-scale --pair-features $WIN \
  && echo "=== hybrid + pair features (175) done $(date)" || echo "=== HYBRID PF 175 FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_hybrid_pf_750_$D --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --head hybrid --aux pattern --sqm-scale --pair-features $WIN \
  && echo "=== hybrid + pair features (750) done $(date)" || echo "=== HYBRID PF 750 FAILED $(date)"
echo "=== night chain 5 finished $(date)"
