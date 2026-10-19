#!/usr/bin/env bash
# probes/dfmp2_run.sh <out dir> (19 Oct 2026; registration GoalGathering/notes/PreRegistration_2026-10-19_DFMP2_Composite_Step.md) — runs in WSL
# under probes/wsl_capped.sh: check W on water (stops when it fails), then the DF-MP2 rows of pyridine and naphthalene at cc-pVDZ and cc-pVTZ
# like their 7 Oct conventional files (probes/results_m1/composite_rows_2026-10-07), each under /usr/bin/time for its peak RSS. Markers
# '=== (DF) …'; the end line '=== (DF) all done'. Resumable: dfmp2_rows.py skips rows already written.
#   bash probes/dfmp2_run.sh /mnt/c/.../probes/results_m1/dfmp2_composite_2026-10-19
set -euo pipefail
OUT=${1:?out dir}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/miniforge3/envs/vpt2/bin/python}
export PSI_SCRATCH=$HOME/psi4_scratch   # not /tmp: WSL clears it when idle (19 Oct 2026)
CONV=$HERE/results_m1/composite_rows_2026-10-07
MOL=$HERE/../modules/05_support_predictor/corpus/molecules
mkdir -p "$OUT" "$PSI_SCRATCH"
mark() { echo "=== (DF) $* $(date '+%F %T')"; }

mark "start: psi4 $("$PY" -c 'import psi4; print(psi4.__version__)'), $(nproc) cores"
if [ ! -f "$OUT/water_check.json" ]; then
  "$PY" "$HERE/dfmp2_rows.py" water --out "$OUT/water_check.json" || { mark "WATER CHECK FAILED - stopped before any row"; exit 1; }
fi
grep -q '"passed": true' "$OUT/water_check.json" || { mark "WATER CHECK FAILED - stopped before any row"; exit 1; }
mark "water check passed"
for spec in pyridine:A_6e858b26e5 naphthalene:A_01f3186607; do
  name=${spec%%:*}; id=${spec#*:}
  for b in ccpvdz ccpvtz; do
    /usr/bin/time -v -o "$OUT/time_${name}_${b}.txt" "$PY" "$HERE/dfmp2_rows.py" rows --like "$CONV/mp2_rows_${name}_${b}.npz" \
      --symbols-from "$MOL/$id/geometry.json" --out "$OUT/dfmp2_rows_${name}_${b}.npz"
    mark "$name $b done, peak RSS $(grep 'Maximum resident' "$OUT/time_${name}_${b}.txt" | awk '{print $NF}') kB"
  done
done
mark "all done"
