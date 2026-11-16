#!/usr/bin/env bash
# probes/xtb_field_for_step.sh <id> <G dir> <out dir> [--dry-run] (16 Nov 2026, TASKS 211) — what the anharmonic step needs of one
# molecule beyond its B3LYP modes: its GFN2-xTB quartic force field and that field's GVPT2 label. Two existing steps, called as the
# repository calls them and nothing more:
#   1. probes/xtb_anharmonic.sh on a one-line list (as probes/runspecs/routea_xtb.json runs it): the xtb minimum from <G dir>/ref.json,
#      the dxtb Hessians at ±0.10 along every mode, dpir.qff with its noise guard -> <out dir>/xtb/<id>/X;
#   2. probes/gvpt2_labels.py --setting X with the polyad fork on the path (as probes/s3_read_inputs.sh runs it) -> <out dir>/gvpt2_x/<id>.json.
# Runs in WSL; m08/anharmonic.py starts it under probes/wsl_capped.sh. SHARDS and OMP_NUM_THREADS pass through to step 1.
# pyVPT2's vpt2.py imports psi4 at its top, so the env `vpt2` must hold psi4; no psi4 calculation runs (the label calls
# process_fermi_solver alone, which is numpy).
# Markers '=== (ANH) start|force field done|label done|peak memory …|done|FAILED: <why>'; exit 0 only after 'done'.
set -euo pipefail
ID=${1:?id}; G=${2:?the G directory with ref.json}; OUT=${3:?out directory}; DRY=${4:-}
HERE=$(cd "$(dirname "$0")" && pwd)
PLAN=$(dirname "$HERE")
PY=${PY:-$HOME/miniforge3/envs/vpt2/bin/python}
FORK=${PYVPT2_FORK:-$HOME/pyvpt2-wt-polyad}
say() { echo "=== (ANH) $* $(date '+%F %T')"; }
fail() { say "FAILED: $*"; exit 1; }

[ -f "$G/ref.json" ] || fail "$G/ref.json is missing"
[ -x "$PY" ] || fail "no python at $PY (the conda env vpt2)"
[ -f "$FORK/pyvpt2/fermi_solver.py" ] || fail "no pyVPT2 fork at $FORK (branch polyad-assignment-and-merge)"
mkdir -p "$OUT"
printf '%s\t%s\n' "$ID" "$G" > "$OUT/ids.tsv.tmp" && mv "$OUT/ids.tsv.tmp" "$OUT/ids.tsv"
printf '{"rule": "one molecule, for the anharmonic step of m08/pipeline.py", "selected": [{"id": "%s", "scaffold": "%s"}]}\n' "$ID" "$ID" \
  > "$OUT/selection.json.tmp" && mv "$OUT/selection.json.tmp" "$OUT/selection.json"
if [ "$DRY" = --dry-run ]; then
  bash "$HERE/xtb_anharmonic.sh" "$OUT/ids.tsv" "$OUT/xtb" --dry-run
  PYTHONPATH="$FORK" "$PY" -c 'import pyvpt2.fermi_solver' || fail "pyVPT2's fermi_solver does not import"
  exit 0
fi

START=$(date +%s)
say "start: $ID, ${SHARDS:-2} x ${OMP_NUM_THREADS:-2} threads"
bash "$HERE/xtb_anharmonic.sh" "$OUT/ids.tsv" "$OUT/xtb" || fail "xtb_anharmonic.sh exit $?"
X=$OUT/xtb/$ID/X
[ -f "$X/qff_report.npz" ] || fail "no force field (see $X)"
[ ! -f "$X/NOISY" ] || fail "the force field is NOISY (dpir.qff's noise guard), so it is not used"
say "force field done: $(ls "$X/hess" | wc -l) Hessians in $(( $(date +%s) - START )) s"

cd "$PLAN"
PYTHONPATH="$FORK" PYTHONUNBUFFERED=1 "$PY" probes/gvpt2_labels.py "$OUT/xtb" --selection "$OUT/selection.json" --setting X \
  --out "$OUT/gvpt2_x" || fail "gvpt2_labels.py exit $?"
[ -f "$OUT/gvpt2_x/$ID.json" ] || fail "no GVPT2 label for $ID"
say "label done"

# the peak of this run's own cgroup, when it runs in one (wsl_capped.sh's systemd scope); the session's cgroup would say nothing
CG=/sys/fs/cgroup$(awk -F: '$1 == 0 { print $3 }' /proc/self/cgroup)
case "$CG" in
  */run-*.scope)
    if [ -r "$CG/memory.peak" ]; then
      say "peak memory $(( $(cat "$CG/memory.peak") / 1048576 )) MB (the scope's memory.peak, page cache included)"
    fi ;;
esac
say "done: $ID in $(( $(date +%s) - START )) s"
