#!/usr/bin/env bash
# probes/fetch_routea_tetracene.sh (4 Nov 2026, S3/TASKS 53; the user: 'tetraceen ophalen') — copies route A's finished tetracene (its G
# folder and both logs under /root/routea) from `routea` while coronene still runs, sha256-checked against the server through
# tools/fetch_server_full.sh. NO_RECORD: a part of the run writes no FETCHED line, so the server's deletion still waits for the full fetch.
#   bash probes/fetch_routea_tetracene.sh   → probes/results_m1/routea_2026-11-02/tetracene_fetch_2026-11-04/routea/…
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
export READY="grep -q '^=== (S2) tetracene: done' /root/dpir_routea2/routea_targets.log"
export NO_RECORD=1
exec bash "$HERE/../tools/fetch_server_full.sh" routea routea_tetracene "$HERE/results_m1/routea_2026-11-02/tetracene_fetch_2026-11-04" \
  routea/tetracene routea/tetracene.log routea/tetracene.20261102-130418.log
