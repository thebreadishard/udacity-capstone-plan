#!/usr/bin/env bash
# probes/run_with_mem_watch.sh <run log> <start regex> <pattern> <mem log> -- <command …> (1 Nov 2026, TASKS 49 step 3) — runs the command
# and, once <start regex> (grep -E) is in <run log>, samples the memory of the python process whose command line contains <pattern> with
# probes/mem_watch_wsl.sh (MEM_WATCH overrides it, for tests), retried every WAIT_S seconds (default 60) until a sample has found the process;
# the sampler then runs until that process is gone. D_8a1c3dddb7 was killed at 115 GB on 1 Nov in a phase no log named: a second explosion
# should show its phase. The command's exit status is the script's.
# no-set-e: the sampler failing must not stop the run; the command's status is returned explicitly
set -u
[ $# -ge 6 ] && [ "$5" = "--" ] || { echo "usage: $0 <run log> <start regex> <pattern> <mem log> -- <command …>"; exit 2; }
LOG=$1; START=$2; PATTERN=$3; MEM=$4; shift 5
HERE=$(cd "$(dirname "$0")" && pwd)
MEM_WATCH=${MEM_WATCH:-$HERE/mem_watch_wsl.sh}
WAIT_S=${WAIT_S:-60}
"$@" &
RUN=$!
until grep -qE -- "$START" "$LOG" 2>/dev/null; do kill -0 "$RUN" 2>/dev/null || break; sleep "$WAIT_S"; done
while kill -0 "$RUN" 2>/dev/null && ! grep -qE "pid [0-9]+" "$MEM" 2>/dev/null; do
  bash "$MEM_WATCH" "$PATTERN" "$MEM" "$WAIT_S"
  sleep "$WAIT_S"
done
wait "$RUN"
