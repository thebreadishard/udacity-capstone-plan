#!/usr/bin/env bash
# Lever 3 (2 Oct 2026): CC gradient stage timings on benzene (CCSD(T)/cc-pVDZ, the (T) C kernels, frozen core derived) in the laptop's WSL at 4 and 8
# threads once chain 23's lane is free, and at 16 threads once chain 24 has finished too (a timing under contention says nothing). Each run is the
# probe's reference gradient only (--only-reference, two-route checks deferred: the kernels were accepted by gate 1); the probe logs SCF+CCSD, lambda and
# gradient seconds. Design input for the throughput task, not a decision run.
set -u
# no-set-e: each timing records its own line
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
S=/mnt/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
G=$P/modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json
PY=$HOME/qc05/bin/python
cd "$P/probes" || exit 1
echo "=== cc timing start $(date)"
"$PY" -c "import e8_cc_hessian_fd as E; p = E.gate1_problem(True, False, True); print('gate 1:', p or 'stamp valid'); raise SystemExit(1 if p else 0)" \
  || { echo "gate 1 stamp missing or stale on this host — running the water acceptance test first"; (cd "$P" && "$PY" -m pytest tests/test_acceptance_water.py -q 2>&1 | tail -2); }
run_one() {  # threads
  local T=$1 out=$S/cc_timing_benzene_t$1
  rm -rf "$out"; mkdir -p "$out"
  echo "--- threads $T start $(date)"
  OMP_NUM_THREADS=$T "$PY" e8_cc_hessian_fd.py "$G" "$out" --threads "$T" --only-reference --two-route-check separate --fast-t-density --fast-t-lambda --max-memory 8000 > "$out/run.log" 2>&1 \
    && grep -E "SCF|CCSD|lambda|gradient|reference:" "$out/e8_fd.log" | cut -c1-160 || { echo "=== TIMING threads $T FAILED $(date)"; tail -5 "$out/run.log"; }
}
until grep -q "=== chain 23 finished" "$P/modules/05_support_predictor/out/E7_rungC_sherlock23_2026-10-01.log" 2>/dev/null; do sleep 300; done
run_one 4
run_one 8
until grep -q "=== chain 24 finished" "$P/modules/05_support_predictor/out/E7_rungC_sherlock24_2026-10-02.log" 2>/dev/null; do sleep 300; done
run_one 16
echo "=== cc timing finished $(date)"
