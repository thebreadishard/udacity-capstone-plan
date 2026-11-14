#!/usr/bin/env bash
# label_route_vs_probe.sh <molecule id> — TASKS 216 test 3: probes/label_route_vs_probe.py in WSL on pyscf 2.15.0 (~/qc215), under
# probes/wsl_capped.sh (CAP_MB) and /usr/bin/time, as the corpus repair itself ran. The comparison needs the same environment as the
# measurement it checks, which is why it goes through WSL and not through the Windows python. Markers "=== (LRVP) …".
set -euo pipefail
ID=${1:-D_ac28161d06}
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
CAP_MB=${CAP_MB:-4096}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB / 2))}   # half the cap, as low_mode_patch.sh: the gradient holds arrays outside max_memory
THREADS=${THREADS:-8}
say() { echo "=== (LRVP) $* $(date '+%F %T')"; }

say "start: $ID, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads, pyscf 2.15.0"
MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
  mkdir -p \$HOME/qc_tmp; cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(LRVP) max RSS %M kB, wall %e s' \
  \$HOME/qc215/bin/python $PW/probes/label_route_vs_probe.py --id $ID --max-memory $PYSCF_MB" || { say "FAILED: the comparison (exit $?)"; exit 1; }
say "done: $ID"
