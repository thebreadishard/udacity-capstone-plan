#!/usr/bin/env bash
# reoptimise_label_settings.sh <molecule id> [--dry-run] — chain 42's rule for a large molecule with a negative mode at the label settings
# (TASKS 49): one pyscf re-optimisation at those settings (probes/reoptimise_at_label_settings.py), then both analytic Hessians and the APT
# (analytic_hessians.py) in the new folder corpus/reoptimised_2026-11-11/<id>. The corpus folder is only read; moving the new folder in is a
# separate, recorded step after the counts are read. Each step runs in WSL (qc05) under probes/wsl_capped.sh (CAP_MB) and /usr/bin/time,
# so the run spec's memory bound is the cap and the peak is measured. A finished optimisation (geometry.json present) and a saved Hessian
# (--reuse-existing) are kept on a resume. Markers "=== (RLS) …".
set -euo pipefail
ID=${1:?usage: reoptimise_label_settings.sh <molecule id> [--dry-run]}
MODE=${2:-}
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
REL_SRC=modules/05_support_predictor/corpus/molecules/$ID
REL_OUT=modules/05_support_predictor/corpus/reoptimised_2026-11-11/$ID
CAP_MB=${CAP_MB:-12288}
THREADS=${THREADS:-8}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB - 584))}   # pyscf's max_memory, below the cap (its default 20000 would plan blocks past it)
say() { echo "=== (RLS) $* $(date '+%F %T')"; }

# in_wsl <label> <python arguments>: one capped, timed qc05 python call from the plan folder
in_wsl() {
  MSYS_NO_PATHCONV=1 wsl -e bash -c "export PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1; \
    mkdir -p \$HOME/qc_tmp; cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- /usr/bin/time -f '(RLS) $1 max RSS %M kB, wall %e s' \
    \$HOME/qc05/bin/python $2"
}

[ -f "$P/$REL_SRC/geometry.json" ] || { say "STOPPED: no $REL_SRC/geometry.json"; exit 1; }
OPT_ARGS="probes/reoptimise_at_label_settings.py $PW/$REL_SRC $PW/$REL_OUT --threads $THREADS --max-memory $PYSCF_MB"
if [ "$MODE" = "--dry-run" ]; then
  if [ -f "$P/$REL_OUT/geometry.json" ]; then
    echo "dry run: $ID optimised already; analytic_hessians.py would label $REL_OUT (cap $CAP_MB MB, pyscf $PYSCF_MB MB, $THREADS threads)"
  else
    in_wsl "$ID dry run" "$OPT_ARGS --dry-run"
  fi
  exit 0
fi

say "start: $ID, cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads"
if [ -f "$P/$REL_OUT/geometry.json" ]; then
  say "optimisation kept from an earlier pass: $REL_OUT/geometry.json"
else
  say "optimisation start"
  in_wsl "$ID optimisation" "$OPT_ARGS" || { say "RUN FAILED: the optimisation of $ID (exit $?)"; exit 1; }
  say "optimisation done"
fi

say "labels start"
rc=0
in_wsl "$ID labels" "modules/05_support_predictor/corpus/analytic_hessians.py $PW/$REL_OUT --threads $THREADS --max-memory $PYSCF_MB --reuse-existing" || rc=$?
case $rc in
  0) say "labels done" ;;
  3) say "labels done, APT FAILED its checks (the Hessians are written; the registration's field route reads the intensities)" ;;
  *) say "RUN FAILED: the labels of $ID (exit $rc)"; exit 1 ;;
esac

counts=$(grep -oE '"n_imaginary_(b3lyp|wb97x)": [0-9]+' "$P/$REL_OUT/result.json" | tr '\n' ' ')
[ "$(echo "$counts" | grep -oE ': [0-9]+' | wc -l)" = 2 ] || { say "RUN FAILED: result.json lacks the two imaginary counts ($counts)"; exit 1; }
if echo "$counts" | grep -qE ': [1-9]'; then
  say "STILL IMAGINARY: $ID $counts- the registration allows one re-optimisation; the user decides"
  exit 5
fi
say "run done: $ID $counts- no imaginary mode"
