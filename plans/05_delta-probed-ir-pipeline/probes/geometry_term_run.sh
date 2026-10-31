#!/usr/bin/env bash
# probes/geometry_term_run.sh [--dry-run] (31 Oct 2026, TASKS 156 (d); PreRegistration_2026-10-31_Geometry_Term.md) — the geometry-term check's
# runs: for every force field at G (S2), ωB97X's Hessians from G's minimum to its own (probes/geometry_term_check.py run), in WSL with the
# qc05 env under a cgroup cap, the thread count for OpenMP and OpenBLAS. It first waits for the laptop's field route to end (WAIT_EXIT: both
# runs together exceed the 13 GB laptop budget). A molecule whose record exists is skipped (restartable). Markers '=== (GT) …'.
# stderr goes to stdout here, inside WSL: through `wsl -e` the two streams kept their own offsets in one log file and pyscf's warnings
# overwrote the field route's start lines (31 Oct).
set -euo pipefail
exec 2>&1
PLAN=$(cd "$(dirname "$0")/.." && pwd)
S2=${GT_S2:-$PLAN/probes/results_m1/s2_anharmonic_2026-10-18/s2}
OUT=${GT_OUT:-$PLAN/probes/results_m1/geometry_term_2026-10-31/runs}
PY=${GT_PYTHON:-/home/thebreadishard/qc05/bin/python}
THREADS=${GT_THREADS:-8}
CAP_MB=${GT_CAP_MB:-6144}
WAIT_EXIT=${GT_WAIT_EXIT:-$PLAN/probes/results_m1/l5_apt_field_2026-10-31/l5_apt_field.exit}
export OMP_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS
mark() { echo "=== (GT) $* $(date '+%F %T')"; }
ids() { for d in "$S2"/*/G/qff_report.npz; do basename "$(dirname "$(dirname "$d")")"; done; }
DRY=0
case ${1:-} in --dry-run) DRY=1 ;; "") ;; *) mark "STOPPED: unknown argument $1"; exit 1 ;; esac
[ -x "$PY" ] || { mark "STOPPED: $PY missing"; exit 1; }
n=$(ids | wc -l)
[ "$n" -gt 0 ] || { mark "STOPPED: no force field under $S2"; exit 1; }
for id in $(ids); do [ -f "$S2/$id/G/ref.json" ] || { mark "STOPPED: no ref.json for $id"; exit 1; }; done
if [ "$DRY" = 1 ]; then mark "dry run: $n force fields, python present, waits for $WAIT_EXIT"; exit 0; fi
mark "armed: $n force fields, waiting for $WAIT_EXIT"
while [ ! -f "$WAIT_EXIT" ]; do sleep 300; done
mark "start: $n molecules, $THREADS threads, cap $CAP_MB MB"
for id in $(ids); do
  [ -f "$OUT/$id/geometry_term_run.npz" ] && continue
  mark "$id start"
  rc=0
  bash "$PLAN/probes/wsl_capped.sh" "$CAP_MB" -- "$PY" "$PLAN/probes/geometry_term_check.py" run "$S2/$id/G" "$OUT/$id" --threads "$THREADS" || rc=$?
  [ "$rc" = 0 ] || { mark "STOPPED: $id failed (exit $rc)"; exit 1; }
  mark "$id done"
done
mark "all done"
