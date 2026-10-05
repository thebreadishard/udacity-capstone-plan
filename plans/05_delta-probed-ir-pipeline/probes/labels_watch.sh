#!/bin/bash
# labels_watch.sh <ip> <status log> <alarm log> [interval s] [stall min] — alarm-only watchdog for the analytic-label lanes (registration 1 of
# Design_2026-10-05_Analytic_Labels_and_Stepping_Stone.md). Every INTERVAL s one ssh: per lane the last log line, the number of analytic ωB97X files,
# the python processes and the free memory → one status line in the status log. An alarm line (and stdout) when no lane has finished a molecule for
# STALL_MIN minutes, when a lane log reports FAILED three times in a row, or when ssh fails three times in a row; one DONE line when all four lanes say
# "LANE <n> DONE". Silence means healthy. ONCE=1 = dry run (one status line, then exit). Runs detached in WSL:
#   setsid nohup bash probes/labels_watch.sh <ip> <status.log> <alarms.log> 1800 180 > /dev/null 2>&1 < /dev/null &
set -u
# no-set-e: the watch loop must survive a failed ssh and report it
IP=$1; LOG=$2; ALARM=$3; INTERVAL=${4:-1800}; STALL_MIN=${5:-180}
KEY=~/.ssh/hetzner_g_measure
fails=0; last_n=-1; last_change=$(date +%s)
while true; do
  now=$(date '+%F %H:%M')
  st=$(ssh -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 root@$IP \
       "ls /root/labels/molecules/*/hessian_wb97x_analytic.npz 2>/dev/null | wc -l; ps -eo args | grep -c analytic_hessian[s]; free -m | awk '/Mem:/ {print \$7}'; for L in 0 1 2 3; do tail -n 1 /root/labels/lane_\$L.log 2>/dev/null | cut -c1-110; done; grep -c 'LANE [0-3] DONE' /root/labels/lane_*.log 2>/dev/null | awk -F: '{s+=\$2} END {print s+0}'; grep -h FAILED /root/labels/lane_*.log 2>/dev/null | tail -n 3 | wc -l" 2>/dev/null)
  if [ -z "$st" ]; then
    fails=$((fails + 1)); echo "$now | ssh failed ($fails)" >> "$LOG"
    [ "$fails" -ge 3 ] && echo "LABELS ALARM $now: ssh failed three times in a row" | tee -a "$ALARM"
    [ -n "${ONCE:-}" ] && exit 0
    sleep "$INTERVAL"; continue
  fi
  fails=0
  n=$(echo "$st" | sed -n 1p); procs=$(echo "$st" | sed -n 2p); avail=$(echo "$st" | sed -n 3p)
  lanes=$(echo "$st" | sed -n 4,7p | tr '\n' ' '); done_lanes=$(echo "$st" | sed -n 8p); recent_fail=$(echo "$st" | sed -n 9p)
  if [ "$n" != "$last_n" ]; then last_n=$n; last_change=$(date +%s); fi
  since=$(( ($(date +%s) - last_change) / 60 ))
  echo "$now | analytic $n | procs $procs | avail ${avail} MB | last change $since min | $lanes" >> "$LOG"
  [ "$done_lanes" -ge 4 ] && { echo "LABELS DONE $now: all four lanes finished ($n analytic files) — run probes/fetch_labels_ccx53.sh $IP" | tee -a "$ALARM"; exit 0; }
  [ "$since" -ge "$STALL_MIN" ] && [ "$procs" -gt 0 ] && echo "LABELS ALARM $now: no new analytic file for $since min ($n so far, $procs python procs)" | tee -a "$ALARM"
  [ "$procs" -eq 0 ] && [ "$done_lanes" -lt 4 ] && echo "LABELS ALARM $now: no python process and only $done_lanes lanes done — a lane died" | tee -a "$ALARM"
  [ "$recent_fail" -ge 3 ] && echo "LABELS ALARM $now: three FAILED molecules in the recent lane logs" | tee -a "$ALARM"
  [ -n "${ONCE:-}" ] && exit 0
  sleep "$INTERVAL"
done
