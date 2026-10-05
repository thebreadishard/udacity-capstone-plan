#!/usr/bin/env bash
# read_test2_after_anchor_1005.sh (5 Oct 2026, 19:4x). Composite test 2's registered read, run automatically when the night queue reports the benzene
# cc-pVTZ anchor assembled ("(N1) TZ FULL ANCHOR DONE"): `probes/cc_composite_full_check.py read` with the DZ anchor of 3 Oct, the TZ anchor, benzene's
# corpus record and the MP2 rows of both bases (16:54–18:16 on 4 Oct). Output modules/05_support_predictor/out/composite_test2_benzene_2026-10-06.{md,json};
# the markers go to the afternoon log. Nothing else runs here. Git Bash, detached:
#   nohup bash probes/read_test2_after_anchor_1005.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: the read records its own marker
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LOG=$P/probes/results_m1/afternoon_2026-10-04.log
export PYTHONUTF8=1
t() { date '+%F %T'; }
until grep -qE "\(N1\) TZ FULL ANCHOR DONE|\(N1\) TZ ASSEMBLY FAILED|\(N1b\) TZ (REMAINING DISPLACEMENTS|TWO-ROUTE CHECK) FAILED" "$LOG"; do sleep 300; done
if ! grep -q "(N1) TZ FULL ANCHOR DONE" "$LOG"; then echo "=== (T2) test 2 read skipped: the TZ anchor did not assemble $(t)"; exit 1; fi
cd "$P" || exit 1
if python probes/cc_composite_full_check.py read probes/results_m1/e8_benzene_ccpvdz_dip_2026-10-03 probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03 A_8448043181 \
     probes/results_m1/composite_mp2_rows_benzene_ccpvdz_2026-10-04.npz probes/results_m1/composite_mp2_rows_benzene_ccpvtz_2026-10-04.npz \
     modules/05_support_predictor/out/composite_test2_benzene_2026-10-06 > modules/05_support_predictor/out/composite_test2_benzene_2026-10-06.log 2>&1; then
  echo "=== (T2) test 2 read done — modules/05_support_predictor/out/composite_test2_benzene_2026-10-06.md $(t)"
else
  echo "=== (T2) TEST 2 READ FAILED — see modules/05_support_predictor/out/composite_test2_benzene_2026-10-06.log $(t)"
fi
