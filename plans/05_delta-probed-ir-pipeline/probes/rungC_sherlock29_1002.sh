#!/usr/bin/env bash
# Chain 29, 2 Oct 2026 (coverage ablation, part two; amendment 22:0x): which part of the 130 carries the coverage effect — the 7 pyrenes (four rings) or the
# 123 three-ring children? Arm "ring4": pool without the pyrenes (743); arm "ring3": pool without the three-ring molecules (627). Carried recipe, three seeds.
set -uo pipefail
# no-set-e: every arm records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
ARM=${1:?ring4|ring3}
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_2026-10-01.txt || { echo "=== chain 29 $ARM not started: no sum-body PASS $(date)"; exit 1; }
F=out/pool_ring4_ids_2026-10-02.txt; [ "$ARM" = ring3 ] && F=out/pool_ring3only_ids_2026-10-02.txt
echo "=== chain 29 $ARM start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_coverage_no${ARM}_2026-10-02 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  --exclude-ids-file "$F" && echo "=== chain 29 $ARM done $(date)" || echo "=== CHAIN 29 $ARM FAILED $(date)"
echo "=== chain 29 $ARM finished $(date)"
