#!/bin/bash
# labels_batch_ccx53.sh (15 Oct 2026, TASKS 61; the cation run's options merged in on 25 Oct 2026, TASKS 121) — a batch of molecules from
# corpus start geometry to analytic labels on a labels server, after another job has ended. Runs ON the server:
#   1. waits until WAIT_COUNT files of the WAIT_LOG glob match WAIT_RE (checked every WAIT_S s);
#   2. psi4 optimisations (psi4_worker.py with the job's "hessians": false) of the molecules without a finished result, LANES at a time;
#   3. analytic labels (analytic_hessians.py, the label lanes' own call, plus LABEL_ARGS), LANES at a time × THREADS, in ids.txt order (its
#      first column; largest first lets the lanes end together). With CAP_MB each molecule runs in a system-scope memory cgroup of that size
#      (wsl_capped.sh) under /usr/bin/time, and one killed at the cap is named so (cation_oom_check.sh against the system journal, tag TAG):
#      pyscf's UKS CPHF does not keep to max_memory (pyscf#3530), so a cap is what keeps one molecule from starving the other lanes.
# Job files: <batch>/molecules/<id>/job.json (probes/rung4_jobs.py); worker.log and labels.log beside them. Markers '=== (<TAG>) …' and one
# line per molecule on stdout; the run exits non-zero when a molecule failed. Restartable: a folder whose result.json says "done" is not
# optimised again, one with both analytic Hessians is not labelled again.
# Settings (environment, checked before the wait): CODE (the workers' folder) /root/labels, QC and QC05 (the psi4 and pyscf pythons), QC_TMP,
#   LANES 4, THREADS 8, WAIT_COUNT 1, WAIT_S 900, LABEL_ARGS (e.g. '--charge 1 --spin 1 --max-memory 24000 --reuse-existing'), CAP_MB (none),
#   CAPPED and OOM_CHECK (beside this script).
#   bash labels_batch_ccx53.sh <batch_dir> <TAG> <wait_log glob> <wait_regex> [--dry-run]
#   e.g. bash /root/labels/labels_batch_ccx53.sh /root/labels/rung4 R4 /root/labels/large_pah/run.log '=== \(L5\) all done'
set -u
# no-set-e: a molecule that fails is reported and the others continue; the end marker counts the failures
BATCH=${1:?batch dir}; TAG=${2:?tag}; WAIT_LOG=${3:?wait log}; WAIT_RE=${4:?wait regex}; DRY=${5:-}
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$BATCH" || exit 1
BATCH=$(pwd)                            # absolute: label() runs from CODE
QC=${QC:-/root/miniforge3/envs/qc/bin/python}
QC05=${QC05:-/root/miniforge3/envs/qc05/bin/python}
CODE=${CODE:-/root/labels}              # psi4_worker.py and analytic_hessians.py
QC_TMP=${QC_TMP:-/root/qc_tmp}
LANES=${LANES:-4}; THREADS=${THREADS:-8}; WAIT_COUNT=${WAIT_COUNT:-1}; WAIT_S=${WAIT_S:-900}
LABEL_ARGS=${LABEL_ARGS:-}; CAP_MB=${CAP_MB:-}
CAPPED=${CAPPED:-$HERE/wsl_capped.sh}; OOM_CHECK=${OOM_CHECK:-$HERE/cation_oom_check.sh}
STATUS=$BATCH/status_$TAG.log           # one line per molecule that failed or was skipped
export PYSCF_TMPDIR=$QC_TMP TMPDIR=$QC_TMP PYTHONUNBUFFERED=1
mark() { echo "=== ($TAG) $* $(date '+%F %T')"; }
for v in LANES THREADS WAIT_COUNT WAIT_S ${CAP_MB:+CAP_MB}; do
  [[ ${!v} =~ ^[1-9][0-9]*$ ]] || { mark "STOPPED: $v must be a positive integer, not '${!v}'"; exit 1; }
done
if [ -n "$CAP_MB" ]; then
  for b in "$CAPPED" "$OOM_CHECK"; do [ -f "$b" ] || { mark "STOPPED: $b missing (CAP_MB is set)"; exit 1; }; done
