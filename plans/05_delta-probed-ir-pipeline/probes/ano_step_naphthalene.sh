#!/usr/bin/env bash
# probes/ano_step_naphthalene.sh <run dir> <basis dir> <geometry.json> (TASKS 300;
# GoalGathering/notes/PreRegistration_2026-11-26_ANO_Step_Naphthalene.md). Naphthalene's MP2 Hessian rows at the corpus geometry by
# psi4's DF-MP2 gradient in ano-pVQZ (a file in <basis dir>, found through PSIPATH) with cc-pVQZ's fitting sets, on the plan of the
# molecule's own symmetry (15 rows), then the plan's first row again with cc-pV5Z's fitting sets as the check on the fitting.
# The cc-pVDZ and cc-pVTZ rows of the composite are held from 19 Oct and are not recomputed. Check W on water is the smoke.
# Markers '=== (ANO2) …', a failure as '=== (ANO2) FAILED: …'; the end line '=== (ANO2) all done'.
# Resumable as probes/ano_step_benzene.sh is: a label whose row file exists and whose log ends with dfmp2_rows.py's end line is
# skipped; an unfinished one continues from its row file. A changed option here or a changed basis file needs a new run dir (the
# start line carries the basis file's sha256).
#   bash probes/ano_step_naphthalene.sh <run>/rows <run>/basis/psi <corpus>/A_01f3186607/geometry.json
set -euo pipefail
RUN=${1:?run dir for the row files}
BASIS_DIR=${2:?folder with ano-pvqz.gbs}
GEOM=${3:?the corpus geometry.json of naphthalene}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/miniforge3/envs/vpt2/bin/python}
export PSI_SCRATCH=${PSI_SCRATCH:-$HOME/psi4_scratch}   # not /tmp: WSL clears it when idle (19 Oct 2026)
export PSIPATH=$BASIS_DIR
THREADS=${THREADS:-8}
MEMORY_GB=${MEMORY_GB:-8}
LABEL=mp2_anopvqz
mark() { echo "=== (ANO2) $* $(date '+%F %T')"; }
for needed in "$GEOM" "$BASIS_DIR/ano-pvqz.gbs" "$HERE/dfmp2_rows.py"; do
  [ -f "$needed" ] || { mark "refusing to start: $needed missing"; exit 1; }
done
mkdir -p "$PSI_SCRATCH" "$RUN"

# rows <label> [options of dfmp2_rows.py]: one row file, its log (appended over launches) and its peak memory
rows() {
  local label=$1 log="$RUN/rows_$1.log"
  shift
  if [ -f "$RUN/rows_$label.npz" ] && [ -f "$log" ] && tail -n 1 "$log" | grep -qa '^=== DF ROWS '; then
    mark "$label already finished in an earlier launch"
    return 0
  fi
  if ! /usr/bin/time -v -o "$RUN/time_$label.txt" "$PY" "$HERE/dfmp2_rows.py" rows --geometry "$GEOM" --basis ano-pvqz --threads "$THREADS" \
      --memory-gb "$MEMORY_GB" --out "$RUN/rows_$label.npz" "$@" 2>&1 | tee -a "$log"; then
    mark "FAILED: $label (see $log)"
    exit 1
  fi
  mark "$label done, peak RSS $(grep 'Maximum resident' "$RUN/time_$label.txt" | awk '{print $NF}') kB"
}

mark "start: psi4 $("$PY" -c 'import psi4; print(psi4.__version__)'), $THREADS threads, psi4 memory $MEMORY_GB GB, PSIPATH $PSIPATH," \
  "ano-pvqz.gbs sha256 $(sha256sum "$BASIS_DIR/ano-pvqz.gbs" | cut -c1-64)"
if ! "$PY" "$HERE/dfmp2_rows.py" water --theory mp2 --out "$RUN/water_check_mp2.json" --threads "$THREADS" --memory-gb "$MEMORY_GB"; then
  mark "FAILED: smoke (check W on water)"
  exit 1
fi
mark "smoke: check W passed"

rows "$LABEL" --df-basis-scf cc-pvqz-jkfit --df-basis-mp2 cc-pvqz-ri
K=$(grep -a -m1 -o ' k=[0-9]*' "$RUN/rows_$LABEL.log" | cut -d= -f2) || true
[ -n "$K" ] || { mark "FAILED: no row in $RUN/rows_$LABEL.log to repeat"; exit 1; }
rows "${LABEL}_fit5z" --df-basis-scf cc-pv5z-jkfit --df-basis-mp2 cc-pv5z-ri --only-row "$K"
mark "all done"
