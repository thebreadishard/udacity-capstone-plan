#!/usr/bin/env bash
# aromir_repair_vs_probe.sh <molecule id> [--dry-run] — TASKS 73, 216 (the user, 15 Nov 2026: test aromir's soft-mode repair on
# D_ac28161d06 against the probe's value): probes/aromir_repair_vs_probe.py in WSL's ~/aromir_v13 (aromir, pyscf 2.15.0) under
# probes/wsl_capped.sh (CAP_MB) and /usr/bin/time. Markers "=== (ARVP) …"; pyscf's own log grows in the result folder's pyscf.log.
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: aromir_repair_vs_probe.sh <molecule id> [--dry-run]"; exit 2; }
ID=$1
MODE=${2:-}
case "$MODE" in ''|--dry-run) ;; *) echo "aromir_repair_vs_probe.sh: '$MODE' is not --dry-run"; exit 2 ;; esac
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
CAP_MB=${CAP_MB:-10240}
THREADS=${THREADS:-8}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB / 2))}   # half the cap: pyscf's grid-response gradient holds one atom's whole grid outside max_memory
REL_OUT=probes/results_m1/aromir_repair_vs_probe_${ID}_2026-11-15
say() { echo "=== (ARVP) $* $(date '+%F %T')"; }

for f in "modules/05_support_predictor/corpus/molecules/$ID/geometry.json" \
         "modules/05_support_predictor/corpus/superseded_2026-11-14/$ID/hessian_b3lyp_analytic.npz" \
         "probes/results_m1/low_mode_patch_2026-11-13/corpus/$ID/hessian_b3lyp_analytic_grfpatch.npz" \
         "probes/results_m1/low_mode_patch_2026-11-13/corpus/$ID/report.json"; do
  [ -f "$P/$f" ] || { say "STOPPED: $f missing"; exit 1; }
done
[ -n "$MODE" ] || say "start: $ID, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads, aromir on pyscf 2.15.0"
ARGS="probes/aromir_repair_vs_probe.py --id $ID --out $PW/$REL_OUT --threads $THREADS --max-memory $PYSCF_MB $MODE"
MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
  mkdir -p \$HOME/qc_tmp; cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(ARVP) $ID max RSS %M kB, wall %e s' \
  \$HOME/aromir_v13/bin/python $ARGS" || { say "RUN FAILED: aromir's repair of $ID (exit $?)"; exit 1; }
[ -n "$MODE" ] && exit 0
[ -f "$P/$REL_OUT/aromir_repair_vs_probe.json" ] || { say "RUN FAILED: $REL_OUT/aromir_repair_vs_probe.json missing"; exit 1; }
say "done: $ID, record in $REL_OUT"
