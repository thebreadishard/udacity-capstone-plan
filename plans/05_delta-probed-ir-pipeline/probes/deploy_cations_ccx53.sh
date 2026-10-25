#!/usr/bin/env bash
# probes/deploy_cations_ccx53.sh <host name in tools/hosts.tsv> (25 Oct 2026; TASKS 121, the user: 'akkoord met de CCX53 na de labels') — puts
# the cation run on the labels CCX53 beside, not inside, its running label lanes: the runner files in the plan's layout under a fresh DEST
# (git archive of HEAD, closed under their own imports; /root/labels is not touched — its lanes keep running their own analytic_hessians.py),
# DEST/COMMIT, the molecule folders of the ids list from shard a (tar over ssh, psi4 and worker logs left out, each geometry.json's sha256
# compared on both sides), and two SMOKES on the server, each in a fresh folder:
#   1. water⁺ (UKS doublet) through analytic_hessians.py under a system-scope cap of 2048 MB — both analytic Hessians must appear;
#   2. the same under a 64 MB cap — it must be killed, and probes/cation_oom_check.sh (system journal, tag CX) must call it an oom-kill.
# The shared steps are probes/deploy_lib.sh's; `--list-files` prints the file list and contacts no server. Exit 0 when both smokes passed.
#   bash probes/deploy_cations_ccx53.sh labels
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name, or --list-files}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
DEST=${DEST:-/root/cations}
IDS=probes/results_m1/cation_ccx53_2026-10-25/ids.tsv
SHARD=modules/05_support_predictor/corpus/shards_pool3/a/molecules
WATER=probes/results_m1/water_dipole_fd_2026-10-02/geometry.json
PY=/root/miniforge3/envs/qc05/bin/python
FILES=(probes/cation_ccx53.sh probes/wsl_capped.sh probes/cation_oom_check.sh probes/library_log.py
       modules/05_support_predictor/corpus/analytic_hessians.py modules/05_support_predictor/corpus/apt.py "$WATER" "$IDS")
if [ "$NAME" = --list-files ]; then printf '%s\n' "${FILES[@]}"; exit 0; fi
. "$HERE/deploy_lib.sh"
SMOKE=${DEST}_smoke

deploy_connect || exit 1
deploy_code cations || exit 1

echo "[$(t) $NAME] 2. the molecule folders of $IDS (tar, sha256 of each geometry.json on both sides)"
mapfile -t ids < <(awk -F'\t' 'NF && $1 !~ /^#/ {print $1}' "$PLAN/$IDS" | tr -d '\r')
( cd "$PLAN/$SHARD" && tar cf - --exclude=psi4.out --exclude=worker_stdout.txt "${ids[@]}" ) \
  | $S "mkdir -p $DEST/molecules && tar xf - -C $DEST/molecules" || { echo "MOLECULE COPY FAILED"; exit 1; }
here_sum=$(cd "$PLAN/$SHARD" && sha256sum "${ids[@]/%//geometry.json}" | sed 's/ [ *]/ /' | LC_ALL=C sort)
there_sum=$($S "cd $DEST/molecules && sha256sum ${ids[*]/%//geometry.json}" < /dev/null | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$here_sum" = "$there_sum" ] || { echo "GEOMETRY SHA256 MISMATCH"; exit 1; }
echo "${#ids[@]} molecule folders, geometry sha256 equal"

run_water() {   # $1 = folder name, $2 = cap in MB; the molecule runs as the cation run runs it
  $S "mkdir -p $SMOKE/$1 /root/qc_tmp && cp $DEST/$WATER $SMOKE/$1/ && cd $DEST/modules/05_support_predictor/corpus && \
      OMP_NUM_THREADS=2 PYSCF_TMPDIR=/root/qc_tmp TMPDIR=/root/qc_tmp PYTHONUNBUFFERED=1 CAP_SCOPE=system \
      bash $DEST/probes/wsl_capped.sh $2 -- /usr/bin/time -f '(CX) $1 max RSS %M kB, wall %e s' \
      $PY analytic_hessians.py $SMOKE/$1 --threads 2 --charge 1 --spin 1 --max-memory 1500 > $SMOKE/$1.log 2>&1" < /dev/null
}
echo "[$(t) $NAME] 3. SMOKE 1: water⁺ under a 2048 MB system-scope cap"
$S "test ! -e $SMOKE" < /dev/null || { echo "$SMOKE EXISTS — a reused smoke folder tests nothing"; exit 1; }
run_water water_plus 2048 && $S "test -f $SMOKE/water_plus/hessian_wb97x_analytic.npz && test -f $SMOKE/water_plus/hessian_b3lyp_analytic.npz" < /dev/null \
  || { echo "SMOKE 1 FAILED — see $SMOKE/water_plus.log"; exit 1; }
$S "grep -a '(CX) water_plus max RSS' $SMOKE/water_plus.log" < /dev/null
echo "[$(t) $NAME] 4. SMOKE 2: the same under 64 MB must be killed and named an oom-kill"
if run_water water_kill 64; then echo "SMOKE 2 FAILED — water⁺ finished under 64 MB, the cap does not bite"; exit 1; fi
$S "cd $DEST && OOM_TAG=CX OOM_JOURNAL=system bash probes/cation_oom_check.sh water_kill" < /dev/null \
  || { echo "SMOKE 2 FAILED — the kill at the cap was not recognised"; exit 1; }
$S "cd $DEST && bash probes/cation_ccx53.sh $IDS --dry-run" < /dev/null || { echo "DRY RUN FAILED"; exit 1; }
echo "[$(t) $NAME] DEPLOY DONE"
