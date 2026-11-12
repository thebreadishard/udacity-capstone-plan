#!/usr/bin/env bash
# s2b_read_inputs.sh <out dir> [--dry-run] — the inputs of S2b's registered read (probes/s2b_read.py, TASKS 53), built as S2's were:
#   1. GVPT2 labels of the S2b molecules on both sides (probes/gvpt2_labels.py with the polyad fork on the path, as its docstring says):
#      G from the three server fetches (s2b1's folder as the root, the molecules fetched from s2b2 and s2b3 passed by --extra), X from
#      the laptop's xtb force fields (s2b_xtb_2026-11-02/xtb);
#   2. <out>/sets.json: S2 (its committed roots and labels) and S2b.
# A molecule's label already written is computed again (gvpt2_labels.py writes every selected molecule; seconds each).
set -euo pipefail
OUT=${1:?usage: s2b_read_inputs.sh <out dir> [--dry-run]}
MODE=${2:-}
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
R=probes/results_m1
ROOT=$R/s2b1_server_2026-11-11/s2b
SEL=$R/s2b_training_set_2026-10-19/selection.json
XTB=$R/s2b_xtb_2026-11-02/xtb

cd "$P"
extra=()
for f in s2b2_server_2026-11-11 s2b3_server_2026-11-09; do
  for g in "$R/$f"/s2b/*/G; do extra+=("$(basename "$(dirname "$g")")=$g"); done
done
n_root=$(find "$ROOT" -mindepth 2 -maxdepth 2 -name G -type d | wc -l)
echo "S2b: $n_root molecules under $ROOT, ${#extra[@]} by --extra, xtb root $XTB"
[ "$MODE" = "--dry-run" ] && exit 0

mkdir -p "$OUT"
in_wsl() {   # one python call from the plan folder in the conda env 'vpt2' (pyVPT2 imports psi4), the polyad fork on the path
  MSYS_NO_PATHCONV=1 wsl -e bash -c "cd $PW && PYTHONPATH=\$HOME/pyvpt2-wt-polyad PYTHONUNBUFFERED=1 \$HOME/miniforge3/envs/vpt2/bin/python $*"
}
in_wsl "probes/gvpt2_labels.py $ROOT --selection $SEL --setting G --out $OUT/gvpt2 --extra ${extra[*]}"
in_wsl "probes/gvpt2_labels.py $XTB --selection $SEL --setting X --out $OUT/gvpt2_x"

extra_json=$(printf '%s\n' "${extra[@]}" | awk -F= 'BEGIN{printf "{"} {printf "%s\"%s\": \"%s\"", (NR>1?", ":""), $1, $2} END{printf "}"}')
tmp=$(mktemp "$OUT/sets.json.XXXX")
cat > "$tmp" <<EOF
[
 {"name": "S2", "root": "$R/s2_anharmonic_2026-10-18/s2", "selection": "$R/s2_training_set_2026-10-14/selection.json",
  "gvpt2_dir": "$R/s2_anharmonic_2026-10-18/gvpt2", "xtb_root": "$R/s2_xtb_2026-10-18/xtb", "xtb_gvpt2_dir": "$R/s2_xtb_2026-10-18/gvpt2_x"},
 {"name": "S2b", "root": "$ROOT", "selection": "$SEL", "gvpt2_dir": "$OUT/gvpt2", "xtb_root": "$XTB", "xtb_gvpt2_dir": "$OUT/gvpt2_x",
  "extra": $extra_json}
]
EOF
mv "$tmp" "$OUT/sets.json"
echo "s2b_read_inputs.sh: $(ls "$OUT/gvpt2" | wc -l) G labels, $(ls "$OUT/gvpt2_x" | wc -l) X labels, $OUT/sets.json"
