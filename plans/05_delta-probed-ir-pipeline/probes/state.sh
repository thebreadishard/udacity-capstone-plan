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
# 20 Sep 2026: the watchers run detached inside WSL (anchor_watch_wsl.sh, e6_watch_wsl.sh); the old Windows night watch is retired
NW=$(wsl.exe -e bash -c "pgrep -fc 'watch_wsl.sh'" 2>/dev/null | tr -d '
')
echo "  WSL watchers running: ${NW:-0} (anchor, E6, and one per Helsinki job (vpt2, r0); relaunch recipe in memory 'Watchdogs in WSL')"
for w in anchor_watch e6_watch vpt2_watch r0_watch; do W=$(ls -t /c/Users/thebr/AppData/Local/Temp/claude/*/*/scratchpad/$w.log 2>/dev/null | head -1); [ -n "$W" ] && { printf "  %s last: " "$w"; tail -1 "$W" | cut -c1-120; }; done
echo "--- memory and disk ---"
printf "  host free %s GB   C: free %s GB\n" \
  "$(powershell.exe -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)" 2>/dev/null | tr -d '\r')" \
  "$(powershell.exe -NoProfile -Command "[math]::Round((Get-PSDrive C).Free/1GB,0)" 2>/dev/null | tr -d '\r')"
echo "--- monitor processes (expect 1 poller + its wrapper; 26 Sep 2026: 93 orphans found) ---"
echo "  $(ps -ef 2>/dev/null | grep -c "[m]onitor_cmd_") monitor_cmd processes; $(ps -ef 2>/dev/null | grep -c "[s]sh -i") ssh sessions"
echo "--- git ---"
echo "  $(git status --porcelain | wc -l) uncommitted paths; HEAD: $(git log --oneline -1)"
echo "--- three most recent ledger entries (first line each) ---"
sed -n '/^## 6. Log/,$p' "$LED" | grep -a '^- \*\*' | head -3 | cut -c1-140 | sed 's/^/  /'
echo "=== grep the ledger only if something above needs explaining ==="

# 20 Sep 2026: the watchers run detached inside WSL and write alarms to files (the app no longer keeps Monitors alive)
echo "--- alarm files of the detached WSL watchers (empty = healthy) ---"
for f in /c/Users/thebr/AppData/Local/Temp/claude/*/*/scratchpad/anchor_alarms.log /c/Users/thebr/AppData/Local/Temp/claude/*/*/scratchpad/e6_alarms.log /c/Users/thebr/AppData/Local/Temp/claude/*/*/scratchpad/vpt2_alarms.log /c/Users/thebr/AppData/Local/Temp/claude/*/*/scratchpad/r0_alarms.log; do [ -f "$f" ] && { printf "  %s: " "$(basename "$f")"; if [ -s "$f" ]; then tail -2 "$f" | cut -c1-140; else echo "(empty)"; fi; }; done
