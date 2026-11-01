#!/usr/bin/env bash
# probes/show_batch_run.sh [--check-only] (1 Nov 2026; TASKS 146) — the pipeline show's batch: every molecule of batch.tsv (written by
# probes/show_batch_select.py: folder name, SMILES, corpus id, role, carbon count) through the pipeline with --reuse-only, so steps 2-3 come
# from the corpus and a molecule the corpus cannot give is refused, not computed. One after the other into one folder; a refused molecule is
# counted and the batch goes on. Run from modules/08_industry_synthesis by its run spec (probes/runspecs/pipeline_show_batch.json);
# --check-only passes to every pipeline call (the refusal checks alone, nothing written).
set -euo pipefail
OUT=${OUT:-../../probes/results_m1/pipeline_show_batch_2026-11-01}
CHECK=${1:-}
export CORPUS_QC_PYTHON=${CORPUS_QC_PYTHON:-C:/Users/thebr/.conda/envs/qc/python.exe} PYTHONUTF8=1
mark() { echo "=== (SHOW) $* $(date '+%F %T')"; }

[ -f "$OUT/batch.tsv" ] || { echo "no $OUT/batch.tsv: run probes/show_batch_select.py first" >&2; exit 1; }
mark "start: $(wc -l < "$OUT/batch.tsv") molecules"
done_n=0; refused_n=0
while IFS=$'\t' read -r name smiles mol_id role n_c; do
  mark "$name start ($mol_id, $role, C$n_c)"
  if python -m m08.pipeline --name "$name" --smiles "$smiles" --out "$OUT" --threads 4 --reuse-only $CHECK < /dev/null; then
    done_n=$((done_n + 1))
  else
    refused_n=$((refused_n + 1))
    mark "$name refused or failed"
  fi
done < "$OUT/batch.tsv"
mark "batch done: $done_n done, $refused_n refused or failed"
