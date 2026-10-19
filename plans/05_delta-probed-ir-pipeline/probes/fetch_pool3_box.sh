#!/usr/bin/env bash
# probes/fetch_pool3_box.sh [date] (19 Oct 2026, TASKS 38) — the full fetch of the pool 3 box before the user deletes it (rule of 3 Oct: copy
# everything a server made; delete only after the FETCHED line): the five corpus runner folders with every psi4.out (the shard fetches of
# tools/fetch_corpus_shards.sh leave psi4 output out), the runner scripts, the smoke run, the id lists and logs in /root, the server's
# fetched.log and the conda environment listings. Refused while a psi4 or runner process still runs. Every file is checked by sha256 against
# the server; only then "FETCHED pool3 <n> files <bytes> bytes sha256-checked <date>" goes to the target's FETCHED.txt and to
# /root/fetched.log on the server.
#   bash probes/fetch_pool3_box.sh                       → probes/results_m1/pool3_box_<date>/
#   VERIFY_ONLY=1 bash probes/fetch_pool3_box.sh <date>  → only the sha256 comparison and the FETCHED line, for a copy already made
set -euo pipefail
trap 'echo "fetch_pool3_box.sh stopped at line $LINENO (exit $?) - NOT fetched" >&2' ERR
DATE=${1:-$(date +%F)}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
IP=$(host_ip pool3)
M=CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
PARTS="$M/corpus_b $M/corpus_p3 $M/corpus_p3b $M/corpus_f5a $M/corpus_f5b f5 smoke next_pool_ids_a.txt next_pool_ids_b.txt opt_log.out pool3_runner_a.sh"
DST="$HERE/results_m1/pool3_box_${DATE}"
if [ -z "${VERIFY_ONLY:-}" ]; then
  [ -e "$DST" ] && { echo "$DST exists - refusing"; exit 1; }
  # the bracket keeps this check's own remote shell out of the match
  host_ssh pool3 "! pgrep -f '[p]si4|[f]ivering_laptop|[p]ool3_runner|[r]un_corpus' > /dev/null" \
    || { echo "a psi4 or runner process still runs on pool3 - not fetched"; exit 1; }
  mkdir -p "$DST/server"
  ssh -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=30 -i "$HOME/.ssh/hetzner_g_measure" "root@$IP" "tar -C /root -czf - $PARTS" \
    | tar -C "$DST" -xzf -
  # a server that never had a fetch has no fetched.log (19 Oct: cat's exit 1 stopped the script here, silently)
  host_ssh pool3 'cat /root/fetched.log 2>/dev/null || echo "(no fetched.log on the server)"' > "$DST/server/fetched_log_at_fetch.txt"
  host_ssh pool3 'for e in $(ls /root/miniforge3/envs); do echo "### $e"; /root/miniforge3/bin/conda list -n "$e"; done' > "$DST/server/conda_lists.txt"
fi
[ -s "$DST/server/conda_lists.txt" ] || { echo "no environment listing in $DST/server - NOT fetched"; exit 1; }
# sha256sum on Git Bash marks binary mode with '*' before the name; compare hash and name only, sorted the same way on both sides
remote=$(host_ssh pool3 "cd /root && find $PARTS -type f -print0 | xargs -0 sha256sum" | sed 's/ [ *]/ /' | LC_ALL=C sort)
local=$(cd "$DST" && find $PARTS -type f -print0 | xargs -0 sha256sum | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$remote" = "$local" ] || { echo "sha256 MISMATCH between server and laptop - see $DST"; diff <(echo "$remote") <(echo "$local") | head; exit 1; }
n=$(echo "$remote" | wc -l); bytes=$(du -sb "$DST" | cut -f1)
line="FETCHED pool3 $n files $bytes bytes sha256-checked $(date '+%F %T')"
echo "$line" | tee -a "$DST/FETCHED.txt"
host_ssh pool3 "echo '$line' >> /root/fetched.log"
