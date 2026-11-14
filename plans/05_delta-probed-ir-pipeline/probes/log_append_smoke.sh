#!/usr/bin/env bash
# log_append_smoke.sh (14 Nov 2026, TASKS 214) — writes a run's log the way the damaged runs wrote theirs: one line from this Windows
# shell, then a long stream from inside WSL, then this shell again. That order is the point. Both sides share the redirected handle,
# and the shell's own offset is still near the start of the file while the child has written far past it, so the shell's closing lines
# can land on top of the child's first ones unless the redirect is O_APPEND.
#
# CAPPED=1 (the default) puts the child under probes/wsl_capped.sh and /usr/bin/time, as `low_mode_patch` and `label_route_vs_probe`
# had it: that adds a systemd scope and a second stream (time writes to stderr at the end), which is the arrangement both damaged logs
# came from. CAPPED=0 runs the child as a plain `wsl -e bash -c`. Markers "=== (LAS) …".
#   bash probes/log_append_smoke.sh            → 1 + 2,000 + 3 lines and the time line
#   N=50 CAPPED=0 bash probes/log_append_smoke.sh
# The checker is probes/log_append_check.py, which counts them in the log the launcher wrote.
set -euo pipefail
N=${N:-2000}
CAPPED=${CAPPED:-1}
CAP_MB=${CAP_MB:-1024}
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
say() { echo "=== (LAS) $* $(date '+%F %T')"; }
CHILD="for i in \$(seq 1 $N); do echo \"wsl \$i: a line long enough that a few hundred of them fill the first kilobytes, \
which is where the damage showed\"; done"

say "start: one line from this shell, $N from WSL (capped=$CAPPED), then this shell again"
if [ "$CAPPED" = "1" ]; then
  MSYS_NO_PATHCONV=1 wsl -e bash -c "cd $PW && bash $PW/probes/wsl_capped.sh $CAP_MB -- \
    /usr/bin/time -f '(LAS) max RSS %M kB, wall %e s' bash -c '$CHILD'"
else
  MSYS_NO_PATHCONV=1 wsl -e bash -c "$CHILD"
fi
for i in 1 2 3; do
  echo "win-after $i: written after the child, where the shell's offset and the file's end part company"
done
say "done"
