#!/usr/bin/env bash
# mode_quartic_scan.sh <setting dir> <out dir> <mode>... [--dry-run] — TASKS 207: probes/mode_quartic_scan.py in WSL on pyscf 2.15.0
# (~/qc215) under probes/wsl_capped.sh (CAP_MB) and /usr/bin/time; grids 75/302 (route A's) and 99/590. Markers "=== (MQS) …".
set -euo pipefail
[ $# -ge 3 ] || { echo "usage: mode_quartic_scan.sh <setting dir> <out dir> <mode>... [--dry-run]"; exit 2; }
SETTING=$1
OUT=$2
shift 2
MODES=()
MODE=""
for a in "$@"; do if [ "$a" = "--dry-run" ]; then MODE=$a; else MODES+=("$a"); fi; done
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
CAP_MB=${CAP_MB:-4096}
THREADS=${THREADS:-8}
say() { echo "=== (MQS) $* $(date '+%F %T')"; }

[ -n "$MODE" ] || say "start: modes ${MODES[*]} of $SETTING, cap $CAP_MB MB, $THREADS threads, pyscf 2.15.0"
ARGS="probes/mode_quartic_scan.py $PW/$SETTING $PW/$OUT --modes ${MODES[*]} --threads $THREADS $MODE"
MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
  mkdir -p \$HOME/qc_tmp; cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(MQS) max RSS %M kB, wall %e s' \
  \$HOME/qc215/bin/python $ARGS" || { say "RUN FAILED: the quartic scan (exit $?)"; exit 1; }
[ -n "$MODE" ] || say "done: $(grep -o '"reading": "[A-Z]*"' "$(cd "$(dirname "$0")/.." && pwd)/$OUT/scan.json" | cut -d'"' -f4 | tr '\n' ' ')"
