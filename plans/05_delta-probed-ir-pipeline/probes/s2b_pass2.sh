#!/usr/bin/env bash
# probes/s2b_pass2.sh <first_pass_log> <list.tsv> <root> <parallel> <threads> <name:basis:grid> (2 Nov 2026; S2b registration amendment 1,
# the user: 'Akkoord voor optie A') — S2b's second pass on one server. Waits until the first pass's log ends ('=== (S2) all done'), then
# re-queues every molecule that pass STOPPED by the stop rule, with the stop rule re-priced on the molecule's own measured first displaced
# Hessian: MAX_FIRST = 1.5 × its wall_s, never below the list's value. A re-queued molecule resumes from what it kept (s1_anharmonic_level.sh
# skips the optimised stub and every Hessian file that exists). Writes <root>/requeue.tsv and runs probes/s2_batch.sh on it.
#   PY=… bash probes/s2b_pass2.sh /root/dpir_s2b/s2b_1of3.log probes/results_m1/…/s2b_ids_1of3.tsv /root/s2b 3 5 'G:6-31g*:75,302'
set -euo pipefail
FIRST=${1:?first pass log}; LIST=${2:?list}; ROOT=${3:?root}; PAR=${4:?parallel}; THR=${5:?threads}; SETTING=${6:?setting}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:?set PY}
name=${SETTING%%:*}
echo "=== (S2P2) waiting for the first pass to end ($FIRST) $(date '+%F %T')"
until grep -q '^=== (S2) all done' "$FIRST"; do sleep 600; done
: > "$ROOT/requeue.tsv.tmp"
for id in $(grep -o '^=== (S2) [A-Za-z0-9_]*: STOPPED' "$FIRST" | awk '{print $3}' | tr -d ':'); do
  geom=$(awk -F'\t' -v i="$id" '$1 == i {print $2}' "$LIST" | tr -d '\r')
  old=$(awk -F'\t' -v i="$id" '$1 == i {print $3}' "$LIST" | tr -d '\r')
  wall=$("$PY" -c "import glob, json, os, sys
f = [p for p in glob.glob(os.path.join(sys.argv[1], '*.json')) if os.path.basename(p) != 'ref.json']
print(min(json.load(open(p))['provenance']['wall_s'] for p in f) if f else 0)" "$ROOT/$id/$name/hess")
  new=$("$PY" -c "import sys; print(max(int(float(sys.argv[2])), round(1.5 * float(sys.argv[1]))))" "$wall" "${old:-0}")
  printf '%s\t%s\t%s\n' "$id" "$geom" "$new" >> "$ROOT/requeue.tsv.tmp"
  echo "=== (S2P2) re-queued $id: first displaced Hessian ${wall} s, MAX_FIRST ${old} → ${new} s"
done
mv "$ROOT/requeue.tsv.tmp" "$ROOT/requeue.tsv"
if [ ! -s "$ROOT/requeue.tsv" ]; then echo "=== (S2P2) nothing was stopped"; echo "=== (S2) all done: pass 2 had nothing to run"; exit 0; fi
echo "=== (S2P2) pass 2 start: $(grep -c . "$ROOT/requeue.tsv") molecules $(date '+%F %T')"
exec bash "$HERE/s2_batch.sh" "$ROOT/requeue.tsv" "$ROOT" "$PAR" "$THR" "$SETTING"
