#!/bin/bash
# labels_half_ready.sh — exit 0 when the labels server has analytic Hessians for every molecule of its smallest-first lists with ≤ 22 atoms (the
# smallest half of the design note's amendment of 8 Oct 2026, 413 molecules); chain 35's half read waits on it (probes/runs/chain35h.json). Prints the
# counts. Reaches the server by name through tools/hosts.sh (machine-id checked). Read-only.
#   bash probes/labels_half_ready.sh
set -u
# no-set-e: an unreachable server or a missing file is a "not yet" (exit 1), never a crash
P=$(cd "$(dirname "$0")/.." && pwd)
# shellcheck source=../tools/hosts.sh
. "$P/tools/hosts.sh"
out=$(host_ssh labels 'cd /root/labels && /root/miniforge3/envs/qc05/bin/python -c "
import glob, json, os
ids = sorted({l.strip() for f in glob.glob(\"small_ids_*.txt\") for l in open(f) if l.strip()})
small = [i for i in ids if len(json.load(open(f\"molecules/{i}/geometry.json\"))[\"symbols\"]) <= 22]
done = sum(os.path.exists(f\"molecules/{i}/hessian_wb97x_analytic.npz\") and os.path.exists(f\"molecules/{i}/hessian_b3lyp_analytic.npz\") for i in small)
print(len(small), done)
"' 2>/dev/null)
n=$(echo "$out" | awk '{print $1}'); d=$(echo "$out" | awk '{print $2}')
echo "labels smallest half: ${d:-?} of ${n:-?} molecules (≤ 22 atoms) have both analytic Hessians"
[ -n "$n" ] && [ "$n" -gt 0 ] && [ "$n" = "$d" ]
