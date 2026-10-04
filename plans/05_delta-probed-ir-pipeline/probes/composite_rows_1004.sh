#!/usr/bin/env bash
# composite_rows_1004.sh (4 Oct 2026, 16:5x). Test 2 of the composite anchor level: the MP2 (frozen core) Hessian rows of benzene's six symmetry-unique
# displacements at cc-pVDZ and then cc-pVTZ (`probes/cc_composite_full_check.py compute`), 4 threads beside chain 34 step 3. Runs inside WSL (qc05):
#   wsl -e bash -c 'cd /mnt/c/.../05_delta-probed-ir-pipeline && setsid nohup bash probes/composite_rows_1004.sh > probes/results_m1/composite_mp2_rows_benzene_2026-10-04.log 2>&1 < /dev/null & disown'
set -uo pipefail
# no-set-e: each basis records its own marker; the TZ rows are still wanted when the DZ step had a problem
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp
mkdir -p "$HOME/qc_tmp"
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
G=$P/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json
cd "$P" || exit 1
for B in cc-pvdz cc-pvtz; do
  OUT=$P/probes/results_m1/composite_mp2_rows_benzene_${B/-/}_2026-10-04.npz
  if OMP_NUM_THREADS=4 ~/qc05/bin/python probes/cc_composite_full_check.py compute "$G" "$OUT" --basis "$B" --threads 4 --max-memory 12000; then
    echo "=== composite rows $B done at $(date +%T)"
  else
    echo "=== composite rows $B FAILED at $(date +%T)"
  fi
done
echo "=== composite rows all done at $(date +%T)"
