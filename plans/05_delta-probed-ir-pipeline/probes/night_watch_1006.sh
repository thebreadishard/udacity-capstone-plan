#!/usr/bin/env bash
# night_watch_1006.sh (6 Oct 2026, 20:0x; the user: "Blijf de zaak maar in de gaten houden"). One watch cycle of at most ~110 minutes, run as a
# background waiter from the session and re-armed on every wake. Every 10 minutes it checks, and exits early (so the session wakes) on an anomaly:
#   laptop  — the WSL keepalive session (scheduled task CapstoneWSLKeepalive) gone; the LNO python gone while cell (b)'s marker is missing;
#   server  — the two MP2 lanes gone while "OOP ROWS DONE/FAILED" is missing; ssh unreachable twice in a row.
# Otherwise it ends with one status line. Alarm-only: silence inside the cycle means healthy.
#   bash probes/night_watch_1006.sh   (from the plan directory; exit 0 = quiet cycle, 1 = anomaly, 2 = a marker landed)
set -uo pipefail
# no-set-e: every check decides its own exit
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LOG=$P/probes/results_m1/afternoon_2026-10-04.log
SSH="ssh -o BatchMode=yes -o ConnectTimeout=20 -i $HOME/.ssh/hetzner_g_measure root@157.180.32.149"
t() { date '+%H:%M'; }
seen_server_marker=0
fails=0
for i in $(seq 1 11); do
  # laptop
  keep=$(wsl -e bash -c "ps -eo args | grep -c '[s]leep infinity'" 2>/dev/null | tr -d '\r')
  if [ "${keep:-0}" = "0" ]; then echo "ANOMALY $(t): WSL keepalive session gone (VM down or task ended)"; exit 1; fi
  if ! grep -qE "\(N2\) LNO cell \(b\) (reuse done|FAILED)|=== evening 1006 finished" "$LOG"; then
    lno=$(wsl -e bash -c "ps -eo args | grep -c '[l]no_curvature_check'" 2>/dev/null | tr -d '\r')
    if [ "${lno:-0}" = "0" ]; then echo "ANOMALY $(t): no LNO python in WSL but cell (b) has no marker"; grep -E "\(N2\)" "$LOG" | tail -n 2; exit 1; fi
  fi
  # server
  srv=$($SSH 'cd ~/e8/composite 2>/dev/null && echo "lanes $(ps -eo args | grep -c "[c]c_composite_full_check") marker $(grep -cE "OOP ROWS (DONE|FAILED|MERGE FAILED)" oop_rows.log) tz $(grep -c "] mp2 cc-pvtz" lane_a_tz.log lane_b_tz.log 2>/dev/null | tr "\n" " ")"' 2>/dev/null)
  if [ -z "$srv" ]; then
    fails=$((fails + 1)); [ "$fails" -ge 2 ] && { echo "ANOMALY $(t): server unreachable twice"; exit 1; }
  else
    fails=0
    lanes=$(echo "$srv" | sed -E 's/.*lanes ([0-9]+).*/\1/'); marker=$(echo "$srv" | sed -E 's/.*marker ([0-9]+).*/\1/')
    if [ "$marker" != "0" ]; then echo "MARKER $(t): server rows finished — $srv"; exit 2; fi
    if [ "$lanes" = "0" ]; then echo "ANOMALY $(t): no MP2 lanes on the server and no marker — $srv"; exit 1; fi
  fi
  if grep -qE "\(N2\) LNO CELL \(a\) FAILED|\(N2\) LNO CELL \(b\) FAILED" "$LOG" && [ "$seen_server_marker" = "0" ]; then echo "MARKER $(t): an LNO cell FAILED"; grep -E "\(N2\)" "$LOG" | tail -n 2; exit 2; fi
  [ "$i" -lt 11 ] && sleep 600
done
echo "quiet cycle $(t): keepalive up; LNO $(grep -E '\(N2\)' "$LOG" | tail -n 1 | cut -c1-60); server $srv"
exit 0
