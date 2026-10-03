#!/usr/bin/env bash
# Chain 34 step 2 (3 Oct 2026, decision 53; pre-registration amendment 11:1x): the carried recipe at 750 with the family-balanced K-diagonal term
# (--kdiag-mode family), seeds 0-2, hold-outs (a) and (b), models saved. Waits for the night sequence (notebook -> LNO -> TZ benzene) to free the laptop
# lane: the TZ marker (done or failed) in the night log. 8 threads: the anthracene analytic Hessians and the night runs are sequenced before it.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
NIGHT=../../probes/results_m1/night_2026-10-03.log
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --kdiag-mode family --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --save-model"
until grep -qE "night: TZ benzene oop done|NIGHT TZ BENZENE OOP FAILED" "$NIGHT" 2>/dev/null; do sleep 900; done
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_2026-10-01.txt || { echo "=== chain 34 not started: no sum-body PASS $(date)"; exit 1; }
grep -q "smoke ok" out/smoke_kdiag_family_2026-10-03.marker 2>/dev/null || { echo "=== chain 34 not started: no smoke marker $(date)"; exit 1; }
echo "=== chain 34 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_chain34_kdfamily_750_2026-10-05 --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== chain 34 (750, family-balanced diagonal term, models saved) done $(date)" || echo "=== CHAIN 34 FAILED $(date)"
echo "=== chain 34 finished $(date)"
# Step 3 (registered 11:1x): analytic B3LYP + wB97X Hessians for the 8 FD hold-out (a) molecules (the second route; T1's CH-oop line is read on these
# only). Anthracene's analytic B3LYP took 83 min on 3 Oct (24 atoms); eight molecules of 20-26 atoms, both functionals: about a laptop-day at 16 threads.
echo "=== chain 34 step 3: analytic hold-out (a) Hessians start $(date)"
python corpus/analytic_hessians.py corpus/molecules/A_72b86c2331 corpus/molecules/A_07cadc7923 corpus/molecules/A_fdc27f1bd1 corpus/molecules/A_e72997e726 \
  corpus/molecules/A_bce5bae234 corpus/molecules/A_541c53d1a5 corpus/molecules/A_08dde334d8 corpus/molecules/A_428228e5a5 --threads 16 \
  > out/chain34_step3_analytic_holdout_a_2026-10-05.log 2>&1 \
  && echo "=== chain 34 step 3 done $(date)" || echo "=== CHAIN 34 STEP 3 FAILED $(date)"
echo "=== chain 34 step 3 finished $(date)"
