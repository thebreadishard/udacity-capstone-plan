#!/usr/bin/env bash
# probes/deploy_large_pah_ccx53.sh <host name in tools/hosts.tsv> (25 Oct 2026; TASKS 49, the user's (b): lever 5 on the labels CCX53 after
# the cations) — the ten large PAHs of lever 5 as one batch folder of probes/labels_batch_ccx53.sh, from HEAD's code (the 13 Oct runner and
# its /root/labels files are not used):
#   1. the files under a fresh DEST (git archive of HEAD, closed under their own imports), DEST/COMMIT;
#   2. the psi4 jobs made ON the server by probes/large_pah_jobs.py into DEST/molecules — a job carries its absolute out_dir, so the jobs of
#      13 Oct (pointing into /root/labels/large_pah) cannot be copied — and their ids compared with chain 42's frozen lists in the corpus and
#      with the two batch lists (the eight smaller, the two largest), which become DEST/ids_small.tsv and DEST/ids_large.tsv;
#   3. the two runner smokes from a psi4 job (probes/deploy_lib.sh's deploy_runner_smokes … opt): the optimisation step, both analytic
#      Hessians, the APT and the analytic-only result.json fields chain 42's wait reads; and the kill at a 64 MB cap named.
# The runs' settings and their dry runs belong to the runspecs (probes/runspecs/l5_small.json, l5_large.json). `--list-files` prints the
# file list and contacts no server. Exit 0 when the ids agree and both smokes passed.
#   bash probes/deploy_large_pah_ccx53.sh labels
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name, or --list-files}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
DEST=${DEST:-/root/l5b}      # /root/l5: the first deploy, its lists .txt (CRLF on checkout, refused by runspec)
RES=probes/results_m1/large_pah_ccx53_2026-10-25
CORPUS=modules/05_support_predictor/corpus
WATER=probes/results_m1/water_dipole_fd_2026-10-02/geometry.json
FILES=(probes/labels_batch_ccx53.sh probes/wsl_capped.sh probes/cation_oom_check.sh probes/library_log.py probes/smoke_job.py
       probes/large_pah_jobs.py probes/results_m1/large_labels_price_2026-10-12/selection.json "$CORPUS/decks/deck_v1.json"
       "$CORPUS/psi4_worker.py" "$CORPUS/analytic_hessians.py" "$CORPUS/apt.py" "$CORPUS/saddle_restarts.py"
       "$CORPUS/large_pah_test_ids_2026-10-12.txt" "$CORPUS/large_pah_train_ids_2026-10-12.txt" "$RES/ids_small.tsv" "$RES/ids_large.tsv" "$WATER")
if [ "$NAME" = --list-files ]; then printf '%s\n' "${FILES[@]}"; exit 0; fi
. "$HERE/deploy_lib.sh"
SMOKE=${DEST}_smoke
ids_of() { grep -hv '^#' "$@" | cut -f1 | tr -d '\r' | sed '/^$/d' | LC_ALL=C sort; }

deploy_connect || exit 1
deploy_code "lever 5" || exit 1

echo "[$(t) $NAME] 2. the psi4 jobs made on the server, their ids against chain 42's lists and the two batch lists"
$S "cd $DEST && $QC05 probes/large_pah_jobs.py $DEST/molecules" < /dev/null || { echo "JOB FILES FAILED"; exit 1; }
made=$($S "cd $DEST/molecules && grep -hv '^#' test_ids.txt train_ids.txt" < /dev/null | tr -d '\r' | LC_ALL=C sort)
frozen=$(cd "$PLAN" && ids_of "$CORPUS/large_pah_test_ids_2026-10-12.txt" "$CORPUS/large_pah_train_ids_2026-10-12.txt")
batches=$(cd "$PLAN" && ids_of "$RES/ids_small.tsv" "$RES/ids_large.tsv")
[ -n "$made" ] && [ "$made" = "$frozen" ] && [ "$made" = "$batches" ] \
  || { echo "ID MISMATCH — made: $(echo $made); chain 42: $(echo $frozen); batches: $(echo $batches)"; exit 1; }
wrong=$($S "cd $DEST/molecules && for d in */; do grep -q \"\\\"out_dir\\\": \\\"$DEST/molecules/\${d%/}\\\"\" \$d/job.json || echo \${d%/}; done" < /dev/null)
[ -z "$wrong" ] || { echo "JOBS WITH ANOTHER out_dir: $wrong"; exit 1; }
$S "cp $DEST/$RES/ids_small.tsv $DEST/$RES/ids_large.tsv $DEST/" < /dev/null || { echo "IDS COPY FAILED"; exit 1; }
echo "$(echo "$made" | wc -l) jobs, ids equal to chain 42's lists and the batches; out_dir in DEST; $DEST/ids_small.tsv, ids_large.tsv"

deploy_runner_smokes '--max-memory 1500' opt || exit 1
echo "[$(t) $NAME] DEPLOY DONE"
