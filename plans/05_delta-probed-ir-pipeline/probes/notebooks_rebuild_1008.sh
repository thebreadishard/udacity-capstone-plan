#!/usr/bin/env bash
# notebooks_rebuild_1008.sh (8 Oct 2026; TASKS 18 and 20) — rebuild and execute the module notebooks after the lay-reader pass and module 05's
# sections 12.4/12.5, one at a time on the free laptop: 05, 07 (the repository .venv: LangGraph), 08, the standout. Module 06 is left out: a re-execution
# retrains seed 2 and changes its verdict (TASKS 26, only on the user's word). Each executed notebook is backed up first and restored if its build
# fails, so a failed build never leaves a half-executed notebook. Markers "=== (NB) …".
#   nohup bash probes/notebooks_rebuild_1008.sh >> probes/results_m1/notebooks_rebuild_2026-10-08.log 2>&1 &
set -uo pipefail
# no-set-e: one module's failure is logged, restored, and the next module builds
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
M=$P/modules
LOGD=$P/probes/results_m1/notebooks_rebuild_2026-10-08
VENV=/c/Users/thebr/Documents/CapstonePlan/.venv/Scripts/python.exe
mkdir -p "$LOGD"
t() { date '+%F %T'; }
export PYTHONUTF8=1
echo "=== (NB) rebuild start $(t)"
for row in "05_support_predictor:deep_learning.ipynb:python" "07_agentic_workflows:agentic_system.ipynb:$VENV" \
           "08_industry_synthesis:integrated_system.ipynb:python" "standout_pattern_proposer:pattern_proposer.ipynb:python"; do
  mod=${row%%:*}; rest=${row#*:}; nb=${rest%%:*}; py=${rest#*:}
  d=$M/$mod/notebook
  cp "$d/$nb" "$LOGD/${mod}_${nb}.bak"
  echo "(NB) $mod start $(t)"
  if (cd "$d" && "$py" make_notebook.py > "$LOGD/$mod.log" 2>&1); then
    echo "=== (NB) $mod done $(t)"
  else
    cp "$LOGD/${mod}_${nb}.bak" "$d/$nb"
    echo "=== (NB) $mod FAILED — executed notebook restored; see $LOGD/$mod.log $(t)"
  fi
done
echo "=== (NB) rebuild finished $(t)"