fi
optimised() { [ -f "molecules/$1/result.json" ] && grep -q '"status": "done"' "molecules/$1/result.json"; }
labelled() { [ -f "molecules/$1/hessian_b3lyp_analytic.npz" ] && [ -f "molecules/$1/hessian_wb97x_analytic.npz" ]; }
met() { grep -lE "$WAIT_RE" $WAIT_LOG 2>/dev/null | wc -l; }   # WAIT_LOG unquoted: it may be a glob of several logs
mapfile -t IDS < <(grep -v '^#' ids.txt | cut -f1 | tr -d '\r' | sed '/^$/d')
missing=$(for id in "${IDS[@]}"; do [ -f "molecules/$id/job.json" ] || echo "$id"; done | wc -l)
to_opt=$(for id in "${IDS[@]}"; do optimised "$id" || echo "$id"; done | wc -l)
to_label=$(for id in "${IDS[@]}"; do labelled "$id" || echo "$id"; done | wc -l)
mark "armed: ${#IDS[@]} molecules ($missing without a job file); $to_opt to optimise, $to_label to label; $LANES lanes × $THREADS threads\
${CAP_MB:+, cap $CAP_MB MB}${LABEL_ARGS:+, label arguments '$LABEL_ARGS'}; waiting for /$WAIT_RE/ in $WAIT_COUNT of $WAIT_LOG"
[ "$missing" = 0 ] || { mark "STOPPED: $missing job files missing"; exit 1; }
need=("$QC05" "$CODE/analytic_hessians.py")
[ "$to_opt" = 0 ] || need+=("$QC" "$CODE/psi4_worker.py")
for b in "${need[@]}"; do [ -e "$b" ] || { mark "STOPPED: $b missing"; exit 1; }; done
[ "$DRY" = "--dry-run" ] && { mark "dry run: wait condition $([ "$(met)" -ge "$WAIT_COUNT" ] && echo met || echo 'not met yet')"; exit 0; }
until [ "$(met)" -ge "$WAIT_COUNT" ]; do sleep "$WAIT_S"; done
mark "start: the wait condition is met"
mkdir -p "$QC_TMP"
: > "$STATUS"
opt() {
  local id=$1
  if optimised "$id"; then echo "  $id optimised already"; return 0; fi
  local t0; t0=$(date +%s)
  if OMP_NUM_THREADS=$THREADS "$QC" "$CODE/psi4_worker.py" "molecules/$id/job.json" > "molecules/$id/worker.log" 2>&1; then
    echo "  $id optimised $(( $(date +%s) - t0 )) s"
  else
    echo "  $id OPTIMISATION FAILED $(( $(date +%s) - t0 )) s (molecules/$id/worker.log)"; echo "$id optimisation failed" >> "$STATUS"
  fi
}
label() {
  local id=$1 d=$BATCH/molecules/$1 t0 cmd extra
  if labelled "$id"; then echo "  $id labelled already"; return 0; fi
  [ -f "$d/geometry.json" ] || { echo "  $id LABELS SKIPPED (no optimised geometry)"; echo "$id skipped" >> "$STATUS"; return 1; }
  read -ra extra <<< "$LABEL_ARGS"
  cmd=("$QC05" analytic_hessians.py "$d" --threads "$THREADS" "${extra[@]}")
  if [ -n "$CAP_MB" ]; then
    cmd=(env CAP_SCOPE=system bash "$CAPPED" "$CAP_MB" -- /usr/bin/time -f "($TAG) $id max RSS %M kB, wall %e s" "${cmd[@]}")
  fi
  echo "  $id labels started $(date '+%F %T')"
  t0=$(date +%s)
  if (cd "$CODE" && OMP_NUM_THREADS=$THREADS "${cmd[@]}" >> "$d/labels.log" 2>&1); then
    echo "  $id labelled $(( $(date +%s) - t0 )) s${CAP_MB:+ - $(grep -a "($TAG) $id max RSS" "$d/labels.log" | tail -n 1)}"
  elif [ -n "$CAP_MB" ] && OOM_TAG=$TAG OOM_JOURNAL=system bash "$OOM_CHECK" "$id" >> "$d/labels.log" 2>&1; then
    echo "  $id KILLED at the cap of $CAP_MB MB $(( $(date +%s) - t0 )) s (molecules/$id/labels.log)"; echo "$id killed at the cap" >> "$STATUS"
  else
    echo "  $id LABELS FAILED $(( $(date +%s) - t0 )) s (molecules/$id/labels.log)"; echo "$id failed" >> "$STATUS"
  fi
}
export -f opt label optimised labelled
export QC QC05 BATCH CODE THREADS LABEL_ARGS CAP_MB CAPPED OOM_CHECK TAG STATUS
mark "optimisations"
printf '%s\n' "${IDS[@]}" | xargs -P "$LANES" -I{} bash -c 'opt {}'
mark "labels"
printf '%s\n' "${IDS[@]}" | xargs -P "$LANES" -I{} bash -c 'label {}'
fails=$(grep -c . "$STATUS")
mark "all done: $fails failures or skips"
[ "$fails" = 0 ]
