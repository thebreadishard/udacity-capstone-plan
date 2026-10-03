#!/usr/bin/env bash
# 3 Oct 2026 (the user: "Copy alles van de server dat je nodig hebt als 'ie klaar is"): complete copies of the CCX53's E8 directory — not the selection
# chain 33 and the benzene⁺ chain take. Fetch 1 when the anthracene watchdog prints HEL2 DONE (so nothing is lost if the server dies before benzene⁺
# finishes), fetch 2 when the benzene⁺ chain prints its HEL2C line (DONE, FAILED or NOT STARTED — every path ends with one). Each fetch: tar of
# /root/e8 (results, scripts, logs; 684 KB at 13:31, a few MB at the end), the bootstrap/env logs in /root, the gate-1 stamp, and a conda/pip listing of
# qc05 for provenance; verified by file count; a HEL2 FETCHED line in the alarm log. Reading files does not touch the running job. Git Bash, detached.
set -uo pipefail
# no-set-e: every step records its own line; a failed fetch is retried on the next trigger
S=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
IP=157.180.32.149
KEY=$HOME/.ssh/hetzner_g_measure
SSH="ssh -i $KEY -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
ALARM=$S/ccx53_alarms.log
t() { date '+%F %T'; }

fetch() {   # $1 = label
  local D="$P/probes/results_m1/ccx53_full_$(date +%F)_$1"
  mkdir -p "$D"
  $SSH 'cd /root && tar czf - e8 *.log .dpir_gate1.json 2>/dev/null' < /dev/null > "$D/e8_full.tgz" 2> "$D/tar.err"
  local sz; sz=$(stat -c %s "$D/e8_full.tgz" 2>/dev/null || echo 0)
  if [ "$sz" -lt 10000 ]; then echo "[$(t)] HEL2 FETCH FAILED ($1): archive $sz bytes, see $D/tar.err" >> "$ALARM"; return 1; fi
  (cd "$D" && tar xzf e8_full.tgz) || { echo "[$(t)] HEL2 FETCH FAILED ($1): archive does not unpack" >> "$ALARM"; return 1; }
  $SSH '/root/miniforge3/bin/conda list -n qc05 2>/dev/null; echo "--- pip"; /root/miniforge3/envs/qc05/bin/python -m pip freeze 2>/dev/null; echo "--- host"; hostname; nproc; free -g | head -2; uname -a' < /dev/null > "$D/environment_qc05.txt" 2>&1
  local n_remote n_local
  n_remote=$($SSH 'find /root/e8 -type f | wc -l' < /dev/null 2>/dev/null)
  n_local=$(find "$D/e8" -type f | wc -l)
  echo "[$(t)] HEL2 FETCHED ($1): $n_local of $n_remote files of /root/e8 in $D ($(du -sh "$D" | cut -f1))" >> "$ALARM"
  [ "$n_local" = "$n_remote" ] || echo "[$(t)] HEL2 FETCH INCOMPLETE ($1): $n_local local vs $n_remote remote" >> "$ALARM"
}

until grep -q "HEL2 DONE" "$ALARM" 2>/dev/null; do sleep 900; done
sleep 120                                                           # let chain 33's own scp finish first
fetch anthracene
until grep -qE "HEL2C (DONE|FAILED|NOT STARTED)" "$ALARM" 2>/dev/null; do sleep 900; done
sleep 120
fetch final
echo "[$(t)] ccx53 full fetch finished"
