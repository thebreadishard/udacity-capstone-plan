#!/usr/bin/env bash
# bootstrap_anchors_cpx62.sh <host name in tools/hosts.tsv> (12 Oct 2026; the user: 'Nee, laten we vol op 4 gaan. Meer ankers.') — a fresh CPX62
# (Ubuntu 24.04, 16 vCPU, 32 GB) becomes an anchor server for CCSD(T)/cc-pVDZ FD Hessians (`probes/e8_cc_hessian_fd.py`) and CC APTs by the field
# route (`probes/cc_apt_field.py`). The CCX53 of 1–6 Oct was set up by hand; this is that recipe as one script. Steps, each with its marker:
#   1. system (build-essential, rsync) + miniforge + env qc05 (python 3.12, pip pyscf 2.14.0, numpy, scipy, psutil, pytest), the labels recipe;
#   2. the plan's files the probes import, in the plan's own layout under /root/dpir (git archive of HEAD: the E8 probe and its checks, the
#      symmetry code, the (T) C kernel sources, the dipole capture, the field route, the parallel anchor runner, gate 1's test with its psi4
#      values, corpus/apt.py) — a fresh directory, never copied over one with results;
#   3. the (T) C kernel built on the server against its pyscf (`t_density_kernel/build.sh`);
#   4. GATE 1 (tests/test_acceptance_water.py in script mode): the stamp ~/.dpir_gate1.json the probe requires; no stamp, no anchor.
# Exit 0 when gate 1 passed on both paths (RHF and UHF) or RHF only (exit 2 of the test is reported, not hidden); 1 otherwise.
#   bash probes/bootstrap_anchors_cpx62.sh anchors3
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
IP=$(host_ip "$NAME") || exit 1
KEY=~/.ssh/hetzner_g_measure
S="ssh -i $KEY -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
t() { date '+%T'; }
host_ssh "$NAME" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $NAME"; exit 1; }

echo "[$(t) $NAME] 1. system + miniforge + env qc05"
$S 'export DEBIAN_FRONTEND=noninteractive; apt-get update -q > /tmp/apt.log 2>&1; apt-get install -yq build-essential rsync htop >> /tmp/apt.log 2>&1;
    test -x /root/miniforge3/bin/conda || { curl -sL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -o /tmp/mf.sh && bash /tmp/mf.sh -b -p /root/miniforge3 > /tmp/mf.log 2>&1; };
    test -x /root/miniforge3/envs/qc05/bin/python || /root/miniforge3/bin/conda create -y -q -n qc05 python=3.12 > /tmp/env.log 2>&1;
    /root/miniforge3/envs/qc05/bin/pip install -q pyscf==2.14.0 numpy scipy psutil pytest >> /tmp/env.log 2>&1;
    /root/miniforge3/envs/qc05/bin/python -c "import pyscf; print(\"pyscf\", pyscf.__version__)"' < /dev/null || { echo "ENV FAILED $NAME"; exit 1; }

echo "[$(t) $NAME] 2. the plan's files under /root/dpir (git archive of HEAD)"
P=plans/05_delta-probed-ir-pipeline
FILES=(probes/e8_cc_hessian_fd.py probes/e8_hessian_checks.py probes/e8_symmetry.py probes/cc_dipole_capture.py probes/cc_apt_field.py
       probes/apt_field_route.py probes/run_anchors_hel23_parallel.sh probes/t_density_kernel/t_density_fast.py
       probes/t_density_kernel/ccsd_t_rdm_kernel.c probes/t_density_kernel/build.sh tests/test_acceptance_water.py
       modules/05_support_predictor/corpus/apt.py)
$S 'test ! -e /root/dpir' < /dev/null || { echo "/root/dpir EXISTS on $NAME — not overwritten (a fresh directory only)"; exit 1; }
( cd "$HERE/../../.." && git archive --format=tar --prefix=dpir/ HEAD "${FILES[@]/#/$P/}" ) | $S 'mkdir -p /root/tmp_dpir && tar xf - -C /root/tmp_dpir && mv /root/tmp_dpir/dpir/plans/05_delta-probed-ir-pipeline /root/dpir && rm -rf /root/tmp_dpir && find /root/dpir -type f | wc -l' \
  || { echo "FILES FAILED $NAME"; exit 1; }

echo "[$(t) $NAME] 3. the (T) C kernel"
$S 'cd /root/dpir/probes/t_density_kernel && bash build.sh /root/miniforge3/envs/qc05/bin/python 2>&1 | tail -1' < /dev/null || { echo "KERNEL BUILD FAILED $NAME"; exit 1; }

echo "[$(t) $NAME] 4. GATE 1 (water, script mode)"
$S 'cd /root/dpir && OMP_NUM_THREADS=8 /root/miniforge3/envs/qc05/bin/python tests/test_acceptance_water.py > /root/dpir/gate1.log 2>&1; echo "rc=$?"; tail -3 /root/dpir/gate1.log' < /dev/null
$S 'test -s /root/.dpir_gate1.json' < /dev/null || { echo "GATE 1 FAILED $NAME — no anchor runs here"; exit 1; }
echo "[$(t) $NAME] BOOTSTRAP DONE"
