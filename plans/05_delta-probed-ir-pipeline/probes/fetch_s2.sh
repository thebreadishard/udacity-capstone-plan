#!/usr/bin/env bash
# probes/fetch_s2.sh [date] (18 Oct 2026, TASKS 59/62) — the full fetch of S2 from s1 once '=== (S2) all done' stands: every molecule folder and
# log (/root/s2), the batch code and its log (/root/dpir_s2), the styrene grid check (/root/s2_gridcheck), the smoke run, the server's
# fetched.log and the conda listings. 3,662 files, mostly displacement JSONs, in one tar stream. The copy, the sha256 check and the FETCHED
# line are tools/fetch_server_full.sh's (VERIFY_ONLY=1 and NO_RECORD=1 pass through).
#   bash probes/fetch_s2.sh                                  → probes/results_m1/s2_anharmonic_<date>/
#   VERIFY_ONLY=1 NO_RECORD=1 bash probes/fetch_s2.sh <date> → re-check an existing copy against the server, nothing written
set -euo pipefail
DATE=${1:-$(date +%F)}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# the runner's own command line (watch.sh's pattern): a bare 's2_batch' would match this very check's remote shell
export READY="grep -q '^=== (S2) all done' /root/dpir_s2/s2.log && ! pgrep -f '^bash (/root/dpir_s2/)?probes/s2_batch\.sh ' > /dev/null"
exec bash "$HERE/../tools/fetch_server_full.sh" s1 s2 "$HERE/results_m1/s2_anharmonic_${DATE}" s2 dpir_s2 s2_gridcheck s2_smoke s2_smoke_ids.tsv s2_smoke.log
