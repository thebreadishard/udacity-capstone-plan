#!/usr/bin/env bash
# rungC_chain34b_1004.sh (4 Oct 2026, 03:1x). Chain 34's registered follow-up (rung C pre-registration, amendment 3 Oct 11:1x, line '3 < other ≤ 3.6'):
# the family-balanced K-diagonal term at weight 0.3 instead of 0.1, everything else chain 34's recipe (750, seeds 0-2, models saved). 6 threads: the
# TZ benzene run holds 8 and the module-05 notebook rebuild 2 (lanes × threads = 16). Registered before it runs (outcome section of 4 Oct 03:1x).
set -uo pipefail
# no-set-e: the marker lines record the outcome
M=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
cd "$M" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
echo "=== chain 34b: kdiag family, weight 0.3, 750, 6 threads start $(t)"
if grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_2026-10-01.txt && grep -q "smoke ok" out/smoke_kdiag_family_2026-10-03.marker; then
  REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.3 --kdiag-mode family --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --save-model"
  python m05/rungC_train.py corpus/molecules out/E7_rungC_chain34b_kdfamily_w03_750_2026-10-04 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 6 --aggregation sum $REC \
    && echo "=== chain 34b done $(t)" || echo "=== CHAIN 34B FAILED $(t)"
else
  echo "=== chain 34b not started: design-check PASS or smoke marker missing $(t)"
fi
echo "=== chain 34b finished $(t)"
