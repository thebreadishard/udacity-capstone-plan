#!/usr/bin/env bash
# bootstrap_psi4_ccx53.sh (13 Oct 2026, TASKS 49 / chain 42) — psi4 on the labels server for the large-PAH optimisations, which the lever-5 price
# already counts on the CCX53 (10 % optimisation allowance). The labels server has only qc05 (pyscf); pool 3 is busy for ≈ 12 more days.
# Steps, each checked:
#   1. pool 3's qc environment exported as an explicit spec (exact builds: psi4 1.11, optking 0.5.0, qcelemental 0.51.2, numpy 2.5.3, python 3.14.7);
#   2. created on the labels server as env 'qc' from that spec (nice 19: the four label lanes keep their cores);
#   3. our optking linear-bend fix applied and checked (probes/optking_patches; missing on two installs once, 9 Oct);
#   4. a water smoke through the corpus's psi4_worker.py with the deck's settings and "hessians": false (optimised, no Hessian files).
# Refuses when /root/miniforge3/envs/qc exists already. Nothing here touches the label lanes or their files.
#   bash probes/bootstrap_psi4_ccx53.sh
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
SCP="scp -q -o BatchMode=yes -o ConnectTimeout=20 -i $HOME/.ssh/hetzner_g_measure"
CORPUS="$HERE/../modules/05_support_predictor/corpus"
TMP=$(mktemp -d)
LABELS_IP=$(host_ip labels)
host_ssh labels 'test ! -e /root/miniforge3/envs/qc' || { echo "env qc exists on the labels server — refusing"; exit 1; }
echo "(1) export pool 3's qc env"
host_ssh pool3 '/root/miniforge3/bin/conda list -n qc --explicit' > "$TMP/qc_spec.txt"
grep -q '/psi4-1.11-' "$TMP/qc_spec.txt" || { echo "the spec has no psi4 1.11 build"; exit 1; }
echo "    $(grep -c '^https' "$TMP/qc_spec.txt") packages"
$SCP "$TMP/qc_spec.txt" "$HERE/optking_patches/apply_optking_fix.py" "$CORPUS/psi4_worker.py" "root@$LABELS_IP:/root/labels/"
echo "(2) create env qc on the labels server (nice 19)"
host_ssh labels 'nice -n 19 /root/miniforge3/bin/conda create -y -q -n qc --file /root/labels/qc_spec.txt > /root/labels/qc_env_create.log 2>&1; echo rc=$?' \
  | grep -qx 'rc=0' || { echo "conda create failed (see /root/labels/qc_env_create.log)"; exit 1; }
host_ssh labels '/root/miniforge3/envs/qc/bin/python -c "import psi4, optking; print(psi4.__version__, optking.__version__)"'
echo "(3) optking fix"
host_ssh labels 'P=/root/miniforge3/envs/qc/bin/python; $P /root/labels/apply_optking_fix.py > /dev/null && $P /root/labels/apply_optking_fix.py --check | grep -c "already patched" | grep -qx 2' \
  || { echo "OPTKING FIX NOT APPLIED"; exit 1; }
echo "(4) water smoke: psi4_worker, deck v1, no Hessians, 2 threads, nice 19"
python - "$CORPUS/decks/deck_v1.json" > "$TMP/job.json" <<'EOF'
import json, sys
deck = json.load(open(sys.argv[1], encoding="utf-8"))
deck.update(threads=2, memory_gb=4)
print(json.dumps({"id": "water_smoke", "layer": "D", "deck": deck, "out_dir": "/root/labels/psi4_smoke/water_smoke", "optimise": True,
                  "grid_check": False, "hessians": False, "xyz_angstrom": [["O", 0.0, 0.0, 0.117], ["H", 0.0, 0.757, -0.469], ["H", 0.0, -0.757, -0.469]]}))
EOF
$SCP "$TMP/job.json" "root@$LABELS_IP:/root/labels/psi4_smoke_job.json"
host_ssh labels 'mkdir -p /root/labels/psi4_smoke && cd /root/labels && OMP_NUM_THREADS=2 nice -n 19 timeout 900 /root/miniforge3/envs/qc/bin/python psi4_worker.py psi4_smoke_job.json > psi4_smoke/smoke.log 2>&1; echo rc=$?;
  ls psi4_smoke/water_smoke; python3 -c "import json; r=json.load(open(\"psi4_smoke/water_smoke/result.json\")); print(r.get(\"status\"), r.get(\"labels\", r.get(\"analytic_only\")))"'
rm -rf "$TMP"
