#!/usr/bin/env bash
# Launch a long probe detached from the calling session (survives the Claude Code window closing):
#   wsl -e bash -lc '/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/launch_detached.sh <logfile> <python args...>'
# Rules of Compute_Budget §3: one anchor job at a time; PYSCF_TMPDIR on the ext4 home (not /tmp); the
# log names the start time. Added 2026-09-10 after the xtight chain died with its session on 2026-09-09.
set -u
cd /mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes || exit 1
export OMP_NUM_THREADS=8 PYSCF_TMPDIR="$HOME/qc_tmp" TMPDIR="$HOME/qc_tmp"
LOG="$1"; shift
echo "=== detached start $(date): python $*" >> "$LOG"
setsid nohup "$HOME/qc05/bin/python" "$@" >> "$LOG" 2>&1 < /dev/null &
disown
sleep 2
echo "launched pid $! -> $LOG"
