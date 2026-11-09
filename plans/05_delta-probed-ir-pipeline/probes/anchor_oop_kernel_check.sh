#!/usr/bin/env bash
# probes/anchor_oop_kernel_check.sh <run dir> [--dry-run] (9 Nov 2026; TASKS 184) — the deferred two-route check of the (T) kernels for
# anchor_oop_checks.sh's piece (a): e8_cc_hessian_fd.py with `--two-route-check only` recomputes <A_MOL>'s reference gradient with the
# lambda and density kernels checked against pyscf's slow routes and compares it with the stored reference.npz; a pass writes
# <run dir>/<A_MOL>_cc_tz/two_route_check.json, which anchor_oop_check.py needs before it reads the CC rows. The gradient settings are
# piece (a)'s, so the comparison is like for like. Inline, the density check passed the 12,800 MB cap (three OOM kills, TASKS 185); this
# step runs alone under a higher cap set by the caller (wsl_capped.sh) on the user's word past the laptop budget. mem_watch_wsl.sh logs
# the python's RSS every 60 s into <A_MOL>_cc_tz/kernel_check_mem.log, the measured peak for any later run of the kind.
# Lines: '=== (AOK) start | done | FAILED (exit N)'.
set -eu
RUN=${1:?run dir}; DRY=${2:-}
PY=${PY:-$HOME/qc05/bin/python}; THREADS=${THREADS:-8}; MEM=${MAX_MEMORY_MB:-10000}; A=${A_MOL:-pyridine}
HERE=$(cd "$(dirname "$0")" && pwd)
PLAN=$(dirname "$HERE")
cd "$PLAN"
DIR="$RUN/${A}_cc_tz"
for f in "$RUN/${A}_planeframe.json" "$RUN/${A}_e8_ks.txt" "$DIR/reference.npz"; do
  [ -f "$f" ] || { echo "anchor_oop_kernel_check.sh: no $f" >&2; exit 2; }
done
if grep -q $'\r' "$RUN/${A}_e8_ks.txt"; then echo "anchor_oop_kernel_check.sh: ${A}_e8_ks.txt has CR line ends" >&2; exit 2; fi
POS=$(cat "$RUN/${A}_e8_ks.txt")
[ -x "$PY" ] || { echo "anchor_oop_kernel_check.sh: no interpreter $PY" >&2; exit 2; }
if [ "$DRY" = --dry-run ]; then
  echo "dry run: $A CC/TZ reference with the kernel checks, positions $POS, $THREADS threads, max_memory $MEM MB, $PY, in $DIR"
  exit 0
fi
export OMP_NUM_THREADS=$THREADS PYSCF_TMPDIR="$HOME/qc_tmp" TMPDIR="$HOME/qc_tmp"
mkdir -p "$PYSCF_TMPDIR"
say() { echo "=== (AOK) $* $(date '+%F %T')"; }
say "start"
setsid nohup bash "$HERE/mem_watch_wsl.sh" "two-route-check only" "$DIR/kernel_check_mem.log" 60 > /dev/null 2>&1 < /dev/null &
rc=0
"$PY" -u "$HERE/e8_cc_hessian_fd.py" "$RUN/${A}_planeframe.json" "$DIR" --basis cc-pvtz --step 0.005 --threads "$THREADS" \
  --max-memory "$MEM" --symmetry --ks "$POS" --fast-t-density --fast-t-lambda --two-route-check only < /dev/null || rc=$?
if [ "$rc" = 0 ]; then say "done"; else say "FAILED (exit $rc)"; fi
exit "$rc"
