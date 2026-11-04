#!/usr/bin/env bash
# probes/methyl_rotor.sh (4 Nov 2026, TASKS 176/177; the user: 'Ja, doe optie 4 met optie 2 ernaast'). The two computations of
# GoalGathering/notes/PreRegistration_2026-11-04_Methyl_Rotor_Variational.md on the laptop (WSL, pyscf in qc05): A, the relaxed torsion scan
# of 4-methylimidazole (13 constrained optimisations, probes/methyl_torsion_scan.py, 4 lanes × 3 threads), then B, its (τ, q20, q21) grid
# (2,904 energies, probes/methyl_rotor_grid.py, 12 lanes × 1 thread). Both resume: a written point is skipped.
#   bash probes/methyl_rotor.sh <out_dir> [--smoke|--dry-run]   (--smoke: scan points 0 and 6, three grid points; --dry-run: stage only)
set -euo pipefail
PY=${PY:-$HOME/qc05/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:?out_dir}
MODE=${2:-}
SCAN_LANES=4; SCAN_THREADS=3; GRID_LANES=12
mark() { echo "=== (ROTOR) $* $(date '+%F %T')"; }
mkdir -p "$OUT/scan" "$OUT/grid"
extra=()
[ "$MODE" = "--smoke" ] && extra=(--smoke)
if [ "$MODE" = "--dry-run" ]; then
  "$PY" -u "$HERE/methyl_rotor_grid.py" "$OUT/grid" --dry-run
  mark "dry run done"; exit 0
fi
mark "A: torsion scan, $SCAN_LANES lanes × $SCAN_THREADS threads"
pids=()
for j in $(seq 0 $((SCAN_LANES - 1))); do
  OMP_NUM_THREADS=$SCAN_THREADS "$PY" -u "$HERE/methyl_torsion_scan.py" "$OUT/scan" --lane "$j" --lanes "$SCAN_LANES" \
    --threads "$SCAN_THREADS" "${extra[@]}" > "$OUT/scan/lane$j.log" 2>&1 & pids+=($!)
done
fail=0; for p in "${pids[@]}"; do wait "$p" || fail=1; done
[ "$fail" = 0 ] || { mark "STOPPED: a scan lane failed (see $OUT/scan/lane*.log)"; exit 1; }
mark "A done: $(ls "$OUT"/scan/scan_k*.json | wc -l) scan points"
mark "B: grid, $GRID_LANES lanes × 1 thread"
pids=()
for j in $(seq 0 $((GRID_LANES - 1))); do
  OMP_NUM_THREADS=1 "$PY" -u "$HERE/methyl_rotor_grid.py" "$OUT/grid" --lane "$j" --lanes "$GRID_LANES" --threads 1 "${extra[@]}" \
    > "$OUT/grid/lane$j.log" 2>&1 & pids+=($!)
done
fail=0; for p in "${pids[@]}"; do wait "$p" || fail=1; done
[ "$fail" = 0 ] || { mark "STOPPED: a grid lane failed (see $OUT/grid/lane*.log)"; exit 1; }
mark "methyl rotor done: $(ls "$OUT"/scan/scan_k*.json | wc -l) scan points, grid lanes $(ls "$OUT"/grid/energies_lane*.json | wc -l)"
