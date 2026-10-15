#!/bin/bash
# labels_batch_ccx53.sh (15 Oct 2026, TASKS 61) — a batch of molecules from corpus start geometry to analytic labels on the labels server, after
# another job has ended: the pattern of probes/large_pah_ccx53.sh (lever 5, armed on 13 Oct and left untouched), with the batch, its tag and
# its wait condition as arguments. Runs ON the labels server:
#   1. waits until WAIT_LOG matches WAIT_RE (checked every 15 min);
#   2. psi4 optimisations (psi4_worker.py with the job's "hessians": false), four at a time × 8 threads, in ids.txt order;
#   3. analytic labels (analytic_hessians.py, the label lanes' own call), four at a time × 8 threads.
# Job files: <batch>/molecules/<id>/job.json (probes/rung4_jobs.py); worker.log and labels.log beside them. Markers '=== (<TAG>) …' on stdout.
# Restartable: a folder whose result.json says "done" is not optimised again, one with both analytic Hessians is not labelled again.
#   bash labels_batch_ccx53.sh <batch_dir> <TAG> <wait_log> <wait_regex> [--dry-run]
#   e.g. bash /root/labels/labels_batch_ccx53.sh /root/labels/rung4 R4 /root/labels/large_pah/run.log '=== \(L5\) all done'
set -u
# no-set-e: a molecule that fails is reported and the others continue; the end marker counts the failures
BATCH=${1:?batch dir}; TAG=${2:?tag}; WAIT_LOG=${3:?wait log}; WAIT_RE=${4:?wait regex}; DRY=${5:-}
cd "$BATCH" || exit 1
QC=/root/miniforge3/envs/qc/bin/python
QC05=/root/miniforge3/envs/qc05/bin/python
export PYSCF_TMPDIR=/root/qc_tmp TMPDIR=/root/qc_tmp
mark() { echo "=== ($TAG) $* $(date '+%F %T')"; }
mapfile -t IDS < <(grep -v '^#' ids.txt | sed '/^$/d')
missing=$(for id in "${IDS[@]}"; do [ -f "molecules/$id/job.json" ] || echo "$id"; done | wc -l)
mark "armed: ${#IDS[@]} molecules ($missing without a job file); waiting for /$WAIT_RE/ in $WAIT_LOG"
[ "$missing" = 0 ] || { mark "STOPPED: $missing job files missing"; exit 1; }
for b in "$QC" "$QC05" /root/labels/psi4_worker.py /root/labels/analytic_hessians.py; do [ -e "$b" ] || { mark "STOPPED: $b missing"; exit 1; }; done
[ "$DRY" = "--dry-run" ] && { mark "dry run: wait condition $(grep -qE "$WAIT_RE" "$WAIT_LOG" 2>/dev/null && echo met || echo 'not met yet')"; exit 0; }
until grep -qE "$WAIT_RE" "$WAIT_LOG" 2>/dev/null; do sleep 900; done
mark "start: the wait condition is met"
opt() {
  local id=$1
  if [ -f "molecules/$id/result.json" ] && grep -q '"status": "done"' "molecules/$id/result.json"; then echo "  $id optimised already"; return 0; fi
  local t0; t0=$(date +%s)
  if OMP_NUM_THREADS=8 "$QC" /root/labels/psi4_worker.py "molecules/$id/job.json" > "molecules/$id/worker.log" 2>&1; then
    echo "  $id optimised $(( $(date +%s) - t0 )) s"
  else
    echo "  $id OPTIMISATION FAILED $(( $(date +%s) - t0 )) s (molecules/$id/worker.log)"
  fi
}
label() {
  local id=$1
  if [ -f "molecules/$id/hessian_b3lyp_analytic.npz" ] && [ -f "molecules/$id/hessian_wb97x_analytic.npz" ]; then echo "  $id labelled already"; return 0; fi
  [ -f "molecules/$id/geometry.json" ] || { echo "  $id LABELS SKIPPED (no optimised geometry)"; return 1; }
  local t0; t0=$(date +%s)
  if (cd /root/labels && OMP_NUM_THREADS=8 "$QC05" analytic_hessians.py "$BATCH/molecules/$id" --threads 8 >> "$BATCH/molecules/$id/labels.log" 2>&1); then
    echo "  $id labelled $(( $(date +%s) - t0 )) s"
  else
    echo "  $id LABELS FAILED $(( $(date +%s) - t0 )) s (molecules/$id/labels.log)"
  fi
}
export -f opt label
export QC QC05 BATCH
mark "optimisations"
printf '%s\n' "${IDS[@]}" | xargs -P 4 -I{} bash -c 'opt {}'
mark "labels"
printf '%s\n' "${IDS[@]}" | xargs -P 4 -I{} bash -c 'label {}'
fails=$(grep -c 'FAILED\|SKIPPED' "$BATCH/run.log" 2>/dev/null || echo 0)
mark "all done: $fails failures or skips"
