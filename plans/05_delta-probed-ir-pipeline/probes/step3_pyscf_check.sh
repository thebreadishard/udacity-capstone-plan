#!/usr/bin/env bash
# step3_pyscf_check.sh <result folder> (14 Nov 2026, TASKS 225) — the pipeline's step 3 run again on pyscf 2.15.0 over a copy of a
# folder it already computed on 2.14.0, and the two compared. The copy is what makes the comparison exact: the geometry, the grid,
# the basis and the thresholds are the ones that wrote the stored file, so the pyscf version is the only difference.
# The command is step 3's own (m08/pipeline.py low_level_command): the label route, B3LYP alone, at the label grid, under the cap.
# Markers "=== (S3P) …".
#   bash probes/step3_pyscf_check.sh probes/results_m1/pipeline_benzene_computed_2026-11-03/benzene
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd)
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
SRC=${1:?the folder whose label file the older pyscf wrote}
OUT=${OUT:-probes/results_m1/step3_pyscf_2026-11-14}
CAP_MB=${CAP_MB:-6144}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB - 584))}   # step 3's own headroom (m08/pipeline.py PYSCF_HEADROOM_MB)
THREADS=${THREADS:-6}
GRID=${GRID:-99,590}                      # m08/pipeline.py LOW_GRID: the corpus's labels
say() { echo "=== (S3P) $* $(date '+%F %T')"; }

cd "$P"
[ -f "$SRC/hessian_b3lyp_analytic.npz" ] || { say "STOPPED: $SRC has no stored B3LYP label"; exit 1; }
FRESH="$OUT/fresh"
rm -rf "$FRESH"
mkdir -p "$FRESH"
# only the inputs travel: the route writes its own labels, and a stored one left in place would be reused instead of recomputed
for f in geometry.json job.json result.json; do [ -f "$SRC/$f" ] && cp "$SRC/$f" "$FRESH/"; done

say "start: $SRC -> $FRESH on pyscf 2.15.0, grid $GRID, $THREADS threads, cap $CAP_MB MB (pyscf $PYSCF_MB MB)"
MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
  mkdir -p \$HOME/qc_tmp; cd $PW/modules/05_support_predictor/corpus && bash $PW/probes/wsl_capped.sh $CAP_MB -- \
  /usr/bin/time -f '(S3P) max RSS %M kB, wall %e s' \$HOME/qc215/bin/python analytic_hessians.py $PW/$FRESH \
  --functionals b3lyp --grid $GRID --threads $THREADS --max-memory $PYSCF_MB" || { say "FAILED: the label route (exit $?)"; exit 1; }

PYTHONUTF8=1 python probes/step3_pyscf_check.py "$SRC" "$FRESH" --out "$OUT"
say "done"
