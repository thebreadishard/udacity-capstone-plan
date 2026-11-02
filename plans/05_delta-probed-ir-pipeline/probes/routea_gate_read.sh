#!/usr/bin/env bash
# probes/routea_gate_read.sh (2 Nov 2026; S3 registration, 'Gate before the targets') — fetches the benzene gate's G setting from `routea`
# (ref.json, qff_report.npz/md, qff_stdout.log, images.json; NOISY if present) into probes/results_m1/routea_2026-11-02/gate/benzene/G
# and reads it with probes/routea_gate_read.py. Exit 0 on PASS, 3 on FAIL, 2 when the gate has not finished.
#   bash probes/routea_gate_read.sh
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(dirname "$HERE")
. "$PLAN/tools/hosts.sh"
IP=$(host_ip routea)
SRC=/root/routea_gate2/benzene/G
host_ssh routea "test -f $SRC/qff_report.npz" || { echo "routea_gate_read.sh: no qff_report.npz on routea yet" >&2; exit 2; }
DST=$PLAN/probes/results_m1/routea_2026-11-02/gate2/benzene/G      # the first gate's record stays under gate/ (S3 amendment 2)
mkdir -p "$DST"
for f in ref.json qff_report.npz qff_report.md qff_stdout.log images.json; do   # SFTP-mode scp expands no remote brace list
  scp -q -i "$HOME/.ssh/hetzner_g_measure" -o BatchMode=yes "root@$IP:$SRC/$f" "$DST/"
done
if host_ssh routea "test -f $SRC/NOISY"; then touch "$DST/NOISY"; fi
MSYS_NO_PATHCONV=1 wsl -e bash -c "cd \"\$(wslpath '$(cygpath -w "$PLAN")')\" && /home/thebreadishard/qc05/bin/python probes/routea_gate_read.py"
