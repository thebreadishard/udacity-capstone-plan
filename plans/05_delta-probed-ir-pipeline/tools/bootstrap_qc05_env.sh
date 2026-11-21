#!/usr/bin/env bash
# tools/bootstrap_qc05_env.sh <host name in tools/hosts.tsv> <pyscf version> (13 Oct 2026) — system packages, miniforge and the env qc05
# (python 3.12, pip pyscf, numpy, scipy, psutil, pytest) on a fresh Ubuntu server: one implementation for every server kind. Taken out of
# step 1 of probes/bootstrap_anchors_cpx62.sh when the S1 server needed the same env (probes/bootstrap_s1_cpx62.sh).
# The pyscf version is required, with no default (21 Nov 2026): each caller names its own, so moving one server kind to a new release —
# the anchor servers to 2.15.1 — never changes another's labels recipe (2.14.0) unseen. pip installs exactly that version, also over
# another one in an existing env, and the step fails unless the env then reports it. Idempotent otherwise: an existing miniforge or env is
# kept. Prints the env's pyscf version; exit 1 when the env is not usable.
#   bash tools/bootstrap_qc05_env.sh s1 2.14.0
set -euo pipefail
NAME=${1:?host name}
PYSCF_VERSION=${2:?pyscf version, e.g. 2.15.1}
[[ $PYSCF_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "pyscf version '$PYSCF_VERSION' is not a release number"; exit 1; }
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/hosts.sh"
IP=$(host_ip "$NAME")
host_ssh "$NAME" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $NAME"; exit 1; }
ssh -i ~/.ssh/hetzner_g_measure -o ConnectTimeout=25 -o BatchMode=yes "root@$IP" "export DEBIAN_FRONTEND=noninteractive; apt-get update -q > /tmp/apt.log 2>&1; apt-get install -yq build-essential rsync htop >> /tmp/apt.log 2>&1;
    test -x /root/miniforge3/bin/conda || { curl -sL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -o /tmp/mf.sh && bash /tmp/mf.sh -b -p /root/miniforge3 > /tmp/mf.log 2>&1; };
    test -x /root/miniforge3/envs/qc05/bin/python || /root/miniforge3/bin/conda create -y -q -n qc05 python=3.12 > /tmp/env.log 2>&1;
    /root/miniforge3/envs/qc05/bin/pip install -q pyscf==$PYSCF_VERSION numpy scipy psutil pytest >> /tmp/env.log 2>&1;
    test \"\$(/root/miniforge3/envs/qc05/bin/pip show pyscf | sed -n 's/^Version: //p')\" = $PYSCF_VERSION && echo pyscf $PYSCF_VERSION" < /dev/null \
  || { echo "ENV FAILED $NAME (pyscf $PYSCF_VERSION)"; exit 1; }
