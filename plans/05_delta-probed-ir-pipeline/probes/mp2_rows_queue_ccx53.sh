#!/usr/bin/env bash
# mp2_rows_queue_ccx53.sh (7 Oct 2026; TASKS 28). The MP2 basis step for every cc-pVDZ anchor: MP2 rows at cc-pVDZ and cc-pVTZ for each
# symmetry-unique displacement, as a queue of single-displacement jobs pulled by W workers (8 threads each), so the CCX53 stays evenly loaded and a
# restart loses at most the jobs in flight (a job whose rows file exists is skipped; a job is claimed by an atomic mkdir).
# Inputs in ~/e8/composite: jobs.txt (one line per job: name|mol_id|basis|k|geometry file, largest first; written on the laptop by
# probes/mp2_rows_jobs.py), the geometries, cc_composite_full_check.py, cc_composite_basis_check.py, e8_symmetry.py.
# Outputs: rows/<name>_<basis>_k<k>.npz; at the end merged files mp2_rows_<name>_<basis>.npz (anthracene: with the out-of-plane rows of test 3).
# Markers in ~/e8/composite/queue.log: "=== QUEUE DONE" or "=== QUEUE FAILED"; hourly heartbeat lines.
#   cd ~/e8/composite && nohup setsid bash mp2_rows_queue_ccx53.sh 4 26000 >> queue.log 2>&1 < /dev/null &
set -uo pipefail
# no-set-e: workers record failures per job; the merge decides the end marker
W=${1:-4}
MEM=${2:-26000}
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp
mkdir -p "$HOME/qc_tmp"
D=$HOME/e8/composite
PY=/root/miniforge3/envs/qc05/bin/python
cd "$D" || exit 1
mkdir -p rows locks
t() { date -u '+%F %T UTC'; }
grep -q $'' jobs.txt && { echo "=== QUEUE REFUSED: jobs.txt has CR line endings $(t)"; exit 1; }
echo "=== QUEUE start: $(grep -c . jobs.txt) jobs, $W workers x 8 threads, max_memory $MEM $(t)"

worker() {
  local w=$1 name mol basis k geom out
  while IFS='|' read -r name mol basis k geom; do
    [ -z "$name" ] && continue
    out=rows/${name}_${basis/-/}_k${k}.npz
    [ -f "$out" ] && continue
    mkdir "locks/${name}_${basis}_${k}" 2>/dev/null || continue
    if OMP_NUM_THREADS=8 $PY cc_composite_full_check.py compute "$geom" "$out.part.npz" --basis "$basis" --threads 8 --max-memory "$MEM" --ks "$k" \
         >> "worker_$w.log" 2>&1; then
      mv "$out.part.npz" "$out"
    else
      echo "--- job FAILED: $name $basis k=$k (worker $w) $(t)"; rm -f "$out.part.npz"
    fi
  done < jobs.txt
}

pids=()
for ((i = 0; i < W; i++)); do worker "$i" & pids+=($!); sleep 3; done
( while true; do
    sleep 3600
    alive=0; for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive=$((alive + 1)); done
    [ "$alive" -eq 0 ] && break
    echo "--- heartbeat $(t): $(ls rows/*.npz 2>/dev/null | grep -vc part) of $(grep -c . jobs.txt) jobs done; $alive workers; $(free -g | awk '/Mem:/{print $7 " GB free"}')"
  done ) &
HB=$!
for p in "${pids[@]}"; do wait "$p"; done
pkill -P "$HB" 2>/dev/null; kill "$HB" 2>/dev/null   # the heartbeat and its sleep must not hold the log open after the workers end (smoke test, 7 Oct)

missing=0
while IFS='|' read -r name mol basis k geom; do
  [ -f "rows/${name}_${basis/-/}_k${k}.npz" ] || missing=$((missing + 1))
done < jobs.txt
if [ "$missing" -gt 0 ]; then echo "=== QUEUE FAILED: $missing jobs without rows $(t)"; exit 1; fi
rc=0
for nb in $(cut -d'|' -f1,3 jobs.txt | sort -u); do
  name=${nb%%|*}; basis=${nb##*|}; b=${basis/-/}
  extra=""
  [ "$name" = "anthracene" ] && extra="mp2_rows_anthracene_oop_${b}.npz"
  # shellcheck disable=SC2086   # extra is one optional file name
  $PY cc_composite_full_check.py merge "mp2_rows_${name}_${b}.npz" rows/${name}_${b}_k*.npz $extra || rc=1
done
[ "$rc" -eq 0 ] && echo "=== QUEUE DONE — fetch mp2_rows_*_cc{pvdz,pvtz}.npz and build the composites $(t)" || echo "=== QUEUE FAILED: merge $(t)"
