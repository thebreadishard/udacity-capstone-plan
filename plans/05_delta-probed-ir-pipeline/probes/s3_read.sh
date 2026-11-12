#!/usr/bin/env bash
# s3_read.sh [--dry-run] — S3's registered read (probes/s3_read.py, TASKS 53) on the sets and targets relabelled with degeneracy from the
# point group and S2b's repeat on them (S3 amendment 6; probes/relabel_sets.py); markers "=== (S3R) …". The dry run checks the inputs exist and exits.
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd)
R=probes/results_m1
L=$R/labels_symmetry_2026-11-12
SETS=$L/sets.json
S2B=$L/s2b_read/s2b_read.json
TARGETS=$L/targets.json
OUT=$L/s3_read
cd "$P"
for f in "$SETS" "$S2B" "$TARGETS"; do [ -f "$f" ] || { echo "=== (S3R) STOPPED: $f missing $(date '+%F %T')"; exit 1; }; done
[ "${1:-}" = "--dry-run" ] && { echo "(S3R) dry run: inputs present"; exit 0; }
echo "=== (S3R) start $(date '+%F %T')"
PYTHONUTF8=1 PYTHONUNBUFFERED=1 python probes/s3_read.py --sets "$SETS" --s2b-read "$S2B" --targets "$TARGETS" --out "$OUT"
echo "=== (S3R) done $(date '+%F %T')"
