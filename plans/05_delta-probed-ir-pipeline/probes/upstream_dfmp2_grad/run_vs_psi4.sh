#!/usr/bin/env bash
# probes/upstream_dfmp2_grad/run_vs_psi4.sh <out dir> <case>… (TASKS 321; GoalGathering/notes/Design_2026-11-26_pyscf_DFMP2_Gradient.md,
# validations 3 and 6) — runs in WSL. Each case is name:corpus-id:basis:jkfit:ri:frozen[:pyscf basis file]; for each, psi4's DF-MP2
# gradient (probes/dfmp2_rows.py's route, env vpt2; skipped when its file exists — the comparison refuses a file of another
# level), the pyscf draft's (its worktree, WT, default ~/pyscf-wt-dfmp2grad2, on PYTHONPATH; env ~/qc215) and their comparison.
# Cases run in the order given, so a small one first is the smoke. A worktree with uncommitted changes is refused: the start line
# names the commit that makes the numbers.
# THREADS (default 8), MAXMEM_MB for pyscf's max_memory (default 8000), PSI4_GB for psi4's memory (default 8), PSIPATH_DIR for a
# basis psi4 does not ship. Markers '=== (DFG) …', a failure as '=== (DFG) FAILED: …', the end line '=== (DFG) all done'.
set -euo pipefail
OUT=${1:?out dir}
shift
mark() { echo "=== (DFG) $* $(date '+%F %T')"; }
[ "$#" -gt 0 ] || { mark "refusing to start: no case given"; exit 1; }
HERE=$(cd "$(dirname "$0")" && pwd)
PLAN=$(cd "$HERE/../.." && pwd)
WT=${WT:-$HOME/pyscf-wt-dfmp2grad2}
THREADS=${THREADS:-8}
MAXMEM_MB=${MAXMEM_MB:-8000}
PSI4_GB=${PSI4_GB:-8}
for needed in "$WT/pyscf/df/grad/mp2.py" "$HOME/qc215/bin/python" "$HOME/miniforge3/envs/vpt2/bin/python" /usr/bin/time; do
  [ -e "$needed" ] || { mark "refusing to start: $needed missing"; exit 1; }
done
COMMIT=$(git -C "$WT" rev-parse --short HEAD) || { mark "refusing to start: $WT is not a git worktree"; exit 1; }
DIRTY=$(git -C "$WT" status --short --untracked-files=no) || { mark "refusing to start: git status failed in $WT"; exit 1; }
[ -z "$DIRTY" ] || { mark "refusing to start: uncommitted changes in $WT"; exit 1; }
mkdir -p "$OUT" "$HOME/pyscf_tmp" "$HOME/psi4_scratch"
export PSI_SCRATCH=$HOME/psi4_scratch   # not /tmp: WSL clears it when idle (19 Oct 2026)
if [ -n "${PSIPATH_DIR:-}" ]; then export PSIPATH=$PSIPATH_DIR; fi
mark "start: draft at $COMMIT, $THREADS threads, pyscf max_memory $MAXMEM_MB MB, psi4 $PSI4_GB GB"

for case in "$@"; do
  IFS=: read -r name mol basis jkfit ri frozen pybasis <<< "$case"
  [ -n "$frozen" ] || { mark "FAILED: case '$case' has fewer than six fields"; exit 1; }
  geom=$PLAN/modules/05_support_predictor/corpus/molecules/$mol/geometry.json
  [ -f "$geom" ] || { mark "FAILED: $name — no geometry $geom"; exit 1; }
  if [ ! -f "$OUT/${name}_psi4.npz" ]; then
    if ! "$HOME/miniforge3/envs/vpt2/bin/python" "$HERE/psi4_grad.py" "$geom" "$basis" "$jkfit" "$ri" "$frozen" "$THREADS" "$PSI4_GB" \
        "$OUT/${name}_psi4.npz" > "$OUT/${name}_psi4.out" 2>&1; then
      mark "FAILED: $name psi4 (see $OUT/${name}_psi4.out)"
      exit 1
    fi
    tail -n 1 "$OUT/${name}_psi4.out"
  fi
  if ! PYTHONPATH=$WT OMP_NUM_THREADS=$THREADS PYSCF_TMPDIR=$HOME/pyscf_tmp /usr/bin/time -v -o "$OUT/${name}_pyscf.time" \
      "$HOME/qc215/bin/python" "$HERE/pyscf_grad.py" "$geom" "$basis" "${pybasis:-$basis}" "$jkfit" "$ri" "$frozen" "$MAXMEM_MB" \
      "$OUT/${name}_pyscf.npz" > "$OUT/${name}_pyscf.log" 2>&1; then
    mark "FAILED: $name pyscf (see $OUT/${name}_pyscf.log)"
    exit 1
  fi
  tail -n 1 "$OUT/${name}_pyscf.log"
  if ! "$HOME/qc215/bin/python" "$HERE/compare_grad.py" "$OUT/${name}_pyscf.npz" "$OUT/${name}_psi4.npz" > "$OUT/${name}_compare.txt" 2>&1; then
    mark "FAILED: $name comparison refused: $(tail -n 1 "$OUT/${name}_compare.txt")"
    exit 1
  fi
  cat "$OUT/${name}_compare.txt"
  mark "$name compared; pyscf's process peak RSS $(grep 'Maximum resident' "$OUT/${name}_pyscf.time" | awk '{print $NF}') kB"
done
mark "all done"
