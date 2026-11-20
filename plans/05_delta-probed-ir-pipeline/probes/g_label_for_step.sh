#!/usr/bin/env bash
# probes/g_label_for_step.sh <id> <geometry.json> <out dir> <threads> [--dry-run] (20 Nov 2026, TASKS 211;
# GoalGathering/notes/PreRegistration_2026-11-20_Anharmonic_Step_Substituted_Molecule.md, part B) — the label the anharmonic
# step is trained against, for one molecule: its B3LYP/6-31G* quartic force field at grid 75,302 ("the G route") and that
# field's GVPT2 label. Two existing steps, called as the repository calls them and nothing more:
#   1. probes/s1_anharmonic_level.sh <geometry> <out dir>/g/<id> <threads> G:6-31g*:75,302 (as probes/s2_batch.sh runs it per
#      molecule): the pyscf minimum from <geometry.json>, the Hessians at ±0.10 along every mode, dpir.qff with its noise guard
#      -> <out dir>/g/<id>/G;
#   2. probes/gvpt2_labels.py --setting G with the polyad fork on the path (as probes/xtb_field_for_step.sh runs it for X)
#      -> <out dir>/gvpt2_g/<id>.json.
# Runs in WSL, from the plan folder this script lies in; both paths are relative to it. Resumable: step 1 skips the minimum
# and every Hessian that exists. MAX_FIRST (seconds allowed for the first displaced Hessian, step 1's stop rule) defaults to
# probes/s2_batch.sh's 1800. A NOISY field (dpir.qff's guard: the two quartic routes disagree by more than 10 cm⁻¹) gets no
# label: the marker says so and the exit is 0, because that is an outcome the registration names, not a failure.
# Markers '=== (GLB) start|force field done|NOISY …|label done|peak memory …|done|FAILED: <why>'; exit 0 only after 'done' or 'NOISY'.
set -euo pipefail
USAGE="usage: g_label_for_step.sh <id> <geometry.json> <out dir> <threads> [--dry-run]"
[ $# -ge 4 ] && [ $# -le 5 ] || { echo "$USAGE"; exit 2; }
ID=$1; GEOM=$2; OUT=$3; THREADS=$4; DRY=${5:-}
[ -z "$DRY" ] || [ "$DRY" = --dry-run ] || { echo "unknown argument '$DRY'; $USAGE"; exit 2; }
case "$THREADS" in ''|*[!0-9]*) echo "threads '$THREADS' is not a whole number; $USAGE"; exit 2 ;; esac
HERE=$(cd -P "$(dirname "$0")" && pwd -P)
PLAN=$(dirname "$HERE")
SETTING="G:6-31g*:75,302"
PY=${PY:-/home/thebreadishard/qc05/bin/python}                 # pyscf, as probes/s1_anharmonic_level.sh's default
PY_LABEL=${PY_LABEL:-$HOME/miniforge3/envs/vpt2/bin/python}    # pyVPT2, as probes/xtb_field_for_step.sh's default
FORK=${PYVPT2_FORK:-$HOME/pyvpt2-wt-polyad}
export PY MAX_FIRST=${MAX_FIRST:-1800}
say() { echo "=== (GLB) $* $(date '+%F %T')"; }
fail() { say "FAILED: $*"; exit 1; }

cd "$PLAN"
[ -f "$GEOM" ] || fail "$GEOM is missing"
[ -x "$PY" ] || fail "no python at $PY (the env with pyscf)"
[ -x "$PY_LABEL" ] || fail "no python at $PY_LABEL (the conda env vpt2)"
[ -f "$FORK/pyvpt2/fermi_solver.py" ] || fail "no pyVPT2 fork at $FORK (branch polyad-assignment-and-merge)"
if [ "$DRY" = --dry-run ]; then
  "$PY" "$HERE/g_label_tools_check.py" "$GEOM" || fail "the pyscf env does not import what the force field needs"
  PYTHONPATH="$FORK" "$PY_LABEL" "$HERE/g_label_tools_check.py" --label || fail "pyVPT2's fermi_solver does not import"
  echo "dry run: $ID from $GEOM, setting $SETTING, $THREADS threads, first displaced Hessian within $MAX_FIRST s, into $OUT"
  exit 0
fi

START=$(date +%s)
G=$OUT/g/$ID/G
mkdir -p "$OUT"
printf '{"rule": "one molecule, for the read of the anharmonic step against its label", "selected": [{"id": "%s", "scaffold": "%s"}]}\n' \
  "$ID" "$ID" > "$OUT/selection.json.tmp" && mv "$OUT/selection.json.tmp" "$OUT/selection.json"
say "start: $ID, setting $SETTING, $THREADS threads"
bash "$HERE/s1_anharmonic_level.sh" "$GEOM" "$OUT/g/$ID" "$THREADS" "$SETTING" || fail "s1_anharmonic_level.sh exit $?"
[ -f "$G/qff_report.npz" ] || fail "no force field (see $G)"
say "force field done: $(find "$G/hess" -name '*.json' | wc -l) Hessians in $(( $(date +%s) - START )) s"

peak() {   # the peak of this run's own cgroup when it runs in a systemd scope (probes/wsl_capped.sh's); the session's would say nothing
  local cg
  cg=/sys/fs/cgroup$(awk -F: '$1 == 0 { print $3 }' /proc/self/cgroup)
  case "$cg" in
    */run-*.scope) [ ! -r "$cg/memory.peak" ] || say "peak memory $(( $(cat "$cg/memory.peak") / 1048576 )) MB (the scope's memory.peak, page cache included)" ;;
  esac
}

if [ -f "$G/NOISY" ]; then
  peak
  say "NOISY: the force field fails dpir.qff's noise guard, so it gets no label and part B is not read ($ID, $(( $(date +%s) - START )) s)"
  exit 0
fi
PYTHONPATH="$FORK" PYTHONUNBUFFERED=1 "$PY_LABEL" probes/gvpt2_labels.py "$OUT/g" --selection "$OUT/selection.json" --setting G \
  --out "$OUT/gvpt2_g" || fail "gvpt2_labels.py exit $?"
[ -f "$OUT/gvpt2_g/$ID.json" ] || fail "no GVPT2 label for $ID"
say "label done"
peak
say "done: $ID in $(( $(date +%s) - START )) s"
