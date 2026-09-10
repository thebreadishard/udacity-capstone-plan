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
PID=$!
disown
# Heartbeat (user's request 2026-09-10): every HEARTBEAT_MIN minutes (default 60) append one line with the
# elapsed time, CPU %, resident memory and the size of PYSCF_TMPDIR, so an unattended run shows it is alive
# even when the python step prints nothing for hours. The loop ends by itself when the job exits.
HB=${HEARTBEAT_MIN:-60}
(
  while kill -0 "$PID" 2>/dev/null; do
    sleep $((HB * 60))
    kill -0 "$PID" 2>/dev/null || break
    read -r ET CPU RSS < <(ps -o etime=,%cpu=,rss= -p "$PID" 2>/dev/null)
    echo "--- heartbeat $(date '+%F %T'): pid $PID alive, elapsed ${ET:-?}, cpu ${CPU:-?} %, rss $(( ${RSS:-0} / 1024 )) MB, tmp $(du -sh "$PYSCF_TMPDIR" 2>/dev/null | cut -f1)" >> "$LOG"
  done
  echo "--- heartbeat $(date '+%F %T'): pid $PID has exited" >> "$LOG"
) > /dev/null 2>&1 &
disown
sleep 2
echo "launched pid $PID -> $LOG (heartbeat every $HB min)"
