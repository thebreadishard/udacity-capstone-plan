#!/usr/bin/env bash
# 3 Oct 2026: anthracene's analytic B3LYP and wB97X Hessians (corpus/analytic_hessians.py, the second route) on the laptop, once the benzene CC dipole run
# has written its Hessian — the anchor's T3 reading then uses a noise-free low level (the FD B3LYP carries the 0.1 noise floor). WSL, detached, nice 5.
set -u
# no-set-e: the step records its own line
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
L=$P/probes/results_m1/e8_benzene_ccpvdz_dip_2026-10-03/e8_fd.log
until grep -qE "Hessian written|FAILED|SELF-CHECK" "$L" 2>/dev/null; do sleep 300; done
echo "=== anthracene analytic start $(date)"
cd $P/modules/05_support_predictor && OMP_NUM_THREADS=8 nice -n 5 ~/qc05/bin/python corpus/analytic_hessians.py corpus/molecules/A_a1e6ec1862 --threads 8 2>&1 | grep -v Warning \
  && echo "=== anthracene analytic done $(date)" || echo "=== ANTHRACENE ANALYTIC FAILED $(date)"
ls -la corpus/molecules/A_a1e6ec1862/ | grep analytic
echo "=== anthracene analytic finished $(date)"
