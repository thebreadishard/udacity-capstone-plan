#!/usr/bin/env bash
# watch.sh (10 Oct 2026) — the one watch, replacing the dated copies watch_1007 … watch_1012 (each a copy of the last with a line changed) and the
# server-specific watchers of deleted servers (hel2_watch_wsl.sh still pointed at 157.180.32.149, now another machine; all removed). Alarm-only;
# one cycle ≈ 110 min (11 checks, 10 min apart), re-armed on every wake. Exit 1 = anomaly, 2 = a new marker (reported once), 0 = quiet cycle.
#   laptop jobs  — probes/watch_jobs.tsv: each job's markers reported once; a job whose process is gone before its end marker is an anomaly.
#   rented hosts — tools/hosts.tsv via tools/hosts.sh: the machine-id is checked on every call, so a re-used IP is an anomaly, not a silent read
#                  of the wrong machine; a host row that is deleted is no longer watched. Labels lanes ('labels'), pool 3 runners ('pool3').
#   specced runs — since 15 Oct 2026 every run launched through tools/runspec.py (probes/runspecs/): its progress contract is checked there.
# The seen markers live in the plan (probes/watch_state/seen.txt, git-ignored), not in a session's scratchpad.
# Overridable for tests: WATCH_JOBS, WATCH_SEEN, WATCH_CYCLES, WATCH_SLEEP, HOSTS_FILE, HOSTS_SSH, RUNSPEC_DIR, RUNSPEC_STATE, RUNSPEC_PYTHON.
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
    while read -r line; do new_marker "$(echo "$line" | cut -c1-110)" && exit 2; done < <(grep -aE "$mark" "$log" | grep -v armed)
    if ! grep -qE "$end" "$log"; then
      # 13 Oct 2026: one ps snapshot missed a live runner (C35h, 16:19, during a WMI launch); a job is gone only when two snapshots 30 s apart miss it
      if [ "$(ps -ef | grep -cE "$proc")" = "0" ]; then
        sleep 30
        [ "$(ps -ef | grep -cE "$proc")" = "0" ] && { echo "ANOMALY $(t): job $name gone without its end marker (two snapshots 30 s apart)"; exit 1; }
      fi
    fi
  done < "$JOBS"
}

lb="" np="" an="" so="" s2o="" s2go="" l5o="" r4o="" ro=""; lfails=0; pfails=0; afails=0; sfails=0; s2fails=0; s2gfails=0; l5fails=0; r4fails=0
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
    # the marker is the stable text only: with the counts in it, every change of the other runner's count re-reported it (13 Oct 23:24)
    [ "$ex" = "1" ] && new_marker "pool 3 runner $r finished" && { echo "  counts: $np"; exit 2; }
  done
  new_marker "pool3 failed count $((af + bf))" > /dev/null && [ "$((af + bf))" != "0" ] && { echo "MARKER $(t): pool 3 a/b done $ad/$bd failed $af/$bf"; exit 2; }
  return 0
}

check_anchors3() {   # anchor set three (probes/anchor_wave.sh): each '=== (AS3)' line once; the wave runner gone before 'wave done' is an anomaly
  has_host anchors3 || return 0
  local rc alive last line
  an=$(host_ssh anchors3 'test -f /root/dpir/anchors.log || { echo NOLOG; exit 0; }; echo "alive $(pgrep -fc "^bash (/root/dpir/)?probes/anchor_wave\.sh ")"; grep "^=== (AS3) " /root/dpir/anchors.log | tail -n 30'); rc=$?
  if [ -z "$an" ]; then remote_fail anchors3 "$rc" afails; return 0; fi
  afails=0
  [ "$an" = "NOLOG" ] && return 0
  alive=$(echo "$an" | head -1 | awk '{print $2}')
  while read -r line; do new_marker "$(echo "$line" | cut -c1-110)" && exit 2; done < <(echo "$an" | tail -n +2)
  last=$(echo "$an" | tail -n 1)
  if [ "$alive" = "0" ] && [[ "$last" != *"wave done"* ]]; then echo "ANOMALY $(t): anchors3 wave runner gone without 'wave done' — $last"; exit 1; fi
  return 0
}

check_server_run() {   # $1 host, $2 log, $3 tag, $4 process ERE, $5 end-marker ERE, $6 unreachable counter, $7 variable for the quiet line,
  # $8 (optional) ERE of routine markers: recorded as seen without waking the session (14 Oct 2026, S2's per-molecule start/done)
  # each '=== (<tag>)' line once; the runner gone before an end marker is an anomaly (S1 13 Oct, S2 14 Oct 2026)
  has_host "$1" || return 0
  local rc alive line out
  out=$(host_ssh "$1" "test -f $2 || { echo NOLOG; exit 0; }; echo \"alive \$(pgrep -fc '$4')\"; grep '^=== ($3) ' $2 | tail -n 30"); rc=$?
  if [ -z "$out" ]; then remote_fail "$1" "$rc" "$6"; return 0; fi
  printf -v "$6" '%d' 0
  printf -v "$7" '%s' "$out"
  [ "$out" = "NOLOG" ] && return 0
  alive=$(echo "$out" | head -1 | awk '{print $2}')
  while read -r line; do
    if [ -n "${8:-}" ] && echo "$line" | grep -qE "$8"; then new_marker "$(echo "$line" | cut -c1-110)" > /dev/null; continue; fi
    new_marker "$(echo "$line" | cut -c1-110)" && exit 2
  done < <(echo "$out" | tail -n +2)
  if [ "$alive" = "0" ] && ! echo "$out" | grep -qE "$5"; then
    echo "ANOMALY $(t): $3 runner on $1 gone without an end marker — $(echo "$out" | tail -n 1)"; exit 1
  fi
  return 0
}

