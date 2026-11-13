#!/usr/bin/env bash
# s3_read.sh [--dry-run] — S3's registered read (probes/s3_read.py, TASKS 53) on the sets and targets relabelled with degeneracy from the
# point group and S2b's repeat on them (S3 amendment 6; probes/relabel_sets.py); markers "=== (S3R) …". The dry run checks the inputs exist and exits.
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd)
R=probes/results_m1
# LABELS, TARGETS and OUT default to the first read's (12 Nov); amendment 7's second read passes the relabelled root of 13 Nov.
# S2B is not derived from LABELS: both reads take their model choices from the same S2b read.
L=${LABELS:-$R/labels_symmetry_2026-11-12}
SETS=$L/sets.json
S2B=${S2B:-$R/labels_symmetry_2026-11-12/s2b_read/s2b_read.json}
TARGETS=${TARGETS:-$L/targets.json}
OUT=${OUT:-$L/s3_read}
cd "$P"
for f in "$SETS" "$S2B" "$TARGETS"; do [ -f "$f" ] || { echo "=== (S3R) STOPPED: $f missing $(date '+%F %T')"; exit 1; }; done
[ "${1:-}" = "--dry-run" ] && { echo "(S3R) dry run: inputs present"; exit 0; }
echo "=== (S3R) start $(date '+%F %T')"
MARKED=${MARKED:?set MARKED to raise, exclude or keep - what this read does with a mode outside the VPT2 domain, TASKS 207}
PYTHONUTF8=1 PYTHONUNBUFFERED=1 python probes/s3_read.py --sets "$SETS" --s2b-read "$S2B" --targets "$TARGETS" --out "$OUT" \
  --marked "$MARKED"
echo "=== (S3R) done $(date '+%F %T')"
