#!/usr/bin/env bash
# rerun_m06_notebook_1005.sh (5 Oct 2026, 15:0x). Module 06's notebook re-execution of the afternoon queue timed out (nbclient's 21,600 s cell limit) in the
# sampling cell at 2 threads — the 26 Sep run used 6 threads on a CCX53. Re-executes it with M06_THREADS=6 once the TZ anchor has released its 8 lanes
# ("(N1) TZ FULL ANCHOR DONE" or a TZ failure marker), beside the LNO cells' 8; then rebuilds the summary. Markers to the afternoon log. Git Bash, detached:
#   nohup bash probes/rerun_m06_notebook_1005.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: the two steps record their own markers
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LOG=$P/probes/results_m1/afternoon_2026-10-04.log
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
until grep -qE "\(N1\) TZ FULL ANCHOR DONE|\(N1\) TZ (ASSEMBLY|TWO-ROUTE CHECK|REMAINING DISPLACEMENTS) FAILED" "$LOG"; do sleep 300; done
echo "=== (C2) module 06 notebook re-execution start (6 threads, after the TZ anchor) $(t)"
cd "$P/modules/06_generative_candidates" || exit 1
if M06_REUSE=1 M06_THREADS=6 python notebook/make_notebook.py > notebook/reexec_2026-10-05.log 2>&1; then
  echo "=== (C2) 06 notebook re-executed $(t)"
  python make_summary.py > out/make_summary_2026-10-05.log 2>&1 && echo "=== (C2) 06 summary rebuilt $(t)" || echo "=== (C2) 06 SUMMARY FAILED $(t)"
else
  echo "=== (C2) 06 NOTEBOOK FAILED — see modules/06_generative_candidates/notebook/reexec_2026-10-05.log $(t)"
fi
