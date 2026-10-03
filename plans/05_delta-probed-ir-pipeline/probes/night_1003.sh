#!/usr/bin/env bash
# Night sequence 3→4 Oct 2026 on the laptop (one job at a time, the whole box each): (1) module-05 notebook build with section 12.3 once anthracene's
# analytic Hessians are done; (2) naphthalene LNO curvature check, two coordinates, 16 threads; (3) benzene CCSD(T)/cc-pVTZ out-of-plane pairs,
# 16 threads. Markers on stdout; the notebook build runs under Windows Python, the rest under WSL's qc05 — this script runs in WSL and calls the
# Windows build through a Git Bash marker file written by notebook_build_once.sh (started from Git Bash).
set -u
# no-set-e: every step records its own line
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
S=/mnt/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
until grep -qE "anthracene analytic finished" $P/modules/05_support_predictor/out/anthracene_analytic_2026-10-03.log 2>/dev/null; do sleep 120; done
echo "=== night: anthracene analytic done; waiting for the notebook build marker $(date)"
until [ -f "$S/notebook_build_1003.finished" ]; do sleep 120; done
echo "=== night: LNO curvature check start $(date)"
cd $P/probes && OMP_NUM_THREADS=16 ~/qc05/bin/python lno_curvature_check.py $P/probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02 \
  $P/modules/05_support_predictor/corpus/molecules/A_01f3186607/geometry.json --threads 16 --max-memory 12000 --ks 0,2 \
  > $P/probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/lno_curvature_run_2026-10-03.log 2>&1 \
  && echo "=== night: LNO done $(date)" || echo "=== NIGHT LNO FAILED $(date)"
OUT=$P/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03; mkdir -p "$OUT"
echo "=== night: TZ benzene oop start $(date)"
cd $P/probes && OMP_NUM_THREADS=16 ~/qc05/bin/python e8_cc_hessian_fd.py $P/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json "$OUT" \
  --threads 16 --basis cc-pvtz --symmetry --ks 5,2,3 --two-route-check separate --fast-t-density --fast-t-lambda --max-memory 10000 > "$OUT/run.log" 2>&1 \
  && echo "=== night: TZ benzene oop done $(date)" || echo "=== NIGHT TZ BENZENE OOP FAILED $(date)"
echo "=== night finished $(date)"
