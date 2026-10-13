#!/usr/bin/env bash
# tools/launch_outside_app.sh <name> <workdir> <command…> (12 Oct 2026) — start a long laptop job so that it survives a relaunch of the Claude
# desktop app. A process started from the app's shell is in the app's process tree. A relaunch on 12 Oct 23:1x killed all of these:
# the five-ring runner, the cation queue script, the chain 40 and 35h runners, both APT recompute lanes in WSL, and WSL itself. `nohup … & disown`
# and `setsid` do not leave that tree.
#
# Here the command goes into a small script under probes/watch_state/launch/<name>_<timestamp>.sh (git-ignored). Windows creates it as a new process
# through WMI (Win32_Process.Create), so its parent is the WMI provider, not the app. A WSL job launched this way keeps its wsl.exe, and with it
# the WSL VM, alive. The command's own redirections decide where its output goes. Prints the new process id; exit 1 when WMI refuses.
# Since 13 Oct 2026 the job runs under conhost --headless (as the scheduled task CapstoneResumeJobs does), so it has no window: in the relaunch
# test of that evening every job of 12 Oct sat in an empty-looking Windows Terminal window, and closing such a window kills its job. The id
# printed is conhost's; the job's bash is its child.
#   bash tools/launch_outside_app.sh fivering /c/…/plans/05_delta-probed-ir-pipeline 'PRIORITY=1 bash probes/fivering_laptop_1015.sh >> probes/results_m1/fivering_laptop_2026-10-10.log 2>&1'
set -euo pipefail
NAME=${1:?name}; WORKDIR=${2:?workdir}; shift 2
CMD="$*"
[ -n "$CMD" ] || { echo "no command"; exit 1; }
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DIR="$HERE/../probes/watch_state/launch"
mkdir -p "$DIR"
SCRIPT="$DIR/${NAME}_$(date +%Y%m%d_%H%M%S).sh"   # never overwrite a wrapper a running bash may still read
{
  echo "#!/usr/bin/env bash"
  echo "# written by tools/launch_outside_app.sh $(date '+%F %T')"
  echo "# no-set-e: a generated wrapper; the command it starts carries its own error handling"
  echo "cd $(printf '%q' "$WORKDIR") || exit 1"
  echo "exec < /dev/null"
  echo "$CMD"
} > "$SCRIPT"
BASH_WIN=$(cygpath -w "$(command -v bash)")
SCRIPT_WIN=$(cygpath -w "$SCRIPT")
pid=$(powershell.exe -NoProfile -NonInteractive -Command \
  "\$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = 'conhost.exe --headless \"$BASH_WIN\" -l \"$SCRIPT_WIN\"'}; if (\$r.ReturnValue -ne 0) { exit 1 }; \$r.ProcessId" | tr -d '\r')
[ -n "$pid" ] || { echo "WMI did not start $NAME"; exit 1; }
echo "$pid"
