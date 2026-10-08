#!/usr/bin/env bash
# cation_gate_p3_2.sh (8 Oct 2026) — TASKS P3-2, the cation noise gate (noise principle; registered 3 Oct): the first ten cation rows of pool 3 get the
# analytic second route, and their per-family FD-against-analytic floor decides whether the remaining cations may stay FD-only (median per family
# ≤ 1.5 cm⁻¹) or every cation row carries the analytic route. The CPX62 has no pyscf, so the analytic Hessians run on the laptop in WSL (qc05, UKS:
# charge 1, spin 1; the route of benzene⁺, 3 Oct: B3LYP FD against analytic 1.47 cm⁻¹).
# Steps: (1) fetch runner a's directory (tools/fetch_corpus_shards.sh, no merge) and copy the first ten cations in order of completion to
# probes/results_m1/cation_gate_2026-10-08/; (2) analytic Hessians in WSL, one molecule per call, 8 threads; (3) the gate
# (probes/rungC_family_floor_ceiling.py --dirs). Markers "=== (G) …" in the log. Run in Git Bash on a free laptop (not beside a training chain):
#   nohup bash probes/cation_gate_p3_2.sh >> probes/results_m1/cation_gate_2026-10-08.log 2>&1 &
set -uo pipefail
# no-set-e: each step writes its own marker; a failed molecule is named and the gate reads it as incomplete
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
B=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
OUT=$P/probes/results_m1/cation_gate_2026-10-08
SH=$P/modules/05_support_predictor/corpus/shards_pool3/a
t() { date '+%F %T'; }
echo "=== (G) cation gate start $(t)"
bash "$P/tools/fetch_corpus_shards.sh" root@46.62.227.91 shards_pool3 "a=$B/corpus_p3" || { echo "=== (G) FETCH FAILED $(t)"; exit 1; }
mapfile -t IDS < <(grep "\] done P3c_" "$SH/pool3_a.log" | awk '{print $4}' | head -n 10)
[ ${#IDS[@]} -eq 10 ] || { echo "=== (G) only ${#IDS[@]} cations done — the gate waits for ten $(t)"; exit 1; }
mkdir -p "$OUT"
for id in "${IDS[@]}"; do
  [ -d "$OUT/$id" ] || cp -r "$SH/molecules/$id" "$OUT/$id"
done
echo "=== (G) ten cations copied: ${IDS[*]} $(t)"
for id in "${IDS[@]}"; do
  if [ -f "$OUT/$id/hessian_wb97x_analytic.npz" ] && [ -f "$OUT/$id/hessian_b3lyp_analytic.npz" ]; then echo "(G) $id analytic exists"; continue; fi
  wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=8; mkdir -p \$HOME/qc_tmp; cd $PW/modules/05_support_predictor/corpus && \$HOME/qc05/bin/python analytic_hessians.py $PW/probes/results_m1/cation_gate_2026-10-08/$id --threads 8 --charge 1 --spin 1" \
    >> "$OUT/analytic.log" 2>&1 && echo "(G) $id analytic done $(t)" || echo "(G) $id ANALYTIC FAILED $(t)"
done
echo "=== (G) analytic route done; the gate $(t)"
cd "$P/modules/05_support_predictor" || exit 1
PYTHONUTF8=1 python ../../probes/rungC_family_floor_ceiling.py out/cation_gate_p3_2_2026-10-08 --dirs $(for id in "${IDS[@]}"; do echo "$OUT/$id"; done) \
  > out/cation_gate_p3_2_2026-10-08.log 2>&1
rc=$?
echo "=== (G) cation gate finished: $([ $rc = 0 ] && echo 'PASS — FD-only cation rows may follow' || echo "NOT PASSED (exit $rc) — see out/cation_gate_p3_2_2026-10-08.md") $(t)"
