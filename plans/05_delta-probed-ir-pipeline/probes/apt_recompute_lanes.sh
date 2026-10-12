#!/usr/bin/env bash
# probes/apt_recompute_lanes.sh <fetched dir> <out dir> <lanes> <threads> (12 Oct 2026, TASKS 44 (b)) — runs ON the laptop in WSL, detached:
# probes/apt_recompute_refined.py over every fetched molecule folder, split round-robin into <lanes> lanes of <threads> threads each, nice 10,
# one python per molecule (a failure costs one molecule; done molecules are skipped, so a restart resumes). One line per molecule to
# <out>/lane_<n>.log; "=== (APTb) lane <n> done" at the end of each lane, "=== (APTb) all lanes done" when every lane has ended.
#   setsid nohup bash probes/apt_recompute_lanes.sh <fetched> <out> 2 4 > <out>/lanes.log 2>&1 < /dev/null &
# no-set-e: a molecule that fails is logged and its lane continues
set -u
FETCHED=${1:?fetched dir}; OUT=${2:?out dir}; LANES=${3:?lanes}; THREADS=${4:?threads}
PLAN=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PY=${PY:-$HOME/qc05/bin/python}
mkdir -p "$OUT"
mapfile -t IDS < <(cd "$FETCHED" && ls -d */ | tr -d / | sort)
echo "=== (APTb) start $(date '+%F %T'): ${#IDS[@]} molecules, $LANES lanes x $THREADS threads"
lane() {
  local n=$1 i id t0
  for ((i = n; i < ${#IDS[@]}; i += LANES)); do
    id=${IDS[$i]}; t0=$(date +%s)
    if OMP_NUM_THREADS=$THREADS nice -n 10 "$PY" "$PLAN/probes/apt_recompute_refined.py" "$FETCHED/$id" --out "$OUT" --threads "$THREADS" >> "$OUT/lane_$n.out" 2>&1; then
      echo "(APTb) lane $n $id ok $(( $(date +%s) - t0 )) s $(date '+%F %T')" >> "$OUT/lane_$n.log"
    else
      echo "(APTb) lane $n $id FAILED $(( $(date +%s) - t0 )) s $(date '+%F %T') — see lane_$n.out" >> "$OUT/lane_$n.log"
    fi
  done
  echo "=== (APTb) lane $n done $(date '+%F %T')" >> "$OUT/lane_$n.log"
}
for ((n = 0; n < LANES; n++)); do lane "$n" & done
wait
echo "=== (APTb) all lanes done $(date '+%F %T'): $(grep -c ' ok ' "$OUT"/lane_*.log | awk -F: '{s += $2} END {print s}') ok, $(cat "$OUT"/lane_*.log | grep -c ' FAILED ') failed"
