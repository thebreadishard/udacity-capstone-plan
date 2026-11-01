#!/usr/bin/env bash
# probes/holdout_a_apt_run.sh [--dry-run] (1 Nov 2026; TASKS 146, the user: the clean hold-out (a) joins the pipeline show) — the eight
# molecules' APTs on the refined, residual-checked response, so that the pipeline's reuse accepts their folders: the seven 'apt' rows of ids.tsv
# through probes/apt_recompute_refined.py (their files are route B: pyscf's Krylov CPHF without a residual check), the 'hessian' row (benzene,
# A_8448043181) through analytic_hessians.py whole, B3LYP only (its Hessian file predates the charge and spin fields the reuse checks).
# In WSL with qc05; LANES lanes of THREADS threads, every step under its own cgroup cap (probes/wsl_capped.sh); a lane takes the next
# unclaimed molecule in ids.tsv's order (largest first). The corpus folders are only read: the outputs go to <dir>/<id>/, and
# probes/holdout_a_apt_install.py puts them into the corpus after the read. A molecule with its APT file is skipped (restartable); a failed
# one is logged and its lane goes on. Markers '=== (HAA) …'; each step's own output in <dir>/<id>/step.log, pyscf's in <dir>/<id>/pyscf.log.
# --dry-run: the inputs, the Python files and the seven source checks (apt_recompute_refined.py --check-only); nothing computed.
set -euo pipefail
exec 2>&1
PLAN=$(cd "$(dirname "$0")/.." && pwd)
DIR=${HAA_DIR:-$PLAN/probes/results_m1/holdout_a_apt_2026-11-01}
CORPUS=${HAA_CORPUS:-$PLAN/modules/05_support_predictor/corpus/molecules}
PY=${HAA_PYTHON:-/home/thebreadishard/qc05/bin/python}
LANES=${HAA_LANES:-2}
THREADS=${HAA_THREADS:-4}
CAP_MB=${HAA_CAP_MB:-6144}
MAX_MEMORY_MB=${HAA_MAX_MEMORY_MB:-4096}
RECOMPUTE=$PLAN/probes/apt_recompute_refined.py
HESSIANS=$PLAN/modules/05_support_predictor/corpus/analytic_hessians.py
APT=dipole_b3lyp_cphf.npz
export OMP_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS
mark() { echo "=== (HAA) $* $(date '+%F %T')"; }
rows() { grep -v '^#' "$DIR/ids.tsv" | grep -v '^$' || true; }

run_step() {   # one molecule; its exit code is returned
  local id=$1 step=$2
  mkdir -p "$DIR/$id"
  if [ "$step" = apt ]; then
    bash "$PLAN/probes/wsl_capped.sh" "$CAP_MB" -- "$PY" "$RECOMPUTE" "$CORPUS/$id" --out "$DIR" --threads "$THREADS" \
      --max-memory "$MAX_MEMORY_MB" >> "$DIR/$id/step.log" 2>&1
  else
    cp "$CORPUS/$id/geometry.json" "$DIR/$id/geometry.json"
    bash "$PLAN/probes/wsl_capped.sh" "$CAP_MB" -- "$PY" "$HESSIANS" "$DIR/$id" --functionals b3lyp --threads "$THREADS" \
      --max-memory "$MAX_MEMORY_MB" >> "$DIR/$id/step.log" 2>&1
  fi
}

lane() {
  local n=$1 id step atoms t0 rc
  while read -r id step atoms; do
    if [ -f "$DIR/$id/$APT" ]; then continue; fi
    # the claim is bash's own O_EXCL create: WSL's mkdir (uutils coreutils 0.8.0, Ubuntu 26.04) let both lanes claim in 81 of 200 trials
    if ! (set -C; : > "$DIR/claims/$id") 2> /dev/null; then continue; fi
    t0=$(date +%s)
    mark "lane $n $id start ($step, $atoms atoms)"
    rc=0
    run_step "$id" "$step" || rc=$?
    if [ "$rc" = 0 ]; then
      mark "lane $n $id done $(( $(date +%s) - t0 )) s"
    else
      mark "lane $n $id FAILED (exit $rc) after $(( $(date +%s) - t0 )) s: see $id/step.log"
    fi
  done < <(rows)
  mark "lane $n done"
}

DRY=0
case ${1:-} in --dry-run) DRY=1 ;; "") ;; *) mark "STOPPED: unknown argument $1"; exit 1 ;; esac
[ -x "$PY" ] || { mark "STOPPED: $PY missing"; exit 1; }
[ -f "$DIR/ids.tsv" ] || { mark "STOPPED: no $DIR/ids.tsv"; exit 1; }
[ -n "$(rows)" ] || { mark "STOPPED: ids.tsv lists no molecule"; exit 1; }
apt_dirs=()
while read -r id step atoms; do
  [ -f "$CORPUS/$id/geometry.json" ] || { mark "STOPPED: no geometry for $id"; exit 1; }
  case $step in
    apt) apt_dirs+=("$CORPUS/$id") ;;
    hessian) ;;
    *) mark "STOPPED: $id has step '$step' (apt or hessian)"; exit 1 ;;
  esac
done < <(rows)
"$PY" -m py_compile "$RECOMPUTE" "$HESSIANS" || { mark "STOPPED: a Python file does not compile"; exit 1; }
if [ "${#apt_dirs[@]}" -gt 0 ]; then
  "$PY" "$RECOMPUTE" "${apt_dirs[@]}" --out "$DIR" --check-only || { mark "STOPPED: a source check failed"; exit 1; }
fi
if [ "$DRY" = 1 ]; then
  mark "dry run: $(rows | wc -l) molecules (${#apt_dirs[@]} APT-only), $LANES lanes x $THREADS threads, cap $CAP_MB MB a step, inputs checked"
  exit 0
fi
rm -rf "$DIR/claims"
mkdir -p "$DIR/claims"
mark "start: $(rows | wc -l) molecules, $LANES lanes x $THREADS threads, cap $CAP_MB MB a step, pyscf max_memory $MAX_MEMORY_MB MB"
for ((n = 0; n < LANES; n++)); do lane "$n" & done
wait
written=0
while read -r id step atoms; do if [ -f "$DIR/$id/$APT" ]; then written=$((written + 1)); fi; done < <(rows)
mark "all done: $written of $(rows | wc -l) APT files written (their checks are read by probes/holdout_a_apt_install.py)"
