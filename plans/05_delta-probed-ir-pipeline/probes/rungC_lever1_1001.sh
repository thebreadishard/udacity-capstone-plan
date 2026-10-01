#!/usr/bin/env bash
# Lever 1, 1 Oct 2026 (the user: 'Doe hefboom 1, het patroon uitbreiden'; amendment 06:4x): pattern (d) on the carried hybrid recipe.
#   0. design-check gate (fresh sum body)      1. diagnostic: benzene alone with pattern d, 5,000 steps (the floor must fall below the 0.15 of pattern c)
#   2. pattern d at A + A2 (175), seeds 0–2    3. pattern d at A + A2 + B (750), seeds 0–2
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d"
python m05/design_check.py corpus/molecules --out out/design_check_lever1_$D --aggregation sum > out/design_check_lever1_$D.txt 2>&1 \
  && grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== DESIGN CHECK FAILED — lever 1 not started $(date)"; exit 1; }
echo "=== lever 1 start $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever1_overfit_benzene_$D --use-analytic --overfit-one A_8448043181 --seeds 0 --threads 8 --aggregation sum \
  --head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 5000 --lr 3e-4 --hybrid-hidden 256 --pattern d \
  && echo "=== lever 1 overfit benzene (pattern d) done $(date)" || echo "=== LEVER 1 OVERFIT FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever1_d_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== lever 1 pattern d (175) done $(date)" || echo "=== LEVER 1 175 FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever1_d_750_$D --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum $REC \
  && echo "=== lever 1 pattern d (750) done $(date)" || echo "=== LEVER 1 750 FAILED $(date)"
echo "=== lever 1 finished $(date)"
