#!/usr/bin/env bash
# probes/pipeline_demo_rerun.sh [--check-only] (30 Oct 2026; TASKS 146) — the three demo molecules through the pipeline's current version, one
# after the other into one folder, so the demo page shows one version: benzene and phenanthrene (hold-out (a), then read against their corpus
# folder's ωB97X truth by probes/pipeline_vs_corpus.py) and module 06's candidate. Run from modules/08_industry_synthesis by its run spec
# (probes/runspecs/pipeline_demo_rerun.json); --check-only passes to every pipeline call and skips the truth reads.
set -euo pipefail
OUT=${OUT:-../../probes/results_m1/pipeline_demo_v04_2026-10-30}
CHECK=${1:-}
export CORPUS_QC_PYTHON=${CORPUS_QC_PYTHON:-C:/Users/thebr/.conda/envs/qc/python.exe} PYTHONUTF8=1
mark() { echo "=== (DEMO) $* $(date '+%F %T')"; }

one() {  # name smiles wsl_cap_mb
  mark "$1 start"
  python -m m08.pipeline --name "$1" --smiles "$2" --out "$OUT" --threads 6 --psi4-memory-gb 4 --wsl-cap-mb "$3" $CHECK
}

one benzene c1ccccc1 6144
one phenanthrene c1ccc2c3ccccc3ccc2c1 8192
one candidate06 'CC(OC(=O)C(F)(F)F)c1ccc(O)c2ncccc12' 8192
if [ "$CHECK" != "--check-only" ]; then
  python ../../probes/pipeline_vs_corpus.py "$OUT/benzene" A_8448043181 > /dev/null
  python ../../probes/pipeline_vs_corpus.py "$OUT/phenanthrene" A_541c53d1a5 > /dev/null
  mark "truth reads written"
fi
mark "demo rerun done"
