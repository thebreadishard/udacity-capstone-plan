#!/usr/bin/env bash
# probes/fetch_s2.sh [date] (18 Oct 2026, TASKS 59/62) — the full fetch of S2 from s1 once '=== (S2) all done' stands: every molecule folder and
# log (/root/s2), the batch code and its log (/root/dpir_s2), the styrene grid check (/root/s2_gridcheck), the smoke run, the server's
# fetched.log and the qc05 package list. 3,662 files, mostly displacement JSONs, so one tar stream instead of one scp per file. Every file is
# checked by sha256 against the server; only then "FETCHED s2 <n> files <bytes> bytes sha256-checked <date>" goes to the target's FETCHED.txt
# and to /root/fetched.log on the server.
#   bash probes/fetch_s2.sh                       → probes/results_m1/s2_anharmonic_<date>/
#   VERIFY_ONLY=1 bash probes/fetch_s2.sh <date>  → only the sha256 comparison and the FETCHED line, for a copy already made
set -euo pipefail
DATE=${1:-$(date +%F)}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
IP=$(host_ip s1)
PARTS="s2 dpir_s2 s2_gridcheck s2_smoke s2_smoke_ids.tsv s2_smoke.log"
DST="$HERE/results_m1/s2_anharmonic_${DATE}"
if [ -z "${VERIFY_ONLY:-}" ]; then
  [ -e "$DST" ] && { echo "$DST exists — refusing"; exit 1; }
  # the runner's own command line (watch.sh's pattern): a bare 's2_batch' would match this very check's remote shell
  host_ssh s1 "grep -q '^=== (S2) all done' /root/dpir_s2/s2.log && ! pgrep -f '^bash (/root/dpir_s2/)?probes/s2_batch\.sh ' > /dev/null" \
    || { echo "S2 not finished (no 'all done' marker, or the batch still runs) — not fetched"; exit 1; }
  mkdir -p "$DST/server"
  ssh -o BatchMode=yes -o ConnectTimeout=20 -i "$HOME/.ssh/hetzner_g_measure" "root@$IP" "tar -C /root -cf - $PARTS" | tar -C "$DST" -xf -
  host_ssh s1 'cat /root/fetched.log 2>/dev/null' > "$DST/server/fetched_log_at_fetch.txt"
  host_ssh s1 '/root/miniforge3/bin/conda list -n qc05' > "$DST/server/qc05_conda_list.txt"
fi
# sha256sum on Git Bash marks binary mode with '*' before the name; compare hash and name only, sorted the same way on both sides
remote=$(host_ssh s1 "cd /root && find $PARTS -type f -print0 | xargs -0 sha256sum" | sed 's/ [ *]/ /' | LC_ALL=C sort)
local=$(cd "$DST" && find $PARTS -type f -print0 | xargs -0 sha256sum | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$remote" = "$local" ] || { echo "sha256 MISMATCH between server and laptop — see $DST"; diff <(echo "$remote") <(echo "$local") | head; exit 1; }
n=$(echo "$remote" | wc -l); bytes=$(du -sb "$DST" | cut -f1)
line="FETCHED s2 $n files $bytes bytes sha256-checked $(date '+%F %T')"
echo "$line" | tee -a "$DST/FETCHED.txt"
host_ssh s1 "echo '$line' >> /root/fetched.log"
