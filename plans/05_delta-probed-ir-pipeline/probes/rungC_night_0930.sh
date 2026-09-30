#!/usr/bin/env bash
# Rung C night chain, 30 Sep → 1 Oct 2026 (the user: "reken op de laptop door totdat we de werkende oplossing hebben gevonden"; registered in the rung-C
# pre-registration, dated amendment 23:1x). Waits for the scaling run, then, each step gated:
#   0. design check of the fresh sum body (PASS or stop)
#   1. diagnostic 1: H_low channels zeroed, 175 molecules (A,A2), winner flags, seed 0        → out/E7_rungC_diag_zerohlow_<D>
#   2. diagnostic 2: overfit benzene alone, 400 epochs, seed 0                                → out/E7_rungC_diag_overfit_benzene_<D>
#   3. rank 2 alone: internal term on the pair model's pattern, class-standardised, 175, 3 seeds → out/E7_rungC_rank2_pattern_<D>
# Rank 1 (rank-2 tensor injection) needs code and its own equivariance test first; it is launched separately when built.
set -uo pipefail
# no-set-e: every step reports its own FAILED line; a failed diagnostic must not stop the next one from being recorded
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-09-30
SCALE=out/E7_rungC_scale_2026-09-30.log
n=0
until grep -q "rung C scaling finished" $SCALE 2>/dev/null; do n=$((n+1)); [ $n -ge 360 ] && { echo "=== NIGHT CHAIN not started: scaling run not finished after 6 h $(date)"; exit 1; }; sleep 60; done
WIN=$(python -c "import json;print(json.load(open('out/E7_rungC_s2_pick_2026-09-27.json'))['flags'])") || exit 1
echo "=== night chain start $(date) flags: $WIN"
python m05/design_check.py corpus/molecules --out out/design_check_night_$D --aggregation sum > out/design_check_night_$D.txt 2>&1 \
  && grep -q "verdict: \*\*PASS\*\*" out/design_check_night_$D.txt || { echo "=== DESIGN CHECK FAILED — night chain not started $(date)"; exit 1; }
echo "=== design check PASS $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_diag_zerohlow_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0 --inner-val 0.15 --threads 8 --aggregation sum --zero-hlow $WIN \
  && echo "=== diag 1 (zero H_low) done $(date)" || echo "=== DIAG 1 FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_diag_overfit_benzene_$D --use-analytic --overfit-one A_8448043181 --seeds 0 --threads 8 --aggregation sum --epochs 400 --aux-weight 1.0 --lr 1e-3 \
  && echo "=== diag 2 (overfit benzene) done $(date)" || echo "=== DIAG 2 FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_rank2_pattern_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --aux pattern $WIN \
  && echo "=== rank 2 (pattern term) done $(date)" || echo "=== RANK 2 FAILED $(date)"
echo "=== night chain finished $(date)"
