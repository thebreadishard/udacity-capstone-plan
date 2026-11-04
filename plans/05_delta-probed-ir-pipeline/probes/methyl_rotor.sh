#!/usr/bin/env bash
# probes/methyl_rotor.sh (4 Nov 2026, TASKS 176/177; the user: 'Ja, doe optie 4 met optie 2 ernaast'). The two computations of
# GoalGathering/notes/PreRegistration_2026-11-04_Methyl_Rotor_Variational.md on the laptop (WSL, pyscf in qc05): A, the relaxed torsion scan
# of 4-methylimidazole (13 constrained optimisations, probes/methyl_torsion_scan.py, 4 lanes × 3 threads), then B, its (τ, q20, q21) grid
# (2,904 energies, probes/methyl_rotor_grid.py, 12 lanes × 1 thread). Both resume: a written point is skipped.
#   bash probes/methyl_rotor.sh <out_dir> [--smoke|--dry-run] [--tau48]   (--smoke: scan points 0 and 6, three grid points; --dry-run:
#   stage only; --tau48: no scan, the 48-point τ grid in <out_dir>/grid_tau48 seeded read only from <out_dir>/grid_tau24, TASKS 176)
set -euo pipefail
PY=${PY:-$HOME/qc05/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:?out_dir}
MODE=""; TAU48=0
for arg in "${@:2}"; do
  case "$arg" in
    --smoke|--dry-run) MODE=$arg ;;
    --tau48) TAU48=1 ;;
    *) echo "methyl_rotor.sh: unknown option $arg" >&2; exit 2 ;;
  esac
done
[ "$TAU48" = 1 ] && [ "$MODE" = "--smoke" ] && { echo "methyl_rotor.sh: --tau48 and --smoke do not combine" >&2; exit 2; }
SCAN_LANES=4; SCAN_THREADS=3; GRID_LANES=12
GDIR=$OUT/grid_tau24; grid_args=()
[ "$TAU48" = 1 ] && { GDIR=$OUT/grid_tau48; grid_args=(--n-tau 48 --reuse "$OUT/grid_tau24"); }
mark() { echo "=== (ROTOR) $* $(date '+%F %T')"; }
mkdir -p "$OUT/scan" "$GDIR"
extra=()
[ "$MODE" = "--smoke" ] && extra=(--smoke)
if [ "$MODE" = "--dry-run" ]; then
  "$PY" -u "$HERE/methyl_rotor_grid.py" "$GDIR" --dry-run "${grid_args[@]}"
  mark "dry run done"; exit 0
fi
if [ "$TAU48" = 1 ]; then
  mark "A skipped: the 48-point τ grid reuses $OUT/grid_tau24"
else
mark "A: torsion scan, $SCAN_LANES lanes × $SCAN_THREADS threads"
pids=()
for j in $(seq 0 $((SCAN_LANES - 1))); do
  OMP_NUM_THREADS=$SCAN_THREADS "$PY" -u "$HERE/methyl_torsion_scan.py" "$OUT/scan" --lane "$j" --lanes "$SCAN_LANES" \
    --threads "$SCAN_THREADS" "${extra[@]}" > "$OUT/scan/lane$j.log" 2>&1 & pids+=($!)
done
fail=0; for p in "${pids[@]}"; do wait "$p" || fail=1; done
[ "$fail" = 0 ] || { mark "STOPPED: a scan lane failed (see $OUT/scan/lane*.log)"; exit 1; }
mark "A done: $(ls "$OUT"/scan/scan_k*.json | wc -l) scan points"
fi
mark "B: grid in $GDIR, $GRID_LANES lanes × 1 thread"
pids=()
for j in $(seq 0 $((GRID_LANES - 1))); do
  OMP_NUM_THREADS=1 "$PY" -u "$HERE/methyl_rotor_grid.py" "$GDIR" --lane "$j" --lanes "$GRID_LANES" --threads 1 "${extra[@]}" \
    "${grid_args[@]}" > "$GDIR/lane$j.log" 2>&1 & pids+=($!)
done
fail=0; for p in "${pids[@]}"; do wait "$p" || fail=1; done
[ "$fail" = 0 ] || { mark "STOPPED: a grid lane failed (see $GDIR/lane*.log)"; exit 1; }
mark "methyl rotor done: $(ls "$OUT"/scan/scan_k*.json | wc -l) scan points, grid lanes $(ls "$GDIR"/energies_lane*.json | wc -l) in $GDIR"
