#!/usr/bin/env bash
# Odds lever 2 (3 Oct 2026): benzene CCSD(T)/cc-pVTZ — the reference gradient and three displacement pairs (H out-of-plane k=20, C out-of-plane k=2,
# H in-plane radial k=18; --ks positions 5,2,3 of the symmetry-unique list [0,1,2,18,19,20]) with the dipole-storing probe, 16 threads, laptop WSL,
# after the naphthalene LNO check and the benzene DZ run have finished (memory: TZ benzene CCSD(T) needs the whole box). Partial run: no assembly.
set -u
# no-set-e: the step records its own line
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
OUT=$P/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03
until grep -qE "LNO curvature check:|Traceback" $P/probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/lno_curvature_run_2026-10-03.log 2>/dev/null \
   && grep -qE "Hessian written|FAILED|SELF-CHECK" $P/probes/results_m1/e8_benzene_ccpvdz_dip_2026-10-03/e8_fd.log 2>/dev/null \
   && grep -qE "anthracene analytic finished" $P/modules/05_support_predictor/out/anthracene_analytic_2026-10-03.log 2>/dev/null \n   && [ -f /mnt/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad/notebook_build_1003.finished ]; do sleep 300; done
mkdir -p "$OUT"
echo "=== TZ benzene oop start $(date)"
cd $P/probes && OMP_NUM_THREADS=16 ~/qc05/bin/python e8_cc_hessian_fd.py $P/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json "$OUT" \
  --threads 16 --basis cc-pvtz --symmetry --ks 5,2,3 --two-route-check separate --fast-t-density --fast-t-lambda --max-memory 10000 > "$OUT/run.log" 2>&1 \
  && echo "=== TZ benzene oop done $(date)" || echo "=== TZ BENZENE OOP FAILED $(date)"
echo "=== TZ benzene oop finished $(date)"
