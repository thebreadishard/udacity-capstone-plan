#!/bin/bash
# pool3_runner_a.sh (8 Oct 2026) — runs ON the CPX62 (copied to /root): pool 3 batch 1, runner a in corpus_p3: the 60 cations (layer P3c, UKS deck),
# then half of the neutrals (layer P3, shard 0/2; runner b in corpus_p3b takes shard 1/2 from the start). The neutrals are 25–40 atoms (median 32),
# so the worker's wall limit is raised from 8 to 48 h for them (the 90-min stall guard stays); cations are 11–30 atoms (16 h).
# Extra arguments (e.g. --dry-run from tools/remote_launch.sh) go to both calls.
set -u
# no-set-e: a failed molecule is logged by run_corpus.py; the neutrals start whatever the cations' exit code
R=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/corpus_p3
PY=/root/miniforge3/envs/qc/bin/python
export CORPUS_QC_PYTHON=$PY
cd "$R" || exit 1
$PY run_corpus.py --layer P3c --threads 8 --memory-gb 12 --worker-max-hours 16 "$@"
echo "[$(date '+%F %T')] runner a: cations finished (exit $?); the neutrals' shard 0/2 next"
$PY run_corpus.py --layer P3 --shard 0/2 --threads 8 --memory-gb 12 --worker-max-hours 48 "$@"
