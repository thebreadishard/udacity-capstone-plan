#!/bin/bash
# no-set-e: polling / diagnostic script — an empty grep or pgrep is a normal outcome and every step handles its own failure (rule of 28 Sep 2026)
# backup_loop.sh — run tools/backup_data.py once a day at 03:30 (laptop time), detached. Alarm-only: the log carries every run; nothing prints to
# stdout after the launch line. Start with:  nohup bash tools/backup_loop.sh > /dev/null 2>&1 &   (one instance; the pid file refuses a second)
# Stop by pid:  kill $(cat "$PIDFILE")
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$HOME/AppData/Local/Temp/claude/backup_loop.log"
PIDFILE="$HOME/AppData/Local/Temp/claude/backup_loop.pid"
HOUR="${BACKUP_HOUR:-03}"; MINUTE="${BACKUP_MINUTE:-30}"
mkdir -p "$(dirname "$LOG")"
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then echo "backup loop already running (pid $(cat "$PIDFILE"))"; exit 1; fi
echo $$ > "$PIDFILE"
echo "[$(date '+%F %T')] backup loop started (pid $$), daily at $HOUR:$MINUTE" >> "$LOG"
while true; do
  now=$(date +%s)
  target=$(date -d "today $HOUR:$MINUTE" +%s 2>/dev/null || date -d "$HOUR:$MINUTE" +%s)
  [ "$target" -le "$now" ] && target=$((target + 86400))
  sleep $((target - now))
  echo "[$(date '+%F %T')] backup run" >> "$LOG"
  (cd "$HERE" && PYTHONUTF8=1 python tools/backup_data.py >> "$LOG" 2>&1) || echo "[$(date '+%F %T')] BACKUP FAILED (see above)" >> "$LOG"
done
