#!/usr/bin/env bash
# probes/deploy_s2.sh <host name in tools/hosts.tsv> (14 Oct 2026, S2; registration GoalGathering/notes/PreRegistration_2026-10-14_S2_Anharmonic_Shift.md)
# — puts S2 on a server that already has the qc05 env (probes/bootstrap_s1_cpx62.sh step 1): the runner files in the plan's layout under a
# fresh DEST (git archive of HEAD; the files must be committed and closed under their own imports), DEST/COMMIT, the corpus geometries of the
# id list IDS by tar over ssh with a sha256 check (the corpus is git-ignored), and a SMOKE: water through probes/s2_batch.sh at G in a fresh
# folder, whose ω must equal S2's smoke on s1 (14 Oct 2026, committed as probes/results_m1/s2_smoke_reference_2026-10-14/water_G_omega.json)
# within its tolerance. Water at G trips the noise guard (S1 smoke, 14.8 cm⁻¹), so the smoke expects 'water: NOISY'. Exit 0 when the smoke
# passed. The shared steps are probes/deploy_lib.sh's; `--list-files` prints the file list and contacts no server.
#   bash probes/deploy_s2.sh s1
#   DEST=/root/dpir_s2b IDS=probes/results_m1/s2b_training_set_2026-10-19/plan/s2b_ids_1of2.tsv bash probes/deploy_s2.sh <host>   (S2b)
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name, or --list-files}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
DEST=${DEST:-/root/dpir_s2}
IDS=${IDS:-probes/results_m1/s2_training_set_2026-10-14/s2_ids.tsv}
SMOKE=/root/s2_smoke_$(basename "$DEST")   # a fresh smoke folder per destination: a reused one skips water and tests nothing (19 Oct 2026)
REF=probes/results_m1/s2_smoke_reference_2026-10-14/water_G_omega.json
FILES=(probes/s2_batch.sh probes/s1_anharmonic_level.sh probes/s1_anharmonic_level.py probes/pyscf_hessians_for_qff.py
       probes/library_log.py probes/scf_converge.py probes/make_qff_displacements.py probes/qff_from_hessians.py src/dpir/__init__.py
       src/dpir/qff.py src/dpir/provenance.py probes/results_m1/water_dipole_fd_2026-10-02/geometry.json "$REF" "$IDS")
if [ "$NAME" = --list-files ]; then printf '%s\n' "${FILES[@]}"; exit 0; fi
. "$HERE/deploy_lib.sh"

deploy_connect || exit 1
$S "test ! -e $SMOKE" < /dev/null || { echo "$SMOKE EXISTS on $NAME — not overwritten"; exit 1; }
deploy_code S2 || exit 1
deploy_geometries "$IDS" || exit 1

echo "[$(t) $NAME] 3. SMOKE: water through s2_batch.sh at G"
$S "cd $DEST && printf 'water\tprobes/results_m1/water_dipole_fd_2026-10-02/geometry.json\n' > $SMOKE.ids.tsv && PY=/root/miniforge3/envs/qc05/bin/python bash probes/s2_batch.sh $SMOKE.ids.tsv $SMOKE 1 4 'G:6-31g*:75,302' > $SMOKE.log 2>&1; grep '^=== (S2)' $SMOKE.log" < /dev/null
$S "grep -q '=== (S2) water: NOISY' $SMOKE.log && cd $DEST && /root/miniforge3/envs/qc05/bin/python -c \"
import json, numpy as np
a = np.load('$SMOKE/water/G/qff_report.npz')['omega_cm']; ref = json.load(open('$REF', encoding='utf-8'))
print('omega', a.round(3), 'reference', np.round(ref['omega_cm'], 3)); assert np.abs(a - ref['omega_cm']).max() < ref['tolerance_cm']
\"" < /dev/null || { echo "SMOKE FAILED $NAME — see $SMOKE.log"; exit 1; }
echo "[$(t) $NAME] DEPLOY DONE"
