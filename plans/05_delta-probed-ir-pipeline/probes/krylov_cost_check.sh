#!/usr/bin/env bash
# probes/krylov_cost_check.sh <cap MB> <threads> <geometry.json> <out dir> -- <E8 arguments> (TASKS 133) — E8's reference gradient twice in
# WSL under probes/wsl_capped.sh with qc05's pyscf 2.14.0 and the CPHF residuals recorded (probes/krylov_cost_check.py): the released CPHF,
# then master's (~/pyscf-wt-base: #3333's lindep in cphf and krylov, swapped in for the Z-vector solve only), then
# probes/krylov_cost_compare.py. Paths are WSL paths (/mnt/c/...).
#   bash probes/krylov_cost_check.sh 8192 8 /mnt/c/.../geometry.json /mnt/c/.../out -- --basis cc-pvdz --fast-t-density --fast-t-lambda
set -euo pipefail
CAP=${1:?cap in MB}; THREADS=${2:?threads}; GEOM=${3:?geometry}; OUT=${4:?out dir}; shift 4
[ "${1:-}" = "--" ] && shift
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
ARGS=$(printf '%q ' "$@")
ENV="export OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1 PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp; mkdir -p \$HOME/qc_tmp; cd $PW/probes"
E8ARGS="--only-reference --two-route-check separate --threads $THREADS --max-memory $((CAP * 85 / 100)) $ARGS"
for RUN in released master; do
  case $RUN in
    released) CPHF="" ;;
    master) CPHF="--upstream-cphf \$HOME/pyscf-wt-base" ;;
  esac
  echo "=== (KC) $RUN start $(date '+%F %T')"
  MSYS_NO_PATHCONV=1 wsl -e bash -c "$ENV && bash wsl_capped.sh $CAP -- /usr/bin/time -f '(KC) max RSS %M kB, wall %e s' \
    \$HOME/qc05/bin/python krylov_cost_check.py $CPHF $GEOM $OUT/$RUN $E8ARGS"
done
MSYS_NO_PATHCONV=1 wsl -e bash -c "$ENV && \$HOME/qc05/bin/python krylov_cost_compare.py $OUT/released $OUT/master $OUT/krylov_compare.json"
echo "=== (KC) run done $(date '+%F %T')"
