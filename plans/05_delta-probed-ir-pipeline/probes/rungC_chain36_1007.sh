#!/usr/bin/env bash
# rungC_chain36_1007.sh (7 Oct 2026; TASKS 23, design note GoalGathering/notes/Design_2026-10-07_Low_Mode_Hinge_Input.md, registered 07:1x before
# this run). Chain 36 = chain 34's recipe (probes/night2_1003.sh) + --hinge-feature, 750, seeds 0–2, 8 threads, beside the LNO cell (8 threads in WSL);
# then the read exactly as chain 34's of 5 Oct (probes/step3_read_1005.sh): rungC_eval_saved --use-analytic per seed, rungC_eval_means against the
# chain record, rungC_low_modes_noise --low 700. The models are read as candidates (--allow-any-model: not carried; named in the records).
# Smoke-tested 07:23–07:27 with and without the flag (the embedding trains only with it); design check PASS (out/design_check_chain36_2026-10-07.md).
#   nohup bash probes/rungC_chain36_1007.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: each step writes its own marker
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
cd "$P/modules/05_support_predictor" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
PRE=out/E7_rungC_chain36_hinge_750_2026-10-07
MODEL=${PRE}_model_n750_seed
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --kdiag-mode family --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --save-model"
echo "=== (C36) chain 36 (chain 34 + hinge input) training start, 8 threads $(t)"
# shellcheck disable=SC2086   # REC is a list of trainer arguments
python m05/rungC_train.py corpus/molecules $PRE --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum \
  $REC --hinge-feature > $PRE.log 2>&1 && echo "=== (C36) chain 36 trained $(t)" || { echo "=== (C36) CHAIN 36 TRAINING FAILED — see $PRE.log $(t)"; exit 1; }
ok=1
for s in 0 1 2; do
  python ../../probes/rungC_eval_saved.py ${MODEL}${s}.pt out/E7_rungC_chain36_eval_analytic_2026-10-07_seed${s} --use-analytic --threads 8 --allow-any-model \
    > out/E7_rungC_chain36_eval_analytic_2026-10-07_seed${s}.log 2>&1 || ok=0
done
python ../../probes/rungC_eval_means.py out/read_chain36_analytic_2026-10-07 out/E7_rungC_chain36_eval_analytic_2026-10-07_seed{0,1,2}.json --against $PRE.json \
  --line "CH-oop<=3" --line "other<=3" --line "ring-ip<=3" > out/read_chain36_analytic_2026-10-07.log 2>&1 || ok=0
python ../../probes/rungC_low_modes_noise.py out/rungC_low_modes_noise_c36_analytic_2026-10-07 ${MODEL}0.pt ${MODEL}1.pt ${MODEL}2.pt --low 700 --threads 8 \
  > out/rungC_low_modes_noise_c36_analytic_2026-10-07.log 2>&1 || ok=0
[ $ok = 1 ] && echo "=== (C36) chain 36 read done — out/read_chain36_analytic_2026-10-07.md, out/rungC_low_modes_noise_c36_analytic_2026-10-07.md $(t)" \
  || echo "=== (C36) CHAIN 36 READ FAILED (one of the three steps) $(t)"
