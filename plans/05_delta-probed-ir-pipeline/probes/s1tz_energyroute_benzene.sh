#!/usr/bin/env bash
# probes/s1tz_energyroute_benzene.sh (28 Oct 2026, TASKS 53; the user: 'Ja'). The grid check left benzene's B3LYP/def2-TZVP out-of-plane
# quartics standing (φ_10,10,10,10 907.0 at 75/302, 906.5 at 99/590), and only the analytic Hessians have seen them. This reads the same
# diagonal quartics from SCF energies along the modes of the run's own reference Hessian (75/302): modes 5 and 10 (out of plane) and 11
# (in-plane control, φ 10.4), q = ±0.1 … ±0.4, 25 SCFs (probes/qff_energy_route.py). A real surface feature if the energies give ≈ 907; a wrong
# analytic Hessian off the plane if they do not. Runs ON s1 from /root/dpir_s1tz_e/probes.
#   bash s1tz_energyroute_benzene.sh --dry-run    → the same code at STO-3G on mode 11, two steps (5 SCFs, seconds), into a smoke folder
set -euo pipefail
PY=${PY:-/root/miniforge3/envs/qc05/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
REF=/root/s1tz_gridcheck/benzene/coarse
DST=/root/s1tz_energyroute/benzene
THREADS=${THREADS:-15}
mark() { echo "=== (S1TZE) $* $(date '+%F %T')"; }
[ -f "$REF/ref.json" ] || { echo "no reference Hessian at $REF/ref.json" >&2; exit 2; }
if [ "${1:-}" = "--dry-run" ]; then
  rm -rf /root/s1tz_energyroute/smoke
  OMP_NUM_THREADS=$THREADS "$PY" "$HERE/qff_energy_route.py" "$REF" /root/s1tz_energyroute/smoke --modes 11 --steps 0.1 0.2 --basis sto-3g --threads "$THREADS"
  mark "dry run done (STO-3G smoke)"
  exit 0
fi
mark "benzene T energy route: modes 5 10 11, B3LYP/def2-TZVP, grid 75,302, $THREADS threads"
OMP_NUM_THREADS=$THREADS "$PY" "$HERE/qff_energy_route.py" "$REF" "$DST" --modes 5 10 11 --basis def2-tzvp --grid 75,302 --threads "$THREADS"
mark "benzene T energy route done"
