#!/usr/bin/env bash
# probes/fetch_anchor.sh <molecule> [date] (13 Oct 2026, TASKS 43/51) — the full fetch of one finished anchor of set three from anchors3, the
# moment its APT passes, so that no anchor lives on the server only: the run folder (gradients, dipoles, Hessian, both APTs, logs), the
# molecule's geometry, the wave log so far and the server's qc05 package list. Every file is checked by sha256 against the server; the line
# "FETCHED <molecule> <n> files <bytes> sha256-checked <date>" goes to the target's FETCHED.txt and to /root/dpir/fetched.log on the server.
#   bash probes/fetch_anchor.sh quinoxaline        → probes/results_m1/e8_quinoxaline_ccpvdz_<date>/
#   VERIFY_ONLY=1 bash probes/fetch_anchor.sh quinoxaline 2026-10-13   → only the sha256 comparison and the FETCHED line, for a copy already made
set -euo pipefail
NAME=${1:?molecule}; DATE=${2:-$(date +%F)}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
IP=$(host_ip anchors3)
SRC=/root/dpir/probes/results/${NAME}_ccpvdz
DST="$HERE/results_m1/e8_${NAME}_ccpvdz_${DATE}"
if [ -z "${VERIFY_ONLY:-}" ]; then
[ -e "$DST" ] && { echo "$DST exists — refusing"; exit 1; }
# PASS, or ACCEPTED: the user's decision recorded on the server when the cross-check failed for a diagnosed cause (14 Oct 2026, azulene;
# apt_cross_check_decision.md in the run folder travels with the fetch)
host_ssh anchors3 "test -f $SRC/apt_ccsd_t_field.npz && grep -qE '=== \(AS3\) $NAME apt (PASS|ACCEPTED)' /root/dpir/anchors.log" \
  || { echo "$NAME: no passed or accepted field-route APT yet — not fetched"; exit 1; }
mkdir -p "$DST/server"
SCP="scp -q -o BatchMode=yes -o ConnectTimeout=20 -i $HOME/.ssh/hetzner_g_measure"
$SCP -r "root@$IP:$SRC/." "$DST/"
$SCP "root@$IP:/root/dpir/geoms/$NAME/geometry.json" "$DST/server/geometry.json"
$SCP "root@$IP:/root/dpir/anchors.log" "$DST/server/anchors_log_at_fetch.txt"
host_ssh anchors3 '/root/miniforge3/bin/conda list -n qc05' > "$DST/server/qc05_conda_list.txt"
fi
# sha256sum on Git Bash marks binary mode with '*' before the name; compare hash and name only, sorted the same way on both sides
remote=$(host_ssh anchors3 "cd $SRC && find . -type f -print0 | xargs -0 sha256sum" | sed 's/ [ *]/ /' | LC_ALL=C sort)
local=$(cd "$DST" && find . -path ./server -prune -o -path ./FETCHED.txt -prune -o -type f -print0 | xargs -0 sha256sum | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$remote" = "$local" ] || { echo "sha256 MISMATCH between server and laptop — see $DST"; diff <(echo "$remote") <(echo "$local") | head; exit 1; }
n=$(echo "$remote" | wc -l); bytes=$(du -sb "$DST" | cut -f1)
line="FETCHED $NAME $n files $bytes bytes sha256-checked $(date '+%F %T')"
echo "$line" | tee -a "$DST/FETCHED.txt"
host_ssh anchors3 "echo '$line' >> /root/dpir/fetched.log"
