#!/usr/bin/env bash
# probes/collect_anchor.sh <host in tools/hosts.tsv> <molecule id> (22 Nov 2026; TASKS 291) — brings one new anchor home and into the
# anchor registry, in stages that each check their own condition, so that it can be run the moment a stage's input exists and run again
# later (probes/fetch_anchor.sh did the first stage for anchor set three's one server):
#   1. CC   — when the server's wave log has the molecule's end: 'hessian DONE' with 'apt PASS' (or the user's 'apt ACCEPTED'), or a
#             terminal failure ('hessian IMAGINARY', 'hessian FAILED', 'apt FAIL'). Either way the full run folder
#             (<CC_ROOT>/probes/results/<id>_ccpvdz: gradients, dipoles, Hessian, APTs, logs), the geometry it ran at and the wave log
#             so far come into <out>/<id>/cc and …/server, every file sha256-compared with the server before the copy takes its name,
#             with 'FETCHED <id> cc …' in the server's fetched.log and the folder's FETCHED.txt: no result lives on a server only, a
#             failed one included. A terminal failure ends the run there (exit 3).
#   2. MP2  — when the MP2 lane finished both bases there (<MP2_ROOT>/rows/<id>: the row files with dfmp2_rows.py's end line in their
#             last attempt's log): that folder into …/<id>/mp2, the same way, 'FETCHED <id> mp2 …'.
#   3. composite — H = CC/DZ + [MP2/TZ − MP2/DZ] by probes/cc_composite_full_check.py build (the anchor's coordinates must be the corpus
#             geometry's, the rows' the anchor's), into …/<id>/composite_<id>.npz/.md/.json.
#   4. registry — probes/composite_promote.py promote: carried on tier TZ when the composite is VALID (chain 33c's rule), else
#             experimental; the entry is then checked (probes/collect_anchor_registry.py: file unchanged, its own verdict).
#             modules/05_support_predictor/out/ANCHORS_STATUS.json and modules/ANCHORS.md are tracked and committed by hand.
# A stage already done is verified, not repeated (a fetched folder is compared with the server again; a built composite and a registered
# path are left as they are). Exit: 0 the anchor is carried in the registry; 2 a stage's input is not there yet (the message says what
# it waits for); 3 the CC run ended in a failure, fetched; 4 registered but not carried (experimental); 1 anything else, the server
# unreachable included — never reported as 'wait'. stdin is not read, so the script can run inside `while read … done < list`.
# Places (environment; the defaults are the servers' and the plan's, the overrides are for tests): CC_ROOT /root/dpir, MP2_ROOT
#   /root/mp2b, COLLECT_OUT probes/results_m1/new_anchors_2026-11 (relative to the plan; a registry path must be), CORPUS_MOLECULES
#   the corpus's molecules; the server is reached through tools/hosts.sh (HOSTS_FILE, HOSTS_SSH).
#   bash probes/collect_anchor.sh anc3 B_00e041576d
set -Eeuo pipefail          # -E: the ERR trap below also names a failure inside a function
HOST=${1:?host name}; ID=${2:?molecule id}
exec < /dev/null
trap 'echo "collect_anchor.sh: stopped at line $LINENO — a command failed"' ERR
[[ $ID =~ ^[A-Za-z0-9_]+$ ]] || { echo "not a molecule id: $ID"; exit 1; }
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
. "$PLAN/tools/hosts.sh"
IP=$(host_ip "$HOST")
CC_ROOT=${CC_ROOT:-/root/dpir}; MP2_ROOT=${MP2_ROOT:-/root/mp2b}
CORPUS_MOLECULES=${CORPUS_MOLECULES:-$PLAN/modules/05_support_predictor/corpus/molecules}
REL=${COLLECT_OUT:-probes/results_m1/new_anchors_2026-11}/$ID
case "$REL" in /*) DST=$REL ;; *) DST=$PLAN/$REL ;; esac
CC_SRC=$CC_ROOT/probes/results/${ID}_ccpvdz
MP2_SRC=$MP2_ROOT/rows/$ID
[ -f "$CORPUS_MOLECULES/$ID/geometry.json" ] \
  || { echo "$ID has no corpus geometry: its DFT row must be merged into the corpus before it can be an anchor"; exit 1; }
host_ssh "$HOST" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $HOST"; exit 1; }

# a stream from the server (tar, cat) through the ssh command host_ssh uses; the machine was pinned by the host_ssh call above
remote() { $HOSTS_SSH "root@$IP" "$1"; }
# ask <command printing one word>: the word, or exit 1 when the server did not answer (never mistaken for 'not yet')
ask() {
  local word
  word=$(host_ssh "$HOST" "$1") || { echo "no answer from $HOST (ssh failed or the wrong machine) — not a 'wait'" >&2; exit 1; }
  [ -n "$word" ] || { echo "empty answer from $HOST" >&2; exit 1; }
  echo "$word"
}
sums_local() { (cd "$1" && find . -type f -print0 | xargs -0 sha256sum | sed 's/ [ *]/ /' | LC_ALL=C sort); }
sums_remote() { host_ssh "$HOST" "cd $1 && find . -type f -print0 | xargs -0 sha256sum" | sed 's/ [ *]/ /' | LC_ALL=C sort; }

# fetch_part <stage> <remote folder> <local folder>: a missing local folder is copied beside its name and takes it only when every
# file equals the server's; an existing one is compared again. The record goes to the server first, then here.
fetch_part() {
  local stage=$1 src=$2 dst=$3 at theirs ours n bytes line
  at=$dst
  if [ ! -d "$dst" ]; then
    at=$dst.partial
    rm -rf "$at"; mkdir -p "$at"
    remote "tar cf - -C $src ." | tar xf - -C "$at"
  fi
  theirs=$(sums_remote "$src"); ours=$(sums_local "$at")
  if [ -z "$theirs" ] || [ "$theirs" != "$ours" ]; then
    echo "sha256 MISMATCH between $HOST:$src and $at"; diff <(echo "$theirs") <(echo "$ours") | head || true; exit 1
  fi
  [ "$at" = "$dst" ] || mv "$at" "$dst"
  n=$(echo "$theirs" | wc -l); bytes=$(du -sb "$dst" | cut -f1)
  if grep -qF "FETCHED $ID $stage $n files $bytes bytes" "$DST/FETCHED.txt" 2>/dev/null; then
    echo "$stage: verified again ($n files, sha256 equal)"
  else
    line="FETCHED $ID $stage $n files $bytes bytes sha256-checked $(date '+%F %T') from $HOST"
    host_ssh "$HOST" "echo '$line' >> $CC_ROOT/fetched.log"
    echo "$line" | tee -a "$DST/FETCHED.txt"
  fi
}

echo "[1] CC run folder"
LOG=$CC_ROOT/anchors.log
# the log is appended to: a relaunch's 'hessian DONE' after a 'hessian FAILED', a re-run's 'apt PASS' or the user's 'apt ACCEPTED' after
# an 'apt FAIL' — the molecule's LAST hessian line and LAST apt line decide, never an earlier one
STATE=$(ask "h=\$(grep -F '=== (AS3) $ID hessian ' $LOG | tail -n 1); a=\$(grep -F '=== (AS3) $ID apt ' $LOG | tail -n 1); \
  case \"\$h\" in \
    *'hessian IMAGINARY'*) echo IMAGINARY ;; \
    *'hessian FAILED'*) echo HESSIAN_FAILED ;; \
    *'hessian DONE'*) case \"\$a\" in \
        *'apt PASS'*|*'apt ACCEPTED'*) if test -f $CC_SRC/hessian_ccsd_t.npz && test -f $CC_SRC/apt_ccsd_t_field.npz; then echo READY; else echo RUNNING; fi ;; \
        *'apt FAIL'*) echo APT_FAILED ;; \
        *) echo RUNNING ;; esac ;; \
    *) echo RUNNING ;; esac")
[ "$STATE" != RUNNING ] || { echo "$ID on $HOST: the wave log has no end for it yet — nothing fetched"; exit 2; }
mkdir -p "$DST"
fetch_part cc "$CC_SRC" "$DST/cc"
if [ ! -d "$DST/server" ]; then
  rm -rf "$DST/server.partial"; mkdir -p "$DST/server.partial"
  remote "cat $CC_ROOT/geoms/$ID/geometry.json" > "$DST/server.partial/geometry.json"
  remote "cat $LOG" > "$DST/server.partial/anchors_log_at_fetch.txt"
  remote "cat $CC_ROOT/COMMIT; /root/miniforge3/envs/qc05/bin/pip freeze 2>/dev/null || true" > "$DST/server.partial/commit_and_qc05_freeze.txt"
  mv "$DST/server.partial" "$DST/server"
fi
[ "$STATE" = READY ] || { echo "$ID on $HOST: the CC run ended as $STATE — its folder is home, no composite is built"; exit 3; }
cmp -s "$DST/server/geometry.json" "$CORPUS_MOLECULES/$ID/geometry.json" \
  || { echo "$ID: the geometry the server ran at is not the corpus geometry file"; exit 1; }

echo "[2] MP2 rows"
ROWS=$(ask "for b in ccpvdz ccpvtz; do test -f $MP2_SRC/dfmp2_rows_\$b.npz && grep -qa 'DF ROWS DONE' $MP2_SRC/rows_\$b.log || { echo UNFINISHED; exit 0; }; done; echo FINISHED")
[ "$ROWS" = FINISHED ] || { echo "$ID on $HOST: the MP2 rows of both bases are not finished yet — the CC folder is home, the composite waits"; exit 2; }
fetch_part mp2 "$MP2_SRC" "$DST/mp2"

echo "[3] composite"
OUT=$REL/composite_$ID
cd "$PLAN"
if [ -f "$OUT.npz" ] && [ -f "$OUT.json" ]; then
  echo "composite found: $OUT.npz"
else
  PYTHONUTF8=1 python probes/cc_composite_full_check.py build "$REL/cc/hessian_ccsd_t.npz" "$ID" "$REL/mp2/dfmp2_rows_ccpvdz.npz" \
    "$REL/mp2/dfmp2_rows_ccpvtz.npz" "$OUT.partial" > "$DST/composite_build.log" 2>&1 \
    || { echo "COMPOSITE BUILD FAILED — see $REL/composite_build.log"; tail -3 "$DST/composite_build.log"; exit 1; }
  for ext in md json npz; do mv "$OUT.partial.$ext" "$OUT.$ext"; done        # the npz last: its presence means the build is whole
  tail -6 "$DST/composite_build.log"
fi

echo "[4] registry"
case "$REL" in /*) echo "COLLECT_OUT is absolute: a registry path is relative to the plan — not registered"; exit 1 ;; esac
if ! PYTHONUTF8=1 python probes/collect_anchor_registry.py status "$OUT.npz" > /dev/null 2>&1; then
  NAME=$(PYTHONUTF8=1 python probes/collect_anchor_registry.py name "$ID")
  PYTHONUTF8=1 python probes/composite_promote.py promote "$OUT.npz" "$ID" "$NAME" "$(date +%F)"
fi
STATUS=$(PYTHONUTF8=1 python probes/collect_anchor_registry.py status "$OUT.npz") || { echo "NOT REGISTERED or its check failed: $OUT.npz"; exit 1; }
echo "COLLECTED $ID from $HOST: $OUT.npz is in the anchor registry as $STATUS"
[ "$STATUS" = carried ] || exit 4
