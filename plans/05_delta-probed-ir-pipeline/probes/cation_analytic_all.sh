#!/usr/bin/env bash
# cation_analytic_all.sh (9 Oct 2026, 06:0x) — the consequence of the P3-2 cation gate as registered (3 Oct; read 9 Oct 05:44, NOT PASSED: CH-oop
# 3.05, other 2.27 against ≤ 1.5): every cation row of pool 3 carries the analytic second route. Waits for the T3 intensity read to release the
# laptop, then loops: fetch runner a's directory (no merge), and for every finished cation without analytic files compute them in WSL (qc05, UKS,
# 6 threads — leaving room for a training beside it) inside the shard folder, so the merge brings them with the row; the gate's ten are copied in
# from the gate directory. Ends when runner a's cations are all done and covered, or after 8 days. Markers "=== (CA) …".
#   nohup bash probes/cation_analytic_all.sh >> probes/results_m1/cation_analytic_2026-10-09.log 2>&1 &
set -uo pipefail
# no-set-e: a failed molecule is named and retried on the next pass
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
B=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
SH=$P/modules/05_support_predictor/corpus/shards_pool3/a
SHW=$PW/modules/05_support_predictor/corpus/shards_pool3/a
GATE=$P/probes/results_m1/cation_gate_2026-10-08
WAIT_LOG=$P/probes/results_m1/t3_intensity_2026-10-09.log
t() { date '+%F %T'; }
echo "=== (CA) armed (pid $$), waiting for the T3 intensity read $(t)"
until grep -qF "(I) T3 intensity read finished" "$WAIT_LOG" 2>/dev/null; do sleep 300; done
echo "=== (CA) start $(t)"
for pass in $(seq 1 192); do                                     # hourly passes, at most 8 days
  bash "$P/tools/fetch_corpus_shards.sh" root@46.62.227.91 shards_pool3 "a=$B/corpus_p3" > /dev/null || echo "(CA) fetch failed, next pass $(t)"
  mapfile -t DONE < <(grep "\] done P3c_" "$SH/pool3_a.log" 2>/dev/null | awk '{print $4}')
  todo=0
  for id in "${DONE[@]}"; do
    d=$SH/molecules/$id
    [ -f "$d/hessian_wb97x_analytic.npz" ] && [ -f "$d/hessian_b3lyp_analytic.npz" ] && continue
    if [ -f "$GATE/$id/hessian_wb97x_analytic.npz" ] && [ -f "$GATE/$id/hessian_b3lyp_analytic.npz" ]; then
      cp "$GATE/$id"/hessian_*_analytic.npz "$GATE/$id/analytic_check.json" "$d/" 2>/dev/null && echo "(CA) $id copied from the gate $(t)"; continue
    fi
    todo=$((todo + 1))
    wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=6; mkdir -p \$HOME/qc_tmp; cd $PW/modules/05_support_predictor/corpus && \$HOME/qc05/bin/python analytic_hessians.py $SHW/molecules/$id --threads 6 --charge 1 --spin 1" \
      >> "$P/probes/results_m1/cation_analytic_2026-10-09.analytic.log" 2>&1 && echo "(CA) $id analytic done $(t)" || echo "(CA) $id ANALYTIC FAILED $(t)"
  done
  n_done=${#DONE[@]}
  if [ "$n_done" -ge 60 ] && [ "$todo" = 0 ]; then echo "=== (CA) all 60 cations carry the analytic route $(t)"; exit 0; fi
  [ "$todo" = 0 ] && sleep 3600
done
echo "=== (CA) STOPPED after 8 days: $n_done cations done on the server $(t)"
