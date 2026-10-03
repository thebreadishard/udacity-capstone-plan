#!/usr/bin/env bash
# P3-5 (decision 54, 3 Oct 2026): benzene⁺ CCSD(T)/cc-pVDZ FD Hessian on the CCX53 after anthracene — the cation fold for T3 (lever 1).
# Sequence: wait until chain 33 has fetched anthracene (its log prints the T3-reread start line after the scp; a STOPPED line stops this chain too) →
# refuse while any E8 process still runs there → upload the cation row's own UKS-B3LYP geometry (probes/results_m1/cations/benzene) → step 1, the
# reference gradient alone (--only-reference, detached through remote_launch; this is the dry run: UHF path, memory, timing per gradient) → step 2, the
# full run in the same output directory (the probe reuses reference.npz), one lane × 32 threads, --symmetry, no fast kernels (RHF only) → poll the
# .exit file, fetch, and write a HEL2C line into the CCX53 alarm log the session's waiter watches. Gate 1 on the CCX53 covers the UHF path
# (stamp 2 Oct 04:20, paths rhf + uhf, checked 3 Oct 12:16). The user deletes the server after the fetch.
set -uo pipefail
# no-set-e: every step records its own line and the chain stops on a named failure
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
S=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
IP=157.180.32.149
KEY=$HOME/.ssh/hetzner_g_measure
SSH="ssh -i $KEY -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
RL=$P/tools/remote_launch.sh
C33=$P/modules/05_support_predictor/out/E7_rungC_sherlock33_2026-10-03.log
ALARM=$S/ccx53_alarms.log
OUT=$P/probes/results_m1/e8_benzene_cation_ccpvdz_2026-10-05
CMD="/root/miniforge3/envs/qc05/bin/python e8_cc_hessian_fd.py molecules/C_benzene/geometry.json results/benzene_cation_ccpvdz --threads 32 --charge 1 --spin 1 --max-memory 100000 --symmetry --two-route-check inline"
t() { date '+%F %T'; }
say() { echo "[$(t)] $*"; }

until grep -qE "chain 33: T3 reread with five anchors start|CHAIN 33 STOPPED" "$C33" 2>/dev/null; do sleep 900; done
if grep -q "CHAIN 33 STOPPED" "$C33"; then say "benzene+ chain not started: chain 33 stopped (anthracene not VALID) — the user decides about the server"; echo "[$(t)] HEL2C NOT STARTED (chain 33 stopped)" >> "$ALARM"; exit 1; fi
say "anthracene fetched by chain 33; checking the CCX53"
n_e8=$($SSH 'ps -eo args | grep -c "[e]8_cc_hessian_fd.py"' < /dev/null 2>/dev/null)
if [ "${n_e8:-1}" != "0" ]; then say "E8 still running on the CCX53 ($n_e8 processes) — not starting"; echo "[$(t)] HEL2C NOT STARTED (E8 busy)" >> "$ALARM"; exit 1; fi
$SSH 'mkdir -p /root/e8/molecules/C_benzene /root/e8/results/benzene_cation_ccpvdz' < /dev/null
scp -q -i $KEY -o BatchMode=yes "$P/probes/results_m1/cations/benzene/geometry.json" root@$IP:/root/e8/molecules/C_benzene/geometry.json || { say "geometry upload FAILED"; echo "[$(t)] HEL2C FAILED (upload)" >> "$ALARM"; exit 1; }

say "step 1: reference gradient only (the dry run of the UHF path on this box)"
bash "$RL" root@$IP /root/e8 e8_benzene_cation_ref --threads 32 -- "$CMD --only-reference" 2>&1 | tail -3
until $SSH 'test -f /root/e8/e8_benzene_cation_ref.exit' < /dev/null 2>/dev/null; do sleep 600; done
rc=$($SSH 'cat /root/e8/e8_benzene_cation_ref.exit' < /dev/null 2>/dev/null)
$SSH 'tail -4 /root/e8/e8_benzene_cation_ref.log' < /dev/null 2>/dev/null | cut -c1-200
if [ "$rc" != "0" ]; then say "reference step FAILED (exit $rc) — chain stops"; echo "[$(t)] HEL2C FAILED (reference, exit $rc)" >> "$ALARM"; exit 1; fi
ref_s=$($SSH 'grep -oE "gradient [0-9]+ s" /root/e8/e8_benzene_cation_ref.log | tail -1' < /dev/null 2>/dev/null)
say "reference done ($ref_s per gradient); step 2: the full symmetric FD run"
bash "$RL" root@$IP /root/e8 e8_benzene_cation --threads 32 -- "$CMD" 2>&1 | tail -3
echo "[$(t)] HEL2C STARTED (benzene+ full run; reference $ref_s)" >> "$ALARM"
until $SSH 'test -f /root/e8/e8_benzene_cation.exit' < /dev/null 2>/dev/null; do sleep 1800; done
rc=$($SSH 'cat /root/e8/e8_benzene_cation.exit' < /dev/null 2>/dev/null)
mkdir -p "$OUT"
scp -q -i $KEY -o BatchMode=yes "root@$IP:/root/e8/results/benzene_cation_ccpvdz/{hessian_ccsd_t*.npz,reference.npz,e8_fd.log,two_route_check.json,two_route_check.log,E8_*.md}" "$OUT/" 2>&1 | tail -1
scp -q -i $KEY -o BatchMode=yes root@$IP:/root/e8/e8_benzene_cation.log "$OUT/launch.log" 2>&1 | tail -1
ls "$OUT" | tr '\n' ' '; echo
if [ "$rc" = "0" ] && [ -f "$OUT/hessian_ccsd_t.npz" ]; then
  echo "[$(t)] HEL2C DONE (benzene+ Hessian fetched to $OUT; the server may be deleted after a look)" >> "$ALARM"; say "benzene+ DONE"
else
  echo "[$(t)] HEL2C FAILED (exit $rc; see $OUT)" >> "$ALARM"; say "benzene+ FAILED (exit $rc)"; exit 1
fi
