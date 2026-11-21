#!/usr/bin/env bash
# tools/bootstrap_psi4_env.sh <host in tools/hosts.tsv> (13 Oct 2026 as probes/bootstrap_psi4_ccx53.sh for the labels server; general since
# 21 Nov 2026) — the corpus's psi4 environment 'qc' on a server that has miniforge (tools/bootstrap_qc05_env.sh puts it there), for the
# deck's B3LYP/6-31G* optimisations (corpus/psi4_worker.py). Steps, each checked:
#   1. env 'qc' created from tools/env_specs/qc_psi4_linux64.txt, the exact builds of the corpus's servers (psi4 1.11, optking 0.5.0,
#      qcelemental 0.51.2, numpy 2.5.3, python 3.14.7; exported from the labels server on 15 Nov 2026), at nice 19 so a run beside it keeps
#      its cores;
#   2. psi4 and optking import, at those versions;
#   3. our optking linear-bend fix applied and checked (probes/optking_patches; it was missing on two installs once, 9 Oct 2026).
# The water smoke through psi4_worker belongs to the deploy that uses the env (probes/deploy_lib.sh's runner smokes with 'opt').
# Refuses when /root/miniforge3/envs/qc exists already.
#   bash tools/bootstrap_psi4_env.sh anc1
set -euo pipefail
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
SPEC=$HERE/env_specs/qc_psi4_linux64.txt
FIX=$PLAN/probes/optking_patches/apply_optking_fix.py
. "$HERE/hosts.sh"
IP=$(host_ip "$NAME")
SCP="scp -q -o BatchMode=yes -o ConnectTimeout=20 -i $HOME/.ssh/hetzner_g_measure"
grep -q '/psi4-1.11-' "$SPEC" || { echo "the spec has no psi4 1.11 build"; exit 1; }
host_ssh "$NAME" 'test -x /root/miniforge3/bin/conda && test ! -e /root/miniforge3/envs/qc' \
  || { echo "$NAME: no miniforge, or env qc exists already — refusing"; exit 1; }
host_ssh "$NAME" 'mkdir -p /root/psi4_env'
$SCP "$SPEC" "$FIX" "root@$IP:/root/psi4_env/"
echo "(1) env qc from $(basename "$SPEC") ($(grep -c '^https' "$SPEC") packages, nice 19)"
host_ssh "$NAME" "nice -n 19 /root/miniforge3/bin/conda create -y -q -n qc --file /root/psi4_env/$(basename "$SPEC") > /root/psi4_env/create.log 2>&1; echo rc=\$?" \
  | grep -qx 'rc=0' || { echo "conda create failed (see /root/psi4_env/create.log on $NAME)"; exit 1; }
echo "(2) versions"
versions=$(host_ssh "$NAME" '/root/miniforge3/envs/qc/bin/python -c "import psi4, optking; print(psi4.__version__, optking.__version__)"')
[ "$versions" = "1.11 0.5.0" ] || { echo "unexpected versions: '$versions'"; exit 1; }
echo "    psi4 1.11, optking 0.5.0"
echo "(3) optking fix"
host_ssh "$NAME" 'P=/root/miniforge3/envs/qc/bin/python; $P /root/psi4_env/apply_optking_fix.py > /dev/null && $P /root/psi4_env/apply_optking_fix.py --check | grep -c "already patched" | grep -qx 2' \
  || { echo "OPTKING FIX NOT APPLIED"; exit 1; }
echo "[$NAME] PSI4 ENV DONE"
