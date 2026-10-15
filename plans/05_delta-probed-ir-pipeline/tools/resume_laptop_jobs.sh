#!/usr/bin/env bash
# tools/resume_laptop_jobs.sh [--dry-run] (13 Oct 2026; the user: an unannounced app or Windows restart must not stop the work for a night or a
# weekend) — relaunches every job of tools/laptop_jobs.tsv that is neither finished nor running. Safe to run at any time and often: it acts only
# on a job that is
#   - not finished: its end marker (probes/watch_jobs.tsv) is not in its log, and
#   - not running: its process pattern is found neither by Windows' ps nor by pgrep inside WSL (a WSL job can outlive its wsl.exe), in two
#     looks 30 s apart (one ps snapshot once missed a live runner).
# Then it starts the job's command through tools/launch_outside_app.sh (WMI). Every job resumes by itself (done items are skipped). One line per
# action and one summary per call go to probes/watch_state/resume.log; a relaunch also goes to probes/watch_state/RELAUNCHED.txt, which
# state.sh shows. A lock keeps two calls from overlapping. Run by the scheduled task CapstoneResumeJobs at logon and every 30 minutes.
# Since 15 Oct 2026 it also runs `tools/runspec.py resume` for the runs launched through tools/runspec.py whose spec is resumable (TASKS 63).
# no-set-e: each job is decided on its own; one failure is logged and the others are still checked
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
JOBS="$HERE/laptop_jobs.tsv"
WATCH="$PLAN/probes/watch_jobs.tsv"
STATE="$PLAN/probes/watch_state"
LOG="$STATE/resume.log"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
mkdir -p "$STATE"
t() { date '+%F %T'; }
say() { echo "[$(t)] $*" >> "$LOG"; [ "$DRY" = 1 ] && echo "$*"; return 0; }
LOCK="$STATE/resume.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +120 2>/dev/null)" ]; then rmdir "$LOCK"; mkdir "$LOCK" || exit 0; else say "another call holds the lock — skipped"; exit 0; fi
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

running() {   # $1 = process ERE; 0 when Windows (ps -ef) or WSL (pgrep -f) sees it
  [ "$(ps -ef | grep -cE "$1")" != "0" ] && return 0
  [ "$(wsl.exe -e pgrep -fc "$1" 2>/dev/null | tr -d '\r')" -gt 0 ] 2>/dev/null && return 0
  return 1
}

n=0; ndone=0; nrun=0; nrel=0; nerr=0
while IFS=$'\t' read -r name cmd; do
  case "$name" in ''|'#'*) continue ;; esac
  n=$((n + 1))
  row=$(awk -F'\t' -v n="$name" '$1 == n' "$WATCH")
  if [ -z "$row" ]; then say "$name: no row in probes/watch_jobs.tsv — not handled"; nerr=$((nerr + 1)); continue; fi
  log=$PLAN/$(echo "$row" | cut -f2); end=$(echo "$row" | cut -f4); proc=$(echo "$row" | cut -f5)
  if [ -f "$log" ] && grep -qE "$end" "$log"; then ndone=$((ndone + 1)); continue; fi
  if running "$proc"; then nrun=$((nrun + 1)); continue; fi
  sleep 30
  if running "$proc"; then nrun=$((nrun + 1)); continue; fi
  if [ "$DRY" = 1 ]; then say "$name: neither finished nor running — would relaunch: $cmd"; nrel=$((nrel + 1)); continue; fi
  if pid=$(bash "$HERE/launch_outside_app.sh" "${name}_resume" "$PLAN" "$cmd"); then
    say "$name: RELAUNCHED (pid $pid): $cmd"; echo "$(t) $name relaunched (pid $pid)" >> "$STATE/RELAUNCHED.txt"; nrel=$((nrel + 1))
  else
    say "$name: RELAUNCH FAILED (WMI): $cmd"; nerr=$((nerr + 1))
  fi
done < "$JOBS"
say "checked $n: $ndone finished, $nrun running, $nrel relaunched$([ "$DRY" = 1 ] && echo ' (dry run)'), $nerr errors"
RUNSPEC_ARGS=(resume); [ "$DRY" = 1 ] && RUNSPEC_ARGS+=(--dry-run)
out=$(python "$HERE/runspec.py" "${RUNSPEC_ARGS[@]}" 2>&1); rc=$?
while IFS= read -r line; do
  [ -n "$line" ] && say "runspec: $line"
  case "$line" in *": RELAUNCHED "*) echo "$(t) runspec $line" >> "$STATE/RELAUNCHED.txt" ;; esac
done <<< "$(printf '%s' "$out" | tr -d '\r')"
[ "$rc" = 0 ] || say "runspec resume FAILED (exit $rc)"
