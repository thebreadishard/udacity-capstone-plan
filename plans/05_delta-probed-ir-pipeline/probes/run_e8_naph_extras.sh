#!/bin/bash
# CCX53, 24 Sep 2026 evening: the three naphthalene partial runs are single-threaded in their (T)-gradient phase (100 % CPU each), so throughput
# comes from more processes, not more threads. Two extra partial runs start as soon as reference.npz exists (they then skip the reference) and work
# the *tails* of the existing ranges in reverse — indices 4,3,9 and 14,13,8 of the 15 symmetry-unique displacements — so the originals, which reach
# those indices last, find the gradient files already written and skip them. Five processes ≈ 100 GB of 122. Wall time ≈ (reference + 6 gradients).
cd /root/e8 || exit 1
PY=/root/miniforge3/envs/qc05/bin/python
OUT=results/naphthalene_ccpvdz; G=molecules/A_01f3186607/geometry.json; LOG=/root/e8/chain_ccx53.log
until [ -f $OUT/reference.npz ]; do sleep 120; done
echo "[$(date "+%F %T")] reference.npz present -> two extra partial runs (ks 4,3,9 and 14,13,8) at 6 threads" >> $LOG
OMP_NUM_THREADS=6 nohup $PY e8_cc_hessian_fd.py $G $OUT --threads 6 --symmetry --ks 4,3,9 > $OUT/partial_extra_A.log 2>&1 &
OMP_NUM_THREADS=6 nohup $PY e8_cc_hessian_fd.py $G $OUT --threads 6 --symmetry --ks 14,13,8 > $OUT/partial_extra_B.log 2>&1 &
wait
echo "[$(date "+%F %T")] extra partial runs done" >> $LOG
