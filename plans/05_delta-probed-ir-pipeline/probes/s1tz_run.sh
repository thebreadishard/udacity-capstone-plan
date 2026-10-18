#!/usr/bin/env bash
# probes/s1tz_run.sh <tag> <ids.tsv> <out_root> <parallel> <threads> [--dry-run] (18 Oct 2026, TASKS 60; registration
# GoalGathering/notes/PreRegistration_2026-10-14_TZ_Anharmonic_Basis.md) — S1-TZ through S2's runner at the registered setting
# T:def2-tzvp:75,302 with the grid gate at 99/590, wrapped by probes/progress_on_growth.sh so that tools/runspec.py sees a progress line while a
# molecule's displaced Hessians land (one T Hessian takes tens of minutes, a molecule a day or more). MAX_FIRST (the stop rule's seconds for a
# molecule's first displaced Hessian) must be set by the caller: benzene's run prices T, the fused pair's comes from that price.
#   MAX_FIRST=7200 bash probes/s1tz_run.sh S1TZA probes/results_m1/s1tz_2026-10-18/ids_benzene.tsv /root/s1tz 1 5
# --dry-run checks the interpreter, the list (LF only, every geometry present) and MAX_FIRST, prints the command, and computes nothing.
set -euo pipefail
TAG=${1:?tag}; LIST=${2:?ids.tsv}; ROOT=${3:?out root}; PAR=${4:?parallel}; THR=${5:?threads}; DRY=${6:-}
SETTING='T:def2-tzvp:75,302'
export PY=${PY:-/root/miniforge3/envs/qc05/bin/python} GATE_GRID=99,590
HERE=$(cd "$(dirname "$0")" && pwd)
[ -n "${MAX_FIRST:-}" ] || { echo "s1tz_run.sh: set MAX_FIRST (the stop rule, seconds)" >&2; exit 2; }
export MAX_FIRST
[ -x "$PY" ] || { echo "s1tz_run.sh: no interpreter $PY" >&2; exit 2; }
if grep -q $'\r' "$LIST"; then echo "s1tz_run.sh: $LIST has CR line ends (the 14 Oct incident)" >&2; exit 2; fi
while IFS=$'\t' read -r id geom; do
  [ -f "$geom" ] || { echo "s1tz_run.sh: $id has no geometry $geom" >&2; exit 2; }
done < "$LIST"
cmd=(bash "$HERE/progress_on_growth.sh" --tag "$TAG" --dir "$ROOT" --name '*.json' --interval 600 --
     bash "$HERE/s2_batch.sh" "$LIST" "$ROOT" "$PAR" "$THR" "$SETTING")
if [ "$DRY" = --dry-run ]; then
  echo "dry run: $(grep -c . "$LIST") molecule(s), MAX_FIRST $MAX_FIRST s, GATE_GRID $GATE_GRID, $PY"
  echo "would run: ${cmd[*]}"
  exit 0
fi
exec "${cmd[@]}"
