#!/usr/bin/env bash
# watch_1007.sh (7 Oct 2026). The day's alarm-only watch, one cycle of ≈ 110 min, re-armed on every wake. Exit 1 = anomaly (a job gone without its
# marker), 2 = a new marker (reported once: the seen markers are kept in the scratchpad), 0 = quiet cycle. Covers:
#   laptop — LNO cell (b) until its marker (the WSL keepalive with it); the composite pipeline (Git Bash) until "(P5) chain 33c finished";
#   server — the MP2 rows queue's workers until "=== QUEUE DONE|FAILED"; ssh unreachable twice in a row.
#   bash probes/watch_1007.sh
set -uo pipefail
# no-set-e: every check decides its own exit
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LOG=$P/probes/results_m1/afternoon_2026-10-04.log
SEEN=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad/watch_1007_seen.txt
SSH="ssh -o BatchMode=yes -o ConnectTimeout=20 -i $HOME/.ssh/hetzner_g_measure root@157.180.32.149"
touch "$SEEN"
t() { date '+%H:%M'; }
new_marker() {   # $1 = a line; prints and records it when not seen before
  grep -qxF "$1" "$SEEN" && return 1
  echo "$1" >> "$SEEN"; echo "MARKER $(t): $1"; return 0
}
fails=0
for i in $(seq 1 11); do
  if ! grep -qE "\(N2\) LNO cell \(b\) (reuse done|FAILED)|\(N2\) LNO CELL \(b\) FAILED" "$LOG"; then
    keep=$(wsl -e bash -c "ps -eo args | grep -c '[s]leep infinity'" 2>/dev/null | tr -d '\r')
    [ "${keep:-0}" = "0" ] && { echo "ANOMALY $(t): WSL keepalive gone"; exit 1; }
    lno=$(wsl -e bash -c "ps -eo args | grep -c '[l]no_curvature_check'" 2>/dev/null | tr -d '\r')
    [ "${lno:-0}" = "0" ] && { echo "ANOMALY $(t): no LNO python and no cell (b) marker"; exit 1; }
  fi
  if ! grep -qE "\(P5\) chain 33c finished|\(P1\) QUEUE FAILED|CHAIN 33c NOT STARTED" "$LOG"; then
    [ "$(ps -ef | grep -c '[c]omposite_pipeline_1007')" = "0" ] && { echo "ANOMALY $(t): composite pipeline not running and not finished"; exit 1; }
  fi
  if grep -q "(C36) chain 36 (chain 34 + hinge input) training start" "$LOG" && ! grep -qE "\(C36\) chain 36 read done|\(C36\) CHAIN 36" "$LOG"; then
    [ "$(ps -ef | grep -c '[r]ungC_chain36_1007')" = "0" ] && { echo "ANOMALY $(t): chain 36 script gone without its read marker"; exit 1; }
  fi
  srv=$($SSH 'cd ~/e8/composite && echo "workers $(ps -eo args | grep -c "[c]c_composite_full_check.py compute") done $(ls rows/*.npz 2>/dev/null | wc -l) end $(tac queue.log | sed "/=== QUEUE start/q" | grep -oE "=== QUEUE (DONE|FAILED|REFUSED)" | head -n 1 | tr " " "_")"' 2>/dev/null)
  if [ -z "$srv" ]; then
    fails=$((fails + 1)); [ "$fails" -ge 2 ] && { echo "ANOMALY $(t): server unreachable twice"; exit 1; }
  else
    fails=0
    end=$(echo "$srv" | sed -nE 's/.* end (=*_QUEUE_[A-Z]+).*/\1/p')
    workers=$(echo "$srv" | sed -E 's/workers ([0-9]+).*/\1/')
    if [ -n "$end" ]; then new_marker "server $end" && exit 2
    elif [ "$workers" = "0" ]; then echo "ANOMALY $(t): no queue workers on the server and no end marker — $srv"; exit 1; fi
  fi
  for m in "(P3) labels server running" "(P3) LABELS BOOTSTRAP FAILED" "(P4) BUILD OR PROMOTION FAILED" "(P4) composites built" "(P5) chain 33c finished" \
           "(N2) LNO cell (b) reuse done" "(N2) LNO CELL (b) FAILED" "CHAIN 33c NOT STARTED" "(P5) CHAIN 33c seed" "(C36) chain 36 read done" "(C36) CHAIN 36"; do
    line=$(grep -F "$m" "$LOG" | tail -n 1 | cut -c1-110)
    [ -n "$line" ] && new_marker "$line" && exit 2
  done
  [ "$i" -lt 11 ] && sleep 600
done
echo "quiet cycle $(t): server $srv"
exit 0
