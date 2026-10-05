#!/bin/bash
# bootstrap_labels_ccx53.sh <ip> — registration 1 of GoalGathering/notes/Design_2026-10-05_Analytic_Labels_and_Stepping_Stone.md (5 Oct 2026; the user:
# "De server: ja"): a fresh CCX53 (Ubuntu, 32 dedicated cores, 128 GB) becomes the analytic-label factory for the 811 corpus molecules that have
# finite-difference labels only. Steps, each with its marker: system + miniforge + env qc05 (python 3.12, pip pyscf 2.14.0, numpy, psutil — the hel1-2
# recipe of 1 Oct without the CC kernel); the corpus's analytic_hessians.py and one small tarball of molecule inputs (geometry.json and the two psi4
# Hessians per molecule, for the per-molecule noise record); THE GATE — benzene's analytic B3LYP Hessian recomputed on the server against the laptop's
# file (max |ΔH| ≤ 1e-6 a.u., same grid 99,590), the lanes do not start without it; then four lanes of 8 threads (probes/labels_lane.sh) over the
# size-balanced id lists scratchpad/labels_ids_{0,1,2,3}.txt, detached with setsid. Nothing is deleted on the laptop; the fetch is a separate script.
#   bash probes/bootstrap_labels_ccx53.sh <ip>
set -u
# no-set-e: every step checks its own result and stops with a named marker
IP=$1
KEY=~/.ssh/hetzner_g_measure
S="ssh -i $KEY -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
C=$P/modules/05_support_predictor/corpus
SP=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
t() { date '+%T'; }
for f in "$SP/labels_ids_0.txt" "$SP/labels_inputs.tgz" "$P/probes/labels_lane.sh"; do [ -f "$f" ] || { echo "MISSING $f (run the preparation first)"; exit 1; }; done

echo "[$(t) $IP] system + miniforge"
$S 'export DEBIAN_FRONTEND=noninteractive; apt-get update -q > /tmp/apt.log 2>&1; apt-get install -yq build-essential rsync htop >> /tmp/apt.log 2>&1; test -x /root/miniforge3/bin/conda || { curl -sL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -o /tmp/mf.sh && bash /tmp/mf.sh -b -p /root/miniforge3 > /tmp/mf.log 2>&1; }; /root/miniforge3/bin/conda --version' < /dev/null || { echo "MINIFORGE FAILED $IP"; exit 1; }
echo "[$(t) $IP] env qc05 (python 3.12, pyscf 2.14.0)"
$S 'test -x /root/miniforge3/envs/qc05/bin/python || /root/miniforge3/bin/conda create -y -q -n qc05 python=3.12 > /tmp/env.log 2>&1; /root/miniforge3/envs/qc05/bin/pip install -q pyscf==2.14.0 numpy psutil >> /tmp/env.log 2>&1; /root/miniforge3/envs/qc05/bin/python -c "import pyscf, numpy; print(\"pyscf\", pyscf.__version__, \"numpy\", numpy.__version__)"' < /dev/null || { echo "ENV FAILED $IP"; exit 1; }
echo "[$(t) $IP] files: analytic_hessians.py, labels_lane.sh, id lists, molecule inputs"
scp -q -i $KEY -o BatchMode=yes "$C/analytic_hessians.py" "$P/probes/labels_lane.sh" "$SP"/labels_ids_[0-3].txt "$SP/labels_inputs.tgz" root@$IP:/root/ || { echo "SCP FAILED $IP"; exit 1; }
$S 'mkdir -p /root/labels && mv /root/analytic_hessians.py /root/labels_lane.sh /root/labels_ids_[0-3].txt /root/labels/ && cd /root/labels && tar xzf /root/labels_inputs.tgz && ls molecules | wc -l' < /dev/null || { echo "UNPACK FAILED $IP"; exit 1; }
echo "[$(t) $IP] GATE: benzene analytic B3LYP against the laptop's file (grid 99,590)"
scp -q -i $KEY -o BatchMode=yes "$C/molecules/A_8448043181/hessian_b3lyp_analytic.npz" root@$IP:/root/labels/gate_benzene_laptop.npz || { echo "GATE SCP FAILED $IP"; exit 1; }
$S 'cd /root/labels && mkdir -p gate/A_8448043181 && cp molecules/A_8448043181/geometry.json gate/A_8448043181/ && export OMP_NUM_THREADS=8 && /root/miniforge3/envs/qc05/bin/python analytic_hessians.py gate/A_8448043181 --threads 8 > gate/gate.log 2>&1 && /root/miniforge3/envs/qc05/bin/python - <<PYEOF
import numpy as np
a = np.load("gate/A_8448043181/hessian_b3lyp_analytic.npz")["H_raw"]; b = np.load("gate_benzene_laptop.npz")["H_raw"]
d = float(np.abs(a - b).max()); print(f"GATE benzene B3LYP: max |H_server - H_laptop| = {d:.2e} a.u. ->", "PASS" if d <= 1e-6 else "FAIL")
raise SystemExit(0 if d <= 1e-6 else 1)
PYEOF' < /dev/null | tee "$SP/labels_gate_$IP.log" || { echo "GATE FAILED $IP — the lanes do not start"; exit 1; }
echo "[$(t) $IP] four lanes × 8 threads, detached"
for L in 0 1 2 3; do
  $S "cd /root/labels && setsid nohup bash labels_lane.sh $L /root/labels/labels_ids_$L.txt > /root/labels/lane_$L.log 2>&1 < /dev/null &" < /dev/null
done
sleep 20
$S 'ps -eo pid,etime,pcpu,args | grep analytic_hessian[s] | wc -l; tail -n 1 /root/labels/lane_*.log' < /dev/null
echo "[$(t) $IP] BOOTSTRAP DONE: four lanes running; watch with probes/labels_watch.sh"
