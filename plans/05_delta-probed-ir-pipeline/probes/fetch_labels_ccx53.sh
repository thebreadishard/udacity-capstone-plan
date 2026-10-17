#!/bin/bash
# fetch_labels_ccx53.sh <ip> — the full fetch of the analytic-label server (rule of 3 Oct: copy everything a server made before it is deleted; delete only
# after the FETCHED line). Copies every molecule's analytic Hessians and analytic_check.json into the corpus (the FD files stay beside them), the APT
# files of the labels route (dipole_b3lyp_cphf.npz, TASKS 44 route C), the lane logs, the gate log and the environment listing into
# probes/results_m1/labels_ccx53_<date>/. Safe to re-run: a file the corpus already holds is kept (route B's ten APTs of 2 Oct, the analytic
# Hessians computed before the server).
# 17 Oct 2026: tar over ssh instead of rsync, which Git Bash does not have — the rsync version printed 'RSYNC … FAILED', exited 0 and still
# wrote a FETCHED line with 44 of 538 Hessians, so chain 35h trained its 'analytic' arm on FD labels. Now every copy is checked, and the FETCHED
# line appears only when every analytic Hessian and APT on the server is in the corpus; otherwise 'NOT FETCHED: …' and exit 1. A complete
# copy while label lanes still run is a 'SNAPSHOT' (exit 0): FETCHED means the server may be deleted, and a running server may not.
#   bash probes/fetch_labels_ccx53.sh <ip>
# Overridable for tests: P (plan folder), REMOTE (the server's labels folder), KEY, ENV_CMD (the environment listing), LANES_CMD (counts running lanes).
set -u
# no-set-e: every step's failure is collected and reported; the exit code says whether the fetch is complete
IP=${1:?server ip}
KEY=${KEY:-$HOME/.ssh/hetzner_g_measure}
P=${P:-/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline}
REMOTE=${REMOTE:-/root/labels}
ENV_CMD=${ENV_CMD:-/root/miniforge3/envs/qc05/bin/pip freeze; uname -a; nproc; free -g | head -2}
LANES_CMD=${LANES_CMD:-pgrep -fc '[l]abels_lane'}
C=$P/modules/05_support_predictor/corpus
D=$P/probes/results_m1/labels_ccx53_$(date +%F)
SSH=(ssh -i "$KEY" -o BatchMode=yes -o ConnectTimeout=25 "root@$IP")
mkdir -p "$D" "$C/molecules"
failed=()

# copy <label> <destination> <remote shell command that writes a tar stream>; a failure on either side of the pipe is recorded
copy() {
  "${SSH[@]}" "$3" | tar xf - --skip-old-files -C "$2"
  local rc=("${PIPESTATUS[@]}")
  [ "${rc[0]}" = 0 ] && [ "${rc[1]}" = 0 ] || failed+=("$1 (ssh ${rc[0]}, tar ${rc[1]})")
}

echo "[$(date '+%T')] analytic Hessians and APTs → corpus"
copy "Hessians" "$C/molecules" "cd $REMOTE/molecules && find . -mindepth 2 -maxdepth 2 \\( -name hessian_b3lyp_analytic.npz -o -name hessian_wb97x_analytic.npz -o -name analytic_check.json -o -name dipole_b3lyp_cphf.npz \\) -print0 | tar cf - --null -T -"
echo "[$(date '+%T')] logs, gate, environment → $D"
copy "logs" "$D" "cd $REMOTE && find . -maxdepth 1 \\( -name '*.log' -o -name '*.txt' \\) -print0 | tar cf - --null -T - \$(test -d gate && echo gate)"
"${SSH[@]}" "$ENV_CMD" > "$D/environment.txt" 2>&1 || failed+=("environment")

# completeness: every file of these kinds on the server must be in the corpus
srv_list=$("${SSH[@]}" "cd $REMOTE/molecules && ls */hessian_wb97x_analytic.npz */hessian_b3lyp_analytic.npz */dipole_b3lyp_cphf.npz 2>/dev/null") || failed+=("server listing")
missing=0
while read -r f; do
  [ -z "$f" ] && continue
  [ -f "$C/molecules/$f" ] || missing=$((missing + 1))
done <<< "$srv_list"
n_srv_w=$(grep -c 'hessian_wb97x_analytic' <<< "$srv_list"); n_srv_a=$(grep -c 'dipole_b3lyp_cphf' <<< "$srv_list")
n_w=$(find "$C/molecules" -mindepth 2 -maxdepth 2 -name hessian_wb97x_analytic.npz | wc -l)
n_b=$(find "$C/molecules" -mindepth 2 -maxdepth 2 -name hessian_b3lyp_analytic.npz | wc -l)
n_a=$(find "$C/molecules" -mindepth 2 -maxdepth 2 -name dipole_b3lyp_cphf.npz | wc -l)
[ "$missing" -gt 0 ] && failed+=("$missing server files not in the corpus")
[ "$n_srv_w" -gt 0 ] || failed+=("the server lists no analytic Hessian")

counts="corpus holds $n_w analytic ωB97X and $n_b analytic B3LYP Hessians (server $n_srv_w ωB97X), $n_a APTs (server $n_srv_a); logs in $D"
if [ "${#failed[@]}" -gt 0 ]; then
  echo "NOT FETCHED $(date '+%F %H:%M') $IP: $(IFS='; '; echo "${failed[*]}") — $counts"
  exit 1
fi
lanes=$("${SSH[@]}" "$LANES_CMD" 2>/dev/null)
if [ "${lanes:-0}" != "0" ]; then
  echo "SNAPSHOT $(date '+%F %H:%M') $IP: complete copy, but $lanes label lanes still run — not the final fetch; $counts"
  exit 0
fi
echo "FETCHED $(date '+%F %H:%M') $IP: $counts"
