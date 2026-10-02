#!/bin/bash
# Next-pool watch for ubuntu-32gb-hel1-2 CPX62 (46.62.227.91), 2 Oct 2026 (from ccx53_watch_anthracene.sh). Two corpus runners (corpus, corpus_b),
# each 100 ids. Every INTERVAL s one ssh: done/failed counts from both manifests, python psi4 processes, available memory, the runners' last lines →
# one status line in $LOG. Lines on stdout (the alarms file) only on: no psi4 python while a runner has not written its exit file, no new result
# for STALL_MIN minutes, three ssh failures in a row; one DONE line when both runners have exit files. ONCE=1 = dry run. Silence = healthy.
set -u
# no-set-e: the watch loop must survive a failed ssh and report it
IP=46.62.227.91; KEY=$HOME/.ssh/hetzner_g_measure
R=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
LOG=${LOG:-/mnt/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad/hel2b_watch.log}
INTERVAL=${INTERVAL:-1800}; STALL_MIN=${STALL_MIN:-360}
fails=0; last_n=-1; last_change=$(date +%s)
while true; do
  now=$(date '+%Y-%m-%d %H:%M')
  st=$(ssh -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 root@$IP \
       "ls $R/corpus/molecules/*/result.json $R/corpus_b/molecules/*/result.json 2>/dev/null | wc -l; \
        ps -eo comm,args | awk '\$1 ~ /^python/ && /psi4_worker|run_corpus/' | wc -l; free -m | awk '/Mem:/ {print \$7}'; \
        ls $R/corpus/nextpool_a.exit $R/corpus_b/nextpool_b.exit 2>/dev/null | wc -l; \
        tail -n 1 $R/corpus/nextpool_a.log 2>/dev/null | cut -c1-110; tail -n 1 $R/corpus_b/nextpool_b.log 2>/dev/null | cut -c1-110" 2>/dev/null)
  if [ -z "$st" ]; then
    fails=$((fails + 1)); echo "$now | ssh failed ($fails)" >> "$LOG"
    [ "$fails" -ge 3 ] && echo "HEL2B ALARM $now: ssh failed three times in a row"
    [ -n "${ONCE:-}" ] && exit 0
    sleep "$INTERVAL"; continue
  fi
  fails=0
  n=$(echo "$st" | sed -n 1p); npy=$(echo "$st" | sed -n 2p); avail=$(echo "$st" | sed -n 3p); nexit=$(echo "$st" | sed -n 4p)
  la=$(echo "$st" | sed -n 5p); lb=$(echo "$st" | sed -n 6p)
  [ "$n" != "$last_n" ] && { last_n=$n; last_change=$(date +%s); }
  age=$(( ( $(date +%s) - last_change ) / 60 ))
  echo "$now | results $n/200 | psi4 procs $npy | avail ${avail} MB | exits $nexit | last change ${age} min | a: $la | b: $lb" >> "$LOG"
  if [ "${nexit:-0}" -ge 2 ]; then echo "HEL2B DONE $now: both runners exited, results $n/200"; exit 0; fi
  if [ "${npy:-0}" -eq 0 ]; then echo "HEL2B ALARM $now: no psi4/runner python process (results $n, exits $nexit)"; exit 1; fi
  if [ "$age" -gt "$STALL_MIN" ]; then echo "HEL2B ALARM $now: no new result for $age min ($n so far, $npy python procs)"; fi
  [ -n "${ONCE:-}" ] && exit 0
  sleep "$INTERVAL"
done
