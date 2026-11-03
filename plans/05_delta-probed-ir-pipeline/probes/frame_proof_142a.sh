#!/usr/bin/env bash
# TASKS 142(a), the proof of the 28 Oct lead: psi4 turns its DFT grid with the nuclear-charge frame, and its energies along benzene's
# modes miss where that frame turns (modes 5 and 11) and not where it stays (mode 10). pyscf keeps its grid in the laboratory frame; the
# same 25 energies at B3LYP/STO-3G, 99/590, computed twice by pyscf, once as they are (--frame lab) and once with every geometry moved into
# its own charge frame (--frame charge, the grid then turns with the atoms as psi4's does). Read by probes/frame_proof_142a_read.py.
#   bash probes/frame_proof_142a.sh <out_dir> [--dry-run]
set -euo pipefail
PY=${PY:-$HOME/qc05/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
REF=$HERE/results_m1/s1tz_gridcheck_2026-10-28/s1tz_gridcheck/benzene/coarse
OUT=${1:?out_dir}
THREADS=${THREADS:-6}
mark() { echo "=== (P142) $* $(date '+%F %T')"; }
[ -f "$REF/ref.json" ] || { echo "no reference Hessian at $REF/ref.json" >&2; exit 2; }
if [ "${2:-}" = "--dry-run" ]; then
  for frame in lab charge; do
    rm -rf "$OUT/smoke_$frame"
    "$PY" -u "$HERE/qff_energy_route.py" "$REF" "$OUT/smoke_$frame" --modes 11 --steps 0.1 0.2 0.3 --basis sto-3g --grid 99,590 \
      --frame "$frame" --threads "$THREADS"
  done
  mark "dry run done (mode 11, three steps, both frames)"
  exit 0
fi
for frame in lab charge; do
  mark "pyscf energy route, frame $frame: modes 5 10 11, B3LYP/STO-3G, 99/590, $THREADS threads"
  "$PY" -u "$HERE/qff_energy_route.py" "$REF" "$OUT/$frame" --modes 5 10 11 --basis sto-3g --grid 99,590 --frame "$frame" --threads "$THREADS"
done
mark "frame proof done"
