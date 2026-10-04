#!/usr/bin/env bash
# step3_read_1005.sh (4 Oct 2026, 21:1x). The registered read that follows chain 34 step 3 (rung C pre-registration, amendment 3 Oct 11:1x and the
# chain 34c outcome of 4 Oct 12:1x: "the analytic hold-out (a) targets are read on other-low before any further training lever"). When the afternoon
# queue reports "(B) chain 34 step 3 done", the three carried chain-34 seeds are read on the hold-outs with the analytic Hessians substituted for the
# finite-difference ones (`probes/rungC_eval_saved.py --use-analytic`), and the low-mode split is read the same way (`probes/rungC_low_modes_noise.py`,
# which takes the analytic targets where they exist — after step 3, on every hold-out (a) molecule). 2 threads, sequential, beside the night queue
# (TZ anchor 8, ten-fold batch route 4, notebooks 2). Nothing is trained. Markers to the afternoon log. Git Bash, detached:
#   nohup bash probes/step3_read_1005.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: each read records its own marker
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
M=$P/modules/05_support_predictor
LOG=$P/probes/results_m1/afternoon_2026-10-04.log
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
until grep -qE "\(B\) chain 34 step 3 done|\(B\) CHAIN 34 STEP 3 FAILED" "$LOG"; do sleep 300; done
if grep -q "(B) CHAIN 34 STEP 3 FAILED" "$LOG"; then echo "=== (R) step-3 read skipped: step 3 failed $(t)"; exit 1; fi
echo "=== (R) step-3 read start: chain 34 on analytic hold-out targets (2 threads) $(t)"
cd "$M" || exit 1
MODEL=out/E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed
ok=1
for s in 0 1 2; do
  python ../../probes/rungC_eval_saved.py ${MODEL}${s}.pt out/E7_rungC_chain34_eval_analytic_2026-10-05_seed${s} --use-analytic --threads 2 > out/E7_rungC_chain34_eval_analytic_2026-10-05_seed${s}.log 2>&1 \
    && echo "=== (R) seed $s read on analytic targets $(t)" || { echo "=== (R) SEED $s READ FAILED $(t)"; ok=0; }
done
python ../../probes/rungC_low_modes_noise.py out/rungC_low_modes_noise_c34_analytic_2026-10-05 ${MODEL}0.pt ${MODEL}1.pt ${MODEL}2.pt --low 700 --threads 2 > out/rungC_low_modes_noise_c34_analytic_2026-10-05.log 2>&1 \
  && echo "=== (R) low-mode read on analytic targets done $(t)" || { echo "=== (R) LOW-MODE READ FAILED $(t)"; ok=0; }
[ $ok = 1 ] && echo "=== (R) step-3 read done — read out/E7_rungC_chain34_eval_analytic_2026-10-05_seed*.md and out/rungC_low_modes_noise_c34_analytic_2026-10-05.md $(t)" \
             || echo "=== (R) STEP-3 READ ENDED WITH FAILURES $(t)"
