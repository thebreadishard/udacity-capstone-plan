#!/usr/bin/env bash
# 3 Oct 2026: build + execute the module-05 notebook (section 12.3) once the naphthalene LNO check and the benzene DZ run have freed the CPU; writes a
# marker file the TZ chain waits for. Git Bash, detached.
set -u
# no-set-e: the build records its own line
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
S=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
until grep -qE "LNO curvature check:|Traceback" $P/probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/lno_curvature_run_2026-10-03.log 2>/dev/null \
   && grep -qE "Hessian written|FAILED|SELF-CHECK" $P/probes/results_m1/e8_benzene_ccpvdz_dip_2026-10-03/e8_fd.log 2>/dev/null; do sleep 300; done
echo "=== notebook build start $(date)"
cd $P/modules/05_support_predictor/notebook && PYTHONUTF8=1 python make_notebook.py > "$S/make_notebook_1003b.log" 2>&1 && echo "=== notebook build done $(date)" || echo "=== NOTEBOOK BUILD FAILED $(date)"
touch "$S/notebook_build_1003.finished"
echo "=== notebook build finished $(date)"
