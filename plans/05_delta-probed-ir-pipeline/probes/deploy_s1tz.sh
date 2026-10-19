#!/usr/bin/env bash
# probes/deploy_s1tz.sh <host name in tools/hosts.tsv> (18 Oct 2026, TASKS 60; registration
# GoalGathering/notes/PreRegistration_2026-10-14_TZ_Anharmonic_Basis.md) — puts S1-TZ on a server that already has the qc05 env, as
# probes/deploy_s2.sh did for S2: the runner files in the plan's layout under a fresh /root/dpir_s1tz (git archive of HEAD; the files must be
# committed; S2's /root/dpir_s2 predates the grid gate), /root/dpir_s1tz/COMMIT, the three corpus geometries by tar over ssh with a sha256
# check (the corpus is git-ignored), and the registration's SMOKE: water through the same runner at T with the grid gate. Water trips the
# noise guard at G (S1 and S2 smokes), so 'done' and 'NOISY' both pass; what the smoke proves is that the T basis, the gate and the whole
# chain to a QFF report run on this server. Exit 0 when the smoke passed.
#   bash probes/deploy_s1tz.sh s1
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
. "$PLAN/tools/hosts.sh"
IP=$(host_ip "$NAME") || exit 1
host_ssh "$NAME" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $NAME"; exit 1; }
S="ssh -i $HOME/.ssh/hetzner_g_measure -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
DEST=${DEST:-/root/dpir_s1tz}   # 19 Oct 2026: another folder while a run still executes from the first
LISTS=(probes/results_m1/s1tz_2026-10-18/ids_benzene.tsv probes/results_m1/s1tz_2026-10-18/ids_fused.tsv)
P=plans/05_delta-probed-ir-pipeline
FILES=(probes/s1tz_run.sh probes/progress_on_growth.sh probes/s2_batch.sh probes/s1_anharmonic_level.sh probes/s1_anharmonic_level.py
       probes/pyscf_hessians_for_qff.py probes/library_log.py probes/scf_converge.py probes/make_qff_displacements.py probes/qff_from_hessians.py src/dpir/__init__.py src/dpir/qff.py
       src/dpir/provenance.py probes/results_m1/water_dipole_fd_2026-10-02/geometry.json "${LISTS[@]}")
t() { date '+%T'; }

echo "[$(t) $NAME] 1. the S1-TZ files under $DEST (git archive of HEAD)"
( cd "$PLAN" && git ls-files --error-unmatch "${FILES[@]}" > /dev/null && git diff --quiet HEAD -- "${FILES[@]}" ) \
  || { echo "S1-TZ FILES NOT TRACKED OR NOT COMMITTED — the server runs HEAD"; exit 1; }
$S "test ! -e $DEST" < /dev/null || { echo "$DEST EXISTS on $NAME — not overwritten"; exit 1; }
( cd "$PLAN/../.." && git archive --format=tar --prefix=x/ HEAD "${FILES[@]/#/$P/}" ) \
  | $S "mkdir -p /root/tmp_s1tz && tar xf - -C /root/tmp_s1tz && mv /root/tmp_s1tz/x/$P $DEST && rm -r /root/tmp_s1tz && find $DEST -type f | wc -l" \
  || { echo "FILES FAILED $NAME"; exit 1; }
git -C "$PLAN" rev-parse HEAD | $S "cat > $DEST/COMMIT" || exit 1

echo "[$(t) $NAME] 2. the geometries of the two lists (tar, sha256 on both sides)"
mapfile -t GEOMS < <(cd "$PLAN" && cut -f2 "${LISTS[@]}")
( cd "$PLAN" && tar cf - "${GEOMS[@]}" ) | $S "tar xf - -C $DEST" || { echo "GEOMETRY COPY FAILED"; exit 1; }
here_sum=$(cd "$PLAN" && sha256sum "${GEOMS[@]}" | sed 's/ [ *]/ /' | LC_ALL=C sort)
there_sum=$($S "cd $DEST && sha256sum ${GEOMS[*]}" < /dev/null | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$here_sum" = "$there_sum" ] || { echo "GEOMETRY SHA256 MISMATCH"; exit 1; }
echo "${#GEOMS[@]} geometries, sha256 equal"

SMOKE=/root/s1tz_smoke_$(basename "$DEST")   # 19 Oct 2026: a fresh smoke folder per destination; a reused one skips water and tests nothing
echo "[$(t) $NAME] 3. SMOKE: water through s1tz_run.sh at T with the grid gate"
$S "cd $DEST && printf 'water\tprobes/results_m1/water_dipole_fd_2026-10-02/geometry.json\n' > $SMOKE.ids.tsv && MAX_FIRST=600 bash probes/s1tz_run.sh S1TZS $SMOKE.ids.tsv $SMOKE 1 4 > $SMOKE.log 2>&1; grep '^=== (S2)' $SMOKE.log" < /dev/null
$S "grep -qE '=== \(S2\) water: (done|NOISY)' $SMOKE.log && test -f $SMOKE/water/T/qff_report.npz && test -f $SMOKE/water/T/grid_gate.log" < /dev/null \
  || { echo "SMOKE FAILED $NAME — see $SMOKE.log"; exit 1; }
$S "cat $SMOKE/water/T/grid_gate.log" < /dev/null
echo "[$(t) $NAME] DEPLOY DONE"
