#!/usr/bin/env bash
# probes/apt_push_refined.sh <recompute out dir> <fetched dir> (12 Oct 2026, TASKS 44 (b)) — puts the refined APT files of
# probes/apt_recompute_refined.py on the labels server in place of the unrefined route-C files they were computed from.
# Only molecules whose recompute passed (recompute.jsonl) go; on the server, per molecule, the current file must still be the very file that was
# fetched (same sha256) — else it is left alone and reported; the old file is kept in /root/labels/apt_unrefined_2026-10-12/<id>.npz; the new
# one goes in by cp to .new + mv. One line per molecule to /root/labels/install.log at the end with the counts.
# no-set-e: per-molecule outcomes are counted and reported; a failed transfer exits 1 before anything is replaced
set -u
OUT=${1:?recompute out dir}; FETCHED=${2:?fetched dir}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
IP=$(host_ip labels) || exit 4
SSH=${HOSTS_SSH:-ssh -o BatchMode=yes -o ConnectTimeout=20 -i $HOME/.ssh/hetzner_g_measure}
host_ssh labels 'mkdir -p /root/labels/apt_refined_2026-10-12 /root/labels/apt_unrefined_2026-10-12' || exit 1
ids=$(python -c "
import json, sys
seen = {}
for line in open(sys.argv[1]):
    r = json.loads(line); seen[r['id']] = r['passed']
print(' '.join(sorted(i for i, ok in seen.items() if ok)))" "$OUT/recompute.jsonl") || exit 1
[ -n "$ids" ] || { echo "no passed molecules in $OUT/recompute.jsonl"; exit 1; }
manifest=$(for id in $ids; do echo "$id $(sha256sum "$FETCHED/$id/dipole_b3lyp_cphf.npz" | cut -d' ' -f1)"; done)
# shellcheck disable=SC2086
(cd "$OUT" && tar czf - $(for id in $ids; do echo "$id/dipole_b3lyp_cphf.npz"; done)) | $SSH "root@$IP" 'tar xzf - -C /root/labels/apt_refined_2026-10-12' || { echo "TRANSFER FAILED: nothing replaced"; exit 1; }
host_ssh labels "cd /root/labels && replaced=0; kept=0; while read -r id sha; do
  cur=molecules/\$id/dipole_b3lyp_cphf.npz
  if [ \"\$(sha256sum \$cur | cut -d' ' -f1)\" != \"\$sha\" ]; then echo \"\$id CHANGED ON THE SERVER: left alone\"; kept=\$((kept + 1)); continue; fi
  [ -f apt_unrefined_2026-10-12/\$id.npz ] || cp \$cur apt_unrefined_2026-10-12/\$id.npz
  cp apt_refined_2026-10-12/\$id/dipole_b3lyp_cphf.npz \$cur.new && mv \$cur.new \$cur && replaced=\$((replaced + 1))
done <<'EOF'
$manifest
EOF
echo \"[\$(date '+%F %T')] refined APT files in place of unrefined route C (TASKS 44 b): \$replaced replaced, \$kept left alone; old files in apt_unrefined_2026-10-12/\" | tee -a install.log"
