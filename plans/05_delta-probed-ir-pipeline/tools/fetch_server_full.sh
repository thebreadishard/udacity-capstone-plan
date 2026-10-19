#!/usr/bin/env bash
# tools/fetch_server_full.sh <host> <label> <dst> <part>… (19 Oct 2026, TASKS 79: one implementation of the full fetch that fetch_s2.sh,
# fetch_s1tz.sh, fetch_pool3_box.sh and fetch_anchors3_server.sh each repeated) — copies the parts (paths under REMOTE_ROOT on the pinned host)
# in one tar stream to <dst>, with the server's fetched.log and every conda environment's listing in <dst>/server, checks every file by sha256
# against the server, and only then writes "FETCHED <label> <n> files <bytes> bytes sha256-checked <date>" to <dst>/FETCHED.txt and to the
# server's FETCHED_LOG (the rule of 3 Oct: a server is deleted only after its FETCHED line).
#   READY='<remote command>'  required: succeeds only when the run is finished (its end marker, no process left); refused otherwise
#   VERIFY_ONLY=1             only the sha256 comparison and the FETCHED line, for a copy already made
#   NO_RECORD=1               compare only, write no FETCHED line anywhere (a re-check of an old copy)
#   REMOTE_ROOT (/root), FETCHED_LOG ($REMOTE_ROOT/fetched.log); HOSTS_FILE and HOSTS_SSH as tools/hosts.sh (tests use a local fake server)
set -euo pipefail
trap 'echo "fetch_server_full.sh stopped at line $LINENO (exit $?) - NOT fetched" >&2' ERR
HOST=${1:?host} LABEL=${2:?label} DST=${3:?destination}
shift 3
[ $# -gt 0 ] || { echo "no parts to fetch - NOT fetched"; exit 2; }
PARTS="$*"
REMOTE_ROOT=${REMOTE_ROOT:-/root}
FETCHED_LOG=${FETCHED_LOG:-$REMOTE_ROOT/fetched.log}
. "$(dirname "${BASH_SOURCE[0]}")/hosts.sh"
IP=$(host_ip "$HOST")

if [ -z "${VERIFY_ONLY:-}" ]; then
  [ -n "${READY:-}" ] || { echo "READY (the remote check that the run is finished) is not set - NOT fetched"; exit 2; }
  [ -e "$DST" ] && { echo "$DST exists - refusing"; exit 1; }
  host_ssh "$HOST" "$READY" > /dev/null || { echo "$LABEL not finished on $HOST (READY failed: $READY) - NOT fetched"; exit 1; }
  mkdir -p "$DST/server"
  # the machine-id pin was checked by host_ssh just above; the stream itself is binary, so it cannot pass through host_ssh's text capture
  $HOSTS_SSH -o ServerAliveInterval=30 "root@$IP" "tar -C $REMOTE_ROOT -czf - $PARTS" | tar -C "$DST" -xzf -
  host_ssh "$HOST" "cat $FETCHED_LOG 2>/dev/null || echo '(no fetched.log on the server)'" > "$DST/server/fetched_log_at_fetch.txt"
  host_ssh "$HOST" "for e in \$(ls $REMOTE_ROOT/miniforge3/envs); do echo \"### \$e\"; $REMOTE_ROOT/miniforge3/bin/conda list -n \"\$e\"; done" \
    > "$DST/server/conda_lists.txt"
fi
# copies made before 19 Oct name their single listing qc05_conda_list.txt
cat "$DST"/server/*conda*list*.txt 2>/dev/null | grep -q . || { echo "no environment listing in $DST/server - NOT fetched"; exit 1; }
# sha256sum on Git Bash marks binary mode with '*' before the name; compare hash and name only, sorted the same way on both sides
remote=$(host_ssh "$HOST" "cd $REMOTE_ROOT && find $PARTS -type f -print0 | xargs -0 sha256sum" | sed 's/ [ *]/ /' | LC_ALL=C sort)
local=$(cd "$DST" && find $PARTS -type f -print0 | xargs -0 sha256sum | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ -n "$remote" ] || { echo "the server lists no file of $PARTS - NOT fetched"; exit 1; }
[ "$remote" = "$local" ] || { echo "sha256 MISMATCH between server and laptop - see $DST"; diff <(echo "$remote") <(echo "$local") | head; exit 1; }
n=$(echo "$remote" | wc -l); bytes=$(du -sb "$DST" | cut -f1)
if [ -n "${NO_RECORD:-}" ]; then echo "VERIFIED $LABEL $n files, sha256 equal (no FETCHED line written)"; exit 0; fi
line="FETCHED $LABEL $n files $bytes bytes sha256-checked $(date '+%F %T')"
echo "$line" | tee -a "$DST/FETCHED.txt"
host_ssh "$HOST" "echo '$line' >> $FETCHED_LOG"
