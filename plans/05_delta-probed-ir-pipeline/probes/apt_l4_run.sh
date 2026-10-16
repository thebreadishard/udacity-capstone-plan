#!/usr/bin/env bash
# probes/apt_l4_run.sh [--dry-run] [--field F --only ID] (16 Oct 2026, TASKS 44's L4) — the field route (probes/apt_field_route.py, labels
# settings) on the five molecules of l4/selection.tsv, in WSL with the qc05 env, four threads for OpenMP *and* OpenBLAS (the #2702 repro
# showed OpenBLAS ignoring lib.num_threads). Geometry from the fetched copies the recompute used. A molecule whose output exists is skipped
# (restartable). Markers '=== (L4) …'; the field script prints a progress line per field component.
# --field F --only ID (diagnosis D1 of L4's miss): one selected molecule at another field, written to <ID>_field_F<F>.npz, markers '(L4D)'.
set -euo pipefail
PLAN=$(cd "$(dirname "$0")/.." && pwd)
L4=$PLAN/probes/results_m1/apt_refine_install_2026-10-12/l4
FETCHED=${L4_FETCHED:-/home/thebreadishard/apt_recompute}
PY=${L4_PYTHON:-/home/thebreadishard/qc05/bin/python}
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
DRY=0; FIELD=1e-3; ONLY=""; TAG=L4
mark() { echo "=== ($TAG) $* $(date '+%F %T')"; }
while [ $# -gt 0 ]; do
  case $1 in
    --dry-run) DRY=1 ;;
    --field) FIELD=${2:?--field needs a value}; shift ;;
    --only) ONLY=${2:?--only needs an id}; TAG=L4D; shift ;;
    *) mark "STOPPED: unknown argument $1"; exit 1 ;;
  esac
  shift
done
mapfile -t IDS < <(grep -v '^#' "$L4/selection.tsv" | cut -f1)
[ "${#IDS[@]}" = 5 ] || { mark "STOPPED: ${#IDS[@]} ids in selection.tsv, the registration needs 5"; exit 1; }
if [ -n "$ONLY" ]; then
  printf '%s\n' "${IDS[@]}" | grep -qx "$ONLY" || { mark "STOPPED: $ONLY is not in selection.tsv"; exit 1; }
  IDS=("$ONLY")
fi
geometry_dir() { for half in fetched fetched_half2; do [ -f "$FETCHED/$half/$1/geometry.json" ] && { echo "$FETCHED/$half/$1"; return 0; }; done; return 1; }
out_file() { if [ "$FIELD" = 1e-3 ]; then echo "$L4/$1_field.npz"; else echo "$L4/$1_field_F$FIELD.npz"; fi; }
for id in "${IDS[@]}"; do geometry_dir "$id" > /dev/null || { mark "STOPPED: no geometry for $id"; exit 1; }; done
[ -x "$PY" ] || { mark "STOPPED: $PY missing"; exit 1; }
if [ "$DRY" = 1 ]; then mark "dry run: ${#IDS[@]} molecules at F = $FIELD, geometry and python present"; exit 0; fi
mark "start: ${#IDS[@]} molecules at F = $FIELD"
for id in "${IDS[@]}"; do
  out=$(out_file "$id")
  if [ -f "$out" ]; then mark "$id done earlier, skipped"; continue; fi
  mark "$id start"
  "$PY" "$PLAN/probes/apt_field_route.py" "$(geometry_dir "$id")" --out "$out" --field "$FIELD" --threads 4
  mark "$id done"
done
mark "all done"
