#!/usr/bin/env bash
# watch.sh (10 Oct 2026) — the one watch, replacing the dated copies watch_1007 … watch_1012 (each a copy of the last with a line changed) and the
# server-specific watchers of deleted servers (hel2_watch_wsl.sh still pointed at 157.180.32.149, now another machine; all removed). Alarm-only;
# one cycle ≈ 110 min (11 checks, 10 min apart), re-armed on every wake. Exit 1 = anomaly, 2 = a new marker (reported once), 0 = quiet cycle.
#   laptop jobs  — probes/watch_jobs.tsv: each job's markers reported once; a job whose process is gone before its end marker is an anomaly.
#   rented hosts — tools/hosts.tsv via tools/hosts.sh: the machine-id is checked on every call, so a re-used IP is an anomaly, not a silent read
#                  of the wrong machine; a host row that is deleted is no longer watched. Labels lanes ('labels'), pool 3 runners ('pool3').
# The seen markers live in the plan (probes/watch_state/seen.txt, git-ignored), not in a session's scratchpad.
# Overridable for tests: WATCH_JOBS, WATCH_SEEN, WATCH_CYCLES, WATCH_SLEEP, HOSTS_FILE, HOSTS_SSH.
#   bash probes/watch.sh
set -uo pipefail
# no-set-e: every check decides its own exit
P=$(cd "$(dirname "$0")/.." && pwd)
JOBS=${WATCH_JOBS:-$P/probes/watch_jobs.tsv}
SEEN=${WATCH_SEEN:-$P/probes/watch_state/seen.txt}
CYCLES=${WATCH_CYCLES:-11}
SLEEP=${WATCH_SLEEP:-600}
# shellcheck source=../tools/hosts.sh
. "$P/tools/hosts.sh"
mkdir -p "$(dirname "$SEEN")"; touch "$SEEN"
t() { date '+%H:%M'; }
new_marker() {   # $1 = a line; prints and records it when not seen before
  grep -qxF "$1" "$SEEN" && return 1
  echo "$1" >> "$SEEN"; echo "MARKER $(t): $1"; return 0
}
has_host() { [ -n "$(_host_row "$1")" ]; }

check_jobs() {
  local name log mark end proc line
  while IFS=$'\t' read -r name log mark end proc; do
    case "$name" in ''|'#'*) continue ;; esac
    log=$P/$log
    [ -f "$log" ] || continue
    while read -r line; do new_marker "$(echo "$line" | cut -c1-110)" && exit 2; done < <(grep -E "$mark" "$log" | grep -v armed)
    if ! grep -qE "$end" "$log"; then
      [ "$(ps -ef | grep -cE "$proc")" = "0" ] && { echo "ANOMALY $(t): job $name gone without its end marker"; exit 1; }
    fi
  done < "$JOBS"
}

lb="" np=""; lfails=0; pfails=0
remote_fail() {   # $1 = host, $2 = rc, $3 = name of the counter variable
  [ "$2" = "3" ] && { echo "ANOMALY $(t): host $1 answers with another machine (re-used IP?) — see tools/hosts.tsv"; exit 1; }
  printf -v "$3" '%d' $(( ${!3} + 1 ))
  [ "${!3}" -ge 2 ] && { echo "ANOMALY $(t): host $1 unreachable twice"; exit 1; }
}

check_labels() {   # the labels server: 'bash labels_lane.sh' processes alive until 'LANE n DONE'
  has_host labels || return 0
  local rc lanes lfail ldone
  lb=$(host_ssh labels 'cd /root/labels 2>/dev/null && echo "lanes $(pgrep -fc "^bash (/root/labels/)?labels_lane(_switch)?\.sh") ok $(cat lane_?.log 2>/dev/null | grep -c " ok ") failed $(cat lane_?.log 2>/dev/null | grep -c " FAILED ") done $(cat lane_?.log 2>/dev/null | grep -c "DONE:")"'); rc=$?
  if [ -z "$lb" ]; then remote_fail labels "$rc" lfails; return 0; fi
  lfails=0
  lanes=$(echo "$lb" | awk '{print $2}'); lfail=$(echo "$lb" | awk '{print $6}'); ldone=$(echo "$lb" | awk '{print $8}')
  if [ "$ldone" = "4" ]; then new_marker "labels: all four lanes DONE — $lb" && exit 2; fi
  if [ "$((lanes + ldone))" -lt 4 ]; then echo "ANOMALY $(t): labels lanes $lanes running + $ldone done < 4 — $lb"; exit 1; fi
  [ "$lfail" != "0" ] && new_marker "labels failed count $lfail" > /dev/null && { echo "MARKER $(t): labels $lb"; exit 2; }
  return 0
}

check_pool3() {   # pool 3's two runners, each alive until remote_launch's <name>.exit exists; a new failed count reported once
  has_host pool3 || return 0
  local rc aa ae ad af ba be bd bf al ex r
  np=$(host_ssh pool3 'B=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor; for r in a b; do d=$B/corpus_p3; [ $r = b ] && d=$B/corpus_p3b; alive=0; kill -0 $(cat $d/pool3_$r.pid 2>/dev/null) 2>/dev/null && alive=1; ex=$([ -f $d/pool3_$r.exit ] && echo 1 || echo 0); printf "%s %s %s %s %s " $r $alive $ex $(grep -c "] done" $d/pool3_$r.log) $(grep -c "] failed" $d/pool3_$r.log); done'); rc=$?
  if [ -z "$np" ]; then remote_fail pool3 "$rc" pfails; return 0; fi
  pfails=0
  read -r _ aa ae ad af _ ba be bd bf <<< "$np"
  for r in a b; do
    if [ $r = a ]; then al=$aa; ex=$ae; else al=$ba; ex=$be; fi
    [ "$al" = "0" ] && [ "$ex" = "0" ] && { echo "ANOMALY $(t): pool 3 runner $r gone without its exit file — $np"; exit 1; }
    [ "$ex" = "1" ] && new_marker "pool 3 runner $r finished — $np" && exit 2
  done
  new_marker "pool3 failed count $((af + bf))" > /dev/null && [ "$((af + bf))" != "0" ] && { echo "MARKER $(t): pool 3 a/b done $ad/$bd failed $af/$bf"; exit 2; }
  return 0
}

for i in $(seq 1 "$CYCLES"); do
  check_jobs
  check_labels
  check_pool3
  [ "$i" -lt "$CYCLES" ] && sleep "$SLEEP"
done
echo "quiet cycle $(t): labels ${lb:-—} | pool3 ${np:-—}"
exit 0
