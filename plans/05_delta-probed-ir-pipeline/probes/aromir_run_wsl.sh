#!/usr/bin/env bash
# aromir_run_wsl.sh <plan folder> <spectrum|baseline> <SMILES | path.xyz> <out, relative> <release, relative> <threads> <pyscf MB> [--dry-run]
# The WSL side of probes/aromir_run.sh (TASKS 73); not called by hand. Runs aromir from ~/aromir_v13 and prints
# "(AROMIR) progress: …" every five minutes while the process's CPU time grows, so a stuck run is seen as silence.
set -uo pipefail
# no-set-e: aromir's exit code is read and passed on
[ $# -ge 7 ] || { echo "aromir_run_wsl.sh: called by probes/aromir_run.sh"; exit 2; }
PW=$1; WHAT=$2; MOLECULE=$3; REL_OUT=$4; RELEASE=$5; THREADS=$6; PYSCF_MB=$7; MODE=${8:-}
AROMIR=$HOME/aromir_v13/bin/aromir
BEAT_S=${BEAT_S:-300}
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1
mkdir -p "$HOME/qc_tmp"
cd "$PW" || exit 2
case "$MOLECULE" in *.xyz) TARGET=(--xyz "$MOLECULE") ;; *) TARGET=("$MOLECULE") ;; esac

if [ "$MODE" = --dry-run ]; then
  "$AROMIR" --version || exit 1
  "$AROMIR" check "${TARGET[@]}" || exit 1
  if [ "$WHAT" = spectrum ]; then "$AROMIR" card --release "$RELEASE" > /dev/null || exit 1; echo "(AROMIR) dry run: the release loads"; fi
  exit 0
fi

ARGS=("$WHAT" "${TARGET[@]}" --out "$REL_OUT" --threads "$THREADS" --max-memory-mb "$PYSCF_MB")
[ "$WHAT" = spectrum ] && ARGS+=(--release "$RELEASE")
/usr/bin/time -f "(AROMIR) max RSS %M kB, wall %e s" "$AROMIR" "${ARGS[@]}" &
TIMER=$!
# a stop from outside takes aromir with it, not the wrapper alone
trap 'pkill -P "$TIMER"; kill "$TIMER" 2> /dev/null' TERM INT HUP
cpu_ticks() { ps -o cputimes= --ppid "$TIMER" 2> /dev/null | awk '{s += $1} END {print s + 0}'; }
LAST=0
SLEPT=0
while kill -0 "$TIMER" 2> /dev/null; do
  sleep 5
  SLEPT=$((SLEPT + 5))
  [ "$SLEPT" -ge "$BEAT_S" ] || continue
  SLEPT=0
  kill -0 "$TIMER" 2> /dev/null || break   # ended during the sleep: no cpu time now is not a stuck run
  NOW=$(cpu_ticks)
  if [ "$NOW" -gt "$LAST" ]; then echo "(AROMIR) progress: cpu $NOW s $(date '+%F %T')"; else echo "(AROMIR) no cpu time since the last line $(date '+%F %T')"; fi
  LAST=$NOW
done
wait "$TIMER"
