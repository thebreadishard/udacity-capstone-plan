#!/usr/bin/env bash
# Lever 5 (2 Oct 2026, 07:4x): atomic polar tensors of the ten hold-out (a) parents by the CPHF route (probes/dipole_derivs_cphf.py; water: 1.3e-5 against
# the FD route, sum rule 4.6e-7), nice 10, 4 threads beside the two torch lanes; then the FD route on benzene as the aromatic second-route check and the
# comparison line. Runs in WSL, detached. Replaces apt_holdout_a_1002.sh (FD on all ten: ≈ 11 h per molecule).
set -u
# no-set-e: a failed molecule is logged and the loop continues
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
S=/mnt/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
cd "$P/modules/05_support_predictor" || exit 1
echo "=== apt cphf holdout a start $(date)"
for i in $(tr -d '\r' < "$S/holdout_a_ids.txt"); do
  d=corpus/molecules/$i
  [ -f "$d/dipole_b3lyp_cphf.npz" ] && { echo "$i: CPHF APT exists, skipped"; continue; }
  H=hessian_b3lyp.npz; [ -f "$d/hessian_b3lyp_analytic.npz" ] && H=hessian_b3lyp_analytic.npz
  echo "--- $i ($H) $(date)"
  OMP_NUM_THREADS=4 nice -n 10 ~/qc05/bin/python "$P/probes/dipole_derivs_cphf.py" "$d" --threads 4 --hessian "$H" 2>&1 | grep -v Warning \
    || echo "=== APT $i FAILED $(date)"
done
B=corpus/molecules/A_8448043181
echo "--- benzene FD second route (one step) $(date)"
OMP_NUM_THREADS=4 nice -n 10 ~/qc05/bin/python "$P/probes/dipole_derivs_fd.py" "$B" --threads 4 --hessian hessian_b3lyp_analytic.npz --no-half-step 2>&1 | grep -v Warning | head -3 \
  || echo "=== benzene FD FAILED $(date)"
~/qc05/bin/python - <<PYEOF
import numpy as np
a = np.load("$B/dipole_b3lyp_cphf.npz"); b = np.load("$B/dipole_b3lyp_fd.npz")
d = float(np.abs(a["apt"] - b["apt"]).max()); di = float(np.abs(a["intensity_km_mol"] - b["intensity_km_mol"]).max())
print(f"benzene two routes: max |P_cphf - P_fd| = {d:.1e} e, max intensity difference {di:.2f} km/mol -> {'PASS' if d < 1e-3 else 'FAIL'}")
PYEOF
echo "=== apt cphf holdout a finished $(date)"
