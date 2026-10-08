#!/usr/bin/env bash
# t3_intensity_benzene_1009.sh (8 Oct 2026, 19:0x; TASKS 32; read-out (3) of the 3 Oct registration, amendment 8 Oct 19:0x in the rung C
# pre-registration) — chain 33c's T3 at the TZ tier again (chain 34's three models, the six carried TZ-tier anchors, 300 epochs, head L2 1), now with
# benzene's CC/TZ atomic polar tensor, so that the held-out benzene fold reads the network's intensities against the CC intensities. Waits for chains
# 38/39 to release the laptop. Markers "=== (I) …".
#   nohup bash probes/t3_intensity_benzene_1009.sh >> probes/results_m1/t3_intensity_2026-10-09.log 2>&1 &
set -uo pipefail
# no-set-e: each seed writes its own marker
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
WAIT_LOG=$P/probes/results_m1/chains38_39_2026-10-09.log
APT=$P/probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/apt_ccsd_t.npz
t() { date '+%F %T'; }
echo "=== (I) armed (pid $$), waiting for chains 38/39 $(t)"
until grep -qE "^=== \(C38\) (chains 38/39 done|CHAINS 38/39)" "$WAIT_LOG" 2>/dev/null; do sleep 300; done
cd "$P" || exit 1
ARGS=$(python probes/composite_promote.py t3-args TZ)
cd "$P/modules/05_support_predictor" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
for s in 0 1 2; do
  # shellcheck disable=SC2086   # ARGS is a list of --anchor arguments
  python m05/rungC_cc_transfer.py corpus/molecules out/E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed$s.pt out/T3_tz_intensity_c34_seed${s}_2026-10-09 \
    --threads 8 --epochs 300 --lr 1e-3 --head-l2 1 $ARGS --apt "A_8448043181=$APT" > out/T3_tz_intensity_c34_seed${s}_2026-10-09.log 2>&1 \
    && echo "=== (I) seed $s done $(t)" || echo "=== (I) SEED $s FAILED $(t)"
done
echo "=== (I) T3 intensity read finished $(t)"
