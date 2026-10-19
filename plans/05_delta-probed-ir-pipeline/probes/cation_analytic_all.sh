#!/usr/bin/env bash
# cation_analytic_all.sh (9 Oct 2026; rewritten 19 Oct 2026) — the consequence of the P3-2 cation gate as registered (3 Oct; read 9 Oct 05:44,
# NOT PASSED: CH-oop 3.05, other 2.27 against ≤ 1.5): every cation row of pool 3 carries the analytic second route. For each of runner a's
# finished cations without both analytic Hessians: copied from the gate directory when the gate computed them, otherwise computed in WSL (qc05,
# UKS, 6 threads) inside the shard folder, so the corpus merge brings them with the row. Markers "=== (CA) …", one line per molecule.
# 19 Oct 2026 (the out-of-memory of 00:46, after which this loop spun 192 passes in an hour on failing WSL calls, fetching every 18 s):
#   - one pass over the local shard (the pool 3 box is fetched and deleted); no waiting loop;
#   - each molecule runs under probes/wsl_capped.sh (CAP_MB, a hard memory bound the run spec cites) and /usr/bin/time, whose max RSS is
#     logged per molecule, so the next cap is a measurement;
#   - three failures in a row stop the run with one line, instead of a retry loop.
# Launched through tools/runspec.py (probes/runspecs/cation_analytic.json). --dry-run lists the work and exits.
#   bash probes/cation_analytic_all.sh [--dry-run]
set -uo pipefail
# no-set-e: a failed molecule is named; three in a row stop the run
P=$(cd "$(dirname "$0")/.." && pwd)
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
SH=$P/modules/05_support_predictor/corpus/shards_pool3/a
SHW=$PW/modules/05_support_predictor/corpus/shards_pool3/a
GATE=$P/probes/results_m1/cation_gate_2026-10-08
ALOG=$P/probes/results_m1/cation_analytic_2026-10-09.analytic.log
CAP_MB=${CAP_MB:-3584}
THREADS=${THREADS:-6}
PYSCF_MB=${PYSCF_MB:-3000}            # pyscf's max_memory, below the cap (its default 20000 would plan blocks past it)
MAX_FAILS_IN_A_ROW=3
t() { date '+%F %T'; }
mapfile -t DONE < <(grep "\] done P3c_" "$SH/pool3_a.log" 2>/dev/null | awk '{print $4}')
[ "${#DONE[@]}" -gt 0 ] || { echo "=== (CA) STOPPED: no finished cation in $SH/pool3_a.log $(t)"; exit 1; }
TODO=()
for id in "${DONE[@]}"; do
  d=$SH/molecules/$id
  [ -f "$d/hessian_wb97x_analytic.npz" ] && [ -f "$d/hessian_b3lyp_analytic.npz" ] && continue
  if [ -f "$GATE/$id/hessian_wb97x_analytic.npz" ] && [ -f "$GATE/$id/hessian_b3lyp_analytic.npz" ]; then
    cp "$GATE/$id"/hessian_*_analytic.npz "$GATE/$id/analytic_check.json" "$d/" && echo "(CA) $id copied from the gate $(t)"
    continue
  fi
  TODO+=("$id")
done
if [ "${1:-}" = "--dry-run" ]; then
  echo "dry run: ${#DONE[@]} finished cations, ${#TODO[@]} to compute, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads; first: ${TODO[0]:-none}"
  exit 0
fi
echo "=== (CA) start: ${#TODO[@]} of ${#DONE[@]} cations to compute, cap $CAP_MB MB, $THREADS threads $(t)"
fails=0; ok=0; failed=0
for id in "${TODO[@]}"; do
  echo "(CA) $id start $(t)"
  if MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
       mkdir -p \$HOME/qc_tmp; cd $PW/modules/05_support_predictor/corpus && \
       bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(CA) $id max RSS %M kB, wall %e s' \
       \$HOME/qc05/bin/python analytic_hessians.py $SHW/molecules/$id --threads $THREADS --charge 1 --spin 1 --max-memory $PYSCF_MB" >> "$ALOG" 2>&1; then
    echo "(CA) $id analytic done $(t) - $(grep -a "(CA) $id max RSS" "$ALOG" | tail -n 1)"
    fails=0; ok=$((ok + 1))
  else
    echo "(CA) $id ANALYTIC FAILED $(t) - $(grep -aE "(CA) $id max RSS|KILLED" "$ALOG" | tail -n 1)"
    fails=$((fails + 1)); failed=$((failed + 1))
    if [ "$fails" -ge "$MAX_FAILS_IN_A_ROW" ]; then
      echo "=== (CA) STOPPED: $MAX_FAILS_IN_A_ROW failures in a row ($ok done, $failed failed); see $ALOG $(t)"
      exit 1
    fi
  fi
done
echo "=== (CA) run done: $ok computed, $failed failed of ${#TODO[@]} $(t)"
[ "$failed" = 0 ]
