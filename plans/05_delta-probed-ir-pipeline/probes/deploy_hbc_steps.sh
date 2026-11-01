#!/usr/bin/env bash
# probes/deploy_hbc_steps.sh <host> (1 Nov 2026, TASKS 49 steps 1-3) — ships HEAD's files for the three runs and dry-runs each on the server:
#   hbc_wb97x and d8a_relabel into the ended batch /root/l5b (deploy_code_over: code files and the two id lists; the molecules stay),
#   hbc_apt_field into a fresh /root/hbcf (deploy_code), with HBC's geometry.
# The specs (probes/runspecs/<name>.json) name the same files; runspec's launch then finds the server copies equal to the checkout.
# no-set-e: every step's result is checked and named
set -u
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
CORPUS=modules/05_support_predictor/corpus
. "$HERE/deploy_lib.sh"
deploy_connect || exit 1

DEST=/root/l5b
FILES=(probes/labels_batch_ccx53.sh probes/wsl_capped.sh probes/cation_oom_check.sh probes/library_log.py probes/run_with_mem_watch.sh
       probes/mem_watch_wsl.sh "$CORPUS/psi4_worker.py" "$CORPUS/analytic_hessians.py" "$CORPUS/apt.py"
       probes/results_m1/l5b_2026-11-01/ids_hbc.tsv probes/results_m1/l5b_2026-11-01/ids_d8a.tsv)
deploy_code_over "HBC steps 1 and 3" || exit 1
$S "cp $DEST/probes/results_m1/l5b_2026-11-01/ids_hbc.tsv $DEST/probes/results_m1/l5b_2026-11-01/ids_d8a.tsv $DEST/" < /dev/null \
  || { echo "IDS COPY FAILED"; exit 1; }

DEST=/root/hbcf
FILES=(probes/wait_then_run.sh probes/l5_apt_field_run.sh probes/apt_field_route.py probes/library_log.py probes/wsl_capped.sh
       "$CORPUS/apt.py" probes/results_m1/hbc_apt_field_2026-11-01/ids.tsv probes/results_m1/hbc_apt_field_2026-11-01/T_76dfc434db/geometry.json)
deploy_code "HBC step 2" || exit 1

echo "[$(t) $NAME] 2. the three dry runs"
L5B="CODE=/root/l5b/$CORPUS LANES=1 CAP_MB=26624"
$S "cd /root/l5b && env $L5B IDS_FILE=ids_hbc.tsv THREADS=24 LABEL_ARGS='--max-memory 100000 --reuse-existing --newton-finish' bash probes/labels_batch_ccx53.sh /root/l5b HBC /root/t74/tasks74_labels.log '^=== \\(T74\\) all done' --dry-run" < /dev/null \
  || { echo "HBC STEP 1 DRY RUN FAILED"; exit 1; }
$S "cd /root/l5b && bash probes/run_with_mem_watch.sh /tmp/none.log never molecules/D_8a1c3dddb7 /tmp/none_mem.log -- env $L5B IDS_FILE=ids_d8a.tsv THREADS=8 LABEL_ARGS='--max-memory 24000 --reuse-existing' bash probes/labels_batch_ccx53.sh /root/l5b D8A /root/t74/tasks74_labels.log '^=== \\(T74\\) all done' --dry-run" < /dev/null \
  || { echo "D STEP 3 DRY RUN FAILED"; exit 1; }
$S "cd /root/hbcf && CAP_SCOPE=system L5F_DIR=/root/hbcf/probes/results_m1/hbc_apt_field_2026-11-01 L5F_PYTHON=$QC05 bash probes/wait_then_run.sh /root/l5b/hbc_wb97x.log never -- bash probes/l5_apt_field_run.sh --dry-run" < /dev/null \
  || { echo "HBC STEP 2 DRY RUN FAILED"; exit 1; }
echo "[$(t) $NAME] deployed and dry-run: hbc_wb97x, d8a_relabel (/root/l5b), hbc_apt_field (/root/hbcf)"
