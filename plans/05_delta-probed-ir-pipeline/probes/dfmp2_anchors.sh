#!/usr/bin/env bash
# probes/dfmp2_anchors.sh <out dir> (20 Oct 2026; registration GoalGathering/notes/PreRegistration_2026-10-19_DFMP2_Composite_Step.md, outcome:
# the DF route carries anchor set three's composite step; the user: 'bouw de geometriemodus en start de vijf ankers') — runs in WSL under
# probes/wsl_capped.sh: the DF-MP2 rows at cc-pVDZ and cc-pVTZ of the five carried candidates of waves 1–2, smallest first, planned from each
# corpus geometry (the anchors' own coordinates), each under /usr/bin/time for its peak RSS. Markers '=== (DFA) …'; the end line
# '=== (DFA) all done'. Resumable: dfmp2_rows.py skips rows already written.
#   bash probes/dfmp2_anchors.sh /mnt/c/.../probes/results_m1/dfmp2_anchors_2026-10-20
set -euo pipefail
OUT=${1:?out dir}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/miniforge3/envs/vpt2/bin/python}
export PSI_SCRATCH=$HOME/psi4_scratch   # not /tmp: WSL clears it when idle (19 Oct 2026)
MOL=$HERE/../modules/05_support_predictor/corpus/molecules
mkdir -p "$OUT" "$PSI_SCRATCH"
mark() { echo "=== (DFA) $* $(date '+%F %T')"; }

mark "start: psi4 $("$PY" -c 'import psi4; print(psi4.__version__)'), five anchors at cc-pVDZ and cc-pVTZ"
for spec in quinoxaline:A_7aa232d4e9 quinoline:A_ff98e1160d isoquinoline:A_d09f8d1ef8 azulene:A_d9139359ab acenaphthylene:A_45187bb7c8; do
  name=${spec%%:*}; id=${spec#*:}
  for b in cc-pvdz cc-pvtz; do
    short=${b//-/}
    /usr/bin/time -v -o "$OUT/time_${name}_${short}.txt" "$PY" "$HERE/dfmp2_rows.py" rows --geometry "$MOL/$id/geometry.json" --basis "$b" \
      --out "$OUT/dfmp2_rows_${name}_${short}.npz"
    mark "$name $short done, peak RSS $(grep 'Maximum resident' "$OUT/time_${name}_${short}.txt" | awk '{print $NF}') kB"
  done
done
mark "all done"
