#!/usr/bin/env bash
# probes/deploy_cations_ccx53.sh <host name in tools/hosts.tsv> (25 Oct 2026; TASKS 121, the user: 'akkoord met de CCX53 na de labels') — puts
# the cation run on the labels CCX53 beside, not inside, its running label lanes: the runner files in the plan's layout under a fresh DEST
# (git archive of HEAD, closed under their own imports; /root/labels is not touched — its lanes keep running their own analytic_hessians.py),
# DEST/COMMIT, the molecule folders of the ids list from shard a (tar over ssh, psi4 and worker logs left out, each geometry.json's sha256
# compared on both sides) with the list as DEST/ids.txt, so DEST is the batch folder of probes/labels_batch_ccx53.sh, and two SMOKES of that
# runner on the server, each water⁺ (UKS doublet) as a one-molecule batch in a fresh folder, the way the run calls it:
#   1. under a system-scope cap of 2048 MB — 'labelled', with both analytic Hessians;
#   2. under a cap of 64 MB — 'KILLED at the cap' (probes/cation_oom_check.sh against the system journal).
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

deploy_runner_smokes '--charge 1 --spin 1 --max-memory 1500' || exit 1
echo "[$(t) $NAME] DEPLOY DONE"
