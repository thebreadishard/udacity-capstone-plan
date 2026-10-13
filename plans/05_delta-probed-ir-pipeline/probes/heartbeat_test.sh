#!/usr/bin/env bash
# probes/heartbeat_test.sh (13 Oct 2026) — the dummy job of the restart test: one line a minute to probes/watch_state/heartbeat.log until the
# file probes/watch_state/heartbeat.STOP exists, then "=== (HB) stopped". Rows HB in watch_jobs.tsv and tools/laptop_jobs.tsv while the test runs.
# no-set-e: a loop that only writes lines
cd "$(dirname "$0")/.." || exit 1
echo "=== (HB) started (pid $$) $(date '+%F %T')"
while [ ! -f probes/watch_state/heartbeat.STOP ]; do echo "beat $(date '+%F %T') pid $$"; sleep 60; done
echo "=== (HB) stopped $(date '+%F %T')"
