#!/usr/bin/env bash
# watch_night_1008.sh (7 Oct 2026, 22:1x; watch_night_1007.sh without the finished jobs, plus the LNO extra coordinate). Alarm-only, one cycle of
# ≈ 110 min, re-armed on every wake. Exit 1 = anomaly (a job gone without its marker), 2 = a new marker (reported once: the seen markers are kept in
# the scratchpad), 0 = quiet cycle. Covers:
#   laptop — the LNO extra coordinate (probes/night_1007_lno.sh, markers (N3)) and the WSL keepalive until "(N3) LNO extra coordinate finished";
#   labels server (CCX53) — four lanes alive until "LANE n DONE"; a new FAILED count reported once; ssh unreachable twice in a row;
#   CPX62 — the two runners of the 200 until both lists are done; a new 'failed' count reported once.
#   bash probes/watch_night_1008.sh
set -uo pipefail
# no-set-e: every check decides its own exit
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LOG3=$P/probes/results_m1/lno_extra_k2_2026-10-07.log
SEEN=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad/watch_1007_seen.txt
KEY=$HOME/.ssh/hetzner_g_measure
LABELS="ssh -o BatchMode=yes -o ConnectTimeout=20 -i $KEY root@157.180.32.149"
CPX62="ssh -o BatchMode=yes -o ConnectTimeout=20 -i $KEY root@46.62.227.91"
touch "$SEEN"
t() { date '+%H:%M'; }
new_marker() {   # $1 = a line; prints and records it when not seen before
  grep -qxF "$1" "$SEEN" && return 1
  echo "$1" >> "$SEEN"; echo "MARKER $(t): $1"; return 0
}
fails=0
for i in $(seq 1 11); do
  if [ -f "$LOG3" ]; then
    while read -r line; do new_marker "$(echo "$line" | cut -c1-110)" && exit 2; done < <(grep -E "\(N3\) LNO (k2 cell|K2 CELL|extra coordinate finished)" "$LOG3")
    if ! grep -qF "(N3) LNO extra coordinate finished" "$LOG3"; then
      keep=$(wsl -e bash -c "ps -eo args | grep -c '[s]leep infinity'" 2>/dev/null | tr -d '\r')
      [ "${keep:-0}" = "0" ] && { echo "ANOMALY $(t): WSL keepalive gone"; exit 1; }
      lno=$(wsl -e bash -c "ps -eo args | grep -c '[l]no_curvature_check'" 2>/dev/null | tr -d '\r')
      [ "${lno:-0}" = "0" ] && { echo "ANOMALY $(t): no LNO python and no (N3) finished marker"; exit 1; }
    fi
  fi
  # the labels server (lever 2): 'bash labels_lane.sh' processes (not their bash -c wrappers) alive until 'LANE n DONE'
  lb=$($LABELS 'cd /root/labels 2>/dev/null && echo "lanes $(pgrep -fc "^bash labels_lane.sh") ok $(cat lane_?.log 2>/dev/null | grep -c " ok ") failed $(cat lane_?.log 2>/dev/null | grep -c " FAILED ") done $(cat lane_?.log 2>/dev/null | grep -c "DONE:")"' 2>/dev/null)
  if [ -z "$lb" ]; then
    fails=$((fails + 1)); [ "$fails" -ge 2 ] && { echo "ANOMALY $(t): labels server unreachable twice"; exit 1; }
  else
    fails=0
    lanes=$(echo "$lb" | awk '{print $2}'); lfail=$(echo "$lb" | awk '{print $6}'); ldone=$(echo "$lb" | awk '{print $8}')
    if [ "$ldone" = "4" ]; then new_marker "labels: all four lanes DONE — $lb" && exit 2; fi
    if [ "$((lanes + ldone))" -lt 4 ]; then echo "ANOMALY $(t): labels lanes $lanes running + $ldone done < 4 — $lb"; exit 1; fi
    [ "$lfail" != "0" ] && new_marker "labels failed count $lfail" > /dev/null && { echo "MARKER $(t): labels $lb"; exit 2; }
  fi
  # the CPX62 with the 200 (lever 5)
  np=$($CPX62 'C=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor; echo "runners $(pgrep -fc "[r]un_corpus.py") done $(grep -c "] done" $C/corpus/nextpool_a.log $C/corpus_b/nextpool_b.log | cut -d: -f2 | paste -sd+ | bc) failed $(grep -c "] failed" $C/corpus/nextpool_a.log $C/corpus_b/nextpool_b.log | cut -d: -f2 | paste -sd+ | bc)"' 2>/dev/null)
  if [ -n "$np" ]; then
    nr=$(echo "$np" | awk '{print $2}'); nf=$(echo "$np" | awk '{print $6}')
    if [ "$nr" = "0" ]; then new_marker "CPX62 runners finished — $np" && exit 2; fi
    new_marker "CPX62 failed count $nf" > /dev/null && [ "$nf" != "1" ] && { echo "MARKER $(t): CPX62 $np"; exit 2; }
  fi
  [ "$i" -lt 11 ] && sleep 600
done
echo "quiet cycle $(t): labels $lb | CPX62 $np"
exit 0
