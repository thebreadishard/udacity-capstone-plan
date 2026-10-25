#!/usr/bin/env bash
# probes/deploy_lib.sh — the steps every server deploy shares, sourced by probes/deploy_s2.sh and probes/deploy_s1tz.sh (19 Oct 2026:
# deploy_s2.sh's file list had fallen behind deploy_s1tz.sh's and would have shipped a runner that fails on import). The caller sets NAME
# (host in tools/hosts.tsv), PLAN, DEST and FILES first.
#   deploy_connect             pins the host's machine-id (tools/hosts.sh) and sets S, the ssh command
#   deploy_code <label>        FILES closed under their own needs (tools/deploy_closure.py), tracked and committed; DEST fresh; git archive
#                              of HEAD into DEST; DEST/COMMIT
#   deploy_geometries <list>…  the geometries named in the lists' second column, tar over ssh, sha256 on both sides
#   deploy_runner_smokes <label args> [opt]   two smokes of probes/labels_batch_ccx53.sh in DEST, water (the caller's WATER) as a
#                              one-molecule batch in a fresh SMOKE folder: labelled under a 2048 MB cap, named killed at the cap under
#                              64 MB; with 'opt' the molecule starts from a psi4 job (probes/smoke_job.py), so the optimisation step
#                              and the analytic-only result.json fields (n_imaginary, chain 42's wait) are smoked too
# Each step prints a named marker and returns 1 on failure; the caller stops.
# no-set-e: sourced into scripts that check every step's result themselves
P=plans/05_delta-probed-ir-pipeline
QC05=/root/miniforge3/envs/qc05/bin/python
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

smoke_batch() {   # $1 = batch and molecule name, $2 = cap in MB, $3 = label arguments, $4 = 'opt' to start from a psi4 job
  local prep="cp $DEST/$WATER molecules/$1/ && echo '{}' > molecules/$1/job.json && echo '{\"status\": \"done\"}' > molecules/$1/result.json"
  [ "${4:-}" = opt ] && prep="$QC05 $DEST/probes/smoke_job.py $DEST/$WATER $SMOKE/$1/molecules/$1"
  $S "mkdir -p $SMOKE/$1/molecules/$1 && cd $SMOKE/$1 && echo $1 > ids.txt && echo READY > ready.log && $prep && \
      CODE=$DEST/modules/05_support_predictor/corpus LANES=1 THREADS=2 CAP_MB=$2 LABEL_ARGS='$3' \
      bash $DEST/probes/labels_batch_ccx53.sh $SMOKE/$1 SM $SMOKE/$1/ready.log READY > $SMOKE/$1/run.log 2>&1" < /dev/null
}

deploy_runner_smokes() {   # $1 = label arguments, $2 = 'opt' to start from a psi4 job
  local m=$SMOKE/water_plus/molecules/water_plus
  $S "test ! -e $SMOKE" < /dev/null || { echo "$SMOKE EXISTS — a reused smoke folder tests nothing"; return 1; }
  echo "[$(t) $NAME] SMOKE 1: water through the runner under a 2048 MB system-scope cap${2:+, from a psi4 job}"
  smoke_batch water_plus 2048 "$1" "${2:-}" && $S "grep -a '  water_plus labelled' $SMOKE/water_plus/run.log && \
    test -f $m/hessian_wb97x_analytic.npz && test -f $m/hessian_b3lyp_analytic.npz" < /dev/null \
    || { echo "SMOKE 1 FAILED — see $SMOKE/water_plus/run.log"; return 1; }
  if [ "${2:-}" = opt ]; then
    $S "grep -a '  water_plus optimised [0-9]' $SMOKE/water_plus/run.log && grep -q '\"labels\": \"analytic_only\"' $m/result.json && \
        grep -q n_imaginary_b3lyp $m/result.json && grep -q n_imaginary_wb97x $m/result.json && test -f $m/dipole_b3lyp_cphf.npz" < /dev/null \
      || { echo "SMOKE 1 FAILED — the psi4 step or chain 42's result.json fields; see $SMOKE/water_plus"; return 1; }
  fi
  echo "[$(t) $NAME] SMOKE 2: the same under 64 MB must be named killed at the cap"
  if smoke_batch water_kill 64 "$1" "${2:-}"; then echo "SMOKE 2 FAILED — the runner reported success under 64 MB"; return 1; fi
  $S "grep -a '  water_kill KILLED at the cap of 64 MB' $SMOKE/water_kill/run.log" < /dev/null \
    || { echo "SMOKE 2 FAILED — the kill at the cap was not named; see $SMOKE/water_kill/run.log"; return 1; }
}
