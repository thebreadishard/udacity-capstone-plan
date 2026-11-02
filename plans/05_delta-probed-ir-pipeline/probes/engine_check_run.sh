#!/usr/bin/env bash
# probes/engine_check_run.sh <queue file> [--dry-run] (2 Nov 2026; TASKS 73, `GoalGathering/notes/PreRegistration_2026-11-01_Engine_Check.md`)
# — the pyscf route of the engine check: per folder of the queue (one path a line, relative to the plan), geomeTRIC from start.json to
# geometry.json (`probes/engine_check.py optimise`), then the two analytic Hessians at that geometry as the corpus labels them
# (`corpus/analytic_hessians.py --functionals b3lyp,wb97x --no-apt --grid 99,590`). In WSL with qc05, one folder at a time in the queue's
# order (the registration's: water's smoke, benzene timed, then the other seven), every step under its own cgroup cap (probes/wsl_capped.sh).
# A folder with both Hessians is skipped and an optimised one is not optimised again, so the run resumes; a failed folder is logged and the
# queue goes on. Markers '=== (ECK) …'; each step's output in <folder>/step.log, pyscf's in <folder>/pyscf.log.
# --dry-run: the queue, the inputs and the Python files checked; nothing computed.
set -euo pipefail
exec 2>&1
PLAN=$(cd "$(dirname "$0")/.." && pwd)
PY=${ECK_PYTHON:-/home/thebreadishard/qc05/bin/python}
THREADS=${ECK_THREADS:-8}
CAP_MB=${ECK_CAP_MB:-6144}
MAX_MEMORY_MB=${ECK_MAX_MEMORY_MB:-4000}
CHECK=$PLAN/probes/engine_check.py
HESSIANS=$PLAN/modules/05_support_predictor/corpus/analytic_hessians.py
export OMP_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS
mark() { echo "=== (ECK) $* $(date '+%F %T')"; }

QUEUE=${1:-}
DRY=0
case ${2:-} in --dry-run) DRY=1 ;; "") ;; *) mark "STOPPED: unknown argument $2"; exit 1 ;; esac
[ -n "$QUEUE" ] && [ -f "$QUEUE" ] || { mark "STOPPED: no queue file '$QUEUE'"; exit 1; }
folders() { grep -v '^#' "$QUEUE" | grep -v '^$' || true; }
[ -n "$(folders)" ] || { mark "STOPPED: the queue lists no folder"; exit 1; }
[ -x "$PY" ] || { mark "STOPPED: $PY missing"; exit 1; }
"$PY" -m py_compile "$CHECK" "$HESSIANS" || { mark "STOPPED: a Python file does not compile"; exit 1; }
"$PY" -I -c 'import geometric, pyscf' || { mark "STOPPED: geomeTRIC or pyscf does not import in $PY"; exit 1; }
while read -r rel; do
  [ -f "$PLAN/$rel/start.json" ] || { mark "STOPPED: no start.json in $rel"; exit 1; }
done < <(folders)
if [ "$DRY" = 1 ]; then
  mark "dry run: $(folders | wc -l) folders, $THREADS threads, cap $CAP_MB MB a step, pyscf max_memory $MAX_MEMORY_MB MB, inputs checked"
  exit 0
fi

mark "start: $(folders | wc -l) folders, $THREADS threads, cap $CAP_MB MB a step, pyscf max_memory $MAX_MEMORY_MB MB"
done_n=0
while read -r rel; do
  d=$PLAN/$rel
  id=$(basename "$d")
  if [ -f "$d/hessian_b3lyp_analytic.npz" ] && [ -f "$d/hessian_wb97x_analytic.npz" ]; then done_n=$((done_n + 1)); continue; fi
  t0=$(date +%s)
  rc=0
  if [ ! -f "$d/geometry.json" ]; then
    mark "$id optimise start"
    # geomeTRIC writes its own files into the working directory: the folder keeps them
    (cd "$d" && bash "$PLAN/probes/wsl_capped.sh" "$CAP_MB" -- "$PY" "$CHECK" optimise "$d" --threads "$THREADS" \
      --max-memory "$MAX_MEMORY_MB" >> "$d/step.log" 2>&1) || rc=$?
    if [ "$rc" != 0 ]; then mark "$id FAILED in the optimisation (exit $rc) after $(( $(date +%s) - t0 )) s: see $rel/step.log"; continue; fi
    mark "$id optimised $(( $(date +%s) - t0 )) s"
  fi
  t1=$(date +%s)
  bash "$PLAN/probes/wsl_capped.sh" "$CAP_MB" -- "$PY" "$HESSIANS" "$d" --functionals b3lyp,wb97x --no-apt --grid 99,590 \
    --threads "$THREADS" --max-memory "$MAX_MEMORY_MB" >> "$d/step.log" 2>&1 || rc=$?
  if [ "$rc" != 0 ]; then mark "$id FAILED in the Hessians (exit $rc) after $(( $(date +%s) - t1 )) s: see $rel/step.log"; continue; fi
  done_n=$((done_n + 1))
  mark "$id done: Hessians $(( $(date +%s) - t1 )) s, in all $(( $(date +%s) - t0 )) s"
done < <(folders)
mark "all done: $done_n of $(folders | wc -l) folders with both Hessians"
