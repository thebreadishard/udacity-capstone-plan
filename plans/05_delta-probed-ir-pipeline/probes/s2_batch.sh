#!/usr/bin/env bash
# probes/s2_batch.sh <ids.tsv> <out_root> <parallel> <threads> <name:basis:grid> (14 Oct 2026, S2; registration
# GoalGathering/notes/PreRegistration_2026-10-14_S2_Anharmonic_Shift.md) — GVPT2 of every molecule of the list (id TAB geometry path, relative
# to the plan folder) at one setting, <parallel> molecules at a time, each through probes/s1_anharmonic_level.sh with its own log
# <out_root>/<id>.log. Resumable: a molecule whose QFF report exists is skipped. Stop rule per molecule: MAX_FIRST (default 1800 s) on its
# first displaced Hessian, or the list's optional third column in seconds (S2b, 19 Oct 2026: 1.5 × the molecule's predicted Hessian,
# probes/s2b_plan.py). Markers '=== (S2) <id>: done|NOISY|STOPPED|FAILED' and at the end '=== (S2) all done: …'.
#   bash probes/s2_batch.sh probes/results_m1/s2_training_set_2026-10-14/s2_ids.tsv /root/s2 3 5 G:6-31g*:75,302
set -uo pipefail
# no-set-e: one molecule's failure is recorded and the others go on
LIST=$1; ROOT=$2; PAR=$3; THR=$4; SETTING=$5
HERE=$(cd "$(dirname "$0")" && pwd)
export ROOT THR SETTING HERE MAX_FIRST=${MAX_FIRST:-1800}
mark() { echo "=== (S2) $* $(date '+%F %T')"; }
one() {   # $1 = id, $2 = geometry path, $3 = MAX_FIRST for this molecule (empty: the batch's)
  local id=$1 g=$2 mf=${3:-$MAX_FIRST} name=${SETTING%%:*} d=$ROOT/$1 rc
  if [ -f "$d/$name/qff_report.npz" ]; then mark "$id: already done, skipped"; return 0; fi
  mark "$id: start"
  [ -f "$ROOT/$id.log" ] && mv "$ROOT/$id.log" "$ROOT/$id.$(date +%Y%m%d-%H%M%S).log"   # a resumed molecule keeps its earlier log
  MAX_FIRST=$mf bash "$HERE/s1_anharmonic_level.sh" "$g" "$d" "$THR" "$SETTING" > "$ROOT/$id.log" 2>&1; rc=$?
  if [ "$rc" = 0 ]; then
    if [ -f "$d/$name/NOISY" ]; then mark "$id: NOISY (excluded by the noise rule)"; else mark "$id: done"; fi
  elif [ -f "$d/$name/GATE_FAILED" ]; then mark "$id: GATE FAILED (grid gate at ${GATE_GRID:-?}; re-price at that grid)"
  elif grep -q 'STOP: the first Hessian took' "$ROOT/$id.log"; then mark "$id: STOPPED (first displaced Hessian over $mf s)"
  else mark "$id: FAILED rc=$rc: $(grep -m1 -E 'not converged|Error|Traceback' "$ROOT/$id.log" | cut -c1-160) (see $ROOT/$id.log)"; fi
}
export -f one mark
mkdir -p "$ROOT"
mark "start: $(grep -c . "$LIST") molecules, $PAR at a time, $THR threads each, setting $SETTING"
tr -d '\r' < "$LIST" | cut -f1-3 | xargs -P "$PAR" -L 1 bash -c 'one "$0" "$1" "$2"'   # CR-proof: a CRLF list failed every molecule (14 Oct 2026)
name=${SETTING%%:*}
n_done=$(find "$ROOT" -path "*/$name/qff_report.npz" | wc -l); n_noisy=$(find "$ROOT" -path "*/$name/NOISY" | wc -l)
mark "all done: $n_done force fields ($n_noisy noisy) of $(grep -c . "$LIST")"
