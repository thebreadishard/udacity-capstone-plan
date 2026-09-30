#!/usr/bin/env bash
# Rung C data-scaling test, 30 Sep 2026 (the user: "de volgende stap zonder de PC … bewijs dat compute ertegenaan gooien werkt").
# C1 (from scratch, stage-2 winner flags, sum body) and C2 (QM9 pretraining, element reset) on the A + A2 + B pool at 449 and 750 molecules
# (hashed order of the mixed pool); the 175 points are the 27/28 Sep records. Laptop, 8 threads. SMOKE=1 runs the mechanics only.
set -uo pipefail
# no-set-e: the C2 run must still start when C1 fails; each step reports its own FAILED line to the log
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-09-30
WIN=$(python -c "import json;print(json.load(open('out/E7_rungC_s2_pick_2026-09-27.json'))['flags'])") || exit 1
if [ "${SMOKE:-}" = 1 ]; then
  python m05/rungC_train.py corpus/molecules out/_smoke_rungC_scale --use-analytic --pool-layers A,A2,B --sizes all --seeds 0 --threads 4 --aggregation sum --smoke $WIN \
    && python m05/rungC_train.py corpus/molecules out/_smoke_rungC_scale_c2 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0 --threads 4 --aggregation sum --smoke \
       --pretrained out/rungC_pretrained_2026-09-27.pt --pretrained-elements 1,6,7,8,9 $WIN && echo "=== SMOKE OK" || echo "=== SMOKE FAILED"
  exit 0
fi
echo "=== rung C scaling start $(date) flags: $WIN"
python m05/rungC_train.py corpus/molecules out/E7_rungC_scale_C1_$D --use-analytic --pool-layers A,A2,B --sizes 449,750 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $WIN \
  && echo "=== C1 done $(date)" || echo "=== C1 FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_scale_C2_$D --use-analytic --pool-layers A,A2,B --sizes 449,750 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum \
  --pretrained out/rungC_pretrained_2026-09-27.pt --pretrained-elements 1,6,7,8,9 $WIN \
  && echo "=== C2 done $(date)" || echo "=== C2 FAILED $(date)"
echo "=== rung C scaling finished $(date)"
