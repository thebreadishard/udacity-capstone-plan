#!/usr/bin/env bash
# watch_1008.sh (8 Oct 2026, 02:5x; watch_night_1008.sh plus chain 37). Earlier: watch_night_1008.sh (7 Oct 22:1x; LNO extra coordinate). Alarm-only, one cycle of
# ≈ 110 min, re-armed on every wake. Exit 1 = anomaly (a job gone without its marker), 2 = a new marker (reported once: the seen markers are kept in
# the scratchpad), 0 = quiet cycle. Covers:
#   laptop — the LNO extra coordinate (probes/night_1007_lno.sh, markers (N3)) and the WSL keepalive until "(N3) LNO extra coordinate finished";
#   labels server (CCX53) — four lanes alive until "LANE n DONE"; a new FAILED count reported once; ssh unreachable twice in a row;
#   laptop — chain 37 (probes/rungC_chain37_1008.sh, Git Bash) alive until its read marker; its (C37) markers reported once.
#   CPX62 — pool 3 batch 1's two runners (8 Oct 02:57): alive until their exit files; a new failed count reported once.
#   bash probes/watch_1009.sh   (8 Oct 17:5x: watch_1008.sh plus chains 38/39)
set -uo pipefail
# no-set-e: every check decides its own exit
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LOG3=$P/probes/results_m1/lno_extra_k2_2026-10-07.log
LOG37=$P/probes/results_m1/chain37_2026-10-08.log
LOGI=$P/probes/results_m1/t3_intensity_2026-10-09.log   # 8 Oct 18:0x: T3 intensity read (markers (I))
LOG38=$P/probes/results_m1/chains38_39_2026-10-09.log   # 8 Oct 17:5x: chains 38/39 (markers (C38))
LOGG=$P/probes/results_m1/cation_gate_2026-10-08.log   # 8 Oct 11:3x: the P3-2 cation gate (markers (G))
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
  if [ -f "$LOG37" ]; then
    while read -r line; do new_marker "$(echo "$line" | cut -c1-110)" && exit 2; done < <(grep -E "\(C37\) (chain 37 trained|chain 37 read done|CHAIN 37)" "$LOG37")
    if ! grep -qE "\(C37\) (chain 37 read done|CHAIN 37)" "$LOG37"; then
      [ "$(ps -ef | grep -c '[r]ungC_chain37_1008')" = "0" ] && { echo "ANOMALY $(t): chain 37 script gone without its read marker"; exit 1; }
    fi
  fi
  if [ -f "$LOGG" ]; then
    while read -r line; do new_marker "$(echo "$line" | cut -c1-110)" && exit 2; done < <(grep -E "^=== \(G\) (ten cations copied|analytic route done|cation gate finished|.*FAILED|GATE NOT STARTED)" "$LOGG")
    if ! grep -qE "^=== \(G\) (cation gate finished|GATE NOT STARTED|FETCH FAILED)" "$LOGG"; then
      [ "$(ps -ef | grep -c '[c]ation_gate_p3_2')" = "0" ] && { echo "ANOMALY $(t): cation gate script gone without its end marker"; exit 1; }
    fi
  fi
  if [ -f "$LOG38" ]; then
    while read -r line; do new_marker "$(echo "$line" | cut -c1-110)" && exit 2; done < <(grep -E "^=== \(C38\) " "$LOG38" | grep -v armed)
    if ! grep -qE "^=== \(C38\) (chains 38/39 done|CHAINS 38/39)" "$LOG38"; then
      [ "$(ps -ef | grep -c '[r]ungC_chains38_39_1009')" = "0" ] && { echo "ANOMALY $(t): chains 38/39 script gone without its end marker"; exit 1; }
    fi
  fi
  if [ -f "$LOGI" ]; then
    while read -r line; do new_marker "$(echo "$line" | cut -c1-110)" && exit 2; done < <(grep -E "^=== \(I\) " "$LOGI" | grep -v armed)
    if ! grep -qF "(I) T3 intensity read finished" "$LOGI"; then
      [ "$(ps -ef | grep -c '[t]3_intensity_benzene_1009')" = "0" ] && { echo "ANOMALY $(t): T3 intensity script gone without its end marker"; exit 1; }
    fi
  fi
  # the labels server (lever 2): 'bash labels_lane.sh' processes (not their bash -c wrappers) alive until 'LANE n DONE'
  lb=$($LABELS 'cd /root/labels 2>/dev/null && echo "lanes $(pgrep -fc "^bash (/root/labels/)?labels_lane(_switch)?\.sh") ok $(cat lane_?.log 2>/dev/null | grep -c " ok ") failed $(cat lane_?.log 2>/dev/null | grep -c " FAILED ") done $(cat lane_?.log 2>/dev/null | grep -c "DONE:")"' 2>/dev/null)
  if [ -z "$lb" ]; then
    fails=$((fails + 1)); [ "$fails" -ge 2 ] && { echo "ANOMALY $(t): labels server unreachable twice"; exit 1; }
  else
    fails=0
    lanes=$(echo "$lb" | awk '{print $2}'); lfail=$(echo "$lb" | awk '{print $6}'); ldone=$(echo "$lb" | awk '{print $8}')
    if [ "$ldone" = "4" ]; then new_marker "labels: all four lanes DONE — $lb" && exit 2; fi
    if [ "$((lanes + ldone))" -lt 4 ]; then echo "ANOMALY $(t): labels lanes $lanes running + $ldone done < 4 — $lb"; exit 1; fi
    [ "$lfail" != "0" ] && new_marker "labels failed count $lfail" > /dev/null && { echo "MARKER $(t): labels $lb"; exit 2; }
  fi
  # the CPX62: pool 3 batch 1 (8 Oct 00:57 UTC) — runner a (corpus_p3: 60 cations, then neutrals shard 0/2), runner b (corpus_p3b: neutrals shard 1/2);
  # each alive until remote_launch's <name>.exit exists; a new failed count is reported once
  np=$($CPX62 'B=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor; for r in a b; do d=$B/corpus_p3; [ $r = b ] && d=$B/corpus_p3b; alive=0; kill -0 $(cat $d/pool3_$r.pid 2>/dev/null) 2>/dev/null && alive=1; ex=$([ -f $d/pool3_$r.exit ] && echo 1 || echo 0); printf "%s %s %s %s %s " $r $alive $ex $(grep -c "] done" $d/pool3_$r.log) $(grep -c "] failed" $d/pool3_$r.log); done' 2>/dev/null)
  if [ -n "$np" ]; then
    read -r _ aa ae ad af _ ba be bd bf <<< "$np"
    for r in a b; do
      if [ $r = a ]; then al=$aa; ex=$ae; else al=$ba; ex=$be; fi
      [ "$al" = "0" ] && [ "$ex" = "0" ] && { echo "ANOMALY $(t): pool 3 runner $r gone without its exit file — $np"; exit 1; }
      [ "$ex" = "1" ] && new_marker "pool 3 runner $r finished — $np" && exit 2
    done
    new_marker "pool3 failed count $((af + bf))" > /dev/null && [ "$((af + bf))" != "0" ] && { echo "MARKER $(t): pool 3 a/b done $ad/$bd failed $af/$bf"; exit 2; }
  fi
  [ "$i" -lt 11 ] && sleep 600
done
echo "quiet cycle $(t): labels $lb | CPX62 $np"
exit 0
