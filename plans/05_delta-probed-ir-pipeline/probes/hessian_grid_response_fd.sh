#!/usr/bin/env bash
# hessian_grid_response_fd.sh <molecule id>... [--dry-run] — TASKS 201 step 2 (the user, 12 Nov 2026: after option 3, before S3):
# probes/hessian_grid_response_fd.py on each corpus molecule in turn, B3LYP and ωB97X at the label grid, in WSL on pyscf 2.15.0 (~/qc215)
# under probes/wsl_capped.sh (CAP_MB) and /usr/bin/time. Points already written are kept on a resume. Markers "=== (GRF) …".
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: hessian_grid_response_fd.sh <molecule id>... [--dry-run]"; exit 2; }
MODE=""
IDS=()
for a in "$@"; do if [ "$a" = "--dry-run" ]; then MODE=$a; else IDS+=("$a"); fi; done
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
CAP_MB=${CAP_MB:-8192}
THREADS=${THREADS:-8}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB / 2))}   # half the cap, as butterfly_fd.sh: the analytic Hessian and the grid response hold arrays outside it
say() { echo "=== (GRF) $* $(date '+%F %T')"; }

[ -n "$MODE" ] || say "start: ${IDS[*]}, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads, pyscf 2.15.0"
for ID in "${IDS[@]}"; do
  REL_IN=modules/05_support_predictor/corpus/molecules/$ID
  REL_OUT=probes/results_m1/hessian_grf_${ID}_2026-11-12
  for f in geometry.json hessian_b3lyp_analytic.npz hessian_wb97x_analytic.npz; do
    [ -f "$P/$REL_IN/$f" ] || { say "STOPPED: $REL_IN lacks $f"; exit 1; }
  done
  ARGS="probes/hessian_grid_response_fd.py $PW/$REL_IN $PW/$REL_OUT --threads $THREADS --max-memory $PYSCF_MB $MODE"
  MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
    mkdir -p \$HOME/qc_tmp; cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(GRF) $ID max RSS %M kB, wall %e s' \
    \$HOME/qc215/bin/python $ARGS" || { say "RUN FAILED: the grid-response FD Hessians of $ID (exit $?)"; exit 1; }
  [ -n "$MODE" ] && continue
  [ -f "$P/$REL_OUT/report.json" ] || { say "RUN FAILED: $REL_OUT/report.json missing"; exit 1; }
  echo "(GRF) $ID report written"
done
[ -n "$MODE" ] || say "done: ${#IDS[@]} molecules"
