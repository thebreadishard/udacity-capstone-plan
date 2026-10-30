#!/usr/bin/env bash
# probes/holdout_a_clean.sh [--check-only] (30 Oct 2026; TASKS 157) — v1.3's three carried seeds read again on the hold-outs with the clean
# hold-out (a) as an extra test set 'a8' (out/holdout_a_clean_2026-10-30.txt: hold-out (a) without the two molecules trained on as layer-B
# twins), with chain 35's read flags (--use-analytic, the frozen hold-out (b)), then probes/holdout_a_clean_read.py. Run from
# modules/05_support_predictor by its run spec (probes/runspecs/holdout_a_clean.json). --check-only compiles the two Python files and checks
# the inputs exist, nothing is read. The v1.3 model files are only read.
set -euo pipefail
IDS=out/holdout_a_clean_2026-10-30.txt
FLAGS=(--use-analytic --threads 4 --holdout-b-file corpus/holdout_b_frozen_2026-10-08.txt --eval-ids-file "a8=$IDS")
mark() { echo "=== (HAC) $* $(date '+%F %T')"; }

if [ "${1:-}" = "--check-only" ]; then
  python -m py_compile ../../probes/rungC_eval_saved.py ../../probes/holdout_a_clean_read.py
  for s in 0 1 2; do test -f "out/E7_rungC_chain35_analytic_model_n750_seed$s.pt"; done
  test -f "$IDS" && test -f corpus/holdout_b_frozen_2026-10-08.txt
  mark "check passed"
  exit 0
fi
for s in 0 1 2; do
  mark "seed $s starting"
  python ../../probes/rungC_eval_saved.py "out/E7_rungC_chain35_analytic_model_n750_seed$s.pt" "out/E7_rungC_chain35_analytic_eval_a8_seed$s" "${FLAGS[@]}"
  mark "seed $s done"
done
python ../../probes/holdout_a_clean_read.py out/E7_rungC_chain35_analytic_eval_a8_seed{0,1,2}.json > out/holdout_a_clean_read_2026-10-30.md
mark "run done"
