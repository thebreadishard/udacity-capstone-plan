#!/usr/bin/env bash
# bootstrap_pool3_cpx62.sh (8 Oct 2026, 03:3x) — pool 3 batch 1 (decision 54; TASKS P3-6) on the CPX62 that finished the 200 (ubuntu-32gb-hel1-2,
# 46.62.227.91). The server's corpus code predates pool 3 (run_corpus.py and psi4_worker.py differ from the laptop's; no cation deck), so batch 1 gets
# its own directory corpus_p3 beside the 200's corpus and corpus_b, which stay untouched until their full fetch (done 8 Oct 02:4x) and the user's delete.
# Steps: (1) copy the current corpus code, both decks, the manifest and ledger, and the 60 cation parents' geometry.json; (2) dry runs of both layers
# (P3c 60 cations, P3 the neutrals); (3) smoke: the water cation through cation_rows.py with the cation deck (UKS, charge 1, doublet) on 4 threads.
# Launch is separate (tools/remote_launch.sh, two runners of 8 threads × 12 GB: --layer P3c and --layer P3), only after this exits 0.
#   bash probes/bootstrap_pool3_cpx62.sh
set -euo pipefail
KEY=$HOME/.ssh/hetzner_g_measure
HOST=root@46.62.227.91
SSH=(ssh -i "$KEY" -o ConnectTimeout=25 -o BatchMode=yes -o ServerAliveInterval=30 "$HOST")
C=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/corpus
R=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/corpus_p3
PY=/root/miniforge3/envs/qc/bin/python
cd "$C"
PARENTS=$(PYTHONUTF8=1 python -c "
import csv, re
rows = [r for r in csv.DictReader(open('manifest.csv', encoding='utf-8')) if r['layer'] == 'P3c']
print(' '.join(sorted({'molecules/' + re.search(r'parent (\S+?)(?:;|$)', r['note']).group(1) + '/geometry.json' for r in rows})))")
echo "(1) copy: code, decks, manifest, ledger, $(echo "$PARENTS" | wc -w) parent geometries"
"${SSH[@]}" "test ! -e $R || { echo '$R exists — refusing to overwrite'; exit 1; }; mkdir -p $R"
# shellcheck disable=SC2086   # PARENTS is a list of paths
tar czf - run_corpus.py psi4_worker.py cation_rows.py status.py check_results.py decks manifest.csv ledger.csv $PARENTS | "${SSH[@]}" "cd $R && tar xzf - && ls | tr '\n' ' '; echo; ls molecules | wc -l"
echo "(1b) optking linear-bend fix (9 Oct 2026: missing on the installs after 30 Sep)"
scp -q -i "$KEY" -o BatchMode=yes "$C/../../../probes/optking_patches/apply_optking_fix.py" "$HOST:/tmp/apply_optking_fix.py" \
  && "${SSH[@]}" "$PY /tmp/apply_optking_fix.py > /dev/null && $PY /tmp/apply_optking_fix.py --check | grep -c 'already patched' | grep -qx 2" \
  || { echo "OPTKING FIX NOT APPLIED"; exit 1; }
echo "(2) dry runs"
"${SSH[@]}" "cd $R && export CORPUS_QC_PYTHON=$PY && $PY run_corpus.py --layer P3c --dry-run 2>&1 | tail -n 4 && $PY run_corpus.py --layer P3 --dry-run 2>&1 | tail -n 4"
echo "(3) smoke: water cation, cation deck, 4 threads"
"${SSH[@]}" "cd $R && export CORPUS_QC_PYTHON=$PY && timeout 1800 $PY cation_rows.py --smoke --out smoke_rows --worker psi4_worker.py --deck decks/deck_v1_cation.json --threads 4 --memory-gb 8 > smoke.log 2>&1; echo \"exit \$?\"; tail -n 6 smoke.log"
