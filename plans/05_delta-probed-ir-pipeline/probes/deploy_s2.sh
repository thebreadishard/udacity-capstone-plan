#!/usr/bin/env bash
# probes/deploy_s2.sh <host name in tools/hosts.tsv> (14 Oct 2026, S2; registration GoalGathering/notes/PreRegistration_2026-10-14_S2_Anharmonic_Shift.md)
# — puts S2 on a server that already has the qc05 env (probes/bootstrap_s1_cpx62.sh step 1): the runner files in the plan's layout under a
# fresh /root/dpir_s2 (git archive of HEAD; the files must be committed), /root/dpir_s2/COMMIT, the 19 corpus geometries of the id list by
# tar over ssh with a sha256 check (the corpus is git-ignored), and a SMOKE: water through probes/s2_batch.sh at G, whose ω must equal the
# S1 smoke's G (/root/s1_smoke_water/G) — the same env, setting and runner on the same server. Water at G trips the noise guard (S1 smoke,
# 14.8 cm⁻¹), so the smoke expects 'water: NOISY'. Exit 0 when the smoke passed.
#   bash probes/deploy_s2.sh s1
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
. "$PLAN/tools/hosts.sh"
IP=$(host_ip "$NAME") || exit 1
host_ssh "$NAME" 'true' || { echo "WRONG OR UNREACHABLE MACHINE $NAME"; exit 1; }
S="ssh -i $HOME/.ssh/hetzner_g_measure -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
DEST=/root/dpir_s2
IDS=probes/results_m1/s2_training_set_2026-10-14/s2_ids.tsv
P=plans/05_delta-probed-ir-pipeline
FILES=(probes/s2_batch.sh probes/s1_anharmonic_level.sh probes/s1_anharmonic_level.py probes/pyscf_hessians_for_qff.py
       probes/make_qff_displacements.py probes/qff_from_hessians.py src/dpir/__init__.py src/dpir/qff.py src/dpir/provenance.py
       probes/results_m1/water_dipole_fd_2026-10-02/geometry.json "$IDS")
t() { date '+%T'; }

echo "[$(t) $NAME] 1. the S2 files under $DEST (git archive of HEAD)"
( cd "$PLAN" && git ls-files --error-unmatch "${FILES[@]}" > /dev/null && git diff --quiet HEAD -- "${FILES[@]}" ) \
  || { echo "S2 FILES NOT TRACKED OR NOT COMMITTED — the server runs HEAD"; exit 1; }
$S "test ! -e $DEST" < /dev/null || { echo "$DEST EXISTS on $NAME — not overwritten"; exit 1; }
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
$S "cd $DEST && printf 'water\tprobes/results_m1/water_dipole_fd_2026-10-02/geometry.json\n' > /root/s2_smoke_ids.tsv && PY=/root/miniforge3/envs/qc05/bin/python bash probes/s2_batch.sh /root/s2_smoke_ids.tsv /root/s2_smoke 1 4 'G:6-31g*:75,302' > /root/s2_smoke.log 2>&1; grep '^=== (S2)' /root/s2_smoke.log" < /dev/null
$S "grep -q '=== (S2) water: NOISY' /root/s2_smoke.log && /root/miniforge3/envs/qc05/bin/python -c \"
import numpy as np
a = np.load('/root/s2_smoke/water/G/qff_report.npz')['omega_cm']; b = np.load('/root/s1_smoke_water/G/qff_report.npz')['omega_cm']
print('omega', a.round(3), 'S1 smoke G', b.round(3)); assert np.abs(a - b).max() < 1e-3
\"" < /dev/null || { echo "SMOKE FAILED $NAME — see /root/s2_smoke.log"; exit 1; }
echo "[$(t) $NAME] DEPLOY DONE"
