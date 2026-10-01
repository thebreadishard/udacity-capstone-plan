#!/bin/bash
# Naphthalene anchor watch for ubuntu-32gb-hel1-2 (157.180.32.149), 1 Oct 2026. Runs detached in WSL; silence = healthy.
# Every INTERVAL s one ssh: the anchors.log tail, the number of gradient files, python processes, available memory → one status line in $LOG.
# Lines on stdout (redirected to the alarms file at launch) only on: an ANCHOR … FAILED line, no python while the chain is not finished,
# no new gradient file for STALL_MIN minutes, or three ssh failures in a row. One DONE line on "CHAIN FINISHED". ONCE=1 = dry run.
set -u
# no-set-e: the watch loop must survive a failed ssh and report it
IP=157.180.32.149; KEY=$HOME/.ssh/hetzner_g_measure
OUT=/root/e8/results/naphthalene_ccpvdz
LOG=${LOG:-/mnt/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad/hel2_watch.log}
INTERVAL=${INTERVAL:-1800}; STALL_MIN=${STALL_MIN:-150}
fails=0; last_n=-1; last_change=$(date +%s)
while true; do
  now=$(date '+%Y-%m-%d %H:%M')
  st=$(ssh -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 root@$IP \
       "tail -n 2 /root/e8/anchors.log 2>/dev/null | tr '\n' ' '; echo; ls $OUT/grad_*.npy 2>/dev/null | wc -l; pgrep -fc e8_cc_hessian_fd.py; free -m | awk '/Mem:/{print \$7}'" 2>/dev/null)
  if [ -z "$st" ]; then
    fails=$((fails + 1)); echo "$now | ssh failed ($fails)" >> "$LOG"
    [ "$fails" -ge 3 ] && echo "HEL2 ALARM $now: ssh failed three times in a row"
    [ -n "${ONCE:-}" ] && exit 0
    sleep "$INTERVAL"; continue
  fi
  fails=0
  tailline=$(echo "$st" | sed -n 1p); n=$(echo "$st" | sed -n 2p); npy=$(echo "$st" | sed -n 3p); avail=$(echo "$st" | sed -n 4p)
  [ "$n" != "$last_n" ] && { last_n=$n; last_change=$(date +%s); }
  age=$(( ( $(date +%s) - last_change ) / 60 ))
  echo "$now | gradients $n | python procs $npy | avail ${avail} MB | last change ${age} min | ${tailline:0:140}" >> "$LOG"
  case "$tailline" in
    *"CHAIN FINISHED"*) echo "HEL2 DONE $now: ${tailline:0:200}"; exit 0 ;;
    *" FAILED"*)        echo "HEL2 ALARM $now: ${tailline:0:200}"; exit 1 ;;
  esac
  if [ "${npy:-0}" -eq 0 ]; then echo "HEL2 ALARM $now: no e8 python process on the server (gradients $n)"; exit 1; fi
  if [ "$age" -gt "$STALL_MIN" ]; then echo "HEL2 ALARM $now: no new gradient file for $age min ($n so far, $npy python procs)"; fi
  [ -n "${ONCE:-}" ] && exit 0
  sleep "$INTERVAL"
done
