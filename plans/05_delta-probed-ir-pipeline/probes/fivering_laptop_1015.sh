#!/bin/bash
# fivering_laptop_1015.sh — TASKS 38, option 3 (the user, 9 Oct 2026: "Optie 3 idd"): the five-membered-ring pool (181 pending A2 children of
# acenaphthylene, carbazole, dibenzofuran, dibenzothiophene; corpus/five_ring_pool_candidates_2026-10-09.txt, breadth-first order) on the laptop:
# ONE runner of 8 threads × 12 GB (deck v1), so 8 threads stay free for training. It works in its own copy of the corpus dir
# (corpus/shards_fivering/laptop: own manifest, ledger and corpus.lock; merged later with merge_shards.py; mirrored nightly since 10 Oct).
# When pool 3's box is free (≈ 23–25 Oct) `touch <dir>/STOP`: the runner stops before its next molecule, and the ids without a result go to the box.
# Runs in Git Bash with the Windows psi4 env (a detached WSL process did not outlive its wsl.exe call on 9 Oct); an app restart kills it — the watch
# reports the missing process, and a relaunch is safe.
#
# Failed molecules (10 Oct 2026, a review the user showed: 'mislukte moleculen worden nooit opnieuw geprobeerd … staat nergens'): the main pass
# skips every id that has a result.json, done or failed, so a relaunch never repeats a molecule. After the main pass (not after a STOP) every id
# whose result says 'failed' is retried ONCE with the corpus's retry rule (run_corpus --retry-failed: Cartesian coordinates, 200 steps, since
# 20 Sep 2026); a molecule that fails again stays failed and is named in the end marker. Retried ids are recorded in <dir>/retried.txt, so a
# relaunch does not retry them a second time.
#
#   PRIORITY=1 nohup bash probes/fivering_laptop_1015.sh >> probes/results_m1/fivering_laptop_2026-10-09.log 2>&1 < /dev/null & disown
#   DRY=1 bash probes/fivering_laptop_1015.sh   → copy + one-molecule dry run, no waiting
#   PRIORITY=1 …   (10 Oct 2026, the user: 'Ja, laat de vijfringpool voorgaan'): wait only until no analytic_hessians.py runs in WSL (the cation
#                  queue script was stopped and its current molecule finishes), not for the cation route's end marker; the cations resume
#                  after this runner through probes/cations_after_fivering.sh
# Overridable for tests: P (plan folder), D (work dir), LIST, PY, PIDFILE, NO_WAIT=1.
set -u
# no-set-e: a waiting loop and one run_corpus call per molecule; each failure is logged and the loop goes on to the next molecule
P=${P:-$(cd "$(dirname "$0")/.." && pwd)}
C=$P/modules/05_support_predictor/corpus
D=${D:-$C/shards_fivering/laptop}
LIST=${LIST:-$C/five_ring_pool_candidates_2026-10-09.txt}
WAIT_LOG=$P/probes/results_m1/cation_analytic_2026-10-09.log
PY=${PY:-/c/Users/thebr/.conda/envs/qc/python.exe}
PIDFILE=${PIDFILE:-$P/probes/results_m1/fivering_laptop.pid}
export CORPUS_QC_PYTHON='C:\Users\thebr\.conda\envs\qc\python.exe' PYTHONUTF8=1
t() { date '+%F %T'; }
status_of() { grep -o '"status": "[a-z]*"' "$D/molecules/$1/result.json" 2>/dev/null | head -1 | cut -d'"' -f4; }
[ -s "$LIST" ] || { echo "=== (F5) NO CANDIDATE LIST $LIST $(t)"; exit 1; }
if [ "${DRY:-0}" != 1 ]; then
  echo $$ > "$PIDFILE"
  echo "=== (F5) armed (pid $$), priority ${PRIORITY:-0} $(t)"
  if [ "${NO_WAIT:-0}" = 1 ]; then
    :
  elif [ "${PRIORITY:-0}" = 1 ]; then
    echo "(F5) priority mode: waiting for the running cation molecule to finish $(t)"
    while wsl.exe -e bash -c 'pgrep -f "[a]nalytic_hessians.py"' > /dev/null 2>&1; do sleep 300; done   # bracket: never matches its own command line
    echo "(F5) no analytic job in WSL; starting $(t)"
  else
    until grep -qE '^=== \(CA\) (all 60 cations|STOPPED)' "$WAIT_LOG" 2>/dev/null; do sleep 600; done
  fi
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
stopped=0
while read -r id; do
  id=${id%$'\r'}
  [ -z "$id" ] && continue
  [ -f "$D/STOP" ] && { echo "=== (F5) STOP file: the runner hands the rest over $(t)"; stopped=1; break; }
  [ -f "$D/molecules/$id/result.json" ] && continue                 # done or failed: the main pass never repeats a molecule
  "$PY" run_corpus.py --ids "$id" --worker-max-hours 8 >> "$D/runner.log" 2>&1
  [ "$(status_of "$id")" = done ] && echo "(F5) $id done $(t)" || echo "(F5) $id FAILED $(t)"
done < "$LIST"
[ "$stopped" = 1 ] && exit 0
touch "$D/retried.txt"
failed_again=""
while read -r id; do                                                  # one retry per failed molecule, Cartesian coordinates, 200 steps
  id=${id%$'\r'}
  [ -z "$id" ] && continue
  [ "$(status_of "$id")" = failed ] || continue
  grep -qxF "$id" "$D/retried.txt" && { failed_again="$failed_again $id"; continue; }
  [ -f "$D/STOP" ] && { echo "=== (F5) STOP file during the retry pass $(t)"; exit 0; }
  echo "$id" >> "$D/retried.txt"
  "$PY" run_corpus.py --ids "$id" --retry-failed --worker-max-hours 8 >> "$D/runner.log" 2>&1
  if [ "$(status_of "$id")" = done ]; then echo "(F5) $id done on retry $(t)"; else echo "(F5) $id FAILED AGAIN $(t)"; failed_again="$failed_again $id"; fi
done < "$LIST"
echo "=== (F5) laptop runner finished: $(ls "$D/molecules" 2>/dev/null | wc -l) molecules with a folder; failed after one retry:${failed_again:- none} $(t)"
