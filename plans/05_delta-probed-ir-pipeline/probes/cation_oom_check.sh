#!/usr/bin/env bash
# probes/cation_oom_check.sh <molecule id> (run inside WSL; 19 Oct 2026) — exit 0 when the systemd scope that ran this molecule under
# probes/wsl_capped.sh ended with result 'oom-kill', 1 when it did not, 2 when no such scope is in the user journal. The kernel's OOM
# killer sends SIGKILL to the process at the cap and systemd then stops the rest of the scope with SIGTERM, so the command's exit code
# is 143 ('Terminated'), not 137: the scope's own result is the reliable sign (P3c_0f27b44587, 19 Oct 12:11:51).
set -u
# no-set-e: grep's no-match is an answer here (exit 1 or 2), not an error
ID=${1:?molecule id}
unit=$(journalctl --user -o cat --no-pager 2>/dev/null | grep -F "(CA) $ID max RSS" | grep -o 'run-p[0-9]*-i[0-9]*\.scope' | tail -n 1)
[ -n "$unit" ] || { echo "no scope found for $ID in the user journal"; exit 2; }
if journalctl --user -o cat --no-pager -u "$unit" 2>/dev/null | grep -q "Failed with result 'oom-kill'"; then
  echo "$unit: oom-kill"
  exit 0
fi
echo "$unit: not an oom-kill"
exit 1
