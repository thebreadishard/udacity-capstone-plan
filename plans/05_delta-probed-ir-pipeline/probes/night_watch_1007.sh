#!/usr/bin/env bash
# night_watch_1007.sh (7 Oct 2026, 03:4x). Second half of the night: the server rows are in (test 3 read 03:27), so the watch covers the laptop only —
# the WSL keepalive, the LNO cell (b) until its marker, chain 33b (Windows python) until its "finished" marker. One cycle of ≈ 110 minutes, run as a
# background waiter and re-armed on every wake; exits early (code 1) on an anomaly, code 2 when a marker lands, 0 after a quiet cycle.
#   bash probes/night_watch_1007.sh
set -uo pipefail
# no-set-e: every check decides its own exit
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LOG=$P/probes/results_m1/afternoon_2026-10-04.log
t() { date '+%H:%M'; }
lno_done() { grep -qE "\(N2\) LNO cell \(b\) (reuse done|FAILED)|=== evening 1006 finished" "$LOG"; }
c33_done() { grep -qE "=== chain 33b finished|=== CHAIN 33b STOPPED" "$LOG"; }
for i in $(seq 1 11); do
  if ! lno_done; then
    keep=$(wsl -e bash -c "ps -eo args | grep -c '[s]leep infinity'" 2>/dev/null | tr -d '\r')
    if [ "${keep:-0}" = "0" ]; then echo "ANOMALY $(t): WSL keepalive session gone (VM down or task ended)"; exit 1; fi
    lno=$(wsl -e bash -c "ps -eo args | grep -c '[l]no_curvature_check'" 2>/dev/null | tr -d '\r')
    if [ "${lno:-0}" = "0" ]; then echo "ANOMALY $(t): no LNO python in WSL but cell (b) has no marker"; grep -E "\(N2\)" "$LOG" | tail -n 2; exit 1; fi
  fi
  if ! c33_done; then
    c33=$(ps -ef | grep -c "[r]ungC_cc_transfer")
    if [ "$c33" = "0" ]; then echo "ANOMALY $(t): no chain 33b python but no 'finished' marker"; grep -E "chain 33b|CHAIN 33b" "$LOG" | tail -n 2; exit 1; fi
  fi
  if grep -qE "CHAIN 33b seed [0-9] FAILED|\(N2\) LNO CELL \(b\) FAILED" "$LOG"; then echo "MARKER $(t): a step FAILED"; grep -E "FAILED" "$LOG" | tail -n 2; exit 2; fi
  if lno_done && c33_done; then echo "MARKER $(t): LNO (b) and chain 33b both finished"; grep -E "\(N2\)|chain 33b" "$LOG" | tail -n 3 | cut -c1-100; exit 2; fi
  [ "$i" -lt 11 ] && sleep 600
done
echo "quiet cycle $(t): $(grep -E '\(N2\)|chain 33b' "$LOG" | tail -n 1 | cut -c1-70)"
exit 0
