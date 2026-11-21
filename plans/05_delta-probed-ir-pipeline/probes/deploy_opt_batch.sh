#!/usr/bin/env bash
# probes/deploy_opt_batch.sh <host in tools/hosts.tsv> <batch folder> (21 Nov 2026; TASKS 291) — puts one host's batch of psi4 optimisation
# jobs (`probes/corpus_opt_jobs.py` → <batch folder>/<host>/molecules/<id>/job.json and ids.txt) on a server as one batch folder of
# probes/labels_batch_ccx53.sh: optimisation at the corpus deck, then the analytic labels. The server needs miniforge with env qc05
# (tools/bootstrap_qc05_env.sh) and the psi4 env qc (tools/bootstrap_psi4_env.sh). Steps, each with its marker:
#   1. the runner files under a fresh DEST (probes/deploy_lib.sh's deploy_code: closed under their own imports, tracked and committed,
#      git archive of HEAD), DEST/COMMIT;
#   2. the host's job files and ids.txt into DEST (tar over ssh); every job's out_dir must be DEST/molecules/<id>, so a batch built for
#      another folder is refused, and the job files' sha256 are compared on both sides;
#   3. the two runner smokes from a psi4 job (deploy_lib.sh's deploy_runner_smokes … opt): water optimised and labelled under a 2048 MB cap,
#      and named killed under 64 MB.
# The run's own settings and its dry run belong to its runspec. Run from the main checkout (batch folders are not in git).
#   DEST=/root/dft1 bash probes/deploy_opt_batch.sh anc1 probes/results_m1/anchor_dft_2026-11-21
#   bash probes/deploy_opt_batch.sh --list-files
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name, or --list-files}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
CORPUS=modules/05_support_predictor/corpus
WATER=probes/results_m1/water_dipole_fd_2026-10-02/geometry.json
FILES=(probes/labels_batch_ccx53.sh probes/wsl_capped.sh probes/cation_oom_check.sh probes/library_log.py probes/smoke_job.py
       probes/large_pah_jobs.py "$CORPUS/decks/deck_v1.json" "$CORPUS/psi4_worker.py" "$CORPUS/analytic_hessians.py" "$CORPUS/apt.py"
       "$CORPUS/constants.py" "$CORPUS/grid_response_blocked.py" "$CORPUS/saddle_restarts.py" "$CORPUS/scf_policy.py"
       "$CORPUS/vibrations.py" "$WATER")
if [ "$NAME" = --list-files ]; then printf '%s\n' "${FILES[@]}"; exit 0; fi
BATCH=${2:?batch folder (relative to the plan)}
DEST=${DEST:?DEST, a fresh folder on the server}
SOURCE=$PLAN/$BATCH/$NAME
[ -f "$SOURCE/ids.txt" ] && [ -d "$SOURCE/molecules" ] || { echo "NO BATCH for $NAME under $BATCH"; exit 1; }
. "$HERE/deploy_lib.sh"
SMOKE=${DEST}_smoke

deploy_connect || exit 1
deploy_code "optimisation batch" || exit 1

echo "[$(t) $NAME] 2. the job files of $BATCH/$NAME (tar, out_dir and sha256 checked)"
mapfile -t ids < <(grep -v '^#' "$SOURCE/ids.txt" | tr -d '\r' | sed '/^$/d')
[ "${#ids[@]}" -gt 0 ] || { echo "EMPTY ids.txt for $NAME"; exit 1; }
for id in "${ids[@]}"; do
  grep -q "\"out_dir\": \"$DEST/molecules/$id\"" "$SOURCE/molecules/$id/job.json" \
    || { echo "JOB $id HAS ANOTHER out_dir — the batch was built for another folder than $DEST"; exit 1; }
done
( cd "$SOURCE" && tar cf - ids.txt molecules ) | $S "tar xf - -C $DEST" || { echo "JOB COPY FAILED"; exit 1; }
here_sum=$(cd "$SOURCE/molecules" && sha256sum "${ids[@]/%//job.json}" | sed 's/ [ *]/ /' | LC_ALL=C sort)
there_sum=$($S "cd $DEST/molecules && sha256sum ${ids[*]/%//job.json}" < /dev/null | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$here_sum" = "$there_sum" ] || { echo "JOB SHA256 MISMATCH"; exit 1; }
echo "${#ids[@]} jobs, out_dir in $DEST, sha256 equal; $DEST/ids.txt"

deploy_runner_smokes '--max-memory 1500' opt || exit 1
echo "[$(t) $NAME] DEPLOY DONE"
