#!/usr/bin/env bash
# Chain 33 (prepared 3 Oct 2026, 10:2x; odds lever 1): when the anthracene watchdog prints HEL2 DONE, fetch the CCX53's result directory, refuse anything
# but a VALID Hessian, and run the T3 leave-one-anchor-out reread with five anchors (benzene, fluorobenzene, pyridine, naphthalene, anthracene) on chain 24's
# three models, with the alpha-tuned and the lambda = 1 head columns (--head-l2 1). Anthracene's low level is its analytic B3LYP Hessian (queued 3 Oct 09:18).
set -uo pipefail
# no-set-e: every step records its own line
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
S=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
OUT=$P/probes/results_m1/e8_anthracene_ccpvdz_2026-10-05
until grep -q "HEL2 DONE" "$S/ccx53_alarms.log" 2>/dev/null; do sleep 900; done
echo "=== chain 33: anthracene DONE seen $(date)"
mkdir -p "$OUT"
scp -q -i ~/.ssh/hetzner_g_measure -o ConnectTimeout=30 "root@157.180.32.149:/root/e8/results/anthracene_ccpvdz/{hessian_ccsd_t*.npz,reference.npz,e8_fd.log,chain.log,two_route_check.json,two_route_check.log,E8_*.md}" "$OUT/" 2>&1 | tail -2
scp -q -i ~/.ssh/hetzner_g_measure -o ConnectTimeout=30 root@157.180.32.149:/root/e8/anchors.log "$OUT/anchors.log" 2>&1 | tail -1
ls "$OUT" | tr '\n' ' '; echo
if [ ! -f "$OUT/hessian_ccsd_t.npz" ]; then echo "=== CHAIN 33 STOPPED: no VALID hessian_ccsd_t.npz in $OUT $(date)"; exit 1; fi
[ -f "$P/modules/05_support_predictor/corpus/molecules/A_a1e6ec1862/hessian_b3lyp_analytic.npz" ] || echo "WARNING: anthracene has no analytic B3LYP Hessian; the FD corpus file is the low level"
cd $P/modules/05_support_predictor || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
R=../../probes/results_m1
echo "=== chain 33: T3 reread with five anchors start $(date)"
for s in 0 1 2; do
  python m05/rungC_cc_transfer.py corpus/molecules out/E7_rungC_carried_kd_750_saved_2026-10-02_model_n750_seed$s.pt out/T3_five_anchors_seed${s}_2026-10-05 --threads 8 --epochs 300 --lr 1e-3 --head-l2 1 \
    --anchor A_8448043181=$R/e8_benzene_ccpvdz_tlambda/hessian_ccsd_t.npz --anchor B_8b12a55d3a=$R/e8_fluorobenzene_ccpvdz_2026-09-30/hessian_ccsd_t.npz \
    --anchor A_6e858b26e5=$R/e8_pyridine_ccpvdz_2026-09-30/hessian_ccsd_t.npz --anchor A_01f3186607=$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz \
    --anchor A_a1e6ec1862=$R/e8_anthracene_ccpvdz_2026-10-05/hessian_ccsd_t.npz \
    && echo "=== chain 33 seed $s done $(date)" || echo "=== CHAIN 33 seed $s FAILED $(date)"
done
echo "=== chain 33 finished $(date)"
