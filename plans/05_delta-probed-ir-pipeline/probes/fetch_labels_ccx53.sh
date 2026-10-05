#!/bin/bash
# fetch_labels_ccx53.sh <ip> — the full fetch of the analytic-label server (rule of 3 Oct: copy everything a server made before it is deleted; delete only
# after the FETCHED line). Copies every molecule's analytic Hessians and analytic_check.json into the corpus (the FD files stay beside them), the lane logs,
# the gate log and the environment listing into probes/results_m1/labels_ccx53_<date>/, then counts and prints the FETCHED line. Safe to re-run.
#   bash probes/fetch_labels_ccx53.sh <ip>
set -u
# no-set-e: the counts at the end say what arrived; a partial fetch must still report
IP=$1
KEY=~/.ssh/hetzner_g_measure
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
C=$P/modules/05_support_predictor/corpus
D=$P/probes/results_m1/labels_ccx53_$(date +%F)
mkdir -p "$D"
RS="rsync -a -e ssh -i $KEY -o BatchMode=yes"
echo "[$(date '+%T')] analytic files → corpus"
rsync -a --include='*/' --include='hessian_b3lyp_analytic.npz' --include='hessian_wb97x_analytic.npz' --include='analytic_check.json' --exclude='*' \
      -e "ssh -i $KEY -o BatchMode=yes" root@$IP:/root/labels/molecules/ "$C/molecules/" || echo "RSYNC MOLECULES FAILED"
echo "[$(date '+%T')] logs, gate, environment → $D"
rsync -a -e "ssh -i $KEY -o BatchMode=yes" --include='*.log' --include='*.txt' --exclude='*' root@$IP:/root/labels/ "$D/" || echo "RSYNC LOGS FAILED"
rsync -a -e "ssh -i $KEY -o BatchMode=yes" root@$IP:/root/labels/gate/ "$D/gate/" 2>/dev/null
ssh -i $KEY -o BatchMode=yes root@$IP '/root/miniforge3/envs/qc05/bin/pip freeze; uname -a; nproc; free -g | head -2' > "$D/environment.txt" 2>&1
n_w=$(ls "$C"/molecules/*/hessian_wb97x_analytic.npz 2>/dev/null | wc -l); n_b=$(ls "$C"/molecules/*/hessian_b3lyp_analytic.npz 2>/dev/null | wc -l)
n_srv=$(ssh -i $KEY -o BatchMode=yes root@$IP 'ls /root/labels/molecules/*/hessian_wb97x_analytic.npz 2>/dev/null | wc -l')
echo "FETCHED $(date '+%F %H:%M') $IP: corpus now holds $n_w analytic ωB97X and $n_b analytic B3LYP Hessians (server had $n_srv ωB97X); logs in $D"
