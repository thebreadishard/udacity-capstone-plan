#!/bin/bash
# large_pah_ccx53.sh (13 Oct 2026, TASKS 49 / chain 42) — runs ON the labels server after its four label lanes: the ten large PAHs of
# selection.json (four test molecules, layer T; six training molecules, layer D) from PAHdb geometry to analytic labels.
#   1. waits until lane_0..3.log each say "LANE <n> DONE" (the corpus labels keep the machine until then);
#   2. psi4 optimisations (corpus deck v1, no Hessians: psi4_worker.py with "hessians": false), four at a time × 8 threads, smallest first;
#   3. analytic labels (analytic_hessians.py, the label lanes' own call) four at a time × 8 threads, smallest first — except the two largest
#      (by atom count: C34H20 with 550 basis functions and HBC with 666), each alone on 32 threads afterwards — memory above 307 is unmeasured.
# Job files: /root/labels/large_pah/molecules/<id>/job.json, in the molecule's own folder (probes/large_pah_jobs.py's convention, run on the
# server with --deck); worker.log and labels.log beside them. Markers '=== (L5) …' in /root/labels/large_pah/run.log. Restartable: a folder with result.json "done" is not optimised again,
# one with both analytic Hessians is not labelled again.
#   setsid nohup bash /root/labels/large_pah_ccx53.sh > /root/labels/large_pah/run.log 2>&1 < /dev/null &
set -u
# no-set-e: a molecule that fails is reported and the others continue; the end marker counts the failures
cd /root/labels/large_pah || exit 1
QC=/root/miniforge3/envs/qc/bin/python
QC05=/root/miniforge3/envs/qc05/bin/python
export PYSCF_TMPDIR=/root/qc_tmp TMPDIR=/root/qc_tmp
mark() { echo "=== (L5) $* $(date '+%F %T')"; }
mark "armed: waiting for the four label lanes"
until [ "$(grep -l 'LANE [0-3] DONE' /root/labels/lane_[0-3].log 2>/dev/null | wc -l)" = 4 ]; do sleep 900; done
# smallest first: atoms per job
mapfile -t IDS < <(for j in molecules/*/job.json; do echo "$($QC05 -c "import json,sys; print(len(json.load(open(sys.argv[1]))['xyz_angstrom']))" "$j") $(basename "$(dirname "$j")")"; done | sort -n | awk '{print $2}')
mark "start: ${#IDS[@]} molecules, smallest first: ${IDS[*]}"
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
  local id=$1 threads=$2
  if [ -f "molecules/$id/hessian_b3lyp_analytic.npz" ] && [ -f "molecules/$id/hessian_wb97x_analytic.npz" ]; then echo "  $id labelled already"; return 0; fi
  [ -f "molecules/$id/geometry.json" ] || { echo "  $id LABELS SKIPPED (no optimised geometry)"; return 1; }
  local t0; t0=$(date +%s)
  if (cd /root/labels && OMP_NUM_THREADS=$threads "$QC05" analytic_hessians.py "large_pah/molecules/$id" --threads "$threads" >> "large_pah/molecules/$id/labels.log" 2>&1); then
    echo "  $id labelled $(( $(date +%s) - t0 )) s on $threads threads"
  else
    echo "  $id LABELS FAILED $(( $(date +%s) - t0 )) s (molecules/$id/labels.log)"
  fi
}
export -f opt label
export QC QC05
mark "optimisations"
printf '%s\n' "${IDS[@]}" | xargs -P 4 -I{} bash -c 'opt {}'
n=${#IDS[@]}
small=("${IDS[@]:0:$((n - 2))}"); large=("${IDS[@]:$((n - 2))}")
mark "labels: ${#small[@]} at 4 × 8 threads, then ${large[*]} alone on 32 threads"
printf '%s\n' "${small[@]}" | xargs -P 4 -I{} bash -c 'label {} 8'
for id in "${large[@]}"; do label "$id" 32; done
fails=$(grep -c 'FAILED\|SKIPPED' run.log 2>/dev/null || echo 0)
mark "all done: $fails failures or skips"
