#!/usr/bin/env bash
# probes/l5_apt_field_run.sh [--dry-run] (31 Oct 2026, TASKS 49; chain 42's registered risk 4) — the field route (probes/apt_field_route.py,
# label settings) for every large PAH whose labels-route APT failed its checks, at F = 1e-3 and 2e-3 (Richardson, as L4's D1 of 16 Oct), in
# WSL with the qc05 env, under a cgroup cap (probes/wsl_capped.sh), the thread count for OpenMP *and* OpenBLAS (the #2702 repro showed
# OpenBLAS ignoring lib.num_threads). ids.tsv is read again before each step, so a molecule found failing later (coronene, at l5_small's end)
# can be appended while the run goes on. An output that exists is skipped and an unfinished one resumes from its checkpoint (restartable).
# Markers '=== (L5F) …'; the field script prints a line per field sign and per component.
set -euo pipefail
PLAN=$(cd "$(dirname "$0")/.." && pwd)
DIR=${L5F_DIR:-$PLAN/probes/results_m1/l5_apt_field_2026-10-31}
PY=${L5F_PYTHON:-/home/thebreadishard/qc05/bin/python}
THREADS=${L5F_THREADS:-8}
CAP_MB=${L5F_CAP_MB:-8192}
GRID=${L5F_GRID:-99,590}
FIELDS=(1e-3 2e-3)
export OMP_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS
mark() { echo "=== (L5F) $* $(date '+%F %T')"; }
ids() { grep -v '^#' "$DIR/ids.tsv" | cut -f1 | grep -v '^$' || true; }
next_step() {   # the first molecule and field without an output
  local id f
  for id in $(ids); do for f in "${FIELDS[@]}"; do [ -f "$DIR/$id/field_F$f.npz" ] || { echo "$id $f"; return 0; }; done; done
  return 1
}
DRY=0
case ${1:-} in --dry-run) DRY=1 ;; "") ;; *) mark "STOPPED: unknown argument $1"; exit 1 ;; esac
[ -x "$PY" ] || { mark "STOPPED: $PY missing"; exit 1; }
[ -f "$DIR/ids.tsv" ] || { mark "STOPPED: no $DIR/ids.tsv"; exit 1; }
[ -n "$(ids)" ] || { mark "STOPPED: ids.tsv lists no molecule"; exit 1; }
for id in $(ids); do [ -f "$DIR/$id/geometry.json" ] || { mark "STOPPED: no geometry for $id"; exit 1; }; done
if [ "$DRY" = 1 ]; then mark "dry run: $(ids | wc -l) molecules at F = ${FIELDS[*]}, grid $GRID, geometry and python present"; exit 0; fi
mark "start: $(ids | wc -l) molecules at F = ${FIELDS[*]}, grid $GRID, $THREADS threads, cap $CAP_MB MB"
while step=$(next_step); do
  read -r id f <<< "$step"
  [ -f "$DIR/$id/geometry.json" ] || { mark "STOPPED: no geometry for $id"; exit 1; }
  mark "$id F=$f start"
  rc=0
  bash "$PLAN/probes/wsl_capped.sh" "$CAP_MB" -- "$PY" "$PLAN/probes/apt_field_route.py" "$DIR/$id" --out "$DIR/$id/field_F$f.npz" \
    --field "$f" --grid "$GRID" --threads "$THREADS" --max-memory $((CAP_MB * 3 / 4)) --checkpoint "$DIR/$id/field_F$f.partial.npz" || rc=$?
  [ "$rc" = 0 ] || { mark "STOPPED: $id F=$f failed (exit $rc)"; exit 1; }
  [ -f "$DIR/$id/field_F$f.npz" ] || { mark "STOPPED: $id F=$f exited 0 without its output"; exit 1; }
  mark "$id F=$f done"
done
mark "all done"
