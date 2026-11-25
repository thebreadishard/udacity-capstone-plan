#!/usr/bin/env bash
# probes/ano_step_benzene.sh <run dir> <basis dir> (TASKS 300; GoalGathering/notes/PreRegistration_2026-11-25_ANO_Step_Benzene.md with its
# amendment 1) — runs in WSL under probes/wsl_capped.sh. Benzene's MP2 Hessian rows at the corpus geometry by psi4's DF-MP2 gradient, on the
# plan of its own symmetry, for every target basis of the registration: cc-pVDZ (the step's lower end), cc-pVTZ (the control), cc-pVQZ,
# roos-ano-tz, ano-pVQZ (a file in <basis dir>, found through PSIPATH), cc-pwCVTZ with the frozen core and with all electrons (the
# core-valence term), and the DF-SCF rows at cc-pVTZ and cc-pVQZ that the basis-set-limit recipe takes apart from the correlation part.
# The ANO sets have no fitting sets of their own name and take cc-pVQZ's; one row of each is repeated with cc-pV5Z's as the check on the
# fitting, right after that set's own rows. Check W on water (both theories) is the smoke. The read is a separate script on Windows.
# Markers '=== (ANO) …', a failure as '=== (ANO) FAILED: …'; the end line '=== (ANO) all done'.
# Resumable: a label whose row file exists and whose log ends with dfmp2_rows.py's end line is skipped (so its time file keeps the peak
# memory of the launch that computed it); an unfinished one continues from its row file, which dfmp2_rows.py refuses when it was made at
# another level. A finished label is not looked at again, and no refusal sees the content of <basis dir> (the start line carries the basis
# file's sha256): a changed option in this script or a changed basis file needs a new run dir.
#   bash probes/ano_step_benzene.sh probes/results_m1/ano_step_benzene_2026-11-25/rows probes/results_m1/ano_step_benzene_2026-11-25/basis/psi
set -euo pipefail
RUN=${1:?run dir for the row files}
BASIS_DIR=${2:?folder with ano-pvqz.gbs}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/miniforge3/envs/vpt2/bin/python}
export PSI_SCRATCH=$HOME/psi4_scratch   # not /tmp: WSL clears it when idle (19 Oct 2026)
export PSIPATH=$BASIS_DIR
GEOM=$HERE/../modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json
THREADS=${THREADS:-8}
MEMORY_GB=${MEMORY_GB:-8}
QZ_FIT=(--df-basis-scf cc-pvqz-jkfit --df-basis-mp2 cc-pvqz-ri)
FIVEZ_FIT=(--df-basis-scf cc-pv5z-jkfit --df-basis-mp2 cc-pv5z-ri)
mark() { echo "=== (ANO) $* $(date '+%F %T')"; }
for needed in "$GEOM" "$BASIS_DIR/ano-pvqz.gbs" "$HERE/dfmp2_rows.py"; do
  [ -f "$needed" ] || { mark "refusing to start: $needed missing"; exit 1; }
done
mkdir -p "$PSI_SCRATCH" "$RUN"

# rows <label> <basis> [options of dfmp2_rows.py]: one row file, its log (appended over launches) and its peak memory
rows() {
  local label=$1 basis=$2 log="$RUN/rows_$1.log"
  shift 2
  if [ -f "$RUN/rows_$label.npz" ] && [ -f "$log" ] && tail -n 1 "$log" | grep -qa '^=== DF ROWS '; then
    mark "$label already finished in an earlier launch"
    return 0
  fi
  if ! /usr/bin/time -v -o "$RUN/time_$label.txt" "$PY" "$HERE/dfmp2_rows.py" rows --geometry "$GEOM" --basis "$basis" --threads "$THREADS" \
      --memory-gb "$MEMORY_GB" --out "$RUN/rows_$label.npz" "$@" 2>&1 | tee -a "$log"; then
    mark "FAILED: $label (see $log)"
    exit 1
  fi
  mark "$label done, peak RSS $(grep 'Maximum resident' "$RUN/time_$label.txt" | awk '{print $NF}') kB"
}

# first_row <label>: the first displacement of the plan, from the log of that label's rows. Called as K=$(…), so its mark goes to stderr.
first_row() {
  local k
  k=$(grep -a -m1 -o ' k=[0-9]*' "$RUN/rows_$1.log" | cut -d= -f2) || true
  [ -n "$k" ] || { mark "FAILED: no row in $RUN/rows_$1.log to repeat" >&2; exit 1; }
  echo "$k"
}

# with_fit_check <label> <basis>: an ANO set's rows with cc-pVQZ's fitting sets, then its first row again with cc-pV5Z's
with_fit_check() {
  local k
  rows "$1" "$2" "${QZ_FIT[@]}"
  k=$(first_row "$1")       # its own statement: a failure inside $(…) used as an argument would not stop the script
  rows "$1_fit5z" "$2" "${FIVEZ_FIT[@]}" --only-row "$k"
}

mark "start: psi4 $("$PY" -c 'import psi4; print(psi4.__version__)'), $THREADS threads, psi4 memory $MEMORY_GB GB, PSIPATH $PSIPATH," \
  "ano-pvqz.gbs sha256 $(sha256sum "$BASIS_DIR/ano-pvqz.gbs" | cut -c1-64)"
for theory in mp2 scf; do
  if ! "$PY" "$HERE/dfmp2_rows.py" water --theory "$theory" --out "$RUN/water_check_$theory.json" --threads "$THREADS" --memory-gb "$MEMORY_GB"; then
    mark "FAILED: smoke (check W on water, $theory)"
    exit 1
  fi
done
mark "smoke: check W passed for mp2 and scf"

rows mp2_ccpvdz cc-pvdz
with_fit_check mp2_anopvqz ano-pvqz          # early: the one basis psi4 does not ship, and the fitting choice, fail here and not after an hour
with_fit_check mp2_roosanotz roos-ano-tz
rows mp2_ccpvtz cc-pvtz
rows scf_ccpvtz cc-pvtz --theory scf
rows mp2_ccpwcvtz_fc cc-pwcvtz --df-basis-scf cc-pvtz-jkfit
rows mp2_ccpwcvtz_ae cc-pwcvtz --df-basis-scf cc-pvtz-jkfit --frozen-core 0
rows mp2_ccpvqz cc-pvqz
rows scf_ccpvqz cc-pvqz --theory scf
mark "all done"
