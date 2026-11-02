#!/usr/bin/env bash
# probes/routea_gate_direct.sh — route A gate diagnosis (2 Nov 2026, S3 amendment 2): the 15 −d Hessians the rerun wrote as images, computed directly at the same geometries, so that
# images-vs-direct (the saving's own error) separates from direct-vs-S1 (the reference minimum's difference).
set -euo pipefail
cd /root/dpir_routea2
PY=/root/miniforge3/envs/qc05/bin/python
G=/root/routea_gate2/benzene/G
D=/root/routea_gate2_direct/G
mkdir -p "$D/stubs_m"
cp -r "$G/hess" "$D/hess"
cp "$G/ref.json" "$D/ref.json"
for f in $("$PY" -c "import json; print(' '.join(json.load(open('$G/images.json'))['images']))"); do
  cp "$G/stubs/$f" "$D/stubs_m/$f"
  rm "$D/hess/$f"
done
echo "=== (GD) computing $(ls "$D/stubs_m" | wc -l) Hessians $(date '+%T')"
"$PY" probes/pyscf_hessians_for_qff.py "$D/stubs_m" "$D/hess" --basis '6-31g*' --grid 75,302 --threads 32
(cd /root/dpir_routea2 && PYTHONPATH=src "$PY" -m dpir.qff "$D/hess" --disp 0.10 --out "$D/qff_report.md" > "$D/qff_stdout.log" 2>&1) || echo "=== (GD) qff rc=$?"
echo "=== (GD) done $(date '+%T')"
