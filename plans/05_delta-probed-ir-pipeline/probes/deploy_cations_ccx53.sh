#!/usr/bin/env bash
# probes/deploy_cations_ccx53.sh <host name in tools/hosts.tsv> (25 Oct 2026; TASKS 121, the user: 'akkoord met de CCX53 na de labels') — puts
# the cation run on the labels CCX53 beside, not inside, its running label lanes: the runner files in the plan's layout under a fresh DEST
# (git archive of HEAD, closed under their own imports; /root/labels is not touched — its lanes keep running their own analytic_hessians.py),
# DEST/COMMIT, the molecule folders of the ids list from shard a (tar over ssh, psi4 and worker logs left out, each geometry.json's sha256
# compared on both sides) with the list as DEST/ids.txt, so DEST is the batch folder of probes/labels_batch_ccx53.sh, and two SMOKES of that
# runner on the server, each water⁺ (UKS doublet) as a one-molecule batch in a fresh folder, the way the run calls it:
#   1. under a system-scope cap of 2048 MB — 'labelled', with both analytic Hessians;
#   2. under a cap of 64 MB — 'KILLED at the cap' (probes/cation_oom_check.sh against the system journal, tag CX).
# The run's own settings and its dry run belong to its runspec (probes/runspecs/cations_ccx53.json). The shared steps are
# probes/deploy_lib.sh's; `--list-files` prints the file list and contacts no server. Exit 0 when both smokes passed.
#   DEST=/root/cations_c bash probes/deploy_cations_ccx53.sh labels      (from the main checkout: the shard folders are not in git)
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name, or --list-files}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
DEST=${DEST:-/root/cations}
IDS=probes/results_m1/cation_ccx53_2026-10-25/ids.tsv
SHARD=modules/05_support_predictor/corpus/shards_pool3/a/molecules
WATER=probes/results_m1/water_dipole_fd_2026-10-02/geometry.json
FILES=(probes/labels_batch_ccx53.sh probes/wsl_capped.sh probes/cation_oom_check.sh probes/library_log.py
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
$S "cp $DEST/$IDS $DEST/ids.txt" < /dev/null || { echo "IDS COPY FAILED"; exit 1; }
echo "${#ids[@]} molecule folders, geometry sha256 equal; $DEST/ids.txt"

smoke_batch() {   # $1 = batch and molecule name, $2 = cap in MB: water⁺ as a one-molecule batch through the runner, as the run calls it
  $S "mkdir -p $SMOKE/$1/molecules/$1 && cd $SMOKE/$1 && cp $DEST/$WATER molecules/$1/ && echo $1 > ids.txt && echo READY > ready.log && \
      echo '{}' > molecules/$1/job.json && echo '{\"status\": \"done\"}' > molecules/$1/result.json && \
      CODE=$DEST/modules/05_support_predictor/corpus LANES=1 THREADS=2 CAP_MB=$2 LABEL_ARGS='--charge 1 --spin 1 --max-memory 1500' \
      bash $DEST/probes/labels_batch_ccx53.sh $SMOKE/$1 CX $SMOKE/$1/ready.log READY > $SMOKE/$1/run.log 2>&1" < /dev/null
}
$S "test ! -e $SMOKE" < /dev/null || { echo "$SMOKE EXISTS — a reused smoke folder tests nothing"; exit 1; }
echo "[$(t) $NAME] 3. SMOKE 1: water⁺ through the runner under a 2048 MB system-scope cap"
smoke_batch water_plus 2048 && $S "grep -a '  water_plus labelled' $SMOKE/water_plus/run.log && \
  test -f $SMOKE/water_plus/molecules/water_plus/hessian_wb97x_analytic.npz && test -f $SMOKE/water_plus/molecules/water_plus/hessian_b3lyp_analytic.npz" \
  < /dev/null || { echo "SMOKE 1 FAILED — see $SMOKE/water_plus/run.log"; exit 1; }
echo "[$(t) $NAME] 4. SMOKE 2: the same under 64 MB must be named killed at the cap"
if smoke_batch water_kill 64; then echo "SMOKE 2 FAILED — the runner reported success under 64 MB"; exit 1; fi
$S "grep -a '  water_kill KILLED at the cap of 64 MB' $SMOKE/water_kill/run.log" < /dev/null \
  || { echo "SMOKE 2 FAILED — the kill at the cap was not named; see $SMOKE/water_kill/run.log"; exit 1; }
echo "[$(t) $NAME] DEPLOY DONE"
