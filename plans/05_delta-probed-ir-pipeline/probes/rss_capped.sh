#!/usr/bin/env bash
# probes/rss_capped.sh <cap_MB> -- command … (18 Oct 2026; incident: a dxtb Hessian took the WSL VM down beside the cation job) — runs the
# command, samples its resident memory (with its children) every second, and kills it the moment the sum passes the cap, so an exploratory
# measurement can never take memory from a running job. Prints 'peak RSS <MB> MB' at the end, or 'KILLED: RSS <MB> MB over the cap'.
#   bash probes/rss_capped.sh 8000 -- python probes/dxtb_hessians_for_qff.py one <record.json> --method autograd
# no-set-e: the command's exit code is read and reported
set -u
CAP=${1:?cap in MB}; shift
[ "${1:-}" = "--" ] && shift
"$@" &
pid=$!
peak=0
tree_rss() { ps -o rss= --ppid "$pid" -p "$pid" 2>/dev/null | awk '{s += $1} END {print int(s / 1024)}'; }
while kill -0 "$pid" 2>/dev/null; do
  r=$(tree_rss)
  [ "${r:-0}" -gt "$peak" ] && peak=$r
  if [ "${r:-0}" -gt "$CAP" ]; then
    kill "$pid" 2>/dev/null
    echo "KILLED: RSS $r MB over the cap of $CAP MB"
    wait "$pid" 2>/dev/null
    exit 3
  fi
  sleep 1
done
wait "$pid"
rc=$?
echo "peak RSS $peak MB (exit $rc)"
exit "$rc"
