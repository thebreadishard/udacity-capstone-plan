#!/bin/bash
# Cheap project digest: answers "where do we stand" in ~30 lines, so nobody reads the ledger for it.
# Written 16 Sep 2026. Costs one tool call; the ledger alone is ~33k tokens.
cd "$(dirname "$0")/../../.." || exit 1
R=plans/05_delta-probed-ir-pipeline
LED="$R/GoalGathering/notes/Mandate_2026-09-13_Affordable_Plan_Obstacle_Ledger.md"
echo "=== $(date '+%Y-%m-%d %H:%M') ============================================"
echo "--- compute jobs (WSL) ---"
J=$(wsl.exe -e bash -c "ps -eo pid,etime,comm --sort=-etime | grep -iE 'python|psi4'" 2>/dev/null | tr -d '\r' | head -5)
[ -n "$J" ] && echo "$J" | sed 's/^/  /' || echo "  (none running)"
echo "--- heartbeats of logs touched in the last 24 h ---"
find "$R/probes" -name '*.log' -mmin -1440 2>/dev/null | while read -r f; do
  h=$(grep -a 'heartbeat' "$f" | tail -1)
  [ -n "$h" ] && printf "  %-42s %s\n" "$(basename "$f")" "${h#--- }"
done
echo "--- guards and watchdogs ---"
for g in $(find "$R/probes" -name 'host_guard*.log' -mmin -1440 2>/dev/null); do
  echo "  $(basename "$g"): $(tail -1 "$g")"
done
[ "$(ps -ef | grep -c "[n]ight_watch.sh")" -gt 0 ] && echo "  night watch: running" || echo "  night watch: NOT RUNNING (re-arm it before an unattended stretch)"
W=$(ls -t /c/Users/thebr/AppData/Local/Temp/claude/*/*/scratchpad/night_watch.log 2>/dev/null | head -1)
[ -n "$W" ] && { echo "  night watch log ($(wc -l < "$W") lines), last:"; tail -1 "$W" | sed 's/^/    /'; }
echo "--- memory and disk ---"
printf "  host free %s GB   C: free %s GB\n" \
  "$(powershell.exe -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)" 2>/dev/null | tr -d '\r')" \
  "$(powershell.exe -NoProfile -Command "[math]::Round((Get-PSDrive C).Free/1GB,0)" 2>/dev/null | tr -d '\r')"
echo "--- git ---"
echo "  $(git status --porcelain | wc -l) uncommitted paths; HEAD: $(git log --oneline -1)"
echo "--- three most recent ledger entries (first line each) ---"
sed -n '/^## 6. Log/,$p' "$LED" | grep -a '^- \*\*' | head -3 | cut -c1-140 | sed 's/^/  /'
echo "=== grep the ledger only if something above needs explaining ==="
