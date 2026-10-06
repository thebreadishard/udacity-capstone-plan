#!/usr/bin/env bash
# morning_1006.sh (6 Oct 2026, 06:2x). Relaunch of the night queue's remaining steps after the WSL VM powered off at 20:45 on 5 Oct: the desktop app's
# restart killed the Git Bash queue (night_1005b.sh) and with it the keepalive session, so the TZ two-route check, the MP2 pricing of the vinyl variant
# and the armed test-2 read died (journalctl boot -2: clean poweroff, no OOM). This script runs INSIDE WSL (setsid nohup), so only the VM's lifetime
# matters, and the VM is held by the scheduled task CapstoneWSLKeepalive (wsl.exe -e sleep infinity under the Task Scheduler, outside the app's tree).
# Steps: (S0) MP2 pricing of the vinyl variant A2_02c8833bd5 (2 threads, 4 GB) beside (N1b) the benzene cc-pVTZ reference two-route check (8 threads,
# 10 GB) → (N1) assembly → (N2) LNO cells (a) xtight and (b) reuse (8 threads, 6 GB). Memory: 10 + 4 ≤ 14 GB, then 6 + 4. Test 2's read
# (probes/cc_composite_full_check.py read) is run by hand when "(N1) TZ FULL ANCHOR DONE" appears in the afternoon log.
# Launch (Git Bash, from the plan directory):
#   wsl -e bash -c "setsid nohup bash /mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/morning_1006.sh \
#     >> /mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/results_m1/afternoon_2026-10-04.log 2>&1 < /dev/null &"
set -uo pipefail
# no-set-e: each step writes its own marker; a failed step stops what depends on it
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp
mkdir -p "$HOME/qc_tmp"
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
R=$PW/probes/results_m1
TZ=$R/e8_benzene_ccpvtz_oop_2026-10-03
GEO=$PW/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json
PY=$HOME/qc05/bin/python
BASE="$PY e8_cc_hessian_fd.py $GEO $TZ --threads 8 --basis cc-pvtz --symmetry --fast-t-density --fast-t-lambda --max-memory 10000"
t() { date '+%F %T'; }
echo "=== morning 1006: armed inside WSL (pid $$); MP2 vinyl pricing beside the TZ two-route check, then assembly, LNO after $(t)"

( echo "=== (S0) MP2 pricing vinyl variant start (2 threads, 4 GB) $(t)"
  bash "$PW/probes/mp2_price_step0b_1005.sh" A2_02c8833bd5 >> "$R/mp2_step0_2026-10-05.log" 2>&1 \
    && echo "=== (S0) MP2 pricing second half done $(t)" || echo "=== (S0) MP2 PRICING SECOND HALF FAILED $(t)" ) &
MP2=$!

cd "$PW/probes" || exit 1
echo "=== (N1b) TZ reference two-route check start (8 threads, 10 GB) $(t)"
OMP_NUM_THREADS=8 $BASE --two-route-check only > "$R/tz_full_tworoute_2026-10-04.log" 2>&1 \
  && echo "=== (N1b) TZ reference two-route check done $(t)" || { echo "=== (N1b) TZ TWO-ROUTE CHECK FAILED $(t)"; wait "$MP2"; exit 1; }
OMP_NUM_THREADS=8 $BASE --two-route-check separate > "$R/tz_full_assemble_2026-10-04.log" 2>&1 \
  && echo "=== (N1) TZ FULL ANCHOR DONE — hessian_ccsd_t.npz in $TZ $(t)" || { echo "=== (N1) TZ ASSEMBLY FAILED $(t)"; wait "$MP2"; exit 1; }

echo "=== (N2) LNO follow-up cells start (8 threads, 6 GB, after the anchor) $(t)"
ANCHOR=$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02
GEOM=$PW/modules/05_support_predictor/corpus/molecules/A_01f3186607/geometry.json
cd "$PW" || exit 1
OMP_NUM_THREADS=8 $PY probes/lno_curvature_check.py "$ANCHOR" "$GEOM" --max-k 2 --threads 8 --max-memory 6000 --xtight \
  --out "$R/lno_curvature_xtight_2026-10-05.json" > "$R/lno_curvature_xtight_2026-10-05.log" 2>&1 \
  && echo "=== (N2) LNO cell (a) xtight done $(t)" || echo "=== (N2) LNO CELL (a) FAILED $(t)"
OMP_NUM_THREADS=8 $PY probes/lno_curvature_check.py "$ANCHOR" "$GEOM" --max-k 2 --threads 8 --max-memory 6000 --reuse-localisation \
  --out "$R/lno_curvature_reuse_2026-10-05.json" > "$R/lno_curvature_reuse_2026-10-05.log" 2>&1 \
  && echo "=== (N2) LNO cell (b) reuse done $(t)" || echo "=== (N2) LNO CELL (b) FAILED $(t)"
wait "$MP2" 2>/dev/null
echo "=== morning 1006 finished $(t)"
