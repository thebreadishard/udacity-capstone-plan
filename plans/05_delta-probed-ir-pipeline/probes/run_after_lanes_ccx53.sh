#!/bin/bash
# CCX53, 24 Sep 2026: when the second-route lanes finish, read the twenty imaginary-mode molecules and build the corrected release
# (layerA2_2026-09-24, --prefer-analytic: healed molecules enter, genuine ones stay out). Seconds to minutes; runs beside the E8 chain.
cd /root/m05run/05_support_predictor || exit 1
PY=/root/miniforge3/envs/qc05/bin/python
LOG=out/after_lanes_2026-09-24.log
echo "[$(date "+%F %T")] waiting for ALL LANES DONE" >> $LOG
until grep -q "ALL LANES DONE" out/analytic_hessians_imaginary_2026-09-23_all.log 2>/dev/null; do sleep 120; done
echo "[$(date "+%F %T")] lanes done -> read-out" >> $LOG
$PY corpus/read_imaginary_second_route.py --out data/second_route/imaginary_second_route_2026-09-24 >> $LOG 2>&1
echo "[$(date "+%F %T")] read-out exit $? -> release" >> $LOG
/root/miniforge3/envs/m05/bin/python m05/build_release.py corpus/molecules data/corpus_release/layerA2_2026-09-24 --prefer-analytic >> $LOG 2>&1
echo "[$(date "+%F %T")] release exit $?; AFTER-LANES DONE" >> $LOG
