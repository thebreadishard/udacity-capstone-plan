#!/usr/bin/env bash
# probes/fetch_s1tz.sh MOLECULE (18 Oct 2026, TASKS 60) — the full fetch of one S1-TZ molecule from s1 once its run has ended with rc 0:
# the molecule's folder (every Hessian, the QFF report, the grid gate), its run log, exit and pid files, the server's fetched.log and the
# qc05 package list. One molecule at a time, as each finishes (the fetch-per-anchor rule), so a later server loss costs one molecule at most.
# FINAL=1 also takes the whole code folder /root/dpir_s1tz (for the last molecule). Every file is checked by sha256 against the server;
# only then "FETCHED s1tz <molecule> <n> files <bytes> bytes sha256-checked <date>" goes to the target's FETCHED.txt and to
# /root/fetched.log on the server.
#   bash probes/fetch_s1tz.sh benzene              → probes/results_m1/s1tz_2026-10-18/benzene/
#   VERIFY_ONLY=1 bash probes/fetch_s1tz.sh benzene → only the sha256 comparison and the FETCHED line, for a copy already made
set -euo pipefail
MOL=${1:?usage: fetch_s1tz.sh benzene|naphthalene|acenaphthylene}
case "$MOL" in
  benzene) WORK=s1tz ;;                     # phase 1 ran in /root/s1tz (s1tz_run.sh's first target)
  naphthalene|acenaphthylene) WORK=s1tz_$MOL ;;
  *) echo "unknown molecule '$MOL' (benzene, naphthalene, acenaphthylene)"; exit 2 ;;
esac
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
IP=$(host_ip s1)
RUN=dpir_s1tz/s1tz_$MOL
PARTS="$WORK $RUN.log $RUN.exit $RUN.pid"
[ -n "${FINAL:-}" ] && PARTS="$WORK dpir_s1tz"
DST="$HERE/results_m1/s1tz_2026-10-18/$MOL"
if [ -z "${VERIFY_ONLY:-}" ]; then
  [ -e "$DST" ] && { echo "$DST exists - refusing"; exit 1; }
  host_ssh s1 "grep -q '^=== (S2) all done' /root/$RUN.log && [ \"\$(cat /root/$RUN.exit 2>/dev/null)\" = 0 ]" \
    || { echo "s1tz $MOL not finished (no 'all done' line, or no exit 0) - not fetched"; exit 1; }
  mkdir -p "$DST/server"
  ssh -o BatchMode=yes -o ConnectTimeout=20 -i "$HOME/.ssh/hetzner_g_measure" "root@$IP" "tar -C /root -cf - $PARTS" | tar -C "$DST" -xf -
  host_ssh s1 'cat /root/fetched.log 2>/dev/null' > "$DST/server/fetched_log_at_fetch.txt"
  host_ssh s1 '/root/miniforge3/bin/conda list -n qc05' > "$DST/server/qc05_conda_list.txt"
fi
# sha256sum on Git Bash marks binary mode with '*' before the name; compare hash and name only, sorted the same way on both sides
remote=$(host_ssh s1 "cd /root && find $PARTS -type f -print0 | xargs -0 sha256sum" | sed 's/ [ *]/ /' | LC_ALL=C sort)
local=$(cd "$DST" && find $PARTS -type f -print0 | xargs -0 sha256sum | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$remote" = "$local" ] || { echo "sha256 MISMATCH between server and laptop - see $DST"; diff <(echo "$remote") <(echo "$local") | head; exit 1; }
n=$(echo "$remote" | wc -l); bytes=$(du -sb "$DST" | cut -f1)
line="FETCHED s1tz $MOL $n files $bytes bytes sha256-checked $(date '+%F %T')"
echo "$line" | tee -a "$DST/FETCHED.txt"
host_ssh s1 "echo '$line' >> /root/fetched.log"
