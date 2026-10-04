#!/usr/bin/env bash
# rungC_chain34c_1004.sh (4 Oct 2026, 08:3x). Chain 34c: the family-balanced K-diagonal term with the 'other' family split at 700 cm⁻¹
# (`--kdiag-mode family-low`, weight 0.1), everything else chain 34's recipe (750, seeds 0-2, models saved). Registered 08:3x (rung C
# pre-registration, amendment 4 Oct 08:3x) after the low-mode read of 08:2x. Smoke first (5 molecules, 2 epochs; the marker gates the run, rule of
# 14 Sep), then the chain at 8 threads: the TZ benzene run holds the other 8 (lanes × threads = 16).
set -uo pipefail
# no-set-e: the marker lines record the outcome
M=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
cd "$M" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --kdiag-mode family-low --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --save-model"
echo "=== chain 34c smoke start $(t)"
if python m05/rungC_train.py corpus/molecules out/smoke_kdiag_family_low_2026-10-04 --use-analytic --pool-layers A,A2,B --smoke --threads 2 --aggregation sum $REC > out/smoke_kdiag_family_low_2026-10-04.log 2>&1; then
  echo "smoke ok $(t)" > out/smoke_kdiag_family_low_2026-10-04.marker
  echo "=== chain 34c smoke ok $(t)"
else
  echo "=== CHAIN 34C SMOKE FAILED $(t) — see out/smoke_kdiag_family_low_2026-10-04.log"; exit 1
fi
if grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_2026-10-01.txt && grep -q "smoke ok" out/smoke_kdiag_family_low_2026-10-04.marker; then
  echo "=== chain 34c: kdiag family-low, weight 0.1, 750, 8 threads start $(t)"
  python m05/rungC_train.py corpus/molecules out/E7_rungC_chain34c_kdfamilylow_750_2026-10-04 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
    && echo "=== chain 34c done $(t)" || echo "=== CHAIN 34C FAILED $(t)"
else
  echo "=== chain 34c not started: design-check PASS or smoke marker missing $(t)"
fi
echo "=== chain 34c finished $(t)"
