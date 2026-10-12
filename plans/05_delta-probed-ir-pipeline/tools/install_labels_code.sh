#!/usr/bin/env bash
# tools/install_labels_code.sh "<install.log note>" (12 Oct 2026, TASKS 44 (a)) — installs the labels route's two files (corpus/apt.py and
# corpus/analytic_hessians.py) on the labels server while its lanes run, as route C (11 Oct) and the software stamp were installed by hand:
#   1. both files to /root/labels/staging_apt, a water smoke there (analytic_hessians.py on water at grid 50,194, 2 threads, nice 19); the APT
#      file must say passed and carry the stamp of the files sent; no smoke, no install;
#   2. the current copies kept as <file>.before_<date>_<hhmm>;
#   3. apt.py first, then analytic_hessians.py, each by cp to <file>.new + mv (atomic): the lanes start one python per molecule, and the old
#      script runs with the new apt.py (every name it imports is kept), so no molecule can start between two incompatible files;
#   4. one line to /root/labels/install.log; the sha256 on the server checked against the laptop's.
# Exit 0 installed; 1 the smoke or a check failed (nothing installed); 3/255 wrong machine / unreachable (from host_ssh).
# no-set-e: every step is checked by hand (a failed smoke or check prints why and exits 1 before anything is installed)
set -u
NOTE=${1:?an install.log note is required}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CORPUS="$HERE/../modules/05_support_predictor/corpus"
. "$HERE/hosts.sh"
IP=$(host_ip labels) || exit 4
SCP=${HOSTS_SCP:-scp -o BatchMode=yes -o ConnectTimeout=20 -i $HOME/.ssh/hetzner_g_measure}
host_ssh labels 'test -d /root/labels/staging_apt/water' || { echo "no staging_apt/water on the labels server (or wrong machine)"; exit 1; }
$SCP "$CORPUS/apt.py" "$CORPUS/analytic_hessians.py" "root@$IP:/root/labels/staging_apt/" || exit 1
local_sha=$(cd "$CORPUS" && sha256sum apt.py analytic_hessians.py | awk '{print substr($1, 1, 12)}' | paste -sd' ')
smoke=$(host_ssh labels 'cd /root/labels/staging_apt && find water -maxdepth 1 -type f ! -name geometry.json -delete &&
  OMP_NUM_THREADS=2 nice -n 19 /root/miniforge3/envs/qc05/bin/python analytic_hessians.py water --threads 2 --grid 50,194 > smoke.log 2>&1; echo rc=$?;
  /root/miniforge3/envs/qc05/bin/python -c "
import json, numpy as np
z = np.load(\"water/dipole_b3lyp_cphf.npz\"); s = json.loads(str(z[\"software\"]))[\"sha256\"]
print(\"smoke\", bool(z[\"passed\"]), str(z[\"route\"]), float(z[\"cphf_residual_before\"]), float(z[\"cphf_residual_after\"]), s[\"apt.py\"], s[\"analytic_hessians.py\"])"')
echo "$smoke"
echo "$smoke" | grep -q '^rc=0$' || { echo "SMOKE FAILED: nothing installed"; exit 1; }
read -r a_sha h_sha <<< "$local_sha"
echo "$smoke" | grep -Eq "^smoke True hessian_response_refined [^ ]+ [^ ]+ $a_sha $h_sha\$" || { echo "SMOKE CHECK FAILED (expected stamp $a_sha $h_sha): nothing installed"; exit 1; }
stamp=$(date +%Y-%m-%d_%H%M)
out=$(host_ssh labels "cd /root/labels && cp apt.py apt.py.before_$stamp && cp analytic_hessians.py analytic_hessians.py.before_$stamp &&
  cp staging_apt/apt.py apt.py.new && mv apt.py.new apt.py && cp staging_apt/analytic_hessians.py analytic_hessians.py.new && mv analytic_hessians.py.new analytic_hessians.py &&
  echo \"[\$(date '+%F %T')] apt.py + analytic_hessians.py → $NOTE (water smoke in staging_apt passed); previous copies *.before_$stamp\" >> install.log &&
  sha256sum apt.py analytic_hessians.py | awk '{print substr(\$1, 1, 12)}' | paste -sd' '; tail -1 install.log")
echo "$out"
[ "$(echo "$out" | head -1)" = "$local_sha" ] || { echo "SHA MISMATCH after install: server $(echo "$out" | head -1), laptop $local_sha"; exit 1; }
echo "INSTALLED ($local_sha)"
