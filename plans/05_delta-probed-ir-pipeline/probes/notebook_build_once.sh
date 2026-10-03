#!/usr/bin/env bash
# 3 Oct 2026: build + execute the module-05 notebook (section 12.3) once anthracene's analytic Hessians have freed the CPU; writes the marker file the
# night sequence (night_1003.sh) waits for. Git Bash, detached.
set -u
# no-set-e: the build records its own line
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
S=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
until grep -qE "anthracene analytic finished" $P/modules/05_support_predictor/out/anthracene_analytic_2026-10-03.log 2>/dev/null; do sleep 120; done
echo "=== notebook build start $(date)"
cd $P/modules/05_support_predictor/notebook && PYTHONUTF8=1 python make_notebook.py > "$S/make_notebook_1003b.log" 2>&1 && echo "=== notebook build done $(date)" || echo "=== NOTEBOOK BUILD FAILED $(date)"
touch "$S/notebook_build_1003.finished"
echo "=== notebook build finished $(date)"
