#!/usr/bin/env bash
# probes/cation_ccx53.sh <ids file> (25 Oct 2026; TASKS 121, the user: 'akkoord met de CCX53 na de labels') — the pool 3 cations the laptop's
# 12 GiB cap could not hold (fluoranthene⁺ was OOM-killed at 12.5 GB in the CPHF stage, which does not keep to pyscf's max_memory), on the
# labels CCX53 once its four label lanes are DONE. Runs from the deploy folder (the plan's layout; probes/deploy_cations_ccx53.sh puts it and
# the molecule folders there):
#   - waits until /root/labels/lane_0..3.log each say 'LANE <n> DONE', with a heartbeat line every WAIT_S seconds;
#   - LANES lanes of THREADS threads take molecules from the ids file (largest first, so the lanes finish together) through a flock'ed
#     counter; each molecule runs analytic_hessians.py (UKS doublet, both functionals, the labels route) under probes/wsl_capped.sh with a
#     system scope capped at CAP_MB, pyscf's max_memory PYSCF_MB below it, and /usr/bin/time's max RSS per molecule;
#   - a molecule killed at the cap is named as such (probes/cation_oom_check.sh against the system journal, tag CX) and its lane goes on;
#   - one marker line per molecule '(CX) <id> done|KILLED|FAILED', a running heartbeat every BEAT_S seconds, '=== (CX) run done' at the end.
# Molecules whose two analytic Hessians exist already are skipped, so a relaunch resumes.
#   bash probes/cation_ccx53.sh probes/results_m1/cation_ccx53_2026-10-25/ids.tsv [--dry-run]
set -uo pipefail
# no-set-e: every molecule's failure is named and the lane goes on; the run's exit says whether any failed
IDS=${1:?ids file (id TAB basis functions TAB atoms), largest first}
HERE=$(cd "$(dirname "$0")/.." && pwd)
MOL=${MOL:-$HERE/molecules}
WORK=${WORK:-$HERE}                      # the queue counter and the lane logs
LABELS=${LABELS:-/root/labels}
LANES=${LANES:-4}
THREADS=${THREADS:-8}
CAP_MB=${CAP_MB:-26624}
PYSCF_MB=${PYSCF_MB:-24000}
PY=${PY:-/root/miniforge3/envs/qc05/bin/python}
WAIT_S=${WAIT_S:-900}
BEAT_S=${BEAT_S:-1800}
CAPPED=${CAPPED:-$HERE/probes/wsl_capped.sh}           # overridable for tests (no systemd there)
OOM_CHECK=${OOM_CHECK:-$HERE/probes/cation_oom_check.sh}
t() { date '+%F %T'; }
mapfile -t TODO < <(awk -F'\t' 'NF && $1 !~ /^#/ {print $1}' "$IDS" | tr -d '\r')
[ "${#TODO[@]}" -gt 0 ] || { echo "=== (CX) STOPPED: no ids in $IDS $(t)"; exit 1; }
for id in "${TODO[@]}"; do
  [ -f "$MOL/$id/geometry.json" ] || { echo "=== (CX) STOPPED: $MOL/$id/geometry.json missing $(t)"; exit 1; }
done
done_both() { [ -f "$MOL/$1/hessian_wb97x_analytic.npz" ] && [ -f "$MOL/$1/hessian_b3lyp_analytic.npz" ]; }
if [ "${2:-}" = "--dry-run" ]; then
  left=0; for id in "${TODO[@]}"; do done_both "$id" || left=$((left + 1)); done
  echo "dry run: ${#TODO[@]} cations listed, $left to compute; $LANES lanes × $THREADS threads, cap $CAP_MB MB (pyscf $PYSCF_MB MB); python $PY"
  exit 0
fi

echo "=== (CX) armed: ${#TODO[@]} cations, $LANES lanes × $THREADS threads, cap $CAP_MB MB (pyscf $PYSCF_MB MB), after the four label lanes $(t)"
until [ "$(grep -l 'LANE [0-3] DONE' "$LABELS"/lane_[0-3].log 2>/dev/null | wc -l)" = 4 ]; do
  echo "=== (CX) waiting: $(grep -l 'LANE [0-3] DONE' "$LABELS"/lane_[0-3].log 2>/dev/null | wc -l) of 4 label lanes done $(t)"
  sleep "$WAIT_S"
done
echo "=== (CX) start: the label lanes are done $(t)"

COUNTER=$WORK/cx_next.counter
echo 0 > "$COUNTER"
next_index() {   # the next queue index, shared by the lanes
  ( flock 9; i=$(cat "$COUNTER"); echo $((i + 1)) > "$COUNTER"; echo "$i" ) 9> "$COUNTER.lock"
}

lane() {   # $1 = lane number
  local n=$1 i id
  while :; do
    i=$(next_index)
    [ "$i" -lt "${#TODO[@]}" ] || break
    id=${TODO[$i]}
    if done_both "$id"; then echo "(CX) $id skipped: both analytic Hessians exist (lane $n) $(t)"; continue; fi
    echo "(CX) $id start (lane $n, $((i + 1)) of ${#TODO[@]}) $(t)"
    if ( cd "$HERE/modules/05_support_predictor/corpus" && \
         OMP_NUM_THREADS=$THREADS PYSCF_TMPDIR=${QC_TMP:-/root/qc_tmp} TMPDIR=${QC_TMP:-/root/qc_tmp} PYTHONUNBUFFERED=1 CAP_SCOPE=system \
         bash "$CAPPED" "$CAP_MB" -- /usr/bin/time -f "(CX) $id max RSS %M kB, wall %e s" \
         "$PY" analytic_hessians.py "$MOL/$id" --threads "$THREADS" --charge 1 --spin 1 --max-memory "$PYSCF_MB" --reuse-existing ) \
         >> "$WORK/cx_lane_$n.log" 2>&1; then
      echo "(CX) $id done (lane $n) $(t) - $(grep -a "(CX) $id max RSS" "$WORK/cx_lane_$n.log" | tail -n 1)"
    elif OOM_TAG=CX OOM_JOURNAL=system bash "$OOM_CHECK" "$id" >> "$WORK/cx_lane_$n.log" 2>&1; then
      echo "(CX) $id KILLED at the cap of $CAP_MB MB (lane $n) $(t)"
    else
      echo "(CX) $id FAILED (lane $n) $(t) - see cx_lane_$n.log"
    fi
  done
  echo "(CX) lane $n finished $(t)"
}

beat() {   # a progress line while the lanes compute (pyscf 2.14 writes nothing during the CPHF, TASKS 109)
  while sleep "$BEAT_S" < /dev/null > /dev/null 2>&1; do   # the sleep holds no pipe of the run's output
    echo "=== (CX) running: $(cat "$COUNTER") of ${#TODO[@]} taken; $(ls "$MOL"/*/hessian_wb97x_analytic.npz 2>/dev/null | wc -l) with ωB97X done $(t)"
  done
}

mkdir -p "${QC_TMP:-/root/qc_tmp}"
beat & BEAT_PID=$!
LANE_PIDS=()
for n in $(seq 0 $((LANES - 1))); do lane "$n" & LANE_PIDS+=($!); done
wait "${LANE_PIDS[@]}"
kill "$BEAT_PID" 2> /dev/null
ok=0; for id in "${TODO[@]}"; do done_both "$id" && ok=$((ok + 1)); done
echo "=== (CX) run done: $ok of ${#TODO[@]} cations with both analytic Hessians $(t)"
[ "$ok" = "${#TODO[@]}" ]
