#!/usr/bin/env bash
# probes/fetch_anchors3_server.sh [date] (19 Oct 2026, TASKS 51; the 15 Nov plan: wave 2 done, full fetch, the user deletes) — the whole
# anchors3 server before deletion: /root/dpir (the run folders of every anchor of set three, the wave logs, anchors.log, the code as
# deployed) and the azulene field diagnosis in /root, the server's fetched.log and the conda listings. The per-anchor fetches
# (probes/fetch_anchor.sh) already hold the anchors; this is the rest and the record that nothing stayed behind. Refused while a python
# job runs. Every file is checked by sha256 against the server; only then "FETCHED anchors3 <n> files <bytes> bytes sha256-checked <date>"
# goes to the target's FETCHED.txt and to /root/dpir/fetched.log on the server.
#   bash probes/fetch_anchors3_server.sh                       → probes/results_m1/anchors3_server_<date>/
#   VERIFY_ONLY=1 bash probes/fetch_anchors3_server.sh <date>  → only the sha256 comparison and the FETCHED line
set -euo pipefail
trap 'echo "fetch_anchors3_server.sh stopped at line $LINENO (exit $?) - NOT fetched" >&2' ERR
DATE=${1:-$(date +%F)}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
IP=$(host_ip anchors3)
PARTS="dpir diag_azulene.cmd.sh diag_azulene.exit diag_azulene_field.py diag_azulene.log diag_azulene.pid"
DST="$HERE/results_m1/anchors3_server_${DATE}"
if [ -z "${VERIFY_ONLY:-}" ]; then
  [ -e "$DST" ] && { echo "$DST exists - refusing"; exit 1; }
  host_ssh anchors3 "! pgrep -f '[m]iniforge3/envs/.*/bin/python' > /dev/null" || { echo "a python job still runs on anchors3 - not fetched"; exit 1; }
  mkdir -p "$DST/server"
  ssh -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=30 -i "$HOME/.ssh/hetzner_g_measure" "root@$IP" "tar -C /root -czf - $PARTS" \
    | tar -C "$DST" -xzf -
  host_ssh anchors3 'cat /root/dpir/fetched.log 2>/dev/null || echo "(no fetched.log on the server)"' > "$DST/server/fetched_log_at_fetch.txt"
  host_ssh anchors3 'for e in $(ls /root/miniforge3/envs); do echo "### $e"; /root/miniforge3/bin/conda list -n "$e"; done' > "$DST/server/conda_lists.txt"
fi
[ -s "$DST/server/conda_lists.txt" ] || { echo "no environment listing in $DST/server - NOT fetched"; exit 1; }
# sha256sum on Git Bash marks binary mode with '*' before the name; compare hash and name only, sorted the same way on both sides
remote=$(host_ssh anchors3 "cd /root && find $PARTS -type f -print0 | xargs -0 sha256sum" | sed 's/ [ *]/ /' | LC_ALL=C sort)
local=$(cd "$DST" && find $PARTS -type f -print0 | xargs -0 sha256sum | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$remote" = "$local" ] || { echo "sha256 MISMATCH between server and laptop - see $DST"; diff <(echo "$remote") <(echo "$local") | head; exit 1; }
n=$(echo "$remote" | wc -l); bytes=$(du -sb "$DST" | cut -f1)
line="FETCHED anchors3 $n files $bytes bytes sha256-checked $(date '+%F %T')"
echo "$line" | tee -a "$DST/FETCHED.txt"
host_ssh anchors3 "echo '$line' >> /root/dpir/fetched.log"
