#!/usr/bin/env bash
# probes/anchor_oop_checks.sh <run dir> [--dry-run] (5 Nov 2026; TASKS 184, the user: 'Doe beide, met een uitzondering op decision 63') — the
# two checks of the anchors' out-of-plane block, one after the other, in the plane frame of <run dir>/<molecule>_planeframe.json, with the
# molecule's out-of-plane Cartesian indices in <molecule>_oop_ks.txt (both from cc_composite_full_check.py planeframe; the molecules are
# A_MOL=pyridine and B_MOL=benzene unless set — the water smoke sets both):
#   (a) pyridine CCSD(T)/cc-pVTZ gradients at the seven out-of-plane displacements through e8_cc_hessian_fd.py (the 4 Oct benzene settings:
#       frozen core by the element rule, step 0.005 bohr, explicit (T) lambda, both (T) C kernels); --ks takes the positions in the
#       runner's symmetry-unique list (<A_MOL>_e8_ks.txt), not Cartesian indices. e8 resumes per gradient file. The two-route check of the
#       kernels is deferred (`--two-route-check separate`): inline it needs more than the run's 12,800 MB cap (three OOM kills, 5-6 Nov,
#       TASKS 185). It runs afterwards as its own step, e8 with `--two-route-check only`, and anchor_oop_check.py refuses the rows until
#       it has passed.
#   (b) benzene MP2 rows at cc-pVTZ and cc-pVQZ for its out-of-plane displacements through cc_composite_full_check.py compute
#       (spherical, frozen core, step 0.005 bohr; --ks there is Cartesian), one file per basis and displacement, merged per basis.
# Each piece whose output exists is skipped, so a relaunch resumes. pyscf's own log: <run dir>/<A_MOL>_cc_tz/pyscf.log, <row file>.pyscf.log.
# Lines: '=== (AOC) <piece>: start | done | FAILED | already done, skipped', last '=== (AOC) all done: N of M'.
# no-set-e: a failed piece is reported and the next one runs; the last line counts them
set -u
RUN=${1:?run dir}; DRY=${2:-}
PY=${PY:-$HOME/qc05/bin/python}; THREADS=${THREADS:-8}; MEM=${MAX_MEMORY_MB:-10000}; A=${A_MOL:-pyridine}; B=${B_MOL:-benzene}
HERE=$(cd "$(dirname "$0")" && pwd)
PLAN=$(dirname "$HERE")
cd "$PLAN" || exit 2
for f in "${A}_planeframe.json" "${A}_oop_ks.txt" "${A}_e8_ks.txt" "${B}_planeframe.json" "${B}_oop_ks.txt"; do
  [ -f "$RUN/$f" ] || { echo "anchor_oop_checks.sh: no $RUN/$f" >&2; exit 2; }
  if [[ $f == *.txt ]] && grep -q $'\r' "$RUN/$f"; then echo "anchor_oop_checks.sh: $f has CR line ends" >&2; exit 2; fi
done
POS=$(cat "$RUN/${A}_e8_ks.txt")
read -r -a OOP_A < "$RUN/${A}_oop_ks.txt"
read -r -a OOP_B < "$RUN/${B}_oop_ks.txt"
[ -x "$PY" ] || { echo "anchor_oop_checks.sh: no interpreter $PY" >&2; exit 2; }
if [ "$DRY" = --dry-run ]; then
  echo "dry run: (a) $A CC/TZ positions $POS = Cartesian ${OOP_A[*]}; (b) $B MP2 TZ/QZ k ${OOP_B[*]}; $THREADS threads," \
       "max_memory $MEM MB, $PY, into $RUN"
  exit 0
fi
export OMP_NUM_THREADS=$THREADS PYSCF_TMPDIR="$HOME/qc_tmp" TMPDIR="$HOME/qc_tmp"
mkdir -p "$PYSCF_TMPDIR"
say() { echo "=== (AOC) $* $(date '+%F %T')"; }
ok=0; n=0

piece_a() {
  local dir="$RUN/${A}_cc_tz" missing=0
  for k in "${OOP_A[@]}"; do for s in p m; do [ -f "$(printf '%s/grad_%02d_%s.npy' "$dir" "$k" "$s")" ] || missing=1; done; done
  if [ "$missing" = 0 ]; then say "${A}_cc_tz: already done, skipped"; return 0; fi
  say "${A}_cc_tz: start"
  "$PY" -u "$HERE/e8_cc_hessian_fd.py" "$RUN/${A}_planeframe.json" "$dir" --basis cc-pvtz --step 0.005 --threads "$THREADS" \
    --max-memory "$MEM" --symmetry --ks "$POS" --fast-t-density --fast-t-lambda --two-route-check separate < /dev/null || return 1
  for k in "${OOP_A[@]}"; do for s in p m; do [ -f "$(printf '%s/grad_%02d_%s.npy' "$dir" "$k" "$s")" ] || return 1; done; done
}

piece_b() {
  local basis=$1 tag=$2 k f parts=()
  for k in "${OOP_B[@]}"; do
    f=$(printf '%s/mp2_rows_%s_planeframe_%s_k%02d.npz' "$RUN" "$B" "$tag" "$k")
    parts+=("$f")
    if [ -f "$f" ]; then say "${B}_mp2_${tag}_k$k: already done, skipped"; continue; fi
    say "${B}_mp2_${tag}_k$k: start"
    "$PY" -u "$HERE/cc_composite_full_check.py" compute "$RUN/${B}_planeframe.json" "$f" --basis "$basis" --threads "$THREADS" \
      --max-memory "$MEM" --ks "$k" < /dev/null || return 1
    say "${B}_mp2_${tag}_k$k: done"
  done
  "$PY" -u "$HERE/cc_composite_full_check.py" merge "$RUN/mp2_rows_${B}_planeframe_$tag.npz" "${parts[@]}" < /dev/null
}

run_piece() {
  local name=$1; shift
  n=$((n + 1))
  if "$@"; then say "$name: done"; ok=$((ok + 1)); else say "$name: FAILED"; fi
}

run_piece "${A}_cc_tz" piece_a
run_piece "${B}_mp2_tz" piece_b cc-pvtz ccpvtz
run_piece "${B}_mp2_qz" piece_b cc-pvqz ccpvqz
say "all done: $ok of $n"
