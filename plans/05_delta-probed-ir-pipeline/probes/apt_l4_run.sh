#!/usr/bin/env bash
# probes/apt_l4_run.sh [--dry-run] (16 Oct 2026, TASKS 44's L4) — the field route (probes/apt_field_route.py, F = 1e-3, labels settings) on the
# five molecules of l4/selection.tsv, in WSL with the qc05 env, four threads for OpenMP *and* OpenBLAS (the #2702 repro showed OpenBLAS
# ignoring lib.num_threads). Geometry from the fetched copies the recompute used. A molecule whose <id>_field.npz exists is skipped
# (restartable). Markers '=== (L4) …'; the field script prints a progress line per field component.
set -euo pipefail
PLAN=$(cd "$(dirname "$0")/.." && pwd)
L4=$PLAN/probes/results_m1/apt_refine_install_2026-10-12/l4
FETCHED=${L4_FETCHED:-/home/thebreadishard/apt_recompute}
PY=${L4_PYTHON:-/home/thebreadishard/qc05/bin/python}
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
mark() { echo "=== (L4) $* $(date '+%F %T')"; }
mapfile -t IDS < <(grep -v '^#' "$L4/selection.tsv" | cut -f1)
[ "${#IDS[@]}" = 5 ] || { mark "STOPPED: ${#IDS[@]} ids in selection.tsv, the registration needs 5"; exit 1; }
geometry_dir() { for half in fetched fetched_half2; do [ -f "$FETCHED/$half/$1/geometry.json" ] && { echo "$FETCHED/$half/$1"; return 0; }; done; return 1; }
for id in "${IDS[@]}"; do geometry_dir "$id" > /dev/null || { mark "STOPPED: no geometry for $id"; exit 1; }; done
[ -x "$PY" ] || { mark "STOPPED: $PY missing"; exit 1; }
if [ "${1:-}" = "--dry-run" ]; then mark "dry run: ${#IDS[@]} molecules, geometry and python present"; exit 0; fi
mark "start: ${#IDS[@]} molecules"
for id in "${IDS[@]}"; do
  out=$L4/${id}_field.npz
  if [ -f "$out" ]; then mark "$id done earlier, skipped"; continue; fi
  mark "$id start"
  "$PY" "$PLAN/probes/apt_field_route.py" "$(geometry_dir "$id")" --out "$out" --threads 4
  mark "$id done"
done
mark "all done"
