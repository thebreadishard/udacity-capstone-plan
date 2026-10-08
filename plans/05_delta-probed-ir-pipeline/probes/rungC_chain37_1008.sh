#!/usr/bin/env bash
# rungC_chain37_1008.sh (8 Oct 2026, 03:0x; registered in the rung C pre-registration, amendment 8 Oct 03:0x, before it runs). Chain 37 = the coverage
# test of 2 Oct (Investigation_2026-10-01_RungC_Sherlock_Day.md, "The test this is") with the recipe now carried: chain 34's (probes/night2_1003.sh)
# on the pool with the 200 merged (8 Oct 02:41: 199 done, 1 failed), --sizes all, seeds 0–2, 8 threads. Waits for the laptop's LNO cells
# ("(N3) LNO extra coordinate finished") so it does not slow them. Then the read: rungC_eval_saved per seed with hold-out (b) frozen at its pre-merge
# list (corpus/holdout_b_frozen_2026-10-08.txt; the 31 new fluoranthene children are read as (b+)), the same read of chain 34's three models as the
# control on the merged corpus, rungC_eval_means against chain 34, and the error map on both trainer records.
#   nohup bash probes/rungC_chain37_1008.sh >> probes/results_m1/chain37_2026-10-08.log 2>&1 &
set -uo pipefail
# no-set-e: each step writes its own marker
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
LNO_LOG=$P/probes/results_m1/lno_extra_k2_2026-10-07.log
cd "$P/modules/05_support_predictor" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
echo "=== (C37) armed (pid $$), waiting for the LNO cells $(t)"
until grep -qF "(N3) LNO extra coordinate finished" "$LNO_LOG"; do sleep 120; done
echo "=== (C37) LNO finished; design check $(t)"
python m05/design_check.py corpus/molecules --aggregation sum --out out/design_check_chain37_2026-10-08 > out/design_check_chain37_2026-10-08.log 2>&1 \
  || { echo "=== (C37) CHAIN 37 NOT STARTED: design check failed $(t)"; exit 1; }
PRE=out/E7_rungC_chain37_coverage_2026-10-08
C34=out/E7_rungC_chain34_kdfamily_750_2026-10-05
FROZEN=corpus/holdout_b_frozen_2026-10-08.txt
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --kdiag-mode family --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --save-model"
echo "=== (C37) chain 37 (chain 34's recipe + the 200) training start, 8 threads $(t)"
# shellcheck disable=SC2086   # REC is a list of trainer arguments
python m05/rungC_train.py corpus/molecules $PRE --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum \
  $REC > $PRE.log 2>&1 && echo "=== (C37) chain 37 trained $(t)" || { echo "=== (C37) CHAIN 37 TRAINING FAILED — see $PRE.log $(t)"; exit 1; }
N=$(ls ${PRE}_model_n*_seed0.pt | sed -E 's/.*_model_n([0-9]+)_seed0\.pt/\1/')
python m05/model_registry.py --add-candidates ${PRE}_model_n${N}_seed{0,1,2}.pt --chain 37 \
  --note "8 Oct 2026: chain 37 = chain 34's recipe on the pool with the 200 merged (the coverage test of 2 Oct, amendment 8 Oct 03:0x in the rung C pre-registration); candidate until its read" \
  > out/registry_chain37_2026-10-08.log 2>&1 || { echo "=== (C37) CHAIN 37 READ NOT STARTED: registry step failed — see out/registry_chain37_2026-10-08.log $(t)"; exit 1; }
ok=1
for s in 0 1 2; do
  python ../../probes/rungC_eval_saved.py ${PRE}_model_n${N}_seed${s}.pt out/E7_rungC_chain37_eval_frozenb_2026-10-08_seed${s} --use-analytic --threads 8 \
    --allow-any-model --holdout-b-file $FROZEN > out/E7_rungC_chain37_eval_frozenb_2026-10-08_seed${s}.log 2>&1 || ok=0
  [ -f out/E7_rungC_chain34_eval_frozenb_2026-10-08_seed${s}.json ] || python ../../probes/rungC_eval_saved.py ${C34}_model_n750_seed${s}.pt \
    out/E7_rungC_chain34_eval_frozenb_2026-10-08_seed${s} --use-analytic --threads 8 --holdout-b-file $FROZEN \
    > out/E7_rungC_chain34_eval_frozenb_2026-10-08_seed${s}.log 2>&1 || ok=0
done
python ../../probes/rungC_eval_means.py out/read_chain37_coverage_2026-10-08 out/E7_rungC_chain37_eval_frozenb_2026-10-08_seed{0,1,2}.json --against $C34.json \
  > out/read_chain37_coverage_2026-10-08.log 2>&1 || ok=0
python ../../probes/rungC_eval_means.py out/read_chain34_frozenb_2026-10-08 out/E7_rungC_chain34_eval_frozenb_2026-10-08_seed{0,1,2}.json --against $C34.json \
  > out/read_chain34_frozenb_2026-10-08.log 2>&1 || ok=0
for c in 34 37; do
  rec=$([ $c = 34 ] && echo $C34.json || echo $PRE.json)
  mkdir -p out/error_map_chain${c}_2026-10-08
  python ../../probes/rungC_error_map.py --records "$rec" --out out/error_map_chain${c}_2026-10-08 > out/error_map_chain${c}_2026-10-08/run.log 2>&1 || ok=0
done
[ $ok = 1 ] && echo "=== (C37) chain 37 read done — out/read_chain37_coverage_2026-10-08.md, out/read_chain34_frozenb_2026-10-08.md, out/error_map_chain{34,37}_2026-10-08 $(t)" \
  || echo "=== (C37) CHAIN 37 READ FAILED (one of the steps) $(t)"
