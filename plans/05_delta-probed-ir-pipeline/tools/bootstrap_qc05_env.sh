#!/usr/bin/env bash
# tools/bootstrap_qc05_env.sh <host name in tools/hosts.tsv> (13 Oct 2026) — system packages, miniforge and the env qc05 (python 3.12, pip
# pyscf 2.14.0, numpy, scipy, psutil, pytest) on a fresh Ubuntu server: the labels recipe, one implementation for every server kind. Taken out
# of step 1 of probes/bootstrap_anchors_cpx62.sh (which now calls it) when the S1 server needed the same env (probes/bootstrap_s1_cpx62.sh).
# Idempotent: an existing miniforge or env is kept. Prints the env's pyscf version; exit 1 when the env is not usable.
#   bash tools/bootstrap_qc05_env.sh s1
set -euo pipefail
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/hosts.sh"
IP=$(host_ip "$NAME")
host_ssh "$NAME" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $NAME"; exit 1; }
ssh -i ~/.ssh/hetzner_g_measure -o ConnectTimeout=25 -o BatchMode=yes "root@$IP" 'export DEBIAN_FRONTEND=noninteractive; apt-get update -q > /tmp/apt.log 2>&1; apt-get install -yq build-essential rsync htop >> /tmp/apt.log 2>&1;
    test -x /root/miniforge3/bin/conda || { curl -sL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -o /tmp/mf.sh && bash /tmp/mf.sh -b -p /root/miniforge3 > /tmp/mf.log 2>&1; };
    test -x /root/miniforge3/envs/qc05/bin/python || /root/miniforge3/bin/conda create -y -q -n qc05 python=3.12 > /tmp/env.log 2>&1;
    /root/miniforge3/envs/qc05/bin/pip install -q pyscf==2.14.0 numpy scipy psutil pytest >> /tmp/env.log 2>&1;
    /root/miniforge3/envs/qc05/bin/python -c "import pyscf; print(\"pyscf\", pyscf.__version__)"' < /dev/null || { echo "ENV FAILED $NAME"; exit 1; }
