#!/usr/bin/env bash
# night2_1003.sh (3 Oct 2026, 19:3x). The night sequence's TZ step failed at once: pyscf wrote its scratch to WSL's /tmp, a 9.8 GB tmpfs, because the detached
# shell had no PYSCF_TMPDIR (it is exported in .bashrc/.profile, which a detached `bash script` does not read). Re-sequenced evening plan for the laptop
# (16 cores): (A) benzene CCSD(T)/cc-pVTZ out-of-plane pairs (odds lever 2) at 8 threads in WSL with PYSCF_TMPDIR=~/qc_tmp (941 GB free), in parallel
# with (B) chain 34 step 2 (the family-balanced K-diagonal term at 750, 8 threads, Windows python) — 8 + 8 = 16; then (C) chain 34 step 3, the eight
# analytic hold-out (a) Hessians under WSL qc05 at 16 threads (the earlier queue script wrongly called the Windows python for this step), after both.
# Replaces probes/rungC_sherlock34_1003.sh. Markers on stdout; the TZ run's own log in its results directory. Git Bash, detached.
set -uo pipefail
# no-set-e: every step records its own line; the TZ run and chain 34 are independent of each other
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
M=$P/modules/05_support_predictor
OUT=$P/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03
ENV='export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp; mkdir -p $HOME/qc_tmp'
t() { date '+%F %T'; }
rm -rf "$OUT" && mkdir -p "$OUT"
echo "=== night2: TZ benzene oop start (8 threads, WSL, PYSCF_TMPDIR=~/qc_tmp) $(t)"
( wsl -e bash -c "$ENV; cd $PW/probes && OMP_NUM_THREADS=8 ~/qc05/bin/python e8_cc_hessian_fd.py $PW/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json $PW/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03 --threads 8 --basis cc-pvtz --symmetry --ks 5,2,3 --two-route-check separate --fast-t-density --fast-t-lambda --max-memory 10000" > "$OUT/run.log" 2>&1 \
  && echo "=== night2: TZ benzene oop done $(t)" || echo "=== NIGHT2 TZ BENZENE OOP FAILED $(t)" ) &
TZ_PID=$!
sleep 240
if ! kill -0 $TZ_PID 2>/dev/null; then echo "=== NIGHT2: the TZ run ended within 4 min — read $OUT/run.log before anything else $(t)"; grep -vE "Warning|warn" "$OUT/run.log" | tail -3 | cut -c1-200; fi
echo "=== night2: chain 34 step 2 start (8 threads) $(t)"
cd "$M" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
if grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_2026-10-01.txt && grep -q "smoke ok" out/smoke_kdiag_family_2026-10-03.marker; then
  REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --kdiag-mode family --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --save-model"
  python m05/rungC_train.py corpus/molecules out/E7_rungC_chain34_kdfamily_750_2026-10-05 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
    && echo "=== chain 34 (750, family-balanced diagonal term, models saved) done $(t)" || echo "=== CHAIN 34 FAILED $(t)"
else
  echo "=== chain 34 not started: design-check PASS or smoke marker missing $(t)"
fi
echo "=== chain 34 step 2 finished $(t)"
wait $TZ_PID
echo "=== night2: TZ run ended $(t)"
echo "=== chain 34 step 3: analytic hold-out (a) Hessians start (WSL qc05, 16 threads) $(t)"
wsl -e bash -c "$ENV; cd $PW/modules/05_support_predictor && OMP_NUM_THREADS=16 ~/qc05/bin/python corpus/analytic_hessians.py corpus/molecules/A_72b86c2331 corpus/molecules/A_07cadc7923 corpus/molecules/A_fdc27f1bd1 corpus/molecules/A_e72997e726 corpus/molecules/A_bce5bae234 corpus/molecules/A_541c53d1a5 corpus/molecules/A_08dde334d8 corpus/molecules/A_428228e5a5 --threads 16" > "$M/out/chain34_step3_analytic_holdout_a_2026-10-05.log" 2>&1 \
  && echo "=== chain 34 step 3 done $(t)" || echo "=== CHAIN 34 STEP 3 FAILED $(t)"
echo "=== night2 finished $(t)"
