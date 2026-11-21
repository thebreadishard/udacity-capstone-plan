#!/usr/bin/env bash
# probes/dfmp2_lane.sh <batch dir> <TAG> <wait log glob> <wait regex> [--dry-run] (21 Nov 2026; TASKS 291) — one lane of the composite
# anchors' MP2 basis step on an anchor server: for every molecule of <batch>/list.txt (lines `id|geometry.json`, in order) the DF-MP2
# Hessian rows at cc-pVDZ and at cc-pVTZ by probes/dfmp2_rows.py (`rows --geometry`: the molecule's own symmetry plans the rows, the
# anchors' step, frozen core by the element rule — the route adopted on 20 Oct 2026,
# GoalGathering/notes/PreRegistration_2026-10-19_DFMP2_Composite_Step.md), into <batch>/rows/<id>/dfmp2_rows_<basis>.npz. The step needs
# the geometry only, not the CC Hessian, so it runs beside or before the molecule's CC run. Runs ON the server:
#   1. waits until a file of the wait-log glob matches the wait regex (checked every WAIT_S s) — e.g. the DFT lane's end, whose core
#      share this lane then takes;
#   2. the rows, one molecule and basis at a time, each under a system-scope memory cap (probes/wsl_capped.sh) and /usr/bin/time; a
#      molecule whose geometry is missing is skipped and counted; a basis killed at the cap is named so (probes/cation_oom_check.sh).
# Markers '=== (<TAG>) …', one line per molecule and basis on stdout, the end line '=== (<TAG>) all done: N failures or skips'; exit
# non-zero when N > 0. Resumable: dfmp2_rows.py keeps every finished row and a finished file is not opened again.
# Settings (environment, checked before the wait): QC (the psi4 python) /root/miniforge3/envs/qc/bin/python, THREADS 4, MEMORY_GB 6,
#   CAP_MB 8192, WAIT_S 600, CAPPED and OOM_CHECK (beside this script).
#   bash probes/dfmp2_lane.sh /root/mp2a MP '/root/dft1/anc1_dft1.log' '=== \(AD\) all done'
set -u
# no-set-e: a molecule that fails is reported and the others continue; the end marker counts the failures
BATCH=${1:?batch dir}; TAG=${2:?tag}; WAIT_LOG=${3:?wait log}; WAIT_RE=${4:?wait regex}; DRY=${5:-}
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$BATCH" || exit 1
BATCH=$(pwd)
QC=${QC:-/root/miniforge3/envs/qc/bin/python}
THREADS=${THREADS:-4}; MEMORY_GB=${MEMORY_GB:-6}; CAP_MB=${CAP_MB:-8192}; WAIT_S=${WAIT_S:-600}
CAPPED=${CAPPED:-$HERE/wsl_capped.sh}; OOM_CHECK=${OOM_CHECK:-$HERE/cation_oom_check.sh}
BASES=(cc-pvdz cc-pvtz)
STATUS=$BATCH/status_$TAG.log
export PSI_SCRATCH=${PSI_SCRATCH:-/root/psi4_scratch} PYTHONUNBUFFERED=1
mark() { echo "=== ($TAG) $* $(date '+%F %T')"; }
for v in THREADS MEMORY_GB CAP_MB WAIT_S; do
  [[ ${!v} =~ ^[1-9][0-9]*$ ]] || { mark "STOPPED: $v must be a positive integer, not '${!v}'"; exit 1; }
done
[ $((MEMORY_GB * 1024)) -lt "$CAP_MB" ] || { mark "STOPPED: MEMORY_GB $MEMORY_GB does not fit under the cap of $CAP_MB MB"; exit 1; }
for b in "$QC" "$HERE/dfmp2_rows.py" "$CAPPED" "$OOM_CHECK" list.txt; do [ -e "$b" ] || { mark "STOPPED: $b missing"; exit 1; }; done
mapfile -t LINES < <(grep -v '^#' list.txt | tr -d '\r' | sed '/^$/d')
[ "${#LINES[@]}" -gt 0 ] || { mark "STOPPED: list.txt names no molecule"; exit 1; }
for line in "${LINES[@]}"; do
  [[ $line =~ ^[A-Za-z0-9_]+\|/[^|]+$ ]] || { mark "STOPPED: not 'id|/absolute/geometry.json': $line"; exit 1; }
done
met() { grep -lE "$WAIT_RE" $WAIT_LOG 2>/dev/null | wc -l; }   # WAIT_LOG unquoted: it may be a glob
finished() { grep -qa 'DF ROWS DONE' "rows/$1/rows_$2.log" 2>/dev/null && [ -f "rows/$1/dfmp2_rows_$2.npz" ]; }
todo=0
for line in "${LINES[@]}"; do for b in "${BASES[@]}"; do finished "${line%%|*}" "${b//-/}" || todo=$((todo + 1)); done; done
mark "armed: ${#LINES[@]} molecules, $todo of $(( ${#LINES[@]} * ${#BASES[@]} )) row files to compute; $THREADS threads, ${MEMORY_GB} GB under a cap\
 of $CAP_MB MB; waiting for /$WAIT_RE/ in $WAIT_LOG"
[ "$DRY" = "--dry-run" ] && { mark "dry run: wait condition $([ "$(met)" -ge 1 ] && echo met || echo 'not met yet')"; exit 0; }
until [ "$(met)" -ge 1 ]; do sleep "$WAIT_S"; done
mark "start: the wait condition is met; psi4 $("$QC" -c 'import psi4; print(psi4.__version__)')"
mkdir -p "$PSI_SCRATCH" rows
: > "$STATUS"
for line in "${LINES[@]}"; do
  id=${line%%|*}; geom=${line#*|}
  if [ ! -f "$geom" ]; then
    echo "  $id SKIPPED (no geometry at $geom)"; echo "$id skipped: no geometry" >> "$STATUS"; continue
  fi
  mkdir -p "rows/$id"
  for b in "${BASES[@]}"; do
    short=${b//-/}; log=rows/$id/rows_$short.log
    if finished "$id" "$short"; then echo "  $id $short rows found"; continue; fi
    t0=$(date +%s)
    if OMP_NUM_THREADS=$THREADS env CAP_SCOPE=system bash "$CAPPED" "$CAP_MB" -- /usr/bin/time -f "($TAG) $id max RSS %M kB, wall %e s ($short)" \
         "$QC" "$HERE/dfmp2_rows.py" rows --geometry "$geom" --basis "$b" --out "rows/$id/dfmp2_rows_$short.npz" \
         --threads "$THREADS" --memory-gb "$MEMORY_GB" >> "$log" 2>&1 && finished "$id" "$short"; then
      echo "  $id $short rows done $(( $(date +%s) - t0 )) s - $(grep -a "($TAG) $id max RSS" "$log" | tail -n 1)"
    elif OOM_TAG=$TAG OOM_JOURNAL=system bash "$OOM_CHECK" "$id" >> "$log" 2>&1; then
      echo "  $id $short KILLED at the cap of $CAP_MB MB $(( $(date +%s) - t0 )) s ($log)"; echo "$id $short killed at the cap" >> "$STATUS"
    else
      echo "  $id $short ROWS FAILED $(( $(date +%s) - t0 )) s ($log)"; echo "$id $short failed" >> "$STATUS"
    fi
  done
done
fails=$(grep -c . "$STATUS")
mark "all done: $fails failures or skips"
[ "$fails" = 0 ]
