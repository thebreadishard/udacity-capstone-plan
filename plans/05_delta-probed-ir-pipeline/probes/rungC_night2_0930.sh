#!/usr/bin/env bash
# Rung C night chain 2, 30 Sep → 1 Oct 2026: rank 1 (rank-2 tensor input of the B3LYP blocks), registered in the rung-C pre-registration (23:5x).
# Waits for night chain 1; gate: diagnostic 2 (overfit benzene) must have reached ratio < 0.1, else the run is refused (the reviewers' rule);
# design check of the tensor-input body; then rank 1 + 2 (tensor input + pattern term) and rank 1 alone, 175 molecules, winner flags, 3 seeds.
set -uo pipefail
# no-set-e: each step reports its own FAILED line so the second run still records when the first fails
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-09-30
N1=out/E7_rungC_night_2026-09-30.log
n=0
until grep -q "night chain finished\|night chain not started\|DESIGN CHECK FAILED" $N1 2>/dev/null; do n=$((n+1)); [ $n -ge 480 ] && { echo "=== NIGHT CHAIN 2 not started: chain 1 not finished after 8 h $(date)"; exit 1; }; sleep 60; done
grep -q "night chain finished" $N1 || { echo "=== NIGHT CHAIN 2 not started: chain 1 did not finish cleanly $(date)"; exit 1; }
OVER=$(python -c "
import json,sys
try:
    r=json.load(open('out/E7_rungC_diag_overfit_benzene_$D.json')); print(r['curve']['1']['per_seed'][0]['a']['coupling_ratio'])
except Exception as e: print('nan')")
python -c "import math,sys; v=float('$OVER'); sys.exit(0 if (not math.isnan(v) and v < 0.1) else 1)" \
  || { echo "=== GATE: diagnostic 2 (overfit benzene) ratio $OVER is not < 0.1 — rank 1 not launched (registered rule) $(date)"; exit 1; }
echo "=== gate passed: overfit-benzene ratio $OVER $(date)"
WIN=$(python -c "import json;print(json.load(open('out/E7_rungC_s2_pick_2026-09-27.json'))['flags'])") || exit 1
python m05/design_check.py corpus/molecules --out out/design_check_night2_$D --aggregation sum --tensor-input > out/design_check_night2_$D.txt 2>&1 \
  && grep -q "verdict: \*\*PASS\*\*" out/design_check_night2_$D.txt || { echo "=== DESIGN CHECK (tensor input) FAILED — not launched $(date)"; exit 1; }
echo "=== rank 1 start $(date) flags: $WIN"
python m05/rungC_train.py corpus/molecules out/E7_rungC_rank12_tensor_pattern_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --tensor-input --aux pattern $WIN \
  && echo "=== rank 1 + 2 done $(date)" || echo "=== RANK 1 + 2 FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_rank1_tensor_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --tensor-input $WIN \
  && echo "=== rank 1 alone done $(date)" || echo "=== RANK 1 ALONE FAILED $(date)"
echo "=== night chain 2 finished $(date)"
