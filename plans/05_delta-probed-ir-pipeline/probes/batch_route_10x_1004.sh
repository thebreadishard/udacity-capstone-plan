#!/usr/bin/env bash
# batch_route_10x_1004.sh (4 Oct 2026, 13:3x). The registered ten-fold conditioned run of the candidate generator's batch route (amendment 13:3x in
# PreRegistration_2026-10-04_Candidate_Generator_Batch_Route.md): cond_seed0 (v0.2), the same four requests at 25,000 samples each, appended to a copy of
# today's export and gated on the union. Waits for the afternoon queue's notebook re-executions ("(C) notebooks done"), then 4 threads beside the LNO
# cells' 12. Git Bash, detached:
#   nohup bash probes/batch_route_10x_1004.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: the steps record their own markers; a failed gate must still leave the export on disk
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
M06=$P/modules/06_generative_candidates
LOG=$P/probes/results_m1/afternoon_2026-10-04.log
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
until grep -q "(C) notebooks done" "$LOG"; do sleep 300; done
echo "=== (E) batch route 10x start: notebooks are done $(t)"
cd "$M06" || exit 1
SRC=out/proposals_2026-10-04; DST=out/proposals_10x_2026-10-04
cp "$SRC.csv" "$DST.csv" && cp "$SRC.json" "$DST.json" || { echo "=== (E) BATCH ROUTE 10x FAILED: could not copy today's export $(t)"; exit 1; }
if python m06/propose.py $DST --runs cond_seed0 --requests "<r3> <hnone>,<r4+> <hnone>,<r3> <hN>,<r4+> <hN>" --n 25000 --temperature 1.0 --threads 4 --allow-any-model --append \
   && python m06/gate.py $DST.csv $DST > out/proposals_10x_2026-10-04_gate_stdout.txt 2>&1; then
  echo "=== (E) batch route 10x done — read out/proposals_10x_2026-10-04.md against the lines on the union $(t)"
else
  echo "=== (E) BATCH ROUTE 10x FAILED $(t)"
fi
