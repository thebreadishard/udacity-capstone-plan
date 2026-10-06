#!/usr/bin/env bash
# mp2_price_step0b_1005.sh (5 Oct 2026, 12:1x). Step 0 of registration 2, second half: the two large molecules priced from four symmetry-unique
# displacements each instead of all of them — the price per molecule is (seconds per displacement) × (number of unique displacements), which four
# displacements measure as well as all do, and the full run of a C1 molecule of 30 atoms would have held two laptop lanes for a day. Prints the number of
# unique displacements for the extrapolation. 2 threads, sequential, WSL (qc05):
#   setsid nohup bash probes/mp2_price_step0b_1005.sh >> probes/results_m1/mp2_step0_2026-10-05.log 2>&1 < /dev/null & disown
set -uo pipefail
# no-set-e: each molecule records its own marker
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
OUT=$P/probes/results_m1/mp2_step0_2026-10-05
cd "$P" || exit 1
IDS=${*:-A_428228e5a5 A2_02c8833bd5}   # 6 Oct 2026: ids as arguments; default = both large molecules
for ID in $IDS; do
  G=$P/modules/05_support_predictor/corpus/molecules/$ID/geometry.json
  NU=$(~/qc05/bin/python - "$G" <<'PYEOF'
import json, sys
import numpy as np
sys.path.insert(0, "probes")
import e8_symmetry as SYM
g = json.load(open(sys.argv[1]))
sym = [s.capitalize() for s in g["symbols"]]; x0 = np.asarray(g["coords_bohr"], float)
ops = SYM.point_group_ops(sym, x0); ks, reps = SYM.unique_displacements(ops, len(sym))
print(len(ks), ",".join(str(k) for k in ks[:4]))
PYEOF
)
  N=${NU%% *}; KS=${NU##* }
  t0=$(date +%s)
  echo "=== step 0b: $ID start — $N symmetry-unique displacements, timing the first four ($KS) $(date '+%F %T')"
  if OMP_NUM_THREADS=2 ~/qc05/bin/python probes/cc_composite_full_check.py compute "$G" "$OUT/mp2_rows_${ID}_631gs_first4.npz" --basis 6-31g* --cart --threads 2 --max-memory 4000 --ks "$KS"; then
    dt=$(( $(date +%s) - t0 ))
    echo "=== step 0b: $ID four displacements in $dt s at 2 threads → whole molecule ≈ $(( dt * N / 4 )) s at 2 threads $(date '+%F %T')"
  else
    echo "=== step 0b: $ID FAILED $(date '+%F %T')"
  fi
done
echo "=== step 0b: priced $IDS (four displacements each) $(date '+%F %T')"
