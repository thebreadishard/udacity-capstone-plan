#!/usr/bin/env bash
# low_mode_patch.sh <ids file> <out dir> [--below CM] [--step BOHR] [--dry-run] [--show-command] — TASKS 201 step 3:
# probes/low_mode_patch_run.py on the corpus molecules named in the ids file (one per line, '#' comments; probes/low_mode_patch.py writes
# it), in WSL on pyscf 2.15.0 (~/qc215) under probes/wsl_capped.sh (CAP_MB) and /usr/bin/time. Points already written are kept on a
# resume. --below and --step go to the runner as they are (its defaults are the repair's: 20 cm⁻¹ and 0.01 bohr; TASKS 218 measures at
# other values). --dry-run lists what the runner would compute; --show-command prints the runner's arguments and starts nothing.
# Both paths are relative to the plan folder this script lies in, so a worktree's copy reads and writes that worktree.
# Markers "=== (LMP) …".
set -euo pipefail
USAGE="usage: low_mode_patch.sh <ids file> <out dir> [--below CM] [--step BOHR] [--dry-run] [--show-command]"
[ $# -ge 2 ] || { echo "$USAGE"; exit 2; }
IDS=$1
OUT=$2
shift 2
EXTRA=()
DRY=""
SHOW=""
while [ $# -gt 0 ]; do
  case "$1" in
    --below|--step) [ $# -ge 2 ] || { echo "$1 needs a value; $USAGE"; exit 2; }; EXTRA+=("$1" "$2"); shift 2 ;;
    --dry-run) DRY=1; EXTRA+=(--dry-run); shift ;;
    --show-command) SHOW=1; shift ;;
    *) echo "unknown argument '$1'; $USAGE"; exit 2 ;;
  esac
done
P=$(cd "$(dirname "$0")/.." && pwd)
# Git Bash names drive C as /c/…, WSL as /mnt/c/…; on Linux or inside WSL a path is its own, also one that starts with a one-letter
# folder. LMP_HOST_KERNEL stands in for `uname -s` in the test.
case "${LMP_HOST_KERNEL:-$(uname -s)}" in
  MINGW*|MSYS*|CYGWIN*) PW=/mnt$P ;;
  *) PW=$P ;;
esac
CAP_MB=${CAP_MB:-4096}
THREADS=${THREADS:-8}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB / 2))}   # half the cap, as the other grid-response runners: the gradient holds arrays outside max_memory
say() { echo "=== (LMP) $* $(date '+%F %T')"; }

[ -f "$P/$IDS" ] || { say "STOPPED: $IDS missing"; exit 1; }
ARGS=(probes/low_mode_patch_run.py "$PW/modules/05_support_predictor/corpus/molecules" "$PW/$OUT" --ids "$PW/$IDS"
      --threads "$THREADS" --max-memory "$PYSCF_MB" ${EXTRA[@]+"${EXTRA[@]}"})
QUOTED=$(printf '%q ' "${ARGS[@]}")     # each argument quoted for the shell inside WSL, so a path with a space stays one argument
if [ -n "$SHOW" ]; then echo "(LMP) cap $CAP_MB MB: python ${QUOTED% }"; exit 0; fi
[ -n "$DRY" ] || say "start: $(grep -vc '^#' "$P/$IDS") molecules from $IDS, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads, pyscf 2.15.0${EXTRA[*]+, ${EXTRA[*]}}"
MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
  mkdir -p \$HOME/qc_tmp; cd $(printf '%q' "$PW") && bash $(printf '%q' "$PW/probes/wsl_capped.sh") $CAP_MB -- \
  /usr/bin/time -f '(LMP) max RSS %M kB, wall %e s' \$HOME/qc215/bin/python $QUOTED" || { say "RUN FAILED: the low-mode patch (exit $?)"; exit 1; }
[ -n "$DRY" ] || say "done: $(ls -d "$P/$OUT"/*/report.json 2>/dev/null | wc -l) reports"
