#!/usr/bin/env bash
# 3 Oct 2026 (the user: "Copy alles van de server dat je nodig hebt als 'ie klaar is"): the CPX62 (ubuntu-32gb-hel1-2, the 200 of the next pool).
# Every 12 h a fetch without merge (fetch_nextpool.sh: manifests, ledgers, finished molecule folders without psi4 scratch into corpus/shards_nextpool/{a,b})
# so a dying server costs at most half a day; when the watchdog prints HEL2B DONE, a last fetch WITH merge into the local corpus, plus a tar of the two
# runners' logs, the bootstrap/env logs and a conda listing of env qc for provenance; a HEL2B FETCHED line in the alarm log. Git Bash, detached.
set -uo pipefail
# no-set-e: a failed fetch is reported and retried at the next interval
S=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
IP=46.62.227.91
KEY=$HOME/.ssh/hetzner_g_measure
SSH="ssh -i $KEY -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
R=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
ALARM=$S/hel2b_alarms.log
t() { date '+%F %T'; }

logs_fetch() {
  local D="$P/probes/results_m1/hel2b_logs_$(date +%F_%H%M)"
  mkdir -p "$D"
  $SSH "cd / && tar czf - root/*.log $R/corpus/*.log $R/corpus_b/*.log $R/corpus/ledger.csv $R/corpus_b/ledger.csv $R/corpus/manifest.csv $R/corpus_b/manifest.csv 2>/dev/null" < /dev/null > "$D/logs.tgz" 2> "$D/tar.err"
  (cd "$D" && tar xzf logs.tgz 2>/dev/null) || echo "[$(t)] HEL2B LOGS FETCH FAILED (see $D/tar.err)" >> "$ALARM"
  $SSH '/root/miniforge3/bin/conda list -n qc 2>/dev/null; echo "--- host"; hostname; nproc; free -g | head -2; uname -a' < /dev/null > "$D/environment_qc.txt" 2>&1
  echo "$D"
}

while ! grep -q "HEL2B DONE" "$ALARM" 2>/dev/null; do
  bash "$S/fetch_nextpool.sh" > "$S/fetch_nextpool_periodic.log" 2>&1 && echo "[$(t)] HEL2B periodic fetch ok: $(tail -1 "$S/fetch_nextpool_periodic.log" | cut -c1-120)" >> "$S/hel2b_fetch.log" \
    || echo "[$(t)] HEL2B PERIODIC FETCH FAILED: $(tail -2 "$S/fetch_nextpool_periodic.log" | tr '\n' ' ' | cut -c1-160)" >> "$ALARM"
  for _ in $(seq 1 48); do grep -q "HEL2B DONE" "$ALARM" 2>/dev/null && break; sleep 900; done
done
sleep 120
bash "$S/fetch_nextpool.sh" merge > "$S/fetch_nextpool_final.log" 2>&1
rc=$?
D=$(logs_fetch)
n_a=$(ls "$P/modules/05_support_predictor/corpus/shards_nextpool/a" 2>/dev/null | wc -l); n_b=$(ls "$P/modules/05_support_predictor/corpus/shards_nextpool/b" 2>/dev/null | wc -l)
if [ "$rc" = "0" ]; then
  echo "[$(t)] HEL2B FETCHED + MERGED: shards a $n_a / b $n_b entries, logs in $D; $(tail -1 "$S/fetch_nextpool_final.log" | cut -c1-140)" >> "$ALARM"
else
  echo "[$(t)] HEL2B FINAL FETCH/MERGE FAILED (exit $rc): $(tail -2 "$S/fetch_nextpool_final.log" | tr '\n' ' ' | cut -c1-200); logs in $D" >> "$ALARM"
fi
echo "[$(t)] hel2b full fetch finished"
