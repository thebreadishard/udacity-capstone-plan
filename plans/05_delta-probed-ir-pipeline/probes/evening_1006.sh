#!/usr/bin/env bash
# evening_1006.sh (6 Oct 2026, 17:5x). The benzene cc-pVTZ anchor's assembly and the LNO cells, after the morning queue's two-route check died: pyscf's
# slow (T) density route was OOM-killed at 14:23 (19.8 GB RSS in a 20 GB VM) and the VM powered off with it. The reference is now checked by the energy
# route (`--two-route-check energy`, 17:35: max |g0 − (E(+h) − E(−h))/2h| = 4.8e-6 a.u. over 6 coordinates at cc-pVTZ, 5.3e-6 at cc-pVDZ where the
# kernel checks had passed inline; limit 2e-5), and the lambda kernel check passed at 09:10 (7.3e-17). Runs INSIDE WSL (setsid nohup); the VM is held
# by the scheduled task CapstoneWSLKeepalive. Steps: (N1) assembly (8 threads, 10 GB) → (N2) LNO cells (a) xtight, (b) reuse (8 threads, 6 GB).
# Test 2's read is run by hand when "(N1) TZ FULL ANCHOR DONE" appears in the afternoon log.
# Launch (Git Bash, from the plan directory):
#   wsl -e bash -c "setsid nohup bash /mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/evening_1006.sh \
#     >> /mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/results_m1/afternoon_2026-10-04.log 2>&1 < /dev/null &"
set -uo pipefail
# no-set-e: each step writes its own marker; a failed step stops what depends on it
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp
mkdir -p "$HOME/qc_tmp"
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
R=$PW/probes/results_m1
TZ=$R/e8_benzene_ccpvtz_oop_2026-10-03
GEO=$PW/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json
PY=$HOME/qc05/bin/python
t() { date '+%F %T'; }
echo "=== evening 1006: armed inside WSL (pid $$); TZ assembly on the energy-route check, LNO after $(t)"

cd "$PW/probes" || exit 1
OMP_NUM_THREADS=8 $PY e8_cc_hessian_fd.py "$GEO" "$TZ" --threads 8 --basis cc-pvtz --symmetry --two-route-check separate --fast-t-density --fast-t-lambda \
  --max-memory 10000 > "$R/tz_full_assemble_2026-10-04.log" 2>&1 \
  && echo "=== (N1) TZ FULL ANCHOR DONE — hessian_ccsd_t.npz in $TZ $(t)" || { echo "=== (N1) TZ ASSEMBLY FAILED $(t)"; exit 1; }

echo "=== (N2) LNO follow-up cells start (8 threads, 6 GB, after the anchor) $(t)"
ANCHOR=$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02
GEOM=$PW/modules/05_support_predictor/corpus/molecules/A_01f3186607/geometry.json
cd "$PW" || exit 1
OMP_NUM_THREADS=8 $PY probes/lno_curvature_check.py "$ANCHOR" "$GEOM" --max-k 2 --threads 8 --max-memory 6000 --xtight \
  --out "$R/lno_curvature_xtight_2026-10-05.json" > "$R/lno_curvature_xtight_2026-10-05.log" 2>&1 \
  && echo "=== (N2) LNO cell (a) xtight done $(t)" || echo "=== (N2) LNO CELL (a) FAILED $(t)"
OMP_NUM_THREADS=8 $PY probes/lno_curvature_check.py "$ANCHOR" "$GEOM" --max-k 2 --threads 8 --max-memory 6000 --reuse-localisation \
  --out "$R/lno_curvature_reuse_2026-10-05.json" > "$R/lno_curvature_reuse_2026-10-05.log" 2>&1 \
  && echo "=== (N2) LNO cell (b) reuse done $(t)" || echo "=== (N2) LNO CELL (b) FAILED $(t)"
echo "=== evening 1006 finished $(t)"
