#!/usr/bin/env bash
# bootstrap_anchors_cpx62.sh <host name in tools/hosts.tsv> (12 Oct 2026; the user: 'Nee, laten we vol op 4 gaan. Meer ankers.') — a fresh CPX62
# (Ubuntu 24.04, 16 vCPU, 32 GB) becomes an anchor server for CCSD(T)/cc-pVDZ FD Hessians (`probes/e8_cc_hessian_fd.py`) and CC APTs by the field
# route (`probes/cc_apt_field.py`), run molecule by molecule by `probes/anchor_wave.sh`. Steps, each with its marker:
#   1. system (build-essential, rsync) + miniforge + env qc05 (`tools/bootstrap_qc05_env.sh`; pyscf as pinned there, 2.15.1 since 21 Nov 2026);
#   2. the plan's files under /root/dpir in the plan's own layout (git archive of HEAD, the commit stamped in /root/dpir/COMMIT) — a fresh
#      directory, never copied over one with results. The list is checked by `tools/deploy_closure.py` before anything is sent: since
#      12 Oct the probes gained imports (constants, vibrations, library_log, src/dpir/symmetry) that the old hand-kept list lacked;
#   3. the (T) C kernel built on the server against its pyscf (`t_density_kernel/build.sh`);
#   4. GATE 1 (tests/test_acceptance_water.py in script mode): the stamp ~/.dpir_gate1.json the probe requires; no stamp, no anchor.
# Exit 0 when gate 1 passed on both paths (RHF and UHF) or RHF only (exit 2 of the test is reported, not hidden); 1 otherwise.
#   bash probes/bootstrap_anchors_cpx62.sh anc1
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
. "$PLAN/tools/hosts.sh"
IP=$(host_ip "$NAME") || exit 1
KEY=~/.ssh/hetzner_g_measure
S="ssh -i $KEY -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
PY=/root/miniforge3/envs/qc05/bin/python
t() { date '+%T'; }
FILES=(probes/e8_cc_hessian_fd.py probes/qc_common.py probes/e8_hessian_checks.py probes/e8_symmetry.py probes/cc_dipole_capture.py
       probes/cc_apt_field.py probes/cc_apt_field_check.py probes/apt_field_route.py probes/library_log.py
       probes/run_anchors_hel23_parallel.sh probes/anchor_wave.sh probes/anchor_wave_progress.sh
       probes/t_density_kernel/t_density_fast.py probes/t_density_kernel/ccsd_t_rdm_kernel.c probes/t_density_kernel/build.sh
       tests/test_acceptance_water.py src/dpir/__init__.py src/dpir/symmetry.py
       modules/05_support_predictor/corpus/apt.py modules/05_support_predictor/corpus/constants.py
       modules/05_support_predictor/corpus/vibrations.py)

( cd "$PLAN" && python tools/deploy_closure.py "${FILES[@]}" ) || { echo "DEPLOY LIST NOT CLOSED — fix FILES before any server is touched"; exit 1; }
host_ssh "$NAME" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $NAME"; exit 1; }

echo "[$(t) $NAME] 1. system + miniforge + env qc05"
bash "$PLAN/tools/bootstrap_qc05_env.sh" "$NAME" || exit 1

echo "[$(t) $NAME] 2. the plan's files under /root/dpir (git archive of HEAD)"
REPO=$(cd "$PLAN/../.." && pwd)
COMMIT=$(git -C "$REPO" rev-parse HEAD)
REL=plans/05_delta-probed-ir-pipeline
$S 'test ! -e /root/dpir' < /dev/null || { echo "/root/dpir EXISTS on $NAME — not overwritten (a fresh directory only)"; exit 1; }
git -C "$REPO" archive --format=tar --prefix=dpir/ HEAD "${FILES[@]/#/$REL/}" \
  | $S "mkdir -p /root/tmp_dpir && tar xf - -C /root/tmp_dpir && mv /root/tmp_dpir/dpir/$REL /root/dpir && rm -rf /root/tmp_dpir && echo $COMMIT > /root/dpir/COMMIT && find /root/dpir -type f | wc -l" \
  || { echo "FILES FAILED $NAME"; exit 1; }

echo "[$(t) $NAME] 3. the (T) C kernel"
$S "cd /root/dpir/probes/t_density_kernel && bash build.sh $PY 2>&1 | tail -1" < /dev/null || { echo "KERNEL BUILD FAILED $NAME"; exit 1; }

echo "[$(t) $NAME] 4. GATE 1 (water, script mode)"
# a stamp left by an earlier gate would pass the test below whatever this run gives, so it goes first
$S "rm -f /root/.dpir_gate1.json && cd /root/dpir && OMP_NUM_THREADS=8 $PY tests/test_acceptance_water.py > /root/dpir/gate1.log 2>&1; echo \"rc=\$?\"; tail -3 /root/dpir/gate1.log" < /dev/null
$S 'test -s /root/.dpir_gate1.json' < /dev/null || { echo "GATE 1 FAILED $NAME — no anchor runs here"; exit 1; }
echo "[$(t) $NAME] BOOTSTRAP DONE (commit ${COMMIT:0:8})"
