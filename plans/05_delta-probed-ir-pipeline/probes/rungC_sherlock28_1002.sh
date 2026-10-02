#!/usr/bin/env bash
# Chain 28, 2 Oct 2026 (coverage ablation, amendment 17:2x): the carried recipe on (a) the pool without its 130 three-and-more-ring molecules (620) and
# (b) the first 620 of the full pool as the same-count control; three seeds each. Lane B starts now; lane A after chain 26.
set -uo pipefail
# no-set-e: every arm records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
ARM=${1:?ablation|control}
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_2026-10-01.txt || { echo "=== chain 28 $ARM not started: no sum-body PASS $(date)"; exit 1; }
if [ "$ARM" = control ]; then
  until grep -q "=== chain 26 finished" out/E7_rungC_sherlock26_2026-10-02.log 2>/dev/null; do sleep 120; done
  echo "=== chain 28 control start $(date)"
  python m05/rungC_train.py corpus/molecules out/E7_rungC_coverage_control620_2026-10-02 --use-analytic --pool-layers A,A2,B --sizes 620 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
    && echo "=== chain 28 control done $(date)" || echo "=== CHAIN 28 control FAILED $(date)"
else
  echo "=== chain 28 ablation start $(date)"
  python m05/rungC_train.py corpus/molecules out/E7_rungC_coverage_ablation620_2026-10-02 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
    --exclude-ids-file out/pool_ring3plus_ids_2026-10-02.txt \
    && echo "=== chain 28 ablation done $(date)" || echo "=== CHAIN 28 ablation FAILED $(date)"
fi
echo "=== chain 28 $ARM finished $(date)"