check_s1srv() { check_server_run s1 /root/dpir/s1.log S1 '^bash (/root/dpir/)?probes/s1_anharmonic_level\.sh ' \
  '^=== \(S1\) (all settings done|SETTINGS FAILED|[A-Z]+: STOPPED|[A-Z]+: QFF FAILED)' sfails so; }
check_s2srv() { check_server_run s1 /root/dpir_s2/s2.log S2 '^bash (/root/dpir_s2/)?probes/s2_batch\.sh ' '^=== \(S2\) all done' s2fails s2o \
  '^=== \(S2\) [A-Za-z0-9_]+: (start|done|already done, skipped) '; }
check_s2gsrv() { check_server_run s1 /root/s2_gridcheck/s2gridcheck.log S2G '^bash /root/dpir_s2/probes/s2_gridcheck_styrene\.sh' \
  '^=== \(S2G\) styrene grid check done' s2gfails s2go; }   # 15 Oct 2026: styrene's grid check, TASKS 62
check_l5srv() { check_server_run labels /root/labels/large_pah/run.log L5 '^bash /root/labels/large_pah_ccx53\.sh' \
  '^=== \(L5\) all done' l5fails l5o; }   # 15 Oct 2026: lever 5 (TASKS 49), armed on the labels server since 13 Oct
check_r4srv() { check_server_run labels /root/labels/rung4/run.log R4 '^bash /root/labels/labels_batch_ccx53\.sh /root/labels/rung4 ' \
  '^=== \(R4\) (all done|STOPPED)' r4fails r4o; }   # 15 Oct 2026: rung 4 (TASKS 61), waits for lever 5's end

check_runs() {   # 15 Oct 2026 (TASKS 63): the runs of tools/runspec.py. Its ANOMALY and MARKER texts stay the same while a situation lasts,
  # so each is reported once through the seen file; QUIET is the summary for the quiet line. A crash of the check is itself reported once.
  local out rc line
  out=$("${RUNSPEC_PYTHON:-python}" "$P/tools/runspec.py" check 2>&1); rc=$?
  out=$(printf '%s' "$out" | tr -d '\r')   # Windows python ends lines with CR LF; the seen file must see the same text twice
  if [ "$rc" != "0" ]; then
    new_marker "runspec check failed: $(echo "$out" | tail -n 1 | cut -c1-80)" > /dev/null && { echo "ANOMALY $(t): tools/runspec.py check exit $rc - $(echo "$out" | tail -n 1)"; exit 1; }
    return 0
  fi
  while IFS= read -r line; do
    case "$line" in
      "ANOMALY "*) new_marker "${line#ANOMALY }" > /dev/null && { echo "ANOMALY $(t): ${line#ANOMALY }"; exit 1; } ;;
      "MARKER "*) new_marker "${line#MARKER }" && exit 2 ;;
      "QUIET "*) ro=${line#QUIET } ;;
    esac
  done <<< "$out"
  return 0
}

check_ci() {   # 13 Oct 2026: six red plan05 runs in a row went unseen for eight hours; a failed run is reported once per commit
  local r
  r=$(gh run list -R thebreadishard/udacity-capstone-plan --workflow plan05 --limit 1 --json status,conclusion,headSha         --jq '.[0] | "\(.status) \(.conclusion) \(.headSha[:8])"' 2>/dev/null) || return 0      # offline or gh missing: no verdict
  case "$r" in
    "completed failure "*) new_marker "CI plan05 FAILED on ${r##* } — gh run list -R thebreadishard/udacity-capstone-plan --workflow plan05" && exit 2 ;;
  esac
  return 0
}

for i in $(seq 1 "$CYCLES"); do
  check_jobs
  check_labels
  check_pool3
  check_anchors3
  check_s1srv
  check_s2srv
  check_s2gsrv
  check_l5srv
  check_r4srv
  check_runs
  check_ci
  [ "$i" -lt "$CYCLES" ] && sleep "$SLEEP"
done
echo "quiet cycle $(t): labels ${lb:-—} | pool3 ${np:-—} | anchors3 $(echo "${an:-—}" | tail -n 1 | cut -c1-80) | s1 $(echo "${so:-—}" | tail -n 1 | cut -c1-60) | s2 $(echo "${s2o:-—}" | tail -n 1 | cut -c1-60) | runs ${ro:-—}"
exit 0
