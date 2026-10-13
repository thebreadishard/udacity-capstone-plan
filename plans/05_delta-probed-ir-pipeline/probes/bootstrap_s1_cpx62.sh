#!/usr/bin/env bash
# bootstrap_s1_cpx62.sh <host name in tools/hosts.tsv> (13 Oct 2026, TASKS 53; the user created ubuntu-32gb-hel1-6: 'Doe S1') — a fresh CPX62
# becomes the S1 server: GVPT2 of benzene at three DFT settings (GoalGathering/notes/PreRegistration_2026-10-13_S1_Anharmonic_Level.md, amended
# for the place), which on the laptop would have waited for the five-ring runner until ≈ 25–28 Oct. Steps, each with its marker:
#   1. tools/bootstrap_qc05_env.sh (the labels recipe: qc05, pyscf 2.14.0);
#   2. the S1 files in the plan's own layout under /root/dpir (git archive of HEAD; the files must be committed), and /root/dpir/COMMIT;
#      the benzene geometry lives in the git-ignored corpus, so it goes by scp and is checked by sha256 on both sides;
#   3. SMOKE: the full S1 on water in the parallel mode at the three settings (/root/s1_smoke_water) — the server's env, the files and the
#      parallel path end to end; its R frequencies are printed beside the laptop smoke's (s1_smoke_water_e: 1710.85, 3721.06, 3844.89 cm⁻¹).
# Exit 0 when the smoke ended with 'all settings done'; 1 otherwise.
#   bash probes/bootstrap_s1_cpx62.sh s1
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$HERE/../tools/hosts.sh"
IP=$(host_ip "$NAME") || exit 1
S="ssh -i $HOME/.ssh/hetzner_g_measure -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
t() { date '+%T'; }

echo "[$(t) $NAME] 1. system + miniforge + env qc05"
bash "$HERE/../tools/bootstrap_qc05_env.sh" "$NAME" || exit 1

echo "[$(t) $NAME] 2. the S1 files under /root/dpir (git archive of HEAD)"
P=plans/05_delta-probed-ir-pipeline
FILES=(probes/s1_anharmonic_level.sh probes/s1_anharmonic_level.py probes/pyscf_hessians_for_qff.py probes/make_qff_displacements.py
       probes/qff_from_hessians.py src/dpir/__init__.py src/dpir/qff.py src/dpir/provenance.py
       probes/results_m1/water_dipole_fd_2026-10-02/geometry.json)
GEOM=modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json      # benzene; git-ignored corpus
( cd "$HERE/.." && git ls-files --error-unmatch "${FILES[@]}" > /dev/null && git diff --quiet HEAD -- "${FILES[@]}" ) \
  || { echo "S1 FILES NOT TRACKED OR NOT COMMITTED — the server runs HEAD"; exit 1; }
$S 'test ! -e /root/dpir' < /dev/null || { echo "/root/dpir EXISTS on $NAME — not overwritten (a fresh directory only)"; exit 1; }
( cd "$HERE/../../.." && git archive --format=tar --prefix=dpir/ HEAD "${FILES[@]/#/$P/}" ) | $S 'mkdir -p /root/tmp_dpir && tar xf - -C /root/tmp_dpir && mv /root/tmp_dpir/dpir/plans/05_delta-probed-ir-pipeline /root/dpir && rm -rf /root/tmp_dpir && find /root/dpir -type f | wc -l' \
  || { echo "FILES FAILED $NAME"; exit 1; }
git -C "$HERE" rev-parse HEAD | $S 'cat > /root/dpir/COMMIT' || { echo "COMMIT STAMP FAILED $NAME"; exit 1; }
$S "mkdir -p /root/dpir/$(dirname "$GEOM")" < /dev/null && scp -q -i "$HOME/.ssh/hetzner_g_measure" -o BatchMode=yes "$HERE/../$GEOM" "root@$IP:/root/dpir/$GEOM" \
  && [ "$(sha256sum < "$HERE/../$GEOM" | cut -c1-64)" = "$($S "sha256sum < /root/dpir/$GEOM" < /dev/null | cut -c1-64)" ] \
  || { echo "GEOMETRY COPY FAILED $NAME"; exit 1; }

echo "[$(t) $NAME] 3. SMOKE: S1 on water, parallel, three settings"
$S 'cd /root/dpir && PY=/root/miniforge3/envs/qc05/bin/python PARALLEL=1 bash probes/s1_anharmonic_level.sh probes/results_m1/water_dipole_fd_2026-10-02/geometry.json /root/s1_smoke_water 4 R:6-31g*:99,590 G:6-31g*:75,302 B:6-31g:99,590 > /root/s1_smoke_water.log 2>&1; echo "rc=$?"; grep "^=== (S1)" /root/s1_smoke_water.log | tail -4' < /dev/null
$S 'grep -q "=== (S1) all settings done" /root/s1_smoke_water.log && /root/miniforge3/envs/qc05/bin/python -c "import json; d = json.load(open(\"/root/s1_smoke_water/compare.json\")); print(\"omega_ref\", [round(w, 2) for w in d[\"omega_ref\"]], \"(laptop smoke: 1710.85, 3721.06, 3844.89)\")"' < /dev/null \
  || { echo "SMOKE FAILED $NAME — see /root/s1_smoke_water.log"; exit 1; }
echo "[$(t) $NAME] BOOTSTRAP DONE"
