#!/usr/bin/env bash
# Rung C night chain 3, 1 Oct 2026: rank 3, the hybrid head (registered in the rung-C pre-registration, 23:xx). Waits for night chain 2, then, on the
# fresh sum body (design check of chain 1 covers it; the encoder is the same body), pool A + A2 (175), winner flags, seeds 0–2, inner validation 15 %:
#   (i)   hybrid head + pattern term                              → out/E7_rungC_rank3_hybrid_<D>
#   (ii)  hybrid head + SQM α per class                            → out/E7_rungC_rank3_hybrid_sqm_<D>
#   (iii) hybrid head + rank-2 tensor input in the encoder         → out/E7_rungC_rank3_hybrid_tensor_<D>
set -uo pipefail
# no-set-e: each step reports its own FAILED line so the next variant still records
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
N2=out/E7_rungC_night2_2026-09-30.log
n=0
until grep -q "night chain 2 finished\|NIGHT CHAIN 2 not started\|GATE:\|FAILED — not launched" $N2 2>/dev/null; do n=$((n+1)); [ $n -ge 600 ] && { echo "=== NIGHT CHAIN 3 not started: chain 2 not finished after 10 h $(date)"; exit 1; }; sleep 60; done
grep -q "design check PASS" out/E7_rungC_night_2026-09-30.log || { echo "=== NIGHT CHAIN 3 not started: chain 1 has no design-check PASS $(date)"; exit 1; }
WIN=$(python -c "import json;print(json.load(open('out/E7_rungC_s2_pick_2026-09-27.json'))['flags'])") || exit 1
echo "=== night chain 3 (hybrid head) start $(date) flags: $WIN"
python m05/rungC_train.py corpus/molecules out/E7_rungC_rank3_hybrid_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --head hybrid --aux pattern $WIN \
  && echo "=== rank 3 hybrid done $(date)" || echo "=== RANK 3 HYBRID FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_rank3_hybrid_sqm_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --head hybrid --aux pattern --sqm-scale $WIN \
  && echo "=== rank 3 hybrid + SQM done $(date)" || echo "=== RANK 3 HYBRID SQM FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_rank3_hybrid_tensor_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --head hybrid --aux pattern --tensor-input $WIN \
  && echo "=== rank 3 hybrid + tensor input done $(date)" || echo "=== RANK 3 HYBRID TENSOR FAILED $(date)"
echo "=== night chain 3 finished $(date)"
