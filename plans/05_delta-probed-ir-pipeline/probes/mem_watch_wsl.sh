#!/usr/bin/env bash
# mem_watch_wsl.sh (4 Oct 2026, 00:1x). The first TZ benzene run of 3 Oct died at 21:30:45 with its log wiped by the relaunch; this logger keeps the
# memory story of a WSL run: every INTERVAL s one line — MemAvailable, SwapFree and the RSS of the python process whose command line contains PATTERN
# — appended to LOG. Exits when the process is gone. Self-match safe: the pattern is matched against /proc/*/cmdline of python processes only.
# Usage (detached, from WSL): setsid nohup bash probes/mem_watch_wsl.sh "e8_cc_hessian_fd" <run dir>/mem_watch.log [60] >/dev/null 2>&1 < /dev/null &
set -u
# no-set-e: a missing /proc entry between two reads must not end the logger
PATTERN=$1; LOG=$2; INTERVAL=${3:-60}
find_pid() {
  for d in /proc/[0-9]*; do
    exe=$(readlink "$d/exe" 2>/dev/null) || continue
    case "$exe" in *python*) ;; *) continue ;; esac
    if tr '\0' ' ' < "$d/cmdline" 2>/dev/null | grep -q -- "$PATTERN"; then echo "${d#/proc/}"; return 0; fi
  done
  return 1
}
while true; do
  pid=$(find_pid) || pid=""
  avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  swapfree=$(awk '/SwapFree/{print int($2/1024)}' /proc/meminfo)
  if [ -n "$pid" ]; then rss=$(awk '/VmRSS/{print int($2/1024)}' "/proc/$pid/status" 2>/dev/null); else rss=""; fi
  echo "$(date +%F_%T) avail_MB $avail swapfree_MB $swapfree pid ${pid:-none} rss_MB ${rss:-0}" >> "$LOG"
  [ -z "$pid" ] && { echo "$(date +%F_%T) process gone; logger exits" >> "$LOG"; exit 0; }
  sleep "$INTERVAL"
done
