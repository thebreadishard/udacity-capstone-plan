#!/bin/bash
# bootstrap_nextpool_1002.sh <ip> — the next pool (2 Oct 2026, the user: "Reken die 200 kandidaten maar op een CPX62"): set up the CPX62 as the layer-B
# shards were (bootstrap_shardB.sh, 25 Sep: miniforge, env qc with psi4 1.11, corpus dir without molecules, water smoke) and run the 200 ids of
# out/next_pool_candidates_2026-10-02.csv as two runners of 8 threads × 12 GB on two copies of the corpus dir (one runner per dir: corpus.lock), each with
# its cost-balanced half of the ids (scratchpad/next_pool_ids_{a,b}.txt), through tools/remote_launch.sh with a one-molecule dry run first.
set -u
# no-set-e: every step checks its own result and exits with a named failure line
IP=$1
KEY=~/.ssh/hetzner_g_measure
S="ssh -i $KEY -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
C=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
R=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor
T=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/tools
SP=/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad
t() { date '+%T'; }
echo "[$(t) $IP] system + miniforge"
$S 'export DEBIAN_FRONTEND=noninteractive; apt-get update -q > /tmp/apt.log 2>&1; apt-get install -yq tmux htop rsync >> /tmp/apt.log 2>&1; test -x /root/miniforge3/bin/conda || { curl -sL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -o /tmp/mf.sh && bash /tmp/mf.sh -b -p /root/miniforge3 > /tmp/mf.log 2>&1; }; /root/miniforge3/bin/conda --version' < /dev/null || { echo "MINIFORGE FAILED $IP"; exit 1; }
echo "[$(t) $IP] env qc (psi4 1.11, numpy, psutil, rdkit)"
$S 'test -x /root/miniforge3/envs/qc/bin/python || /root/miniforge3/bin/conda create -y -q -n qc -c conda-forge psi4=1.11 numpy psutil rdkit > /tmp/env.log 2>&1; /root/miniforge3/envs/qc/bin/python -c "import psi4, rdkit; print(\"qc ok psi4\", psi4.__version__)"' < /dev/null || { echo "ENV qc FAILED $IP"; $S 'tail -5 /tmp/env.log' < /dev/null; exit 1; }
echo "[$(t) $IP] corpus dir (scripts, manifest, decks; no molecules) — two copies"
TGZ=$SP/corpus_scripts_$IP.tgz
(cd "$C/.." && tar czf "$TGZ" --exclude='psi4.out' --exclude='worker_stdout.txt' --exclude='__pycache__' --exclude='psi.*.clean' --exclude='*.log' --exclude='corpus.lock' --exclude='molecules' --exclude='*.pre_fetch*' --exclude='*.pre_merge*' --exclude='restart_jobs_*' --exclude='rehash_layerB_proposal_*' 05_support_predictor/corpus)
scp -q -i $KEY -o BatchMode=yes "$TGZ" root@$IP:/root/corpus_scripts.tgz && $S "rm -rf $R/05_support_predictor $R/corpus $R/corpus_b; mkdir -p $R && cd $R/.. && tar xzf /root/corpus_scripts.tgz && cp -r $R/corpus $R/corpus_b && ls $R/corpus | wc -l && ls $R/corpus_b | wc -l" < /dev/null || { echo "CORPUS DIR FAILED $IP"; exit 1; }
scp -q -i $KEY -o BatchMode=yes "$SP/next_pool_ids_a.txt" "$SP/next_pool_ids_b.txt" root@$IP:/root/ || { echo "ID LISTS FAILED $IP"; exit 1; }
echo "[$(t) $IP] optking linear-bend fix (9 Oct 2026: missing on the installs after 30 Sep)"
scp -q -i $KEY -o BatchMode=yes "$C/../../probes/optking_patches/apply_optking_fix.py" root@$IP:/tmp/apply_optking_fix.py \
  && $S "/root/miniforge3/envs/qc/bin/python /tmp/apply_optking_fix.py > /dev/null && /root/miniforge3/envs/qc/bin/python /tmp/apply_optking_fix.py --check | grep -c 'already patched' | grep -qx 2" < /dev/null \
  || { echo "OPTKING FIX NOT APPLIED $IP"; exit 1; }
echo "[$(t) $IP] water smoke (psi4 worker, deck v1, 8 threads)"
$S "PY=/root/miniforge3/envs/qc/bin/python; mkdir -p /root/smoke; \$PY - <<PYEOF
import json
deck = json.load(open('$R/corpus/decks/deck_v1.json')); deck['threads'] = 8; deck['memory_gb'] = 12
job = {'id': 'smoke_water', 'layer': 'A', 'xyz_angstrom': [['O',0.0,0.0,0.1173],['H',0.0,0.7572,-0.4692],['H',0.0,-0.7572,-0.4692]], 'deck': deck, 'out_dir': '/root/smoke', 'optimise': True, 'grid_check': False}
json.dump(job, open('/root/smoke/job.json','w'))
PYEOF
cd $R/corpus && \$PY psi4_worker.py /root/smoke/job.json > /dev/null 2>&1; \$PY -c \"import json; r=json.load(open('/root/smoke/result.json')); print('smoke', r['status'], r['timings_s']['total'], 's')\"" < /dev/null 2>&1 | grep -v pydantic
$S "grep -q '\"status\": \"done\"' /root/smoke/result.json" < /dev/null || { echo "WATER SMOKE FAILED $IP"; exit 1; }
for H in a b; do
  D=$R/corpus; [ "$H" = b ] && D=$R/corpus_b
  echo "[$(t) $IP] launch runner $H in $D (dry run of one molecule first)"
  bash "$T/remote_launch.sh" root@$IP $D nextpool_$H --dry-run "--dry-run --max-molecules 1" -- "export CORPUS_QC_PYTHON=/root/miniforge3/envs/qc/bin/python; /root/miniforge3/envs/qc/bin/python run_corpus.py --ids \$(tr -d '\\n\\r' < /root/next_pool_ids_$H.txt) --threads 8 --memory-gb 12" || { echo "LAUNCH $H FAILED $IP"; exit 1; }
done
echo "[$(t) $IP] BOOTSTRAP DONE: two runners of 100 ids each"
