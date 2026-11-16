#!/usr/bin/env bash
# probes/anharmonic_field_timing.sh [--dry-run] (16 Nov 2026, TASKS 211) — what the pipeline's anharmonic step costs on one small
# molecule: time and peak memory of step 6 (m08/anharmonic.py) on benzene, with the pipeline's defaults (2 dxtb processes of 2
# threads in a scope of its own, probes/run_in_scope.sh, capped at 1536 MB). The step is run as the pipeline runs it, on a copy of the stored pipeline result
# probes/results_m1/pipeline_benzene_computed_2026-11-03/benzene (git holds none of its arrays, so the copy is made here, once);
# the stored result is not touched. Run by probes/runspecs/anharmonic_field_timing.json.
# Read afterwards: '[anharmonic] done: … s; field {… seconds, peak_memory_mb …}' in the run's log, and the copy's anharmonic.json.
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd)
SRC=$P/probes/results_m1/pipeline_benzene_computed_2026-11-03/benzene
OUT=$P/probes/results_m1/anharmonic_step_2026-11-16/timing/benzene
if [ ! -f "$OUT/pipeline.json" ]; then
  [ -f "$SRC/pipeline.json" ] || { echo "anharmonic_field_timing.sh: $SRC is not on this machine" >&2; exit 2; }
  mkdir -p "$OUT"
  for f in geometry.json hessian_b3lyp_analytic.npz correction.npz dipole_b3lyp_cphf.npz analytic_check.json result.json pipeline.json; do
    cp "$SRC/$f" "$OUT/$f"          # pipeline.json last: its presence says the copy is whole
  done
fi
cd "$P/modules/08_industry_synthesis"
exec env PYTHONUTF8=1 python -m m08.anharmonic "$OUT" --threads 4 --shards 2 --cap-mb 1536 "$@"
