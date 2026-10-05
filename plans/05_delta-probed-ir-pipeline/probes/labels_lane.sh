#!/bin/bash
# labels_lane.sh <lane id> <id list> — runs ON the labels server (registration 1 of Design_2026-10-05_Analytic_Labels_and_Stepping_Stone.md): one lane
# of analytic B3LYP + ωB97X Hessians (`analytic_hessians.py`, 8 threads) over its list of corpus ids, one molecule per call so that a failure costs one
# molecule, skipping ids whose analytic ωB97X file already exists (restartable). One status line per molecule to the lane log; "LANE <n> DONE" at the end.
#   setsid nohup bash /root/labels/labels_lane.sh 0 /root/labels/ids_0.txt > /root/labels/lane_0.log 2>&1 < /dev/null &
set -u
# no-set-e: a molecule that fails is logged and the lane continues
LANE=$1; LIST=$2
PY=/root/miniforge3/envs/qc05/bin/python
cd /root/labels || exit 1
export OMP_NUM_THREADS=8 PYSCF_TMPDIR=/root/qc_tmp TMPDIR=/root/qc_tmp
mkdir -p /root/qc_tmp
n=0; ok=0; fail=0; skip=0
while read -r id; do
  [ -z "$id" ] && continue
  n=$((n + 1))
  if [ -f "molecules/$id/hessian_wb97x_analytic.npz" ] && [ -f "molecules/$id/hessian_b3lyp_analytic.npz" ]; then
    skip=$((skip + 1)); echo "[$(date '+%F %T')] lane $LANE $id skipped (analytic files exist)"; continue
  fi
  t0=$(date +%s)
  if $PY analytic_hessians.py "molecules/$id" --threads 8 >> "lane_${LANE}_molecules.log" 2>&1; then
    ok=$((ok + 1)); echo "[$(date '+%F %T')] lane $LANE $id ok $(( $(date +%s) - t0 )) s ($ok ok, $fail failed, $skip skipped of $n)"
  else
    fail=$((fail + 1)); echo "[$(date '+%F %T')] lane $LANE $id FAILED $(( $(date +%s) - t0 )) s — see lane_${LANE}_molecules.log"
  fi
done < "$LIST"
echo "[$(date '+%F %T')] LANE $LANE DONE: $ok ok, $fail failed, $skip skipped of $n"
