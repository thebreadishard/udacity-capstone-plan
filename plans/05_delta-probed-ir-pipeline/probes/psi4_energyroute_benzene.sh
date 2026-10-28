#!/usr/bin/env bash
# probes/psi4_energyroute_benzene.sh <out_dir> [--dry-run] (28 Oct 2026, TASKS 53; the user: 'Ja, eerst psi4'). pyscf's energies along
# benzene's modes confirmed its analytic Hessians (φ_10,10,10,10 933.1 against 907.0), so the large out-of-plane quartics are pyscf's
# B3LYP/def2-TZVP surface. This computes the same energies in psi4 (probes/qff_energy_route.py --program psi4): modes 5, 10 (out of plane)
# and 11 (in-plane control) along the modes of the s1tz reference Hessian, q = ±0.1 … ±0.4, 25 SCFs at grid 99/590 (pyscf's Hessian
# quartics are the same at 75/302 and 99/590). The level of theory if psi4 gives ≈ 933 too; pyscf's implementation if it does not.
# Runs in WSL inside probes/wsl_capped.sh, with the vpt2 environment's psi4 1.10.
#   --dry-run → the same code at STO-3G on mode 11, three steps (7 SCFs), into <out_dir>/smoke
set -euo pipefail
PY=${PY:-$HOME/miniforge3/envs/vpt2/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
REF=$HERE/results_m1/s1tz_gridcheck_2026-10-28/s1tz_gridcheck/benzene/coarse
OUT=${1:?out_dir}
THREADS=${THREADS:-8}
mark() { echo "=== (P4E) $* $(date '+%F %T')"; }
[ -f "$REF/ref.json" ] || { echo "no reference Hessian at $REF/ref.json" >&2; exit 2; }
if [ "${2:-}" = "--dry-run" ]; then
  rm -rf "$OUT/smoke"
  "$PY" -u "$HERE/qff_energy_route.py" "$REF" "$OUT/smoke" --program psi4 --modes 11 --steps 0.1 0.2 0.3 --basis sto-3g --grid 99,590 --threads "$THREADS"
  mark "dry run done (STO-3G smoke)"
  exit 0
fi
mark "benzene energy route in psi4: modes 5 10 11, B3LYP/def2-TZVP, grid 99,590, $THREADS threads"
"$PY" -u "$HERE/qff_energy_route.py" "$REF" "$OUT/benzene" --program psi4 --modes 5 10 11 --basis def2-tzvp --grid 99,590 --threads "$THREADS"
mark "benzene psi4 energy route done"
