#!/usr/bin/env bash
# probes/s1tz_gridcheck_benzene.sh (28 Oct 2026, TASKS 53; the user: 'Ja'). S1-TZ's read said 'the basis matters', but only the out-of-plane
# modes moved (+41 to +251 cm⁻¹, positive anharmonic shifts) while the in-plane ones agree with G to ≈ 1 cm⁻¹: suspected grid noise in the
# diagonal quartics, which the grid gate (harmonic ω only) and the two-route guard (a systematic error) cannot see. This recomputes, at grid
# 99/590 and at the same geometries, the ± displacements of benzene's two worst out-of-plane modes (5: ω 717, +127; 10: ω 992, +251) and one
# in-plane control (11: ω 1016, −17.5) — 6 Hessians; the 99/590 reference Hessian exists already (the grid gate's refhess_gate). Then
# probes/qff_grid_recheck.py reads φ_iiii and φ_iijj at both grids: grid noise if the out-of-plane ones fall to G's size, the basis if they stay.
# The pattern of probes/s2_gridcheck_styrene.sh (17 Oct: styrene's NOISY flag was grid noise). Runs ON s1 from /root/dpir_s1tz/probes.
#   bash s1tz_gridcheck_benzene.sh --dry-run    → copies the stubs and the reference; computes nothing
set -euo pipefail
PY=${PY:-/root/miniforge3/envs/qc05/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=/root/s1tz/A_8448043181/T
DST=/root/s1tz_gridcheck/benzene
MODES="05 10 11"
THREADS=${THREADS:-15}
mark() { echo "=== (S1TZG) $* $(date '+%F %T')"; }
mkdir -p "$DST/stubs" "$DST/hess" "$DST/coarse"
for m in $MODES; do
  cp "$SRC/stubs/mode${m}_p.json" "$SRC/stubs/mode${m}_m.json" "$DST/stubs/"
  cp "$SRC/hess/mode${m}_p.json" "$SRC/hess/mode${m}_m.json" "$DST/coarse/"
done
cp "$SRC/refhess/ref.json" "$DST/coarse/ref.json"        # 75/302, the run's grid
cp "$SRC/refhess_gate/ref.json" "$DST/hess/ref.json"     # 99/590, the grid gate's Hessian at the same geometry
mark "benzene T grid check: $(ls "$DST/stubs" | wc -l) stubs, coarse $(ls "$DST/coarse" | wc -l) files, fine reference copied"
[ "${1:-}" = "--dry-run" ] && exit 0
mark "6 Hessians at B3LYP/def2-TZVP, grid 99,590, $THREADS threads"
OMP_NUM_THREADS=$THREADS "$PY" "$HERE/pyscf_hessians_for_qff.py" "$DST/stubs" "$DST/hess" --basis def2-tzvp --grid 99,590 --threads "$THREADS"
mark "benzene T grid check done ($(ls "$DST/hess" | grep -c '\.json$') Hessians)"
