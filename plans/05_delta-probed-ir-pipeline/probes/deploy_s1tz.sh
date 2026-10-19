#!/usr/bin/env bash
# probes/deploy_s1tz.sh <host name in tools/hosts.tsv> (18 Oct 2026, TASKS 60; registration
# GoalGathering/notes/PreRegistration_2026-10-14_TZ_Anharmonic_Basis.md) — puts S1-TZ on a server that already has the qc05 env, as
# probes/deploy_s2.sh does for S2: the runner files in the plan's layout under a fresh DEST (git archive of HEAD; the files must be committed
# and closed under their own imports), DEST/COMMIT, the corpus geometries of the id lists by tar over ssh with a sha256 check (the corpus is
# git-ignored), and the registration's SMOKE: water through the same runner at T with the grid gate. Water trips the noise guard at G (S1
# and S2 smokes), so 'done' and 'NOISY' both pass; what the smoke proves is that the T basis, the gate and the whole chain to a QFF report run
# on this server. Exit 0 when the smoke passed. The shared steps are probes/deploy_lib.sh's; `--list-files` prints the file list and
# contacts no server.
#   bash probes/deploy_s1tz.sh s1
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name, or --list-files}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
DEST=${DEST:-/root/dpir_s1tz}   # 19 Oct 2026: another folder while a run still executes from the first
L=probes/results_m1/s1tz_2026-10-18
LISTS=("$L/ids_benzene.tsv" "$L/ids_fused.tsv" "$L/ids_naphthalene.tsv" "$L/ids_acenaphthylene.tsv")   # every list a run spec names (19 Oct 2026)
FILES=(probes/s1tz_run.sh probes/progress_on_growth.sh probes/s2_batch.sh probes/s1_anharmonic_level.sh probes/s1_anharmonic_level.py
       probes/pyscf_hessians_for_qff.py probes/library_log.py probes/scf_converge.py probes/make_qff_displacements.py probes/qff_from_hessians.py
       src/dpir/__init__.py src/dpir/qff.py src/dpir/provenance.py probes/results_m1/water_dipole_fd_2026-10-02/geometry.json "${LISTS[@]}")
if [ "$NAME" = --list-files ]; then printf '%s\n' "${FILES[@]}"; exit 0; fi
. "$HERE/deploy_lib.sh"
SMOKE=/root/s1tz_smoke_$(basename "$DEST")   # 19 Oct 2026: a fresh smoke folder per destination; a reused one skips water and tests nothing

deploy_connect || exit 1
deploy_code S1-TZ || exit 1
deploy_geometries "${LISTS[@]}" || exit 1

echo "[$(t) $NAME] 3. SMOKE: water through s1tz_run.sh at T with the grid gate"
$S "cd $DEST && printf 'water\tprobes/results_m1/water_dipole_fd_2026-10-02/geometry.json\n' > $SMOKE.ids.tsv && MAX_FIRST=600 bash probes/s1tz_run.sh S1TZS $SMOKE.ids.tsv $SMOKE 1 4 > $SMOKE.log 2>&1; grep '^=== (S2)' $SMOKE.log" < /dev/null
$S "grep -qE '=== \(S2\) water: (done|NOISY)' $SMOKE.log && test -f $SMOKE/water/T/qff_report.npz && test -f $SMOKE/water/T/grid_gate.log" < /dev/null \
  || { echo "SMOKE FAILED $NAME — see $SMOKE.log"; exit 1; }
$S "cat $SMOKE/water/T/grid_gate.log" < /dev/null
echo "[$(t) $NAME] DEPLOY DONE"
