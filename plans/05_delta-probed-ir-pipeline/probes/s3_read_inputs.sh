#!/usr/bin/env bash
# s3_read_inputs.sh <out dir> [--dry-run] — the targets' inputs of S3's registered read (probes/s3_read.py, TASKS 53;
# PreRegistration_2026-11-02_S3_Route_A_Transfer.md, 'Read': "the targets are read by the same loader: G labels from gvpt2_labels.py, xtb
# partners from s2_xtb_read"), built as probes/s2b_read_inputs.sh built S2b's:
#   1. <out>/selection.json: tetracene and coronene, each its own scaffold (the loader groups by scaffold);
#   2. GVPT2 labels on both sides (probes/gvpt2_labels.py with the polyad fork on the path): G from route A's fetched force fields
#      (routea_server_2026-11-10/routea), X from the laptop's xtb force fields (routea_2026-11-02/xtb);
#   3. <out>/targets.json, one computed set "S3 targets".
# The training sets are S2b's read's own sets.json, unchanged.
set -euo pipefail
OUT=${1:?usage: s3_read_inputs.sh <out dir> [--dry-run]}
MODE=${2:-}
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
R=probes/results_m1
ROOT=$R/routea_server_2026-11-10/routea
XTB=$R/routea_2026-11-02/xtb

cd "$P"
for id in tetracene coronene; do
  for d in "$ROOT/$id/G/qff_report.npz" "$XTB/$id/X/qff_report.npz"; do
    [ -f "$d" ] || { echo "s3_read_inputs.sh: $d missing" >&2; exit 1; }
  done
done
echo "S3 targets: tetracene and coronene, G under $ROOT, X under $XTB"
[ "$MODE" = "--dry-run" ] && exit 0
mkdir -p "$OUT"

tmp=$(mktemp "$OUT/selection.json.XXXX")
cat > "$tmp" <<'EOF'
{"rule": "S3's targets (PreRegistration_2026-11-02_S3_Route_A_Transfer.md): tetracene and coronene, never in S2 or S2b; each its own scaffold",
 "selected": [
  {"id": "tetracene", "smiles": "c1ccc2cc3cc4ccccc4cc3cc2c1", "n_atoms": 30, "rigid": true, "scaffold": "c1ccc2cc3cc4ccccc4cc3cc2c1"},
  {"id": "coronene", "smiles": "c1cc2ccc3ccc4ccc5ccc6ccc1c1c2c3c4c5c61", "n_atoms": 36, "rigid": true,
   "scaffold": "c1cc2ccc3ccc4ccc5ccc6ccc1c1c2c3c4c5c61"}
 ]}
EOF
mv "$tmp" "$OUT/selection.json"

in_wsl() {   # one python call from the plan folder in the conda env 'vpt2' (pyVPT2 imports psi4), the polyad fork on the path
  MSYS_NO_PATHCONV=1 wsl -e bash -c "cd $PW && PYTHONPATH=\$HOME/pyvpt2-wt-polyad PYTHONUNBUFFERED=1 \$HOME/miniforge3/envs/vpt2/bin/python $*"
}
in_wsl "probes/gvpt2_labels.py $ROOT --selection $OUT/selection.json --setting G --out $OUT/gvpt2"
in_wsl "probes/gvpt2_labels.py $XTB --selection $OUT/selection.json --setting X --out $OUT/gvpt2_x"

tmp=$(mktemp "$OUT/targets.json.XXXX")
cat > "$tmp" <<EOF
[
 {"name": "S3 targets", "root": "$ROOT", "selection": "$OUT/selection.json", "gvpt2_dir": "$OUT/gvpt2", "xtb_root": "$XTB",
  "xtb_gvpt2_dir": "$OUT/gvpt2_x", "extra": {}}
]
EOF
mv "$tmp" "$OUT/targets.json"
echo "s3_read_inputs.sh: $(ls "$OUT/gvpt2" | wc -l) G labels, $(ls "$OUT/gvpt2_x" | wc -l) X labels, $OUT/targets.json"
