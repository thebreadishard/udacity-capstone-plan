#!/usr/bin/env bash
# probes/deploy_s2.sh <host name in tools/hosts.tsv> (14 Oct 2026, S2; registration GoalGathering/notes/PreRegistration_2026-10-14_S2_Anharmonic_Shift.md)
# — puts S2 on a server that already has the qc05 env (probes/bootstrap_s1_cpx62.sh step 1): the runner files in the plan's layout under a
# fresh DEST (git archive of HEAD; the files must be committed), DEST/COMMIT, the corpus geometries of the id list IDS by tar over ssh with a
# sha256 check (the corpus is git-ignored), and a SMOKE: water through probes/s2_batch.sh at G in a fresh folder, whose ω must equal S2's
# smoke on s1 (14 Oct 2026, committed as probes/results_m1/s2_smoke_reference_2026-10-14/water_G_omega.json) within its tolerance. Water at
# G trips the noise guard (S1 smoke, 14.8 cm⁻¹), so the smoke expects 'water: NOISY'. Exit 0 when the smoke passed.
#   bash probes/deploy_s2.sh s1
#   DEST=/root/dpir_s2b IDS=probes/results_m1/s2b_training_set_2026-10-19/plan/s2b_ids_1of2.tsv bash probes/deploy_s2.sh <host>   (S2b)
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
. "$PLAN/tools/hosts.sh"
IP=$(host_ip "$NAME") || exit 1
host_ssh "$NAME" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $NAME"; exit 1; }
S="ssh -i $HOME/.ssh/hetzner_g_measure -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
DEST=${DEST:-/root/dpir_s2}
IDS=${IDS:-probes/results_m1/s2_training_set_2026-10-14/s2_ids.tsv}
SMOKE=/root/s2_smoke_$(basename "$DEST")   # a fresh smoke folder per destination: a reused one skips water and tests nothing (19 Oct 2026)
REF=probes/results_m1/s2_smoke_reference_2026-10-14/water_G_omega.json
P=plans/05_delta-probed-ir-pipeline
FILES=(probes/s2_batch.sh probes/s1_anharmonic_level.sh probes/s1_anharmonic_level.py probes/pyscf_hessians_for_qff.py
       probes/library_log.py probes/scf_converge.py probes/make_qff_displacements.py probes/qff_from_hessians.py src/dpir/__init__.py
       src/dpir/qff.py src/dpir/provenance.py probes/results_m1/water_dipole_fd_2026-10-02/geometry.json "$REF" "$IDS")
t() { date '+%T'; }

echo "[$(t) $NAME] 1. the S2 files under $DEST (git archive of HEAD)"
( cd "$PLAN" && git ls-files --error-unmatch "${FILES[@]}" > /dev/null && git diff --quiet HEAD -- "${FILES[@]}" ) \
  || { echo "S2 FILES NOT TRACKED OR NOT COMMITTED — the server runs HEAD"; exit 1; }
$S "test ! -e $DEST && test ! -e $SMOKE" < /dev/null || { echo "$DEST or $SMOKE EXISTS on $NAME — not overwritten"; exit 1; }
# -c core.autocrlf=false: on Windows git archive otherwise writes CRLF into the .py files (19 Oct 2026: runspec's sha256 check failed)
( cd "$PLAN/../.." && git -c core.autocrlf=false archive --format=tar --prefix=x/ HEAD "${FILES[@]/#/$P/}" ) \
  | $S "mkdir -p /root/tmp_s2 && tar xf - -C /root/tmp_s2 && mv /root/tmp_s2/x/$P $DEST && rm -r /root/tmp_s2 && find $DEST -type f | wc -l" \
  || { echo "FILES FAILED $NAME"; exit 1; }
git -C "$PLAN" rev-parse HEAD | $S "cat > $DEST/COMMIT" || exit 1

echo "[$(t) $NAME] 2. the geometries of $IDS (tar, sha256 on both sides)"
mapfile -t GEOMS < <(cut -f2 "$PLAN/$IDS")
( cd "$PLAN" && tar cf - "${GEOMS[@]}" ) | $S "tar xf - -C $DEST" || { echo "GEOMETRY COPY FAILED"; exit 1; }
here_sum=$(cd "$PLAN" && sha256sum "${GEOMS[@]}" | sed 's/ [ *]/ /' | LC_ALL=C sort)
there_sum=$($S "cd $DEST && sha256sum ${GEOMS[*]}" < /dev/null | sed 's/ [ *]/ /' | LC_ALL=C sort)
[ "$here_sum" = "$there_sum" ] || { echo "GEOMETRY SHA256 MISMATCH"; exit 1; }
echo "${#GEOMS[@]} geometries, sha256 equal"

echo "[$(t) $NAME] 3. SMOKE: water through s2_batch.sh at G"
$S "cd $DEST && printf 'water\tprobes/results_m1/water_dipole_fd_2026-10-02/geometry.json\n' > $SMOKE.ids.tsv && PY=/root/miniforge3/envs/qc05/bin/python bash probes/s2_batch.sh $SMOKE.ids.tsv $SMOKE 1 4 'G:6-31g*:75,302' > $SMOKE.log 2>&1; grep '^=== (S2)' $SMOKE.log" < /dev/null
$S "grep -q '=== (S2) water: NOISY' $SMOKE.log && cd $DEST && /root/miniforge3/envs/qc05/bin/python -c \"
import json, numpy as np
a = np.load('$SMOKE/water/G/qff_report.npz')['omega_cm']; ref = json.load(open('$REF', encoding='utf-8'))
print('omega', a.round(3), 'reference', np.round(ref['omega_cm'], 3)); assert np.abs(a - ref['omega_cm']).max() < ref['tolerance_cm']
\"" < /dev/null || { echo "SMOKE FAILED $NAME — see $SMOKE.log"; exit 1; }
echo "[$(t) $NAME] DEPLOY DONE"
