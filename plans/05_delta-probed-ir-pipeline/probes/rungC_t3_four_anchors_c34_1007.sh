#!/usr/bin/env bash
# rungC_t3_four_anchors_c34_1007.sh (7 Oct 2026, 05:3x). The comparison the chain 33 amendment of 3 Oct asks for before any gain is attributed to the
# fifth anchor: the same leave-one-anchor-out transfer with the four DZ anchors (benzene, fluorobenzene, pyridine, naphthalene) on chain 34's three
# models, so that the five-anchor read (T3_five_anchors_c34_*_2026-10-07) and the four-anchor read differ only in the anchor set, not in the model
# (T3b of 2 Oct ran on chain 24). Same recipe: 300 epochs, lr 1e-3, head L2 1, 8 threads, Windows python (torch).
#   nohup bash probes/rungC_t3_four_anchors_c34_1007.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: each seed writes its own marker
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
MODEL=out/E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed
cd "$P/modules/05_support_predictor" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
R=../../probes/results_m1
echo "=== T3 four anchors on chain 34: start $(date '+%F %T')"
for s in 0 1 2; do
  python m05/rungC_cc_transfer.py corpus/molecules ${MODEL}$s.pt out/T3_four_anchors_c34_seed${s}_2026-10-07 --threads 8 --epochs 300 --lr 1e-3 --head-l2 1 \
    --anchor A_8448043181=$R/e8_benzene_ccpvdz_tlambda/hessian_ccsd_t.npz --anchor B_8b12a55d3a=$R/e8_fluorobenzene_ccpvdz_2026-09-30/hessian_ccsd_t.npz \
    --anchor A_6e858b26e5=$R/e8_pyridine_ccpvdz_2026-09-30/hessian_ccsd_t.npz --anchor A_01f3186607=$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz \
    > out/T3_four_anchors_c34_seed${s}_2026-10-07.log 2>&1 \
    && echo "=== T3 four anchors on chain 34: seed $s done $(date '+%F %T')" || echo "=== T3 FOUR ANCHORS seed $s FAILED $(date '+%F %T')"
done
echo "=== T3 four anchors on chain 34: finished $(date '+%F %T')"
