#!/usr/bin/env bash
# low_mode_patch.sh <ids file> <out dir> [--dry-run] — TASKS 201 step 3: probes/low_mode_patch_run.py on the corpus molecules named in the
# ids file (one per line, '#' comments; probes/low_mode_patch.py writes it), in WSL on pyscf 2.15.0 (~/qc215) under probes/wsl_capped.sh
# (CAP_MB) and /usr/bin/time. Points already written are kept on a resume. Markers "=== (LMP) …".
set -euo pipefail
[ $# -ge 2 ] || { echo "usage: low_mode_patch.sh <ids file> <out dir> [--dry-run]"; exit 2; }
IDS=$1
OUT=$2
MODE=${3:-}
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
CAP_MB=${CAP_MB:-4096}
THREADS=${THREADS:-8}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB / 2))}   # half the cap, as the other grid-response runners: the gradient holds arrays outside max_memory
say() { echo "=== (LMP) $* $(date '+%F %T')"; }

[ -f "$P/$IDS" ] || { say "STOPPED: $IDS missing"; exit 1; }
[ -n "$MODE" ] || say "start: $(grep -vc '^#' "$P/$IDS") molecules from $IDS, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads, pyscf 2.15.0"
ARGS="probes/low_mode_patch_run.py $PW/modules/05_support_predictor/corpus/molecules $PW/$OUT --ids $PW/$IDS --threads $THREADS --max-memory $PYSCF_MB $MODE"
MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
  mkdir -p \$HOME/qc_tmp; cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(LMP) max RSS %M kB, wall %e s' \
  \$HOME/qc215/bin/python $ARGS" || { say "RUN FAILED: the low-mode patch (exit $?)"; exit 1; }
[ -n "$MODE" ] || say "done: $(ls -d "$P/$OUT"/*/report.json 2>/dev/null | wc -l) reports"
