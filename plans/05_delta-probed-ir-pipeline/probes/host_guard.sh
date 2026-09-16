#!/usr/bin/env bash
# Host-memory guard for a detached WSL run (Compute_Budget §3). Polls the WINDOWS host's free memory
# once a minute and stops the run while the machine is still usable; the run resumes with --resume.
# Usage: host_guard.sh <logfile> <pattern matching the python job> [threshold_GB] [wait_minutes]
# 2026-09-16: written as a script after the inline version stopped the TZ cells at 0.06 GB free - a
# threshold so low that Windows itself was already starving. Default is now 2.0 GB.
set -u
LOG="$1"; PAT="$2"; THRESH="${3:-2.0}"; WAITMIN="${4:-720}"
echo "GUARD armed $(date '+%F %T'): waiting for '$PAT' (max ${WAITMIN} min), will stop it below ${THRESH} GB host free" >> "$LOG"
waited=0
while : ; do
  PID=$(wsl.exe -e bash -c "pgrep -f '$PAT'" 2>/dev/null | tr -d '\r' | head -1)
  [ -n "$PID" ] && break
  waited=$((waited+1)); [ "$waited" -ge "$WAITMIN" ] && { echo "GUARD ENDS $(date '+%F %T'): '$PAT' never appeared in ${WAITMIN} min" >> "$LOG"; exit 0; }
  sleep 60
done
echo "GUARD $(date '+%F %T'): job seen (pid $PID); guarding host memory (stop below ${THRESH} GB free)" >> "$LOG"
while : ; do
  wsl.exe -e bash -c "kill -0 $PID" 2>/dev/null || { echo "GUARD ENDS $(date '+%F %T'): the job exited on its own" >> "$LOG"; exit 0; }
  FREE=$(powershell.exe -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" 2>/dev/null | tr ',' '.' | tr -d '\r')
  case "$FREE" in ''|*[!0-9.]*) sleep 60; continue;; esac
  if awk -v f="$FREE" -v t="$THRESH" 'BEGIN{exit !(f<t)}'; then
    echo "GUARD $(date '+%F %T'): host free ${FREE} GB < ${THRESH} -> stopping pid $PID (resumable with --resume)" >> "$LOG"
    wsl.exe -e bash -c "kill -TERM $PID" 2>/dev/null
    sleep 40
    wsl.exe -e bash -c "kill -0 $PID" 2>/dev/null && wsl.exe -e bash -c "kill -KILL $PID" 2>/dev/null
    echo "GUARD ENDS $(date '+%F %T'): stopped" >> "$LOG"
    exit 0
  fi
  sleep 60
done
