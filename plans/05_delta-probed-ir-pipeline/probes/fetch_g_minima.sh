#!/usr/bin/env bash
# probes/fetch_g_minima.sh <out_dir> <host>:<remote_root> [<host>:<remote_root> …] (2 Nov 2026; S2b's and S3's GFN2-xTB force fields)
# — copies every <remote_root>/<id>/G/ref.json that exists (the G reference record at the G minimum, written once the reference Hessian is
# done) to <out_dir>/<id>/G/ref.json, skipping ids already fetched, and rewrites <out_dir>/ids.tsv (id TAB local G directory, relative to the
# plan) for probes/xtb_anharmonic.sh. Hosts are pinned by tools/hosts.sh. Prints how many were new and how many are listed.
#   bash probes/fetch_g_minima.sh probes/results_m1/s2b_xtb_2026-11-02/minima s2b1:/root/s2b s2b2:/root/s2b s2b3:/root/s2b
set -euo pipefail
OUT=${1:?out dir, relative to the plan}; shift
[ $# -ge 1 ] || { echo "fetch_g_minima.sh: name at least one <host>:<remote_root>" >&2; exit 2; }
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(dirname "$HERE")
. "$PLAN/tools/hosts.sh"
cd "$PLAN"
mkdir -p "$OUT"
new=0
for spec in "$@"; do
  host=${spec%%:*}; root=${spec#*:}
  ip=$(host_ip "$host")
  for id in $(host_ssh "$host" "cd $root 2>/dev/null && ls -d */G/ref.json 2>/dev/null | cut -d/ -f1"); do
    [ -f "$OUT/$id/G/ref.json" ] && continue
    mkdir -p "$OUT/$id/G"
    scp -q -i "$HOME/.ssh/hetzner_g_measure" -o BatchMode=yes "root@$ip:$root/$id/G/ref.json" "$OUT/$id/G/ref.json.tmp"
    mv "$OUT/$id/G/ref.json.tmp" "$OUT/$id/G/ref.json"
    new=$((new + 1))
  done
done
find "$OUT" -path '*/G/ref.json' | sort | while read -r f; do
  d=$(dirname "$f"); printf '%s\t%s\n' "$(basename "$(dirname "$d")")" "$d"
done > "$OUT/ids.tsv.tmp"
mv "$OUT/ids.tsv.tmp" "$OUT/ids.tsv"
echo "fetch_g_minima.sh: $new new, $(grep -c . "$OUT/ids.tsv" || true) listed in $OUT/ids.tsv"
