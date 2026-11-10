#!/usr/bin/env bash
# probes/anchor_oop_dfmp2.sh <run dir> (10 Nov 2026; TASKS 184 (b) by the amendment of 10 Nov in
# GoalGathering/notes/PreRegistration_2026-11-05_Anchor_CH-oop_Checks.md; the user: 'Oké' on option 1) — runs in WSL under probes/wsl_capped.sh:
# check W on water as the smoke (the analytic DF-MP2 gradient against finite differences of its energy), then benzene's out-of-plane rows by
# psi4's DF-MP2 gradient at cc-pVTZ and cc-pVQZ on the plan of the conventional TZ file in <run dir>, each under /usr/bin/time for its peak
# RSS. The read (`anchor_oop_check.py qz ... --df-tz`) loads the corpus and runs on Windows afterwards. Markers '=== (AOD) …'; the end line
# '=== (AOD) all done'. Resumable: dfmp2_rows.py skips rows already written.
#   bash probes/anchor_oop_dfmp2.sh probes/results_m1/anchor_oop_checks_2026-11-05
set -euo pipefail
RUN=${1:?run dir with the conventional TZ rows}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/miniforge3/envs/vpt2/bin/python}
export PSI_SCRATCH=$HOME/psi4_scratch   # not /tmp: WSL clears it when idle (19 Oct 2026)
GEOM=$HERE/../modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json
CONV=$RUN/mp2_rows_benzene_planeframe_ccpvtz.npz
THREADS=${THREADS:-8}
MEMORY_GB=${MEMORY_GB:-8}
mkdir -p "$PSI_SCRATCH"
mark() { echo "=== (AOD) $* $(date '+%F %T')"; }
[ -f "$CONV" ] || { mark "refusing to continue: no conventional TZ rows at $CONV"; exit 1; }

mark "start: psi4 $("$PY" -c 'import psi4; print(psi4.__version__)'), $THREADS threads, psi4 memory $MEMORY_GB GB"
if ! "$PY" "$HERE/dfmp2_rows.py" water --out "$RUN/dfmp2_water_check.json" --threads "$THREADS" --memory-gb "$MEMORY_GB"; then
  mark "smoke: FAILED (check W on water)"
  exit 1
fi
mark "smoke: check W passed"
for b in cc-pvtz cc-pvqz; do
  short=${b//-/}
  extra=()
  [ "$b" = cc-pvtz ] || extra=(--other-basis "$b")
  /usr/bin/time -v -o "$RUN/time_dfmp2_${short}.txt" "$PY" "$HERE/dfmp2_rows.py" rows --like "$CONV" --symbols-from "$GEOM" "${extra[@]}" \
    --threads "$THREADS" --memory-gb "$MEMORY_GB" --out "$RUN/dfmp2_rows_benzene_planeframe_${short}.npz"
  mark "benzene $short done, peak RSS $(grep 'Maximum resident' "$RUN/time_dfmp2_${short}.txt" | awk '{print $NF}') kB"
done
mark "all done"
