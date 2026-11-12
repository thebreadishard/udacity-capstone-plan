#!/usr/bin/env bash
# probes/cpu_heartbeat.sh PID OUT [INTERVAL_S] — a heartbeat for a library phase that logs nothing for hours (pyscf's XC part of the partial
# Hessian: ≈ 4 x its JK part, 2.6 h silent on D_ac28161d06). Every INTERVAL_S seconds (default 600) it reads the process's CPU time
# (utime + stime of /proc/PID/stat, all its threads) and appends one line to OUT only when it grew, so a runspec's heartbeat_glob that names
# OUT stays quiet on a process that stopped computing (a deadlock, a wait on I/O) and the gap raises the alarm. A process that spins without
# progress still grows; the runspec's estimate overrun catches that. Ends when PID is gone.
#   nohup bash probes/cpu_heartbeat.sh 1349 results_m1/cphf_check_215_D_ac28161d06_2026-11-12/cpu_heartbeat.log &
# no-set-e: a read of /proc that fails ends the loop on purpose (the process is gone)
set -u
PID=${1:?usage: cpu_heartbeat.sh PID OUT [INTERVAL_S]}
OUT=${2:?usage: cpu_heartbeat.sh PID OUT [INTERVAL_S]}
INTERVAL=${3:-600}
TICKS=$(getconf CLK_TCK)

cpu_ticks() {
  # the command name (field 2) may hold spaces: read the fields after its closing parenthesis; utime and stime are the 12th and 13th there
  local stat
  stat=$(cat "/proc/$PID/stat" 2>/dev/null) || return 1
  echo "${stat##*) }" | awk '{print $12 + $13}'
}

last=$(cpu_ticks) || { echo "cpu_heartbeat.sh: no process $PID" >&2; exit 2; }
echo "cpu_heartbeat start pid=$PID cpu_s=$((last / TICKS)) $(date '+%F %T')" >> "$OUT"
while now=$(cpu_ticks); do
  if [ "$now" -gt "$last" ]; then
    echo "cpu_heartbeat pid=$PID cpu_s=$((now / TICKS)) (+$(((now - last) / TICKS))) $(date '+%F %T')" >> "$OUT"
  fi
  last=$now
  sleep "$INTERVAL"
done
echo "cpu_heartbeat end pid=$PID gone $(date '+%F %T')" >> "$OUT"
