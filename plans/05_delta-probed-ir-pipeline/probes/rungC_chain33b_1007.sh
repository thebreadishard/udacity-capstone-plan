#!/usr/bin/env bash
# rungC_chain33b_1007.sh (7 Oct 2026, 03:4x). Chain 33 with five anchors, run now: anthracene's anchor is the composite of test 3 (CC/DZ with the
# out-of-plane block corrected by MP2/TZ − MP2/DZ; read 03:27: 86 and 115 cm⁻¹ for the two softest modes, no imaginary mode, within 40 cm⁻¹ of ωB97X →
# "repaired", the composite anchor enters T3 with provisional lines). The original rungC_chain33_1004.sh waited for a VALID hessian_ccsd_t.npz that the
# CC/DZ run cannot give (IMAGINARY, the small-basis arene artefact); this script names the composite file explicitly so the record shows which anchor
# was used. Three seeds of chain 34, 8 threads each in turn, Windows python (torch), beside the LNO cell in WSL (8 threads; 16 cores).
#   nohup bash probes/rungC_chain33b_1007.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: each seed writes its own marker
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
MODEL=out/E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed
ANTHRACENE=$P/modules/05_support_predictor/out/composite_test3_anthracene_2026-10-07.npz
[ -f "$ANTHRACENE" ] || { echo "=== CHAIN 33b STOPPED: no composite anthracene anchor at $ANTHRACENE $(date '+%F %T')"; exit 1; }
cd "$P/modules/05_support_predictor" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
R=../../probes/results_m1
echo "=== chain 33b: T3 reread with five anchors (anthracene = composite of test 3) start $(date '+%F %T')"
for s in 0 1 2; do
  python m05/rungC_cc_transfer.py corpus/molecules ${MODEL}$s.pt out/T3_five_anchors_c34_seed${s}_2026-10-07 --threads 8 --epochs 300 --lr 1e-3 --head-l2 1 \
    --anchor A_8448043181=$R/e8_benzene_ccpvdz_tlambda/hessian_ccsd_t.npz --anchor B_8b12a55d3a=$R/e8_fluorobenzene_ccpvdz_2026-09-30/hessian_ccsd_t.npz \
    --anchor A_6e858b26e5=$R/e8_pyridine_ccpvdz_2026-09-30/hessian_ccsd_t.npz --anchor A_01f3186607=$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz \
    --anchor A_a1e6ec1862=$ANTHRACENE > out/T3_five_anchors_c34_seed${s}_2026-10-07.log 2>&1 \
    && echo "=== chain 33b seed $s done $(date '+%F %T')" || echo "=== CHAIN 33b seed $s FAILED $(date '+%F %T')"
done
echo "=== chain 33b finished $(date '+%F %T')"
