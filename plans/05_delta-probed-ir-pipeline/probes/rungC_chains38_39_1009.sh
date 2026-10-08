#!/usr/bin/env bash
# rungC_chains38_39_1009.sh (8 Oct 2026, 18:3x; registered in the rung C pre-registration, amendment 8 Oct 18:3x, before it runs). Waits for the cation
# gate to release the laptop, then, one training at a time on 8 threads (chain 34's recipe, three seeds each):
#   chain 39 size (≤ 20 atoms, hold-out (s) = pool molecules of ≥ 27 atoms) and its control (370 of any size below 27, same (s));
#   chain 38 ablation (the pool without the five-membered-ring families) and its control (the first 853 of the full pool), models saved, registered
#   as candidates, read on the frozen hold-out (b) per seed and as seed means.
#   nohup bash probes/rungC_chains38_39_1009.sh >> probes/results_m1/chains38_39_2026-10-09.log 2>&1 &
set -uo pipefail
# no-set-e: each step writes its own marker
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
GATE_LOG=$P/probes/results_m1/cation_gate_2026-10-08.log
cd "$P/modules/05_support_predictor" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
echo "=== (C38) armed (pid $$), waiting for the cation gate $(t)"
until grep -qE "^=== \(G\) (cation gate finished|GATE NOT STARTED|FETCH FAILED)" "$GATE_LOG"; do sleep 300; done
echo "=== (C38) laptop free; design check $(t)"
python m05/design_check.py corpus/molecules --aggregation sum --out out/design_check_chains38_39_2026-10-09 > out/design_check_chains38_39_2026-10-09.log 2>&1 \
  || { echo "=== (C38) CHAINS 38/39 NOT STARTED: design check failed $(t)"; exit 1; }
REC="--head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --kdiag-mode family --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f"
BASE="--use-analytic --pool-layers A,A2,B --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum"
train() {   # $1 = record prefix, rest = extra trainer arguments
  local pre=$1; shift
  echo "(C38) $pre start $(t)"
  # shellcheck disable=SC2086   # REC and BASE are argument lists
  python m05/rungC_train.py corpus/molecules "$pre" $BASE $REC "$@" > "$pre.log" 2>&1 && echo "=== (C38) $pre trained $(t)" \
    || { echo "=== (C38) $pre TRAINING FAILED $(t)"; return 1; }
}
ok=1
train out/E7_rungC_chain39_size_le20_2026-10-09 --sizes all --size-test-min-atoms 27 --pool-max-atoms 20 || ok=0
train out/E7_rungC_chain39_control_2026-10-09 --sizes 370 --size-test-min-atoms 27 || ok=0
train out/E7_rungC_chain38_ablation_fivering_2026-10-09 --sizes all --exclude-ids-file corpus/ablation_five_ring_families_2026-10-08.txt --save-model || ok=0
train out/E7_rungC_chain38_control_2026-10-09 --sizes 853 --save-model || ok=0
for c in ablation_fivering control; do
  pre=out/E7_rungC_chain38_${c}_2026-10-09
  ls ${pre}_model_n*_seed0.pt > /dev/null 2>&1 || { ok=0; continue; }
  N=$(ls ${pre}_model_n*_seed0.pt | sed -E 's/.*_model_n([0-9]+)_seed0\.pt/\1/')
  python m05/model_registry.py --add-candidates ${pre}_model_n${N}_seed{0,1,2}.pt --chain 38 \
    --note "9 Oct 2026: chain 38 ($c) — which family covers hold-out (b); registered 8 Oct 18:3x in the rung C pre-registration; candidate until its read" \
    >> out/registry_chain38_2026-10-09.log 2>&1 || { ok=0; continue; }
  for s in 0 1 2; do
    python ../../probes/rungC_eval_saved.py ${pre}_model_n${N}_seed${s}.pt out/E7_rungC_chain38_${c}_eval_frozenb_2026-10-09_seed${s} --use-analytic --threads 8 \
      --allow-any-model --holdout-b-file corpus/holdout_b_frozen_2026-10-08.txt > out/E7_rungC_chain38_${c}_eval_frozenb_2026-10-09_seed${s}.log 2>&1 || ok=0
  done
  python ../../probes/rungC_eval_means.py out/read_chain38_${c}_2026-10-09 out/E7_rungC_chain38_${c}_eval_frozenb_2026-10-09_seed{0,1,2}.json --against $pre.json \
    > out/read_chain38_${c}_2026-10-09.log 2>&1 || ok=0
done
[ $ok = 1 ] && echo "=== (C38) chains 38/39 done — records out/E7_rungC_chain39_*_2026-10-09.md, out/read_chain38_*_2026-10-09.md $(t)" \
  || echo "=== (C38) CHAINS 38/39: A STEP FAILED — see the logs $(t)"
