#!/bin/bash
# E8 on the CCX53 (24 Sep 2026): wait for the second-route lanes to finish, then
#  1. benzene CCSD(T)/cc-pVDZ FD Hessian with --symmetry (12 gradients) — end-to-end smoke of the new code path; must match the 72-gradient Hessian
#     of hel1-16 (copied here as results/benzene_full/hessian_ccsd_t.npz) to 0.5 cm-1;
#  2. naphthalene CCSD(T)/cc-pVDZ FD Hessian with --symmetry (30 gradients), the user's authorisation of 24 Sep ("Doe maar");
#  3. the locality read-out and the between-branch extension on naphthalene.
cd /root/e8 || exit 1
PY=/root/miniforge3/envs/qc05/bin/python
LOG=/root/e8/chain_ccx53.log
T=32
echo "[$(date "+%F %T")] chain armed; waiting for the second-route lanes" >> $LOG
while pgrep -f "corpus/analytic_hessians.py" > /dev/null; do sleep 120; done
echo "[$(date "+%F %T")] lanes done -> benzene symmetric smoke" >> $LOG
mkdir -p results/benzene_sym results/naphthalene_ccpvdz
OMP_NUM_THREADS=$T $PY e8_cc_hessian_fd.py molecules/A_8448043181/geometry.json results/benzene_sym --threads $T --symmetry >> $LOG 2>&1
rc=$?
if [ $rc -ne 0 ] || [ ! -f results/benzene_sym/hessian_ccsd_t.npz ]; then echo "[$(date "+%F %T")] BENZENE SYMMETRIC SMOKE FAILED rc=$rc - chain stops" >> $LOG; exit 1; fi
$PY e8_compare_hessians.py results/benzene_sym/hessian_ccsd_t.npz results/benzene_full/hessian_ccsd_t.npz molecules/A_8448043181/geometry.json --tol-cm 0.5 >> $LOG 2>&1
if [ $? -ne 0 ]; then echo "[$(date "+%F %T")] BENZENE SYMMETRIC vs FULL: FAIL - chain stops (user decides)" >> $LOG; exit 1; fi
echo "[$(date "+%F %T")] benzene symmetric = full: PASS -> naphthalene symmetric FD run (30 gradients)" >> $LOG
OMP_NUM_THREADS=$T $PY e8_cc_hessian_fd.py molecules/A_01f3186607/geometry.json results/naphthalene_ccpvdz --threads $T --symmetry >> $LOG 2>&1
echo "[$(date "+%F %T")] naphthalene FD run exit $?" >> $LOG
[ -f results/naphthalene_ccpvdz/hessian_ccsd_t.npz ] || { echo "[$(date "+%F %T")] NAPHTHALENE FAILED - no Hessian" >> $LOG; exit 1; }
OMP_NUM_THREADS=$T $PY e8_cc_locality.py molecules/A_01f3186607/geometry.json results/naphthalene_ccpvdz/hessian_ccsd_t.npz results/naphthalene_ccpvdz/E8_locality_naphthalene --threads $T >> $LOG 2>&1
echo "[$(date "+%F %T")] naphthalene verdict: $(grep -o 'verdict [a-z]*' results/naphthalene_ccpvdz/E8_locality_naphthalene.md 2>/dev/null | tail -1)" >> $LOG
OMP_NUM_THREADS=$T $PY e8_between_extension.py molecules/A_01f3186607/geometry.json results/naphthalene_ccpvdz/hessian_ccsd_t.npz results/naphthalene_ccpvdz/E8_between_naphthalene --threads $T >> $LOG 2>&1
echo "[$(date "+%F %T")] chain finished" >> $LOG
