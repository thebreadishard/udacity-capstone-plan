#!/bin/bash
# fivering_laptop_1015.sh — TASKS 38, option 3 (the user, 9 Oct 2026: "Optie 3 idd"): the five-membered-ring pool (181 pending A2 children of
# acenaphthylene, carbazole, dibenzofuran, dibenzothiophene; corpus/five_ring_pool_candidates_2026-10-09.txt, breadth-first order) starts on the
# laptop when the cation route ends (probes/cation_analytic_all.sh, ≈ 15 Oct): ONE runner of 8 threads × 12 GB (deck v1), so 8 threads stay free
# for training. It works in its own copy of the corpus dir (corpus/shards_fivering/laptop: own manifest, ledger and corpus.lock; merged later with
# merge_shards.py). When pool 3's box is free (≈ 23–25 Oct) `touch <dir>/STOP`: the runner stops before its next molecule, and the ids without a
# result go to the box. Runs in Git Bash with the Windows psi4 env, like probes/cation_analytic_all.sh (a detached WSL process did not outlive its
# wsl.exe call on 9 Oct, and there is no sudo for a system unit); an app restart kills it — the watch reports the missing pid, and a relaunch is
# safe (molecules with a result are skipped).
#
#   setsid nohup bash probes/fivering_laptop_1015.sh >> probes/results_m1/fivering_laptop_2026-10-09.log 2>&1 < /dev/null &
#   DRY=1 bash probes/fivering_laptop_1015.sh   → copy + one-molecule dry run, no waiting
set -u
# no-set-e: a waiting loop and one run_corpus call per molecule; each failure is logged and the loop goes on to the next molecule
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
C=$P/modules/05_support_predictor/corpus
D=$C/shards_fivering/laptop
LIST=$C/five_ring_pool_candidates_2026-10-09.txt
WAIT_LOG=$P/probes/results_m1/cation_analytic_2026-10-09.log
PY=/c/Users/thebr/.conda/envs/qc/python.exe
export CORPUS_QC_PYTHON='C:\Users\thebr\.conda\envs\qc\python.exe' PYTHONUTF8=1
t() { date '+%F %T'; }
[ -s "$LIST" ] || { echo "=== (F5) NO CANDIDATE LIST $LIST $(t)"; exit 1; }
if [ "${DRY:-0}" != 1 ]; then
  echo $$ > "$P/probes/results_m1/fivering_laptop.pid"
  echo "=== (F5) armed (pid $$), waiting for the cation route to end $(t)"
  until grep -qE '^=== \(CA\) (all 60 cations|STOPPED)' "$WAIT_LOG" 2>/dev/null; do sleep 600; done
fi
if [ ! -f "$D/manifest.csv" ]; then
  mkdir -p "$D" && (cd "$C" && cp run_corpus.py psi4_worker.py cation_rows.py check_results.py status.py manifest.csv "$D/" && cp -r decks "$D/" \
    && head -1 ledger.csv > "$D/ledger.csv") || { echo "=== (F5) COPY FAILED $(t)"; exit 1; }
  echo "(F5) corpus copy in $D $(t)"
fi
cd "$D" || exit 1
if [ "${DRY:-0}" = 1 ]; then
  "$PY" run_corpus.py --ids "$(head -1 "$LIST" | tr -d '\r')" --dry-run; echo "(F5) dry run exit $?"; exit 0
fi
echo "=== (F5) start: $(grep -c . "$LIST") candidates, one runner, deck v1 (8 threads, 12 GB) $(t)"
while read -r id; do
  id=${id%$'\r'}
  [ -z "$id" ] && continue
  [ -f "$D/STOP" ] && { echo "=== (F5) STOP file: the runner hands the rest over $(t)"; break; }
  [ -f "$D/molecules/$id/result.json" ] && continue
  "$PY" run_corpus.py --ids "$id" --worker-max-hours 8 >> "$D/runner.log" 2>&1
  grep -q '"status": "done"' "$D/molecules/$id/result.json" 2>/dev/null && echo "(F5) $id done $(t)" || echo "(F5) $id FAILED $(t)"
done < "$LIST"
echo "=== (F5) laptop runner finished: $(ls "$D/molecules" 2>/dev/null | wc -l) molecules with a folder $(t)"
