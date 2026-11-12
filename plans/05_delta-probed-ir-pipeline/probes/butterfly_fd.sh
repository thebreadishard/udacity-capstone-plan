#!/usr/bin/env bash
# butterfly_fd.sh <molecule id> [--dry-run] — TASKS 49, the user's option 3 of 12 Nov 2026: probes/butterfly_fd.py on the re-optimised
# molecule in corpus/reoptimised_2026-11-11/<id>, in WSL on pyscf 2.15.0 (~/qc215) under probes/wsl_capped.sh (CAP_MB) and /usr/bin/time,
# so the run spec's memory bound is the cap and the peak is measured. Points already written are kept on a resume. Markers "=== (BFD) …".
set -euo pipefail
ID=${1:?usage: butterfly_fd.sh <molecule id> [--dry-run]}
MODE=${2:-}
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
REL_IN=modules/05_support_predictor/corpus/reoptimised_2026-11-11/$ID
REL_OUT=probes/results_m1/butterfly_fd_${ID}_2026-11-12
CAP_MB=${CAP_MB:-9216}
THREADS=${THREADS:-8}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB - 584))}   # pyscf's max_memory, below the cap, as butterfly_scan.sh
say() { echo "=== (BFD) $* $(date '+%F %T')"; }

[ -f "$P/$REL_IN/geometry.json" ] && [ -f "$P/$REL_IN/hessian_b3lyp_analytic.npz" ] || { say "STOPPED: $REL_IN lacks geometry or Hessian"; exit 1; }
ARGS="probes/butterfly_fd.py $PW/$REL_IN $PW/$REL_OUT --threads $THREADS --max-memory $PYSCF_MB"
[ "$MODE" = "--dry-run" ] && ARGS="$ARGS --dry-run"
[ "$MODE" = "--dry-run" ] || say "start: $ID, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads, pyscf 2.15.0"
MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
  mkdir -p \$HOME/qc_tmp; cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(BFD) $ID max RSS %M kB, wall %e s' \
  \$HOME/qc215/bin/python $ARGS" || { say "RUN FAILED: the gradient differences of $ID (exit $?)"; exit 1; }
[ "$MODE" = "--dry-run" ] && exit 0
call=$(grep -oE '"verdict": "[A-Z]+"' "$P/$REL_OUT/fd.json" | cut -d'"' -f4)
[ -n "$call" ] || { say "RUN FAILED: $REL_OUT/fd.json has no verdict"; exit 1; }
say "done: verdict $call"
