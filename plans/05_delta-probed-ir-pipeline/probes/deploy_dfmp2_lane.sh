#!/usr/bin/env bash
# probes/deploy_dfmp2_lane.sh <host in tools/hosts.tsv> (21 Nov 2026; TASKS 291) — puts the MP2 basis step's lane (probes/dfmp2_lane.sh)
# on an anchor server that has the psi4 env qc (tools/bootstrap_psi4_env.sh). Steps, each with its marker:
#   1. the lane's files under a fresh DEST (probes/deploy_lib.sh's deploy_code: closed under their own imports, tracked and committed,
#      git archive of HEAD), DEST/COMMIT;
#   2. DEST/list.txt, made on the server from what it holds: the CC wave's molecules (/root/dpir/wave.txt, their geometries under
#      /root/dpir/geoms) first, then the DFT batch's (/root/dft1/ids.txt, geometries written by the optimisation under
#      /root/dft1/molecules) — each server's own molecules, in its own cheapest-first order; a list without a molecule is refused;
#   3. check W on the server (dfmp2_rows.py water: the analytic DF-MP2 gradient against 5-point finite differences of the energy at
#      cc-pVDZ and cc-pVTZ, line 1e-6 Eh/bohr) under the lane's cap: the registration's check was run on psi4 1.10.2, the servers
#      carry 1.11, so it is run again where the rows will be computed. No pass, no lane.
# The run's own settings and its dry run belong to its runspec. `--list-files` prints the file list and contacts no server.
#   DEST=/root/mp2a bash probes/deploy_dfmp2_lane.sh anc1
# no-set-e: every step checks its own result and stops with a named marker
set -u
NAME=${1:?host name, or --list-files}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLAN=$(cd "$HERE/.." && pwd)
CORPUS=modules/05_support_predictor/corpus
FILES=(probes/dfmp2_lane.sh probes/dfmp2_rows.py probes/dfmp2_swap_check.py probes/cc_composite_full_check.py
       probes/cc_composite_basis_check.py probes/anchor_deck_rehearsal.py probes/e8_symmetry.py probes/qc_common.py probes/library_log.py
       probes/wsl_capped.sh probes/cation_oom_check.sh "$CORPUS/constants.py" "$CORPUS/vibrations.py" src/dpir/__init__.py
       src/dpir/symmetry.py)
if [ "$NAME" = --list-files ]; then printf '%s\n' "${FILES[@]}"; exit 0; fi
DEST=${DEST:?DEST, a fresh folder on the server}
QC=/root/miniforge3/envs/qc/bin/python
. "$HERE/deploy_lib.sh"

deploy_connect || exit 1
$S "test -x $QC" < /dev/null || { echo "NO PSI4 ENV on $NAME (tools/bootstrap_psi4_env.sh)"; exit 1; }
deploy_code "MP2 lane" || exit 1

echo "[$(t) $NAME] 2. list.txt from the server's own wave and DFT batch"
$S "cd $DEST && { cut -d'|' -f1,2 /root/dpir/wave.txt; grep -v '^#' /root/dft1/ids.txt | sed '/^\$/d; s#.*#&|/root/dft1/molecules/&/geometry.json#'; } > list.txt \
    && test -s list.txt && ! cut -d'|' -f1 list.txt | sort | uniq -d | grep -q . && echo \"\$(wc -l < list.txt) molecules\"" < /dev/null \
  || { echo "LIST FAILED on $NAME (no wave or DFT batch there, or a molecule listed twice)"; exit 1; }

echo "[$(t) $NAME] 3. check W (water, DF-MP2 analytic gradient against finite differences) under a 2048 MB cap"
$S "mkdir -p $DEST/check_w /root/psi4_scratch && cd $DEST && PSI_SCRATCH=/root/psi4_scratch OMP_NUM_THREADS=2 CAP_SCOPE=system \
    bash probes/wsl_capped.sh 2048 -- $QC probes/dfmp2_rows.py water --out check_w/water.json --threads 2 --memory-gb 1 > check_w/water.log 2>&1; \
    grep -a 'water cc-pv\\|WATER CHECK' check_w/water.log; grep -qa '=== WATER CHECK PASS' check_w/water.log" < /dev/null \
  || { echo "CHECK W FAILED on $NAME — see $DEST/check_w/water.log; no MP2 rows are computed there"; exit 1; }
echo "[$(t) $NAME] DEPLOY DONE"
