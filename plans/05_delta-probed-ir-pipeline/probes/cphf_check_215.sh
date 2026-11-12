#!/usr/bin/env bash
# cphf_check_215.sh <molecule id> [--dry-run] — TASKS 49 (the user, 12 Nov 2026: test the CPHF cause on D_ac28161d06 with 2.15.0):
# probes/cphf_check_215.py on the re-optimised label folder and option 3's fd.json, in WSL on pyscf 2.15.0 (~/qc215) under
# probes/wsl_capped.sh (CAP_MB) and /usr/bin/time. Markers "=== (CPHF) …".
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: cphf_check_215.sh <molecule id> [--dry-run]"; exit 2; }
ID=$1
MODE=${2:-}
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
CAP_MB=${CAP_MB:-12288}
THREADS=${THREADS:-8}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB / 2))}   # half the cap, as butterfly_fd.sh: the Hessian holds arrays outside max_memory
REL_IN=modules/05_support_predictor/corpus/reoptimised_2026-11-11/$ID
REL_FD=probes/results_m1/butterfly_fd_${ID}_2026-11-12/fd.json
REL_OUT=probes/results_m1/cphf_check_215_${ID}_2026-11-12
say() { echo "=== (CPHF) $* $(date '+%F %T')"; }

for f in "$REL_IN/geometry.json" "$REL_IN/hessian_b3lyp_analytic.npz" "$REL_FD"; do
  [ -f "$P/$f" ] || { say "STOPPED: $f missing"; exit 1; }
done
[ -n "$MODE" ] || say "start: $ID, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads, pyscf 2.15.0"
ARGS="probes/cphf_check_215.py $PW/$REL_IN $PW/$REL_FD $PW/$REL_OUT --threads $THREADS --max-memory $PYSCF_MB $MODE"
MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
  mkdir -p \$HOME/qc_tmp; cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(CPHF) $ID max RSS %M kB, wall %e s' \
  \$HOME/qc215/bin/python $ARGS" || { say "RUN FAILED: the 2.15.0 Hessian of $ID (exit $?)"; exit 1; }
[ -n "$MODE" ] && exit 0
[ -f "$P/$REL_OUT/report.json" ] || { say "RUN FAILED: $REL_OUT/report.json missing"; exit 1; }
say "done: verdict $(grep -o '"verdict": "[A-Z ]*"' "$P/$REL_OUT/report.json" | cut -d'"' -f4)"
