#!/usr/bin/env bash
# probes/progress_on_growth.sh --tag T --dir DIR --name GLOB [--interval S] -- command … (17 Oct 2026; TASKS 38's five-ring runners on the pool 3
# box) — runs the command and gives tools/runspec.py the progress lines it needs when the command itself prints one line per unit of work and a
# unit takes longer than a runspec's progress gap (a five-ring molecule: 3–12 h on 8 threads). Every --interval seconds it sums the bytes of the
# files named GLOB under DIR (psi4.out grows with every displaced gradient) and prints '=== (T) progress: …' only when the sum changed, so a
# hung job prints nothing and the gap raises the alarm. The command's own output passes through; the last line is '=== (T) command ended rc=N'
# and the wrapper exits with the command's code.
#   bash probes/progress_on_growth.sh --tag F5A --dir corpus_f5a/molecules --name psi4.out -- bash fivering_laptop_1015.sh
# no-set-e: the command's exit code is read and reported, not propagated by the shell
set -u
TAG="" DIR="" NAME="" INTERVAL=600
while [ $# -gt 0 ]; do
  case "$1" in
    --tag) TAG=$2; shift 2 ;;
    --dir) DIR=$2; shift 2 ;;
    --name) NAME=$2; shift 2 ;;
    --interval) INTERVAL=$2; shift 2 ;;
    --) shift; break ;;
    *) echo "progress_on_growth.sh: unknown option $1" >&2; exit 2 ;;
  esac
done
[ -n "$TAG" ] && [ -n "$DIR" ] && [ -n "$NAME" ] && [ $# -gt 0 ] || { echo "usage: --tag T --dir DIR --name GLOB [--interval S] -- command …" >&2; exit 2; }
say() { echo "=== ($TAG) $* $(date '+%F %T')"; }
total_bytes() { find "$DIR" -name "$NAME" -type f -printf '%s\n' 2>/dev/null | awk '{s += $1} END {print s + 0}'; }

"$@" &
job=$!
last=$(total_bytes)
while kill -0 "$job" 2>/dev/null; do
  sleep "$INTERVAL" & wait $!
  now=$(total_bytes)
  [ "$now" != "$last" ] && say "progress: $NAME under $DIR at $now bytes (+$((now - last)))"
  last=$now
done
wait "$job"; rc=$?
say "command ended rc=$rc"
exit "$rc"
