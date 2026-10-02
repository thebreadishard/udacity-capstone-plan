#!/usr/bin/env bash
# Chain 30, 3 Oct 2026 (coverage curve of a scaffold family; amendment 01:1x): how many three-ring children does the pool need? Arm "keep25": the pool with
# only 31 of its 123 three-ring molecules (the rest excluded, 658); arm "keep50": 62 kept (689). Carried recipe, three seeds. Compared with no-ring3 (0 kept)
# and the control (all 123).
set -uo pipefail
# no-set-e: every arm records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
ARM=${1:?keep25|keep50}
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_2026-10-01.txt || { echo "=== chain 30 $ARM not started: no sum-body PASS $(date)"; exit 1; }
F=out/pool_ring3_drop_for_${ARM}_2026-10-03.txt
echo "=== chain 30 $ARM start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_coverage_ring3${ARM}_2026-10-03 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  --exclude-ids-file "$F" && echo "=== chain 30 $ARM done $(date)" || echo "=== CHAIN 30 $ARM FAILED $(date)"
echo "=== chain 30 $ARM finished $(date)"
