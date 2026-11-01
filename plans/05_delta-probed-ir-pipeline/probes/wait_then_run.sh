#!/usr/bin/env bash
# probes/wait_then_run.sh <log> <regex> -- <command …> (1 Nov 2026, TASKS 49 step 2) — runs the command once a line matching <regex>
# (grep -E) is in <log>, checked every WAIT_S seconds (default 900): a server job that must follow another one whose runner has no wait of
# its own (probes/l5_apt_field_run.sh after hbc_wb97x). A command whose last argument is --dry-run runs at once: that is the launcher's
# dry run (runspec appends dry_run_args), which must not wait days. The command's exit status is the script's.
set -euo pipefail
[ $# -ge 4 ] && [ "$3" = "--" ] || { echo "usage: $0 <log> <regex> -- <command …>"; exit 2; }
LOG=$1; RE=$2; shift 3
WAIT_S=${WAIT_S:-900}
if [ "${!#}" != "--dry-run" ]; then
  echo "=== (WAIT) waiting for /$RE/ in $LOG $(date '+%F %T')"
  until grep -qE -- "$RE" "$LOG" 2>/dev/null; do sleep "$WAIT_S"; done
  echo "=== (WAIT) condition met $(date '+%F %T')"
fi
exec "$@"
