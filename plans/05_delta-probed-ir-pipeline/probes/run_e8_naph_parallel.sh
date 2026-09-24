#!/bin/bash
# E8 naphthalene on the CCX53, three partial runs in parallel (24 Sep 2026, 11:xx): pyscf's CCSD(T) gradient does not scale past ~16 threads
# (benzene: 695 s at 24 threads on the CCX53 against 663–692 s at 16 on a CPX62), so three processes of 10 threads on the 15 symmetry-unique
# displacements (0:5, 5:10, 10:15) triple the throughput. Each partial run computes the reference gradient itself if reference.npz is missing
# (identical content; the duplicate is CPU, not wall time). When all three are done, one assembling run (no --ks; every gradient file present)
# reconstructs the Hessian by symmetry, then the locality read-out and the between-branch extension.
cd /root/e8 || exit 1
PY=/root/miniforge3/envs/qc05/bin/python
LOG=/root/e8/chain_ccx53.log
OUT=results/naphthalene_ccpvdz
G=molecules/A_01f3186607/geometry.json
mkdir -p $OUT
echo "[$(date "+%F %T")] naphthalene: three partial symmetric runs (ks 0:5, 5:10, 10:15) at 10 threads each" >> $LOG
for R in 0:5 5:10 10:15; do
  OMP_NUM_THREADS=10 nohup $PY e8_cc_hessian_fd.py $G $OUT --threads 10 --symmetry --ks $R > $OUT/partial_${R/:/-}.log 2>&1 &
  sleep 20      # let the first process create reference.npz before the others look for it (they would recompute it otherwise)
done
wait
echo "[$(date "+%F %T")] partial runs done ($(ls $OUT/grad_*.npy 2>/dev/null | wc -l) gradient files) -> assembling run" >> $LOG
OMP_NUM_THREADS=24 $PY e8_cc_hessian_fd.py $G $OUT --threads 24 --symmetry >> $LOG 2>&1
[ -f $OUT/hessian_ccsd_t.npz ] || { echo "[$(date "+%F %T")] NAPHTHALENE FAILED - no Hessian after assembly" >> $LOG; exit 1; }
OMP_NUM_THREADS=24 $PY e8_cc_locality.py $G $OUT/hessian_ccsd_t.npz $OUT/E8_locality_naphthalene --threads 24 >> $LOG 2>&1
echo "[$(date "+%F %T")] naphthalene verdict: $(grep -o 'verdict [a-z]*' $OUT/E8_locality_naphthalene.md 2>/dev/null | tail -1)" >> $LOG
OMP_NUM_THREADS=24 $PY e8_between_extension.py $G $OUT/hessian_ccsd_t.npz $OUT/E8_between_naphthalene --threads 24 >> $LOG 2>&1
echo "[$(date "+%F %T")] chain finished" >> $LOG
