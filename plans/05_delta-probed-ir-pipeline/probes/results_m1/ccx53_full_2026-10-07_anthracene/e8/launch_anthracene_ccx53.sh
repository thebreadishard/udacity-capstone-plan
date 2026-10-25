#!/bin/bash
# ubuntu-128gb-hel1-2 (CCX53), 2 Oct 2026: water smoke of the chain with the separate two-route lane, then anthracene (frozen core derived, symmetry-reduced
# FD, both C kernels, 4 partial runs x 8 threads x 22000 MB + a check lane 8 threads x 16000 MB, memory guard) detached. anchors.log carries the ANCHOR lines.
set -euo pipefail
cd /root/e8
export PYSCF_TMPDIR=/root/qc_tmp TMPDIR=/root/qc_tmp; mkdir -p /root/qc_tmp
PY=/root/miniforge3/envs/qc05/bin/python
rm -rf results/smoke_parallel
OMP_NUM_THREADS=4 TWO_ROUTE=separate CT=1 CM=1500 ROOT=/root/e8 PY=$PY LOG=/root/e8/smoke.log SMOKE=water.json bash run_anchors_hel23_parallel.sh
grep -q "SMOKE PARALLEL OK" /root/e8/smoke.log || { echo "SMOKE FAILED"; exit 1; }
grep -q '"passed": true' results/smoke_parallel/two_route_check.json || { echo "SMOKE: two-route file not passing"; exit 1; }
tail -2 /root/e8/smoke.log
export TWO_ROUTE=separate CT=8 CM=16000
export ANCHOR_LIST="anthracene|molecules/A_a1e6ec1862/geometry.json|results/anthracene_ccpvdz|4|8|22000|--fast-t-density --fast-t-lambda"
nohup setsid bash run_anchors_hel23_parallel.sh > /root/e8/chain_stdout_anthracene.log 2>&1 < /dev/null &
echo "LAUNCHED pid $! $(date -u)"
