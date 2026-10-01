#!/usr/bin/env bash
# Sherlock chain 2, 1 Oct 2026 (amendment 08:0x): H5 pattern ceilings on naphthalene / 2-methylnaphthalene / styrene (pattern d, sum body),
# then lever 2a: fresh mean body vs the QM9-pretrained mean body under the hybrid head, pattern d, 175, seeds 0–2. Design-check gates first.
set -uo pipefail
# no-set-e: every step records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
D=2026-10-01
until grep -q "=== lever 1 finished" out/E7_rungC_lever1_$D.log; do sleep 60; done
PRE=out/rungC_pretrained_mean_2026-09-28.pt
REC="--head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern d"
grep -q "verdict: \*\*PASS\*\*" out/design_check_lever1_$D.txt || { echo "=== chain 2 not started: no sum-body PASS from lever 1 $(date)"; exit 1; }
python m05/design_check.py corpus/molecules --out out/design_check_sherlock_mean_$D --aggregation mean > out/design_check_sherlock_mean_$D.txt 2>&1 \
  && grep -q "verdict: \*\*PASS\*\*" out/design_check_sherlock_mean_$D.txt || { echo "=== DESIGN CHECK (mean) FAILED — chain 2 not started $(date)"; exit 1; }
python m05/design_check.py corpus/molecules --out out/design_check_sherlock_pre_$D --aggregation mean --checkpoint $PRE --as-finetune > out/design_check_sherlock_pre_$D.txt 2>&1 \
  && grep -q "verdict: \*\*PASS\*\*" out/design_check_sherlock_pre_$D.txt || { echo "=== DESIGN CHECK (pretrained) FAILED — chain 2 not started $(date)"; exit 1; }
echo "=== chain 2 start $(date)"
for M in naphthalene:A_01f3186607 methylnaphthalene:A_69789470db styrene:A_8f6ed7c002; do
  NAME=${M%%:*}; ID=${M##*:}
  python m05/rungC_train.py corpus/molecules out/E7_rungC_lever1_overfit_${NAME}_$D --use-analytic --overfit-one $ID --seeds 0 --threads 8 --aggregation sum \
    --head hybrid --aux pattern --sqm-scale --pair-features --aux-weight 1.0 --epochs 5000 --lr 3e-4 --hybrid-hidden 256 --pattern d \
    && echo "=== H5 overfit $NAME done $(date)" || echo "=== H5 OVERFIT $NAME FAILED $(date)"
done
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever2a_fresh_mean_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation mean $REC \
  && echo "=== lever 2a fresh mean (175) done $(date)" || echo "=== LEVER 2A FRESH FAILED $(date)"
python m05/rungC_train.py corpus/molecules out/E7_rungC_lever2a_pretrained_mean_175_$D --use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation mean --pretrained $PRE $REC \
  && echo "=== lever 2a pretrained mean (175) done $(date)" || echo "=== LEVER 2A PRETRAINED FAILED $(date)"
echo "=== chain 2 finished $(date)"
