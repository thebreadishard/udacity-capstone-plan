#!/usr/bin/env bash
# Chain 31, 3 Oct 2026 (cross-family coverage; amendment 04:1x): does a three-ring parent stay covered by the OTHER three-ring families when its own children
# leave the pool? Arm "phen": the 12 phenanthrene children excluded (read phenanthrene); arm "phenanthridine": the 34 phenanthridine children excluded (read
# phenanthridine). Carried recipe, three seeds.
set -uo pipefail
# no-set-e: every arm records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
ARM=${1:?phen|phenanthridine}
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_2026-10-01.txt || { echo "=== chain 31 $ARM not started: no sum-body PASS $(date)"; exit 1; }
F=out/pool_${ARM}_children_ids_2026-10-03.txt
echo "=== chain 31 $ARM start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_coverage_no${ARM}children_2026-10-03 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  --exclude-ids-file "$F" && echo "=== chain 31 $ARM done $(date)" || echo "=== CHAIN 31 $ARM FAILED $(date)"
echo "=== chain 31 $ARM finished $(date)"
