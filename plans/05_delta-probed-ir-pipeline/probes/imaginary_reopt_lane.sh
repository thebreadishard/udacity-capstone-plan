#!/usr/bin/env bash
# imaginary_reopt_lane.sh <source molecules dir> <out dir> <ids file> <threads> [--dry-run] (20 Nov 2026, TASKS 215;
# GoalGathering/notes/PreRegistration_2026-11-20_Imaginary_Label_Reoptimisation.md) — one lane of the repair at the source of the
# corpus molecules whose analytic label has an imaginary mode. Per id of the list (first field of a line; '#' comments), the two
# existing steps as probes/reoptimise_label_settings.sh runs them for one molecule on the laptop, here without WSL and into any out dir:
#   1. probes/reoptimise_at_label_settings.py <source>/<id> <out>/<id>: the push along a negative lowest B3LYP mode and geomeTRIC
#      at the labels' SCF; kept when <out>/<id>/geometry.json exists (the script writes it last);
#   2. corpus/analytic_hessians.py <out>/<id> --reuse-existing: both analytic Hessians, the APT and, for a mode below 20 cm⁻¹,
#      the route's own low-mode repair (which needs pyscf 2.15.0); a label file that exists is kept.
# The source folders are only read; nothing is written outside <out dir>. PY is the python with pyscf 2.15.0 and geomeTRIC
# (default: the server env qc215); MAX_MEMORY_MB is pyscf's max_memory (default 24000, as the labels server ran the largest molecules).
# --dry-run: step 1's own dry run per id (inputs checked, lowest mode and basis size printed, no SCF, nothing written).
# Markers '=== (IRL) lane start|<id>: start|optimisation done|labels done|no imaginary mode|STILL IMAGINARY …|FAILED …|lane done …'.
# no-set-e: one molecule's failure is recorded with its marker and the lane goes on to the next
set -uo pipefail
USAGE="usage: imaginary_reopt_lane.sh <source molecules dir> <out dir> <ids file> <threads> [--dry-run]"
[ $# -ge 4 ] && [ $# -le 5 ] || { echo "$USAGE"; exit 2; }
SRC=$1; OUT=$2; IDS=$3; THREADS=$4; DRY=${5:-}
[ -z "$DRY" ] || [ "$DRY" = --dry-run ] || { echo "unknown argument '$DRY'; $USAGE"; exit 2; }
case "$THREADS" in ''|*[!0-9]*) echo "threads '$THREADS' is not a whole number; $USAGE"; exit 2 ;; esac
HERE=$(cd -P "$(dirname "$0")" && pwd -P)
PLAN=$(dirname "$HERE")
PY=${PY:-/root/miniforge3/envs/qc215/bin/python}
MAX_MEMORY_MB=${MAX_MEMORY_MB:-24000}
say() { echo "=== (IRL) $* $(date '+%F %T')"; }
[ -x "$PY" ] || { say "FAILED: no python at $PY"; exit 1; }
[ -f "$IDS" ] || { say "FAILED: no ids file $IDS"; exit 1; }
[ -d "$SRC" ] || { say "FAILED: no source folder $SRC"; exit 1; }
export OMP_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1
mapfile -t LIST < <(tr -d '\r' < "$IDS" | grep -v '^#' | awk 'NF { print $1 }')
[ "${#LIST[@]}" -gt 0 ] || { say "FAILED: $IDS names no molecule"; exit 1; }

if [ "$DRY" = --dry-run ]; then
  for id in "${LIST[@]}"; do
    if [ -f "$OUT/$id/geometry.json" ]; then echo "dry run: $id optimised already; its labels would be finished"; continue; fi
    "$PY" "$HERE/reoptimise_at_label_settings.py" "$SRC/$id" "$OUT/$id" --threads "$THREADS" --max-memory "$MAX_MEMORY_MB" --dry-run \
      || { echo "dry run FAILED for $id"; exit 1; }
  done
  echo "dry run: ${#LIST[@]} molecules, $THREADS threads, pyscf max_memory $MAX_MEMORY_MB MB, into $OUT"
  exit 0
fi

mkdir -p "$OUT"
say "lane start: ${#LIST[@]} molecules from $IDS, $THREADS threads, pyscf max_memory $MAX_MEMORY_MB MB"
n_clean=0; n_imag=0; n_failed=0
for id in "${LIST[@]}"; do
  t0=$(date +%s)
  say "$id: start"
  if [ -f "$OUT/$id/geometry.json" ]; then
    say "$id: optimisation kept from an earlier pass"
  else
    if ! "$PY" "$HERE/reoptimise_at_label_settings.py" "$SRC/$id" "$OUT/$id" --threads "$THREADS" --max-memory "$MAX_MEMORY_MB"; then
      say "$id: FAILED in the optimisation (not converged or an error; no geometry.json is written)"; n_failed=$((n_failed + 1)); continue
    fi
    say "$id: optimisation done in $(( $(date +%s) - t0 )) s"
  fi
  rc=0
  "$PY" "$PLAN/modules/05_support_predictor/corpus/analytic_hessians.py" "$OUT/$id" --threads "$THREADS" --max-memory "$MAX_MEMORY_MB" \
    --reuse-existing --lane "imaginary_reopt_lane.sh $(basename "$IDS")" || rc=$?
  case $rc in
    0) say "$id: labels done" ;;
    3) say "$id: labels done, APT FAILED its checks (the Hessians are written)" ;;
    *) say "$id: FAILED in the labels (exit $rc)"; n_failed=$((n_failed + 1)); continue ;;
  esac
  counts=$(grep -oE '"n_imaginary_(b3lyp|wb97x)": [0-9]+' "$OUT/$id/result.json" | tr '\n' ' ')
  if [ "$(echo "$counts" | grep -oE ': [0-9]+' | wc -l)" != 2 ]; then
    say "$id: FAILED: result.json lacks the two imaginary counts ($counts)"; n_failed=$((n_failed + 1))
  elif echo "$counts" | grep -qE ': [1-9]'; then
    say "$id: STILL IMAGINARY $counts($(( $(date +%s) - t0 )) s)"; n_imag=$((n_imag + 1))
  else
    say "$id: no imaginary mode $counts($(( $(date +%s) - t0 )) s)"; n_clean=$((n_clean + 1))
  fi
done
say "lane done: ${#LIST[@]} molecules, $n_clean without an imaginary mode, $n_imag still imaginary, $n_failed failed"
