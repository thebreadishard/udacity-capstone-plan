#!/usr/bin/env bash
# probes/run_in_scope.sh <unit> <cap_MB> <budget_s> <kill_after_s> -- command …      (16 Nov 2026, TASKS 211)
# probes/run_in_scope.sh --check
# Runs the command inside WSL in a systemd user scope of the caller's own name, with a memory cap and a time budget, and
# guarantees that nothing of it is left when it returns. The scope is what makes that a matter of ownership: every process the
# command starts is in the unit's cgroup, whatever its name, its session or the signals it ignores, and the unit is asked.
#
# The systemd-run call mirrors probes/wsl_capped.sh's (--user --scope --quiet -p MemoryMax=<cap>M -p MemorySwapMax=0) and adds
# --unit; that file is not used here, because its scope has a name only systemd knows.
# The budget: `timeout --kill-after=<kill_after_s> <budget_s>` sends SIGTERM to the process group, then SIGKILL to its child. Here
# timeout is uutils coreutils 0.10.0, and on this WSL (16 Nov 2026) a grandchild that ignored SIGTERM outlived both. So after
# the command, whatever its exit, the unit's cgroup is read: processes still in it get `systemctl --user kill --signal=KILL`
# on the unit, the cgroup is read again, and survivors are an error (exit 70), never a silence.
# Exit: the command's own code; 124 when the budget was reached (also where the exit itself was a kill's, by the clock);
# 137 / 143 with the line 'KILLED: over the cap …' as wsl_capped.sh prints it; 70 when processes survive; 2 on a usage error or
# where no systemd user scope can be made ('--check' asks only that, and exits 0 or 2).
# Markers '=== (SCOPE) …'. SCOPE_UNIT is exported for the command (probes/xtb_field_for_step.sh reads its own scope's peak memory).
set -u
# no-set-e: the command's exit code is read and reported
can_scope() { command -v systemd-run > /dev/null && command -v systemctl > /dev/null && systemd-run --user --scope --quiet true 2> /dev/null; }
if [ "${1:-}" = --check ]; then
  can_scope || { echo "run_in_scope.sh: no systemd user scope can be made here (systemd-run --user --scope), so no run can be owned and stopped"; exit 2; }
  exit 0
fi
UNIT=${1:?unit name}; CAP=${2:?cap in MB}; BUDGET=${3:?budget in s}; GRACE=${4:?seconds between SIGTERM and SIGKILL}; shift 4
[ "${1:-}" = "--" ] && shift
[ "$#" -gt 0 ] || { echo "run_in_scope.sh: no command"; exit 2; }
for n in "$CAP" "$BUDGET" "$GRACE"; do
  case "$n" in ''|*[!0-9]*) echo "run_in_scope.sh: '$n' is not a whole number"; exit 2 ;; esac
done
case "$UNIT" in ''|*[!A-Za-z0-9_.-]*) echo "run_in_scope.sh: unit name '$UNIT' has characters outside A-Z a-z 0-9 _ . -"; exit 2 ;; esac
can_scope || { echo "run_in_scope.sh: no systemd user scope can be made here - not run"; exit 2; }

left() {   # the number of processes in the unit's cgroup; 0 when the unit is gone
  local cg
  cg=$(systemctl --user show "$UNIT.scope" -p ControlGroup --value 2> /dev/null)
  if [ -n "$cg" ] && [ -r "/sys/fs/cgroup$cg/cgroup.procs" ]; then wc -l < "/sys/fs/cgroup$cg/cgroup.procs" 2> /dev/null || echo 0; else echo 0; fi
}

export SCOPE_UNIT=$UNIT
START=$(date +%s)
timeout --kill-after="$GRACE" "$BUDGET" \
  systemd-run --user --scope --quiet --unit "$UNIT" -p MemoryMax="${CAP}M" -p MemorySwapMax=0 "$@"
rc=$?
ELAPSED=$(( $(date +%s) - START ))

n=$(left)
if [ "$n" -gt 0 ]; then
  systemctl --user kill --signal=KILL "$UNIT.scope" 2> /dev/null
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    [ "$(left)" -eq 0 ] && break
    sleep 0.5
  done
  if [ "$(left)" -gt 0 ]; then
    echo "=== (SCOPE) FAILED: $(left) process(es) of $UNIT survive SIGKILL on the unit $(date '+%F %T')"
    exit 70
  fi
  echo "=== (SCOPE) $n process(es) left in $UNIT were killed; none is left $(date '+%F %T')"
fi
systemctl --user reset-failed "$UNIT.scope" 2> /dev/null

if [ "$rc" -eq 124 ] || { [ "$ELAPSED" -ge "$BUDGET" ] && { [ "$rc" -eq 137 ] || [ "$rc" -eq 143 ]; }; }; then
  echo "=== (SCOPE) stopped at the budget of $BUDGET s (exit $rc after $ELAPSED s) $(date '+%F %T')"
  exit 124
fi
case "$rc" in
  137|143) echo "KILLED: over the cap of $CAP MB, or stopped from outside: journalctl -b | grep -E 'oom-kill|Killed process' tells which" ;;
esac
exit "$rc"
