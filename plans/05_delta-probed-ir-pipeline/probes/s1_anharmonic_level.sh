#!/usr/bin/env bash
# S1 of the spectral-shape design (13 Oct 2026, TASKS 53): GVPT2 of one molecule at several DFT settings, each at its own minimum, with the
# existing QFF tools; then the Δ_anh comparison against the first setting. Registration:
# GoalGathering/notes/PreRegistration_2026-10-13_S1_Anharmonic_Level.md.
#
#   bash probes/s1_anharmonic_level.sh <geometry.json> <out_root> <threads> <name:basis:grid> [<name:basis:grid> ...]
#   e.g. ... corpus/molecules/A_8448043181/geometry.json /home/u/s1_benzene 4 R:6-31g*:99,590 G:6-31g*:75,302 B:6-31g:99,590
#
# Resumable: every step skips what exists (the optimised stub, the Hessians by file name). Markers '=== (S1) ...' for the watch.
# WAIT_LOG / WAIT_RE: wait until the log shows the pattern (S1 waits for the five-ring runner's end). MAX_FIRST: the registration's stop rule,
# seconds allowed for the first displaced Hessian of the first setting (default 900). PARALLEL=1 (13 Oct 2026, the S1 server): one
# process per setting, <threads> each; a failed setting is named in '=== (S1) SETTINGS FAILED: …' after the others have ended.
# GATE_GRID (14 Oct 2026, S1-TZ): before any displacement, the reference Hessian is recomputed at this finer grid and the harmonic ω compared
# (s1_anharmonic_level.py gate, line GATE_LINE, default 1.0 cm⁻¹); a failed gate stops the setting with a GATE_FAILED file and marker.
set -euo pipefail
PY=${PY:-/home/thebreadishard/qc05/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
PLAN=$(dirname "$HERE")
DISP=${DISP:-0.10}                        # decision 46: the step of T3 (0.10) gave T2's fundamentals with half the route noise
geom=$1; root=$2; thr=$3; shift 3
export OMP_NUM_THREADS=$thr
mark() { echo "=== (S1) $* $(date '+%F %T')"; }
if [ -n "${WAIT_LOG:-}" ]; then
  mark "waiting for /${WAIT_RE}/ in $WAIT_LOG"
  until grep -qE "$WAIT_RE" "$WAIT_LOG" 2>/dev/null; do sleep 600; done
fi
MAX_FIRST=${MAX_FIRST:-900}
PARALLEL=${PARALLEL:-0}
mark "start: $# settings, step $DISP, $thr threads$([ "$PARALLEL" = 1 ] && echo ' per setting, the settings in parallel'), geometry $geom"

run_setting() {   # $1 = name:basis:grid; $2 = 1 for the first setting, whose first displaced Hessian the stop rule times
  local name basis grid d
  IFS=: read -r name basis grid <<< "$1"
  d=$root/$name
  mkdir -p "$d/refstub" "$d/stubs" "$d/hess"
  if [ ! -f "$d/refstub/ref.json" ]; then
    mark "$name: optimising (B3LYP/$basis, grid $grid)"
    "$PY" "$HERE/s1_anharmonic_level.py" optimise "$geom" "$d/refstub/ref.json" --basis "$basis" --grid "$grid" --threads "$thr"
  fi
  "$PY" "$HERE/pyscf_hessians_for_qff.py" "$d/refstub" "$d/refhess" --basis "$basis" --grid "$grid" --threads "$thr"
  cp "$d/refhess/ref.json" "$d/ref.json"
  if [ -n "${GATE_GRID:-}" ]; then
    "$PY" "$HERE/pyscf_hessians_for_qff.py" "$d/refstub" "$d/refhess_gate" --basis "$basis" --grid "$GATE_GRID" --threads "$thr"
    if "$PY" "$HERE/s1_anharmonic_level.py" gate "$d/ref.json" "$d/refhess_gate/ref.json" --line "${GATE_LINE:-1.0}" > "$d/grid_gate.log" 2>&1; then
      mark "$name: $(cat "$d/grid_gate.log")"
    else
      mark "$name: GRID GATE FAILED — $(cat "$d/grid_gate.log")"; touch "$d/GATE_FAILED"; return 1
    fi
  fi
  "$PY" "$HERE/make_qff_displacements.py" "$d/ref.json" "$d/stubs" --disp "$DISP"
  cp "$d/ref.json" "$d/hess/ref.json"      # the reference stub carries the same name, so it is not computed twice
  mark "$name: $(ls "$d/stubs" | wc -l) Hessians to compute"
  if [ "$2" = 1 ]; then
    "$PY" "$HERE/pyscf_hessians_for_qff.py" "$d/stubs" "$d/hess" --basis "$basis" --grid "$grid" --threads "$thr" --max-first-seconds "$MAX_FIRST" ${GUESS_FROM_PREVIOUS:+--guess-from-previous}       || { mark "$name: STOPPED by the stop rule or a failure (first displaced Hessian > ${MAX_FIRST} s?) — re-price"; exit 1; }
  else
    "$PY" "$HERE/pyscf_hessians_for_qff.py" "$d/stubs" "$d/hess" --basis "$basis" --grid "$grid" --threads "$thr" ${GUESS_FROM_PREVIOUS:+--guess-from-previous}
  fi
  # dpir.qff refuses a force field whose two finite-difference routes disagree by > 10 cm⁻¹: for S1 that refusal is an outcome (the setting
  # fails), recorded, and the numbers are then assembled with --allow-noisy for the record only (the registration's rule)
  if (cd "$PLAN" && PYTHONPATH=src "$PY" -m dpir.qff "$d/hess" --disp "$DISP" --out "$d/qff_report.md" > "$d/qff_stdout.log" 2>&1); then
    mark "$name: QFF and VPT2 done"
  else
    grep -q NoisyForceFieldError "$d/qff_stdout.log" || { mark "$name: QFF FAILED (see $d/qff_stdout.log)"; exit 1; }
    mark "$name: NOISY — $(grep -o 'quartic route disagreement max [0-9.]* cm⁻¹' "$d/qff_stdout.log" | head -1); assembled with --allow-noisy for the record"
    touch "$d/NOISY"
    (cd "$PLAN" && PYTHONPATH=src "$PY" -m dpir.qff "$d/hess" --disp "$DISP" --allow-noisy --out "$d/qff_report.md" > "$d/qff_stdout.log" 2>&1)
  fi
}

names=()
for spec in "$@"; do names+=("$root/${spec%%:*}"); done
if [ "$PARALLEL" = 1 ]; then
  # 13 Oct 2026 (the S1 server): one process per setting. A failed setting does not stop the others — their Hessians stay usable at a
  # re-pricing, since every step resumes — and the comparison runs only when every setting has finished.
  pids=(); i=0
  for spec in "$@"; do
    i=$((i + 1)); ( run_setting "$spec" "$([ "$i" = 1 ] && echo 1 || echo 0)" ) & pids+=("$!")
  done
  failed=""; i=0
  for spec in "$@"; do wait "${pids[$i]}" || failed="$failed ${spec%%:*}"; i=$((i + 1)); done
  [ -z "$failed" ] || { mark "SETTINGS FAILED:$failed"; exit 1; }
else
  first=1
  for spec in "$@"; do run_setting "$spec" "$first"; first=0; done
fi
if [ "${#names[@]}" -gt 1 ]; then
  "$PY" "$HERE/s1_anharmonic_level.py" compare "${names[@]}" --out "$root/compare.json"
  mark "all settings done"
else
  mark "all settings done (one setting: no comparison)"      # 14 Oct 2026: S2 runs one setting per molecule (probes/s2_batch.sh)
fi
