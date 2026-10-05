#!/usr/bin/env bash
# night_1005b.sh (5 Oct 2026, 16:2x). Replaces night_1005.sh after the WSL incident of 15:09: the TZ anchor's python died (the memory of three WSL jobs —
# TZ 10 GB, MP2 pricing 6 GB and the afternoon queue's LNO cell (b), which my pre-emption had not stopped — exceeded the VM's 20 GB), its wsl session
# ended, and with no session attached the WSL VM shut down at 15:10 (Hyper-V port removed 15:11:10), taking the MP2 pricing with it. Three rules in this
# script: (1) a keepalive session holds the VM for the whole night; (2) the WSL jobs' max_memory values sum to ≤ 14 GB at any time (TZ 10 + MP2 4; LNO 6
# only after the TZ anchor); (3) nothing of the afternoon queue is left to pre-empt (it is gone). Sequence:
#   (K)  keepalive: `wsl -e sleep infinity`, detached, for as long as this script runs;
#   (N1) the TZ anchor resumes (coordinates 0 and 1 are on disk; 19 remains), then the reference's two-route check, then the assembly — 8 threads;
#   (S0) the MP2 pricing's second half (`probes/mp2_price_step0b_1005.sh`, 2 threads, 4 GB) beside it, now;
#   (N2) LNO cells (a) and (b) at 8 threads, 6 GB, after the TZ anchor is assembled (not beside it);
#   module 06's re-execution (`probes/rerun_m06_notebook_1005.sh`) runs on the Windows side already.
# Markers to the afternoon log. Git Bash, detached:
#   nohup bash probes/night_1005b.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: every step records its own marker; the steps are independent except for the memory order
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
ENV='export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp; mkdir -p $HOME/qc_tmp'
TZ=$PW/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03
GEO=$PW/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json
BASE="OMP_NUM_THREADS=8 ~/qc05/bin/python e8_cc_hessian_fd.py $GEO $TZ --threads 8 --basis cc-pvtz --symmetry --two-route-check separate --fast-t-density --fast-t-lambda --max-memory 10000"
t() { date '+%F %T'; }
wsl -e sleep infinity < /dev/null > /dev/null 2>&1 &
KEEP=$!
echo "=== night b: armed; keepalive wsl session pid $KEEP; TZ resumes now, MP2 pricing beside it, LNO after the anchor $(t)"

( echo "=== (S0) MP2 pricing second half start (2 threads, 4 GB) $(t)"
  wsl -e bash -c "$ENV; cd $PW && sed -i 's/--max-memory 6000/--max-memory 4000/' probes/mp2_price_step0b_1005.sh && bash probes/mp2_price_step0b_1005.sh" >> "$P/probes/results_m1/mp2_step0_2026-10-05.log" 2>&1 \
    && echo "=== (S0) MP2 pricing second half done $(t)" || echo "=== (S0) MP2 PRICING SECOND HALF FAILED $(t)" ) &

echo "=== (N1b) TZ benzene full anchor: resume (coordinate 19), 8 threads $(t)"
wsl -e bash -c "$ENV; cd $PW/probes && $BASE --ks 0,1,4" >> "$P/probes/results_m1/tz_full_remaining_2026-10-04.log" 2>&1 \
  && echo "=== (N1b) TZ remaining displacements done $(t)" || { echo "=== (N1b) TZ REMAINING DISPLACEMENTS FAILED $(t)"; kill $KEEP 2>/dev/null; exit 1; }
wsl -e bash -c "$ENV; cd $PW/probes && ${BASE/--two-route-check separate/--two-route-check only}" > "$P/probes/results_m1/tz_full_tworoute_2026-10-04.log" 2>&1 \
  && echo "=== (N1b) TZ reference two-route check done $(t)" || { echo "=== (N1b) TZ TWO-ROUTE CHECK FAILED $(t)"; kill $KEEP 2>/dev/null; exit 1; }
wsl -e bash -c "$ENV; cd $PW/probes && $BASE" > "$P/probes/results_m1/tz_full_assemble_2026-10-04.log" 2>&1 \
  && echo "=== (N1) TZ FULL ANCHOR DONE — hessian_ccsd_t.npz in $TZ $(t)" || { echo "=== (N1) TZ ASSEMBLY FAILED $(t)"; kill $KEEP 2>/dev/null; exit 1; }

wait %1 2>/dev/null
echo "=== (N2) LNO follow-up cells start (8 threads, 6 GB, after the anchor) $(t)"
ANCHOR=$PW/probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02
GEOM=$PW/modules/05_support_predictor/corpus/molecules/A_01f3186607/geometry.json
wsl -e bash -c "$ENV; cd $PW && OMP_NUM_THREADS=8 ~/qc05/bin/python probes/lno_curvature_check.py $ANCHOR $GEOM --max-k 2 --threads 8 --max-memory 6000 --xtight --out $PW/probes/results_m1/lno_curvature_xtight_2026-10-05.json" > "$P/probes/results_m1/lno_curvature_xtight_2026-10-05.log" 2>&1 \
  && echo "=== (N2) LNO cell (a) xtight done $(t)" || echo "=== (N2) LNO CELL (a) FAILED $(t)"
wsl -e bash -c "$ENV; cd $PW && OMP_NUM_THREADS=8 ~/qc05/bin/python probes/lno_curvature_check.py $ANCHOR $GEOM --max-k 2 --threads 8 --max-memory 6000 --reuse-localisation --out $PW/probes/results_m1/lno_curvature_reuse_2026-10-05.json" > "$P/probes/results_m1/lno_curvature_reuse_2026-10-05.log" 2>&1 \
  && echo "=== (N2) LNO cell (b) reuse done $(t)" || echo "=== (N2) LNO CELL (b) FAILED $(t)"
kill $KEEP 2>/dev/null
echo "=== night b finished $(t)"
