#!/usr/bin/env bash
# afternoon_1004.sh (4 Oct 2026, 11:4x). The laptop's queue for the afternoon and night, after the two morning runs release their threads (16 cores):
#   (A) when chain 34c has finished (its log says "chain 34c finished"): the candidate generator's batch route, steps (a) export and (b) gate
#       (pre-registered 11:3x), 4 threads — TASKS 22;
#   (B) when the TZ run has ended ("TZ relaunch 4 done" in night2_2026-10-03.log): chain 34 step 3, the eight analytic hold-out (a) Hessians under WSL
#       qc05 at 12 threads (the night2 command of 3 Oct, 16 → 12 so that (A) and the notebooks fit beside it); then
#   (C) the notebook re-executions of the lay-reader pass (decision 58 split): 05, 06, standout, 07, 08 at 2 threads, sequential, each with its
#       summary rebuilt where the module has one; then
#   (D) the LNO follow-up cells on naphthalene (registered 3 Oct 23:3x): (a) --xtight, then (b) --reuse-localisation, 12 threads, through the night.
# Markers on stdout (the log this script is started with); every step records its own line. Git Bash, detached:
#   nohup bash probes/afternoon_1004.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: every step records its own marker; a failed step must not stop the later, independent ones
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
M=$P/modules/05_support_predictor
M06=$P/modules/06_generative_candidates; mkdir -p "$M06/out"
ENV='export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp; mkdir -p $HOME/qc_tmp'
NIGHT2=$P/probes/results_m1/night2_2026-10-03.log
C34C=$M/out/E7_rungC_chain34c_kdfamilylow_750_2026-10-04.log
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
echo "=== afternoon queue armed $(t)"

# (A) batch route after chain 34c
( until grep -q "chain 34c finished" "$C34C"; do sleep 120; done
  echo "=== (A) batch route start: chain 34c has finished $(t)"
  cd "$M06" || exit 1
  PRE=out/proposals_2026-10-04
  if python m06/propose.py $PRE --runs seed0,seed1 --n 10000 --temperature 1.0 --threads 4 --allow-any-model \
     && python m06/propose.py $PRE --runs cond_seed0 --requests "<r3> <hnone>,<r4+> <hnone>,<r3> <hN>,<r4+> <hN>" --n 2500 --temperature 1.0 --threads 4 --allow-any-model --append \
     && python m06/gate.py $PRE.csv $PRE > out/proposals_2026-10-04_gate_stdout.txt 2>&1; then
    echo "=== (A) batch route done — read out/proposals_2026-10-04.md against the lines $(t)"
  else
    echo "=== (A) BATCH ROUTE FAILED $(t)"
  fi ) &
A_PID=$!

# (B) step 3 after the TZ run, then (C) notebooks, then (D) LNO
until grep -qE "TZ relaunch 4 done|TZ RELAUNCH 4 FAILED" "$NIGHT2"; do sleep 120; done
echo "=== (B) TZ run has ended; chain 34 step 3 start (WSL qc05, 12 threads) $(t)"
wsl -e bash -c "$ENV; cd $PW/modules/05_support_predictor && OMP_NUM_THREADS=12 ~/qc05/bin/python corpus/analytic_hessians.py corpus/molecules/A_72b86c2331 corpus/molecules/A_07cadc7923 corpus/molecules/A_fdc27f1bd1 corpus/molecules/A_e72997e726 corpus/molecules/A_bce5bae234 corpus/molecules/A_541c53d1a5 corpus/molecules/A_08dde334d8 corpus/molecules/A_428228e5a5 --threads 12" > "$M/out/chain34_step3_analytic_holdout_a_2026-10-04.log" 2>&1 \
  && echo "=== (B) chain 34 step 3 done $(t)" || echo "=== (B) CHAIN 34 STEP 3 FAILED $(t)"

echo "=== (C) notebook re-executions start (2 threads each, sequential) $(t)"
run_nb() {  # module dir, env assignments...
  local d=$1; shift
  ( cd "$P/modules/$d" && env "$@" python notebook/make_notebook.py > "notebook/reexec_2026-10-04.log" 2>&1 ) \
    && echo "=== (C) $d notebook re-executed $(t)" || echo "=== (C) $d NOTEBOOK FAILED — see modules/$d/notebook/reexec_2026-10-04.log $(t)"
}
run_nb 05_support_predictor M05_THREADS=2
( cd "$M" && python make_summary.py > out/make_summary_2026-10-04.log 2>&1 ) && echo "=== (C) 05 summary rebuilt $(t)" || echo "=== (C) 05 SUMMARY FAILED $(t)"
run_nb 06_generative_candidates M06_REUSE=1 M06_THREADS=2
( cd "$M06" && python make_summary.py > out/make_summary_2026-10-04.log 2>&1 ) && echo "=== (C) 06 summary rebuilt $(t)" || echo "=== (C) 06 SUMMARY FAILED $(t)"
run_nb standout_pattern_proposer PP_THREADS=2
( cd "$P/modules/standout_pattern_proposer" && python make_summary.py > out/make_summary_2026-10-04.log 2>&1 ) && echo "=== (C) standout summary rebuilt $(t)" || echo "=== (C) STANDOUT SUMMARY FAILED $(t)"
run_nb 07_agentic_workflows PYTHONUTF8=1
run_nb 08_industry_synthesis PYTHONUTF8=1
echo "=== (C) notebooks done $(t)"

wait $A_PID
echo "=== (D) LNO follow-up cells start (12 threads) $(t)"
ANCHOR=$PW/probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02
GEOM=$PW/modules/05_support_predictor/corpus/molecules/A_01f3186607/geometry.json
wsl -e bash -c "$ENV; cd $PW && OMP_NUM_THREADS=12 ~/qc05/bin/python probes/lno_curvature_check.py $ANCHOR $GEOM --max-k 2 --threads 12 --max-memory 8000 --xtight --out $PW/probes/results_m1/lno_curvature_xtight_2026-10-04.json" > "$P/probes/results_m1/lno_curvature_xtight_2026-10-04.log" 2>&1 \
  && echo "=== (D) LNO cell (a) xtight done $(t)" || echo "=== (D) LNO CELL (a) FAILED $(t)"
wsl -e bash -c "$ENV; cd $PW && OMP_NUM_THREADS=12 ~/qc05/bin/python probes/lno_curvature_check.py $ANCHOR $GEOM --max-k 2 --threads 12 --max-memory 8000 --reuse-localisation --out $PW/probes/results_m1/lno_curvature_reuse_2026-10-04.json" > "$P/probes/results_m1/lno_curvature_reuse_2026-10-04.log" 2>&1 \
  && echo "=== (D) LNO cell (b) reuse done $(t)" || echo "=== (D) LNO CELL (b) FAILED $(t)"
echo "=== afternoon queue finished $(t)"
