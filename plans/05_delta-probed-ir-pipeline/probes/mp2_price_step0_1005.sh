#!/usr/bin/env bash
# mp2_price_step0_1005.sh (5 Oct 2026, 08:2x). Registration 2, step 0 of GoalGathering/notes/Design_2026-10-05_Analytic_Labels_and_Stepping_Stone.md: the
# price of an MP2 Hessian at the corpus basis (6-31G*, Cartesian d, frozen core) by finite differences of analytic gradients over the symmetry-unique
# displacements (`probes/cc_composite_full_check.py compute --cart`), on five done pool molecules of 12–30 atoms, 2 threads each, sequential. Output:
# one npz of rows per molecule in probes/results_m1/mp2_step0_2026-10-05/ and the per-displacement timings in this log; the read is seconds per molecule
# against the registered line (above 2 h per molecule on 8 threads the stone is priced out for the pool). Runs inside WSL (qc05), detached:
#   wsl -e bash -c 'cd /mnt/c/.../05_delta-probed-ir-pipeline && setsid nohup bash probes/mp2_price_step0_1005.sh > probes/results_m1/mp2_step0_2026-10-05.log 2>&1 < /dev/null & disown'
set -uo pipefail
# no-set-e: each molecule records its own marker; a failed one does not stop the next
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp
mkdir -p "$HOME/qc_tmp"
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
OUT=$P/probes/results_m1/mp2_step0_2026-10-05
mkdir -p "$OUT"
cd "$P" || exit 1
for ID in A_8448043181 A_01f3186607 A_fdc27f1bd1 A_428228e5a5 A2_02c8833bd5; do
  G=$P/modules/05_support_predictor/corpus/molecules/$ID/geometry.json
  t0=$(date +%s)
  echo "=== step 0: $ID start $(date '+%F %T')"
  if OMP_NUM_THREADS=2 ~/qc05/bin/python probes/cc_composite_full_check.py compute "$G" "$OUT/mp2_rows_${ID}_631gs.npz" --basis 6-31g* --cart --threads 2 --max-memory 6000; then
    echo "=== step 0: $ID done in $(( $(date +%s) - t0 )) s at 2 threads $(date '+%F %T')"
  else
    echo "=== step 0: $ID FAILED after $(( $(date +%s) - t0 )) s $(date '+%F %T')"
  fi
done
echo "=== step 0: all five molecules done $(date '+%F %T')"
