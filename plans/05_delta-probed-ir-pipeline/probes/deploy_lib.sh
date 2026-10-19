#!/usr/bin/env bash
# probes/deploy_lib.sh — the steps every server deploy shares, sourced by probes/deploy_s2.sh and probes/deploy_s1tz.sh (19 Oct 2026:
# deploy_s2.sh's file list had fallen behind deploy_s1tz.sh's and would have shipped a runner that fails on import). The caller sets NAME
# (host in tools/hosts.tsv), PLAN, DEST and FILES first.
#   deploy_connect             pins the host's machine-id (tools/hosts.sh) and sets S, the ssh command
#   deploy_code <label>        FILES closed under their own needs (tools/deploy_closure.py), tracked and committed; DEST fresh; git archive
#                              of HEAD into DEST; DEST/COMMIT
#   deploy_geometries <list>…  the geometries named in the lists' second column, tar over ssh, sha256 on both sides
# Each step prints a named marker and returns 1 on failure; the caller stops.
# no-set-e: sourced into scripts that check every step's result themselves
P=plans/05_delta-probed-ir-pipeline
t() { date '+%T'; }

deploy_connect() {
  . "$PLAN/tools/hosts.sh"
  IP=$(host_ip "$NAME") || return 1
  host_ssh "$NAME" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $NAME"; return 1; }
  S="ssh -i $HOME/.ssh/hetzner_g_measure -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
}

deploy_code() {   # $1 = what is deployed, for the messages
  local tmp
  tmp=/root/tmp_deploy_$(basename "$DEST")
  echo "[$(t) $NAME] 1. the $1 files under $DEST (git archive of HEAD)"
  ( cd "$PLAN" && python tools/deploy_closure.py "${FILES[@]}" ) || { echo "$1 FILES INCOMPLETE — a shipped file needs one the list lacks"; return 1; }
  ( cd "$PLAN" && git ls-files --error-unmatch "${FILES[@]}" > /dev/null && git diff --quiet HEAD -- "${FILES[@]}" ) \
    || { echo "$1 FILES NOT TRACKED OR NOT COMMITTED — the server runs HEAD"; return 1; }
  $S "test ! -e $DEST" < /dev/null || { echo "$DEST EXISTS on $NAME — not overwritten"; return 1; }
  # -c core.autocrlf=false: on Windows git archive otherwise writes CRLF into the .py files (19 Oct 2026: runspec's sha256 check failed)
  ( cd "$PLAN/../.." && git -c core.autocrlf=false archive --format=tar --prefix=x/ HEAD "${FILES[@]/#/$P/}" ) \
    | $S "mkdir -p $tmp && tar xf - -C $tmp && mv $tmp/x/$P $DEST && rm -r $tmp && find $DEST -type f | wc -l" \
    || { echo "FILES FAILED $NAME"; return 1; }
  git -C "$PLAN" rev-parse HEAD | $S "cat > $DEST/COMMIT"
}

deploy_geometries() {   # $@ = id lists (id TAB geometry path …), relative to the plan
  local geoms here_sum there_sum
  echo "[$(t) $NAME] 2. the geometries of $* (tar, sha256 on both sides)"
  mapfile -t geoms < <(cd "$PLAN" && cut -f2 "$@" | tr -d '\r' | LC_ALL=C sort -u)
  ( cd "$PLAN" && tar cf - "${geoms[@]}" ) | $S "tar xf - -C $DEST" || { echo "GEOMETRY COPY FAILED"; return 1; }
  here_sum=$(cd "$PLAN" && sha256sum "${geoms[@]}" | sed 's/ [ *]/ /' | LC_ALL=C sort)
  there_sum=$($S "cd $DEST && sha256sum ${geoms[*]}" < /dev/null | sed 's/ [ *]/ /' | LC_ALL=C sort)
  [ "$here_sum" = "$there_sum" ] || { echo "GEOMETRY SHA256 MISMATCH"; return 1; }
  echo "${#geoms[@]} geometries, sha256 equal"
}
