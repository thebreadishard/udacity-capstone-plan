#!/usr/bin/env bash
# tz_relaunch_1004.sh (4 Oct 2026, 00:5x). The TZ benzene out-of-plane run of night2_1003.sh, relaunched alone after the out-of-core fix of the (T)
# two-particle density (software ledger row 35); same arguments as night2's TZ line, 8 threads, PYSCF_TMPDIR in the WSL home. The first manual
# relaunch of 00:56 failed in 4 s because `$HOME` inside a doubly nested `bash -c` was expanded on the Windows side (/c/Users/thebr/qc_tmp does not
# exist in WSL); here the environment line is single-quoted exactly as in night2. Markers go to the night2 log; the run's own output appends to run.log.
set -uo pipefail
# no-set-e: the marker lines record the outcome either way
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
OUT=$P/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03
N2=$P/probes/results_m1/night2_2026-10-03.log
ENV='export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp; mkdir -p $HOME/qc_tmp'
t() { date '+%F %T'; }
echo "=== TZ relaunch 3 (out-of-core (T) density, tz_relaunch_1004.sh) start $(t)" >> "$N2"
wsl -e bash -c "$ENV; cd $PW/probes && OMP_NUM_THREADS=8 ~/qc05/bin/python e8_cc_hessian_fd.py $PW/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json $PW/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03 --threads 8 --basis cc-pvtz --symmetry --ks 5,2,3 --two-route-check separate --fast-t-density --fast-t-lambda --max-memory 10000" >> "$OUT/run.log" 2>&1 \
  && echo "=== TZ relaunch 3 done $(t)" >> "$N2" || echo "=== TZ RELAUNCH 3 FAILED $(t)" >> "$N2"
