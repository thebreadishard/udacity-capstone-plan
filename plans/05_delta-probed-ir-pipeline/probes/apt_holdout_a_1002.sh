#!/usr/bin/env bash
# Lever 5 (2 Oct 2026): atomic polar tensors of the ten hold-out (a) parents by FD of analytic B3LYP/6-31G* dipoles (probes/dipole_derivs_fd.py),
# one step (the sum rule is the second route), nice 10, 4 threads beside the two torch lanes. Runs in WSL, detached.
set -u
# no-set-e: a failed molecule is logged and the loop continues
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
cd "$P/modules/05_support_predictor" || exit 1
echo "=== apt holdout a start $(date)"
for i in $(tr -d "" < /mnt/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad/holdout_a_ids.txt); do
  d=corpus/molecules/$i
  [ -f "$d/dipole_b3lyp_fd.npz" ] && { echo "$i: APT exists, skipped"; continue; }
  H=hessian_b3lyp.npz; [ -f "$d/hessian_b3lyp_analytic.npz" ] && H=hessian_b3lyp_analytic.npz
  echo "--- $i ($H) $(date)"
  OMP_NUM_THREADS=4 nice -n 10 ~/qc05/bin/python "$P/probes/dipole_derivs_fd.py" "$d" --threads 4 --hessian "$H" --no-half-step 2>&1 | grep -v Warning | tail -n +1 \
    || echo "=== APT $i FAILED $(date)"
done
echo "=== apt holdout a finished $(date)"
