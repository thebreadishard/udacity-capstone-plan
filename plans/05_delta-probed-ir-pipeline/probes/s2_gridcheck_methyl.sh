#!/usr/bin/env bash
# probes/s2_gridcheck_methyl.sh (3 Nov 2026, TASKS 156 (c); the user: 'begin met 156(c)'). Styrene's grid re-check (17 Oct) showed its vinyl
# NOISY flag was grid noise; the methyl class was not settled. Imidazole+CH3 (B_151c8ce719) tripped S2's noise guard on its methyl torsion
# (mode 0, 108 cm⁻¹; route disagreement 5.6 cm⁻¹ at grid 75/302, its worst pairs with modes 2, 11, 22, 24, 25, 26; probes/qff_noise_diagnosis.py).
# This recomputes, at grid 99/590 and at the same geometries, the reference and the ± displacements of those seven modes — 15 Hessians — on
# the laptop (WSL, pyscf in qc05), so that probes/qff_grid_recheck.py reads the route disagreement at both grids and
# probes/s2_gridcheck_methyl_read.py applies the rule registered in its docstring.
#   bash probes/s2_gridcheck_methyl.sh <out_dir> [--dry-run]      (--dry-run: stages the stubs and the coarse subset, computes nothing)
set -euo pipefail
PY=${PY:-$HOME/qc05/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$HERE/results_m1/s2_anharmonic_2026-10-18/s2/B_151c8ce719/G
OUT=${1:?out_dir}
THREADS=${THREADS:-6}
MODES="00 02 11 22 24 25 26"
mark() { echo "=== (S2M) $* $(date '+%F %T')"; }
[ -f "$SRC/refstub/ref.json" ] && [ -f "$SRC/refhess/ref.json" ] || { mark "STOPPED: no reference in $SRC"; exit 1; }
mkdir -p "$OUT/stubs" "$OUT/coarse_subset" "$OUT/fine_99_590"
cp "$SRC/refstub/ref.json" "$OUT/stubs/ref.json"
cp "$SRC/refhess/ref.json" "$OUT/coarse_subset/ref.json"
for m in $MODES; do
  cp "$SRC/stubs/mode${m}_p.json" "$SRC/stubs/mode${m}_m.json" "$OUT/stubs/"
  cp "$SRC/hess/mode${m}_p.json" "$SRC/hess/mode${m}_m.json" "$OUT/coarse_subset/"
done
mark "imidazole+CH3 grid check: $(ls "$OUT/stubs" | wc -l) stubs, $(ls "$OUT/coarse_subset" | wc -l) coarse Hessians staged"
[ "${2:-}" = "--dry-run" ] && { "$PY" -c 'import pyscf; print("pyscf", pyscf.__version__)'; mark "dry run done"; exit 0; }
mark "15 Hessians at grid 99,590, B3LYP/6-31G*, $THREADS threads"
OMP_NUM_THREADS=$THREADS "$PY" -u "$HERE/pyscf_hessians_for_qff.py" "$OUT/stubs" "$OUT/fine_99_590" --basis '6-31g*' --grid 99,590 \
  --threads "$THREADS"
mark "imidazole+CH3 grid check done ($(ls "$OUT/fine_99_590"/*.json | wc -l) Hessians)"
