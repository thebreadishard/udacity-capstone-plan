#!/usr/bin/env bash
# s3_read.sh [--dry-run] — S3's registered read (probes/s3_read.py, TASKS 53) on S2b's read's training sets and the targets built by
# probes/s3_read_inputs.sh; markers "=== (S3R) …". The dry run checks the inputs exist and exits.
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd)
R=probes/results_m1
SETS=$R/s2b_read_2026-11-12/sets.json
S2B=$R/s2b_read_2026-11-12/read/s2b_read.json
TARGETS=$R/s3_read_2026-11-12/targets.json
OUT=$R/s3_read_2026-11-12/read
cd "$P"
for f in "$SETS" "$S2B" "$TARGETS"; do [ -f "$f" ] || { echo "=== (S3R) STOPPED: $f missing $(date '+%F %T')"; exit 1; }; done
[ "${1:-}" = "--dry-run" ] && { echo "(S3R) dry run: inputs present"; exit 0; }
echo "=== (S3R) start $(date '+%F %T')"
PYTHONUTF8=1 PYTHONUNBUFFERED=1 python probes/s3_read.py --sets "$SETS" --s2b-read "$S2B" --targets "$TARGETS" --out "$OUT"
echo "=== (S3R) done $(date '+%F %T')"
