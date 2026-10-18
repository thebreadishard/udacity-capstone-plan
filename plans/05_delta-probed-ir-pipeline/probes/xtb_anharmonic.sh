#!/usr/bin/env bash
# probes/xtb_anharmonic.sh <list.tsv> <out_root> [--dry-run] (18 Oct 2026; S2 amendment 4) — GFN2-xTB quartic force fields for the molecules
# of the list (id TAB the molecule's B3LYP G setting directory, relative to the plan folder), one after another, in the layout of S2:
# <out_root>/<id>/X/{refstub,refhess,stubs,hess,ref.json,qff_report.md,qff_report.npz}. The same steps as probes/s1_anharmonic_level.sh with
# GFN2-xTB in place of pyscf: the minimum by the xtb binary from the G minimum; every Hessian by dxtb (central differences of its exact
# autograd forces, probes/dxtb_hessians_for_qff.py — the binary's Hessian file is rotation-projected), SHARDS processes of OMP_NUM_THREADS
# at nice 10; the ±0.10 displacements (make_qff_displacements.py); dpir.qff with its noise guard (a NOISY field is assembled with
# --allow-noisy for the record and marked). Resumable.
# Markers '=== (XTB) <id>: done|NOISY|FAILED' and '=== (XTB) all done'; one progress line per Hessian from xtb_hessians_for_qff.py.
#   MSYS_NO_PATHCONV=1 wsl -e bash /mnt/c/.../probes/xtb_anharmonic.sh probes/results_m1/s2_xtb_2026-10-18/ids.tsv probes/results_m1/s2_xtb_2026-10-18/xtb
# no-set-e: one molecule's failure is recorded and the others go on
set -uo pipefail
LIST=${1:?list}; ROOT=${2:?out root}; DRY=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
PLAN=$(dirname "$HERE")
PY=${PY:-$HOME/miniforge3/envs/vpt2/bin/python}
PY_DXTB=${PY_DXTB:-$HOME/miniforge3/envs/dxtb/bin/python}
SHARDS=${SHARDS:-2}
export XTB=${XTB:-$HOME/miniforge3/envs/xtb/bin/xtb} OMP_NUM_THREADS=${OMP_NUM_THREADS:-2} OMP_STACKSIZE=1G
DISP=0.10
cd "$PLAN" || exit 2
mark() { echo "=== (XTB) $* $(date '+%F %T')"; }
[ -x "$PY" ] && [ -x "$XTB" ] && [ -x "$PY_DXTB" ] || { echo "xtb_anharmonic.sh: missing $PY, $PY_DXTB or $XTB" >&2; exit 2; }
if grep -q $'\r' "$LIST"; then echo "xtb_anharmonic.sh: $LIST has CR line ends" >&2; exit 2; fi
while IFS=$'\t' read -r id gdir; do
  [ -f "$gdir/ref.json" ] || { echo "xtb_anharmonic.sh: $id has no $gdir/ref.json" >&2; exit 2; }
done < "$LIST"
if [ "$DRY" = --dry-run ]; then
  echo "dry run: $(grep -c . "$LIST") molecules, $SHARDS × $OMP_NUM_THREADS threads, $PY, $PY_DXTB, $("$XTB" --version 2>&1 | grep -o 'xtb version [0-9.]*')"
  exit 0
fi

one() {   # $1 = id, $2 = G setting directory
  local id=$1 g=$2 d=$ROOT/$1/X
  if [ -f "$d/qff_report.npz" ]; then mark "$id: already done, skipped"; return 0; fi
  mark "$id: start"
  mkdir -p "$d/refstub" "$d/stubs" "$d/hess"
  [ -f "$d/refstub/ref.json" ] || "$PY" "$HERE/xtb_hessians_for_qff.py" opt "$g/ref.json" "$d/refstub/ref.json" || return 1
  nice -n 10 "$PY_DXTB" -W ignore "$HERE/dxtb_hessians_for_qff.py" hess "$d/refstub" "$d/refhess" --method forces-fd || return 1
  cp "$d/refhess/ref.json" "$d/ref.json"
  "$PY" "$HERE/make_qff_displacements.py" "$d/ref.json" "$d/stubs" --disp "$DISP" || return 1
  cp "$d/ref.json" "$d/hess/ref.json"      # the reference stub carries the same name, so it is not computed twice
  mark "$id: $(ls "$d/stubs" | wc -l) Hessians to compute"
  local k pids=()
  for k in $(seq 0 $((SHARDS - 1))); do
    nice -n 10 "$PY_DXTB" -W ignore "$HERE/dxtb_hessians_for_qff.py" hess "$d/stubs" "$d/hess" --method forces-fd --shard "$k/$SHARDS" &
    pids+=("$!")
  done
  for k in "${pids[@]}"; do wait "$k" || return 1; done
  [ "$(ls "$d/hess"/*.json | wc -l)" -eq "$(ls "$d/stubs"/*.json | wc -l)" ] || { echo "missing Hessians in $d/hess" >&2; return 1; }
  if PYTHONPATH=src "$PY" -m dpir.qff "$d/hess" --disp "$DISP" --out "$d/qff_report.md" > "$d/qff_stdout.log" 2>&1; then
    mark "$id: done"
  else
    grep -q NoisyForceFieldError "$d/qff_stdout.log" || return 1
    touch "$d/NOISY"
    PYTHONPATH=src "$PY" -m dpir.qff "$d/hess" --disp "$DISP" --allow-noisy --out "$d/qff_report.md" > "$d/qff_stdout.log" 2>&1
    mark "$id: NOISY — $(grep -o 'route disagreement .*max [0-9.]* cm⁻¹' "$d/qff_report.md" | head -1) (excluded by the noise rule)"
  fi
}

mark "start: $(grep -c . "$LIST") molecules, $OMP_NUM_THREADS threads"
while IFS=$'\t' read -r id gdir; do
  one "$id" "$gdir" < /dev/null || mark "$id: FAILED (see $ROOT/$id/X)"
done < "$LIST"
mark "all done: $(find "$ROOT" -path '*/X/qff_report.npz' | wc -l) force fields ($(find "$ROOT" -path '*/X/NOISY' | wc -l) noisy)"
