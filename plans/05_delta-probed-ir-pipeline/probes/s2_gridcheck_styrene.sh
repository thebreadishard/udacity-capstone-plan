#!/usr/bin/env bash
# probes/s2_gridcheck_styrene.sh (15 Oct 2026, TASKS 62; the user: 'Doe de roostertoets van styreen maar op hel1-6, als dat geen lopende run
# schaadt'). Styrene tripped S2's noise guard on its vinyl torsion (route disagreement 10.7 cm⁻¹ at grid 75/302; probes/qff_noise_diagnosis.py).
# This recomputes, at grid 99/590 and at the same geometries, the reference and the ± displacements of the modes in its worst constants
# (0, 1, 4, 5, 18, 33) — 13 Hessians — so that probes/qff_grid_recheck.py can read the route disagreement at both grids: grid noise if it falls
# well below the guard, the large-amplitude torsion if it stays. It harms no running run: it waits until every S2 molecule has started and fewer
# than three S2 molecule pipelines run (a lane is free), then uses that lane's 5 threads. Runs ON s1 from /root/dpir_s2/probes.
#   bash s2_gridcheck_styrene.sh --dry-run    → copies the stubs and prints the condition; computes nothing
set -euo pipefail
PY=${PY:-/root/miniforge3/envs/qc05/bin/python}
SRC=/root/s2/A_8f6ed7c002/G
DST=/root/s2_gridcheck/styrene
LOG=/root/dpir_s2/s2.log
N_MOL=${N_MOL:-19}                      # S2's molecule count ('=== (S2) start: 19 molecules')
MODES="00 01 04 05 18 33"
mark() { echo "=== (S2G) $* $(date '+%F %T')"; }
started() { grep -cE '^=== \(S2\) [A-Za-z0-9]+_[0-9a-f]+: start ' "$LOG" || true; }
lanes() { pgrep -fc '^bash /root/dpir_s2/probes/s1_anharmonic_level\.sh ' || true; }
mkdir -p "$DST/stubs" "$DST/hess"
cp "$SRC/refstub/ref.json" "$DST/stubs/ref.json"
for m in $MODES; do cp "$SRC/stubs/mode${m}_p.json" "$SRC/stubs/mode${m}_m.json" "$DST/stubs/"; done
mark "styrene grid check: $(ls "$DST/stubs" | wc -l) stubs; S2 started $(started)/$N_MOL, lanes busy $(lanes)"
[ "${1:-}" = "--dry-run" ] && exit 0
until [ "$(started)" -ge "$N_MOL" ] && [ "$(lanes)" -lt 3 ]; do sleep 600; done
mark "a lane is free (S2 started $(started), lanes busy $(lanes)); 13 Hessians at grid 99,590, 5 threads"
OMP_NUM_THREADS=5 "$PY" /root/dpir_s2/probes/pyscf_hessians_for_qff.py "$DST/stubs" "$DST/hess" --basis '6-31g*' --grid 99,590 --threads 5
mark "styrene grid check done ($(ls "$DST/hess" | wc -l) Hessians)"
