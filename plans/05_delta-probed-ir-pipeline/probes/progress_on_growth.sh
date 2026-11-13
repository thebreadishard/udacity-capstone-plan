#!/usr/bin/env bash
# probes/progress_on_growth.sh --tag T --dir DIR --name GLOB [--interval S] -- command … (17 Oct 2026; TASKS 38's five-ring runners on the pool 3
# box) — runs the command and gives tools/runspec.py the progress lines it needs when the command itself prints one line per unit of work and a
# unit takes longer than a runspec's progress gap (a five-ring molecule: 3–12 h on 8 threads). Every --interval seconds it sums the bytes of the
# files named GLOB under DIR (psi4.out grows with every displaced gradient) and prints '=== (T) progress: …' only when the sum changed, so a
# hung job prints nothing and the gap raises the alarm. The command's own output passes through; the last line is '=== (T) command ended rc=N'
# and the wrapper exits with the command's code.
#   bash probes/progress_on_growth.sh --tag F5A --dir corpus_f5a/molecules --name psi4.out -- bash fivering_laptop_1015.sh
#
# --cpu-heartbeat adds a second kind of line, '=== (T) cpu: the command's tree at N s (+M)', printed on the same interval and only when
# the CPU time of the command's process subtree grew (13 Nov 2026, TASKS 208: pyscf logs nothing during the XC part of an analytic
# Hessian, ≈ 2.6 h on a 38-atom molecule, so a healthy run woke the watch at 23:33). A runspec that wants it names that line among its
# progress patterns. The sum walks the subtree of the command, never the process group, so the wrapper's own shell cannot keep a stalled
# job looking alive.
# no-set-e: the command's exit code is read and reported, not propagated by the shell
set -u
TAG="" DIR="" NAME="" INTERVAL=600 CPU_HEARTBEAT=""
TICKS=$(getconf CLK_TCK)
CPU_MIN_GROWTH_S=1   # a heartbeat only when the tree burned at least this much CPU since the last look: starting a shell costs a tick or
                     # two, and a line for that would make a sleeping job look alive (13 Nov 2026, the test that caught it)
while [ $# -gt 0 ]; do
  case "$1" in
    --tag) TAG=$2; shift 2 ;;
    --dir) DIR=$2; shift 2 ;;
    --name) NAME=$2; shift 2 ;;
    --interval) INTERVAL=$2; shift 2 ;;
    --cpu-heartbeat) CPU_HEARTBEAT=1; shift ;;
    --) shift; break ;;
    *) echo "progress_on_growth.sh: unknown option $1" >&2; exit 2 ;;
  esac
done
[ -n "$TAG" ] && [ -n "$DIR" ] && [ -n "$NAME" ] && [ $# -gt 0 ] || { echo "usage: --tag T --dir DIR --name GLOB [--interval S] [--cpu-heartbeat] -- command …" >&2; exit 2; }
say() { echo "=== ($TAG) $* $(date '+%F %T')"; }
total_bytes() { find "$DIR" -name "$NAME" -type f -printf '%s\n' 2>/dev/null | awk '{s += $1} END {print s + 0}'; }

# the subtree rooted at $1, in clock ticks: utime + stime, the 12th and 13th fields after the command name (which may hold spaces).
# A process whose /proc entry vanishes mid-read, or a system without /proc, yields nothing and the caller reads 0 — no heartbeat line,
# so the runspec's gap raises the alarm rather than a stalled job looking healthy.
tree_cpu_ticks() {
  awk -v root="$1" '{
      rest = substr($0, index($0, ") ") + 2)
      split(rest, f, " ")
      cpu[$1] = f[12] + f[13]
      parent[$1] = f[2]
    }
    END {
      for (p in cpu) {
        q = p
        for (n = 0; q != "" && q != "0" && n < 64; n++) {
          if (q == root) { total += cpu[p]; break }
          q = parent[q]
        }
      }
      print total + 0
    }' /proc/[0-9]*/stat 2>/dev/null
}

"$@" &
job=$!
last=$(total_bytes)
last_cpu=0
step=$(( INTERVAL < 5 ? INTERVAL : 5 ))   # 19 Oct 2026: the command's end is seen within a step, not after a whole interval (a dry run waited 10 min)
while kill -0 "$job" 2>/dev/null; do
  waited=0
  while [ "$waited" -lt "$INTERVAL" ] && kill -0 "$job" 2>/dev/null; do
    sleep "$step" & wait $!
    waited=$((waited + step))
  done
  now=$(total_bytes)
  [ "$now" != "$last" ] && say "progress: $NAME under $DIR at $now bytes (+$((now - last)))"
  last=$now
  if [ -n "$CPU_HEARTBEAT" ]; then
    cpu=$(tree_cpu_ticks "$job"); cpu=${cpu:-0}
    grew=$(((cpu - last_cpu) / TICKS))
    [ "$grew" -ge "$CPU_MIN_GROWTH_S" ] && say "cpu: the command's tree at $((cpu / TICKS)) s (+$grew)"
    last_cpu=$cpu
  fi
done
wait "$job"; rc=$?
say "command ended rc=$rc"
exit "$rc"
