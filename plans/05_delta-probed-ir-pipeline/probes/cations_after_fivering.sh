#!/bin/bash
# cations_after_fivering.sh (10 Oct 2026; the user: "Ja, laat de vijfringpool voorgaan") — the cation analytic route (probes/cation_analytic_all.sh)
# was stopped after its current molecule so that the five-ring pool runs first on the laptop (probes/fivering_laptop_1015.sh, PRIORITY=1). This
# waits for that runner's end (all candidates done, or the STOP hand-over to pool 3's box), then relaunches the cation route, which skips every
# cation that already carries both analytic Hessians. The two cannot run side by side: ≈ 12 GB each.
# 10 Oct 10:4x (a review the user showed: 'wacht eeuwig als de F5-marker nooit komt'): the runner's pid is checked on every pass; a runner gone
# without its end marker gives a (CA) marker once per pid, so the watch wakes the session (relaunch the runner or touch its STOP file); a relaunched
# runner writes a new pid and is followed again; after MAX_DAYS without an end the chain gives up with a marker instead of waiting for ever.
#
#   nohup bash probes/cations_after_fivering.sh >> probes/results_m1/cation_analytic_2026-10-09.log 2>&1 < /dev/null & disown
# Overridable for tests: F5LOG, F5PID, SLEEP_S, MAX_DAYS, CA_CMD.
set -u
# no-set-e: a waiting loop; the relaunch is the last command
P=$(cd "$(dirname "$0")/.." && pwd)   # the plan folder, wherever the checkout is (CI runs on Linux)
F5LOG=${F5LOG:-$P/probes/results_m1/fivering_laptop_2026-10-09.log}
F5PID=${F5PID:-$P/probes/results_m1/fivering_laptop.pid}
SLEEP_S=${SLEEP_S:-900}
MAX_DAYS=${MAX_DAYS:-21}
CA_CMD=${CA_CMD:-bash probes/cation_analytic_all.sh}
t() { date '+%F %T'; }
echo "=== (CA) paused for the five-ring pool (pid $$): waiting for (F5)'s end $(t)"
start=$(date +%s); warned_pid=""
until grep -qE '^=== \(F5\) (laptop runner finished|STOP file)' "$F5LOG" 2>/dev/null; do
  pid=$(tr -d '\r\n ' < "$F5PID" 2>/dev/null)
  if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null && [ "$warned_pid" != "$pid" ]; then
    echo "=== (CA) RESUME CHAIN WAITING: the five-ring runner (pid $pid) is gone without its end marker — relaunch it (PRIORITY=1) or touch its STOP file $(t)"
    warned_pid=$pid
  fi
  if [ "$(( $(date +%s) - start ))" -ge "$(( MAX_DAYS * 86400 ))" ]; then
    echo "=== (CA) RESUME CHAIN GAVE UP after $MAX_DAYS days without (F5)'s end — relaunch the cation route by hand $(t)"; exit 1
  fi
  sleep "$SLEEP_S"
done
# the runner prints its end marker after its last molecule has returned, so nothing of it is left running here
echo "=== (CA) resumed after the five-ring pool $(t)"
cd "$P" || exit 1
exec $CA_CMD
