#!/usr/bin/env bash
# night_1005.sh (5 Oct 2026, 05:5x). Replaces probes/night_1004.sh before any of its steps had started: step 3 ran slower than planned (the eighth
# molecule, 26 atoms, 1.5 h per functional), so waiting for the notebooks before the TZ anchor would have cost two more hours. Now:
#   (N1) the full benzene CCSD(T)/cc-pVTZ anchor starts as soon as chain 34 step 3 has released its 12 threads ("(B) chain 34 step 3 done"):
#        (i) the three remaining symmetry-unique displacements (positions 0,1,4 = coordinates 0,1,19), (ii) the reference's two-route check
#        (`--two-route-check only`), (iii) the assembly — 8 threads, ≈ 12 h; beside it the step-3 read (2) and the notebooks (2), then the ten-fold
#        batch route (4): 16 lanes at most;
#   (N0) when the afternoon queue starts its LNO step at 12 threads ("(D) LNO follow-up cells start"), that step is pre-empted (WSL python and the
#        afternoon script stopped; its notebooks are done by then);
#   (N2) LNO cells (a) and (b) at 8 threads once the ten-fold batch route has ended ("(E) batch route 10x done|FAILED").
# Markers to the afternoon log. Git Bash, detached:
#   nohup bash probes/night_1005.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: every step records its own marker; the TZ anchor and the LNO cells are independent of each other
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LOG=$P/probes/results_m1/afternoon_2026-10-04.log
ENV='export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp; mkdir -p $HOME/qc_tmp'
TZ=$PW/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03
GEO=$PW/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json
BASE="OMP_NUM_THREADS=8 ~/qc05/bin/python e8_cc_hessian_fd.py $GEO $TZ --threads 8 --basis cc-pvtz --symmetry --two-route-check separate --fast-t-density --fast-t-lambda --max-memory 10000"
t() { date '+%F %T'; }
echo "=== night (5 Oct): armed; the TZ anchor starts when step 3 is done $(t)"

( until grep -qE "\(B\) chain 34 step 3 done|\(B\) CHAIN 34 STEP 3 FAILED" "$LOG"; do sleep 120; done
  echo "=== (N1) TZ benzene full anchor: remaining displacements start (8 threads) $(t)"
  wsl -e bash -c "$ENV; cd $PW/probes && $BASE --ks 0,1,4" > "$P/probes/results_m1/tz_full_remaining_2026-10-04.log" 2>&1 \
    && echo "=== (N1) TZ remaining displacements done $(t)" || { echo "=== (N1) TZ REMAINING DISPLACEMENTS FAILED $(t)"; exit 1; }
  wsl -e bash -c "$ENV; cd $PW/probes && ${BASE/--two-route-check separate/--two-route-check only}" > "$P/probes/results_m1/tz_full_tworoute_2026-10-04.log" 2>&1 \
    && echo "=== (N1) TZ reference two-route check done $(t)" || { echo "=== (N1) TZ TWO-ROUTE CHECK FAILED $(t)"; exit 1; }
  wsl -e bash -c "$ENV; cd $PW/probes && $BASE" > "$P/probes/results_m1/tz_full_assemble_2026-10-04.log" 2>&1 \
    && echo "=== (N1) TZ FULL ANCHOR DONE — hessian_ccsd_t.npz in $TZ $(t)" || echo "=== (N1) TZ ASSEMBLY FAILED $(t)" ) &

( until grep -q "(D) LNO follow-up cells start" "$LOG"; do sleep 60; done
  sleep 30
  wsl -e bash -c "pkill -f 'lno_curvature_chec[k]'"; ps -ef | awk '/afternoon_100[4]\.sh/ {print $2}' | xargs -r kill 2>/dev/null
  echo "=== (N0) afternoon queue's LNO step pre-empted $(t)" ) &

until grep -qE "\(E\) batch route 10x done|\(E\) BATCH ROUTE 10x FAILED" "$LOG"; do sleep 300; done
until grep -q "(N0) afternoon queue's LNO step pre-empted" "$LOG"; do sleep 60; done
echo "=== (N2) LNO follow-up cells start (8 threads) $(t)"
ANCHOR=$PW/probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02
GEOM=$PW/modules/05_support_predictor/corpus/molecules/A_01f3186607/geometry.json
wsl -e bash -c "$ENV; cd $PW && OMP_NUM_THREADS=8 ~/qc05/bin/python probes/lno_curvature_check.py $ANCHOR $GEOM --max-k 2 --threads 8 --max-memory 6000 --xtight --out $PW/probes/results_m1/lno_curvature_xtight_2026-10-04.json" > "$P/probes/results_m1/lno_curvature_xtight_2026-10-04.log" 2>&1 \
  && echo "=== (N2) LNO cell (a) xtight done $(t)" || echo "=== (N2) LNO CELL (a) FAILED $(t)"
wsl -e bash -c "$ENV; cd $PW && OMP_NUM_THREADS=8 ~/qc05/bin/python probes/lno_curvature_check.py $ANCHOR $GEOM --max-k 2 --threads 8 --max-memory 6000 --reuse-localisation --out $PW/probes/results_m1/lno_curvature_reuse_2026-10-04.json" > "$P/probes/results_m1/lno_curvature_reuse_2026-10-04.log" 2>&1 \
  && echo "=== (N2) LNO cell (b) reuse done $(t)" || echo "=== (N2) LNO CELL (b) FAILED $(t)"
wait
echo "=== night queue finished $(t)"
