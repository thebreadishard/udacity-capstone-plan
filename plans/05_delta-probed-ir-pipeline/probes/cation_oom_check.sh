#!/usr/bin/env bash
# probes/cation_oom_check.sh <molecule id> (19 Oct 2026; 25 Oct 2026) — exit 0 when the systemd scope that ran this molecule under
# probes/wsl_capped.sh was OOM-killed, 1 when it was not, 2 when no such scope is in the journal. The kernel's OOM killer sends SIGKILL to
# the process at the cap and systemd then stops the rest of the scope with SIGTERM, so the command's exit code is 143 ('Terminated'), not
# 137: the scope's journal is the reliable sign (P3c_0f27b44587, 19 Oct 12:11:51).
# 25 Oct 2026 (TASKS 122): fluoranthene⁺ was killed at 08:39:48 and systemd wrote "Failed with result 'oom-kill'" at 08:39:49 — one second
# after this check had read the journal and answered 'not an oom-kill'. Now the kernel's own line ("The kernel OOM killer killed some
# processes in this unit", written with the kill) counts too, and the check waits up to OOM_WAIT seconds for the scope's final result.
#   OOM_TAG      the marker in the /usr/bin/time format that names the molecule (default CA: '(CA) <id> max RSS'; the CCX53 run uses CX)
#   OOM_JOURNAL  --user (default; the WSL runs' user scopes) or 'system' (a root run's system scopes on a server)
#   OOM_WAIT     seconds to wait for the scope's result (default 20)
set -u
# no-set-e: grep's no-match is an answer here (exit 1 or 2), not an error
ID=${1:?molecule id}
TAG=${OOM_TAG:-CA}
WAIT=${OOM_WAIT:-20}
case "${OOM_JOURNAL:---user}" in
  --user) J=(journalctl --user -o cat --no-pager) ;;
  system) J=(journalctl -o cat --no-pager) ;;
  *) echo "OOM_JOURNAL must be --user or system, not '${OOM_JOURNAL}'"; exit 2 ;;
esac
unit=$("${J[@]}" 2>/dev/null | grep -F "($TAG) $ID max RSS" | grep -o 'run-[a-z0-9-]*\.scope' | tail -n 1)
[ -n "$unit" ] || { echo "no scope found for $ID in the journal"; exit 2; }
for _ in $(seq 0 "$WAIT"); do
  log=$("${J[@]}" -u "$unit" 2>/dev/null)
  if echo "$log" | grep -q -e "Failed with result 'oom-kill'" -e "The kernel OOM killer killed some processes in this unit"; then
    echo "$unit: oom-kill"
    exit 0
  fi
  echo "$log" | grep -q -e "Failed with result" -e "Deactivated successfully" -e "Consumed .* CPU time" && break
  sleep 1
done
echo "$unit: not an oom-kill"
exit 1
