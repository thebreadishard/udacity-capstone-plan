#!/usr/bin/env bash
# xtb_qff_timing.sh (14 Nov 2026, TASKS 211) — how long a GFN2-xTB quartic force field takes when it is given more cores. The printed
# anharmonic step's registered model (x2*, kernel ridge on FX) carries the matched xtb mode's own shift, so an unseen molecule needs
# one of these before the pipeline can print a band, and the demo of 25 November allows the whole pipeline half an hour.
#
# The same molecule as on 19 October, B_0603418c5b, which took 53 minutes there at SHARDS=2 x OMP=2 (four cores). Here SHARDS x
# OMP_NUM_THREADS come from the environment, into a scratch root, so the S2 record is untouched. Markers "=== (XQT) …".
#   SHARDS=4 OMP_NUM_THREADS=2 bash probes/xtb_qff_timing.sh
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd)
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
ID=${ID:-B_0603418c5b}
GDIR=${GDIR:-probes/results_m1/s2_anharmonic_2026-10-18/s2/$ID/G}
OUT=${OUT:-probes/results_m1/xtb_qff_timing_2026-11-14}
SHARDS=${SHARDS:-4}
OMP_NUM_THREADS=${OMP_NUM_THREADS:-2}
say() { echo "=== (XQT) $* $(date '+%F %T')"; }

cd "$P"
[ -f "$GDIR/ref.json" ] || { say "FAILED: $GDIR/ref.json is missing, so there is no B3LYP minimum to start from"; exit 1; }
rm -rf "$OUT"
mkdir -p "$OUT"
printf '%s\t%s\n' "$ID" "$GDIR" > "$OUT/ids.tsv"

say "start: $ID on $SHARDS x $OMP_NUM_THREADS = $((SHARDS * OMP_NUM_THREADS)) cores (19 Oct: 53 min on 2 x 2)"
START=$(date +%s)
MSYS_NO_PATHCONV=1 wsl -e bash -c "cd $PW && SHARDS=$SHARDS OMP_NUM_THREADS=$OMP_NUM_THREADS \
  bash $PW/probes/xtb_anharmonic.sh $PW/$OUT/ids.tsv $PW/$OUT/xtb" || { say "FAILED: the quartic force field (exit $?)"; exit 1; }
say "done: $ID in $(( ($(date +%s) - START) / 60 )) minutes on $((SHARDS * OMP_NUM_THREADS)) cores"
