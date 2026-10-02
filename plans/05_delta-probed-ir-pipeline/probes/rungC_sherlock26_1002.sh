#!/usr/bin/env bash
# Chain 26, 2 Oct 2026 (lever 5 step 2): read chain 24's three saved models on the hold-outs with probes/rungC_eval_saved.py once chain 25 has finished
# (lane A free) and the ten hold-out (a) APTs are in (apt_holdout_a_cphf loop finished) - the registered intensity read-outs on the full set.
set -uo pipefail
# no-set-e: every model records its own line
cd /c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
until grep -q "=== chain 25 finished\|chain 25 not started" out/E7_rungC_sherlock25_2026-10-02.log 2>/dev/null && grep -q "=== apt cphf holdout a finished" out/apt_holdout_a_cphf_2026-10-02.log 2>/dev/null; do sleep 300; done
echo "=== chain 26 start $(date)"
for s in 0 1 2; do
  M=out/E7_rungC_carried_kd_750_saved_2026-10-02_model_n750_seed$s.pt
  [ -f "$M" ] || { echo "=== chain 26 seed $s: no model $M $(date)"; continue; }
  python ../../probes/rungC_eval_saved.py "$M" out/eval_saved_carried750_seed${s}_2026-10-02 --use-analytic --threads 8 \
    && echo "=== chain 26 seed $s done $(date)" || echo "=== CHAIN 26 seed $s FAILED $(date)"
done
echo "=== chain 26 finished $(date)"
