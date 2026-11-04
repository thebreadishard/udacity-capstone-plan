#!/usr/bin/env bash
# probes/mp2_631gs_anchors.sh <ids.tsv> <out_dir> [--dry-run] (4 Nov 2026; TASKS 183 (1), the user: 'Akkoord met 183') — the MP2/6-31G* rows
# of each listed molecule (id TAB corpus geometry.json, paths relative to the plan) through `cc_composite_full_check.py compute`: pyscf
# conventional MP2, Cartesian d functions (the corpus's 6-31G*), frozen core by the element rule, the anchors' step 0.005 bohr, the corpus
# frame — the route and settings of the 5 Oct step 0, whose benzene and naphthalene files are reused. One molecule after another; a molecule
# whose row file exists is skipped, so a relaunch resumes per molecule. pyscf's own log goes to <row file>.pyscf.log.
# Lines: '=== (M631) <id>: start | done | FAILED | already done, skipped', last '=== (M631) all done: N of M'.
# no-set-e: a failed molecule is reported and the next one runs; the last line counts them
set -u
LIST=${1:?ids.tsv (id TAB geometry.json)}; OUT=${2:?out dir}; DRY=${3:-}
PY=${PY:-$HOME/qc05/bin/python}; THREADS=${THREADS:-8}; MEM=${MAX_MEMORY_MB:-8000}
HERE=$(cd "$(dirname "$0")" && pwd)
PLAN=$(dirname "$HERE")
cd "$PLAN" || exit 2
if grep -q $'\r' "$LIST"; then echo "mp2_631gs_anchors.sh: $LIST has CR line ends" >&2; exit 2; fi
n=0
while IFS=$'\t' read -r id geom; do
  [ -f "$geom" ] || { echo "mp2_631gs_anchors.sh: no geometry $geom for $id" >&2; exit 2; }
  n=$((n + 1))
done < "$LIST"
[ -x "$PY" ] || { echo "mp2_631gs_anchors.sh: no interpreter $PY" >&2; exit 2; }
if [ "$DRY" = --dry-run ]; then
  echo "dry run: $n molecule(s), $THREADS threads, max_memory $MEM MB, $PY, rows to $OUT"
  exit 0
fi
mkdir -p "$OUT"
say() { echo "=== (M631) $* $(date '+%F %T')"; }
ok=0
while IFS=$'\t' read -r id geom; do
  out="$OUT/mp2_rows_${id}_631gs.npz"
  if [ -f "$out" ]; then say "$id: already done, skipped"; ok=$((ok + 1)); continue; fi
  say "$id: start"
  if "$PY" -u "$HERE/cc_composite_full_check.py" compute "$geom" "$out" --basis '6-31g*' --cart --threads "$THREADS" --max-memory "$MEM" < /dev/null; then
    say "$id: done"; ok=$((ok + 1))
  else
    say "$id: FAILED"
  fi
done < "$LIST"
say "all done: $ok of $n"
