#!/bin/bash
# Obstacle 9 chain on hel1-14 (24 September 2026; the user: "Zet benzeen⁺ en naftaleen⁺ maar op hel1-14 zodra route 2 klaar is").
# 1. waits for the environments (prep_cation_envs.sh: env qc = psi4 1.11, env qclno = qc05 + the laptop's LNO code);
# 2. smokes both paths on the water cation at once (light, niced) so a broken path shows tonight, not on Friday;
# 3. waits for route 2 (ROUTE 2 NAPHTHALENE DONE in its log, or its process gone);
# 4. cation rows benzene+ and naphthalene+ (UKS deck v1-cation, 16 threads, 24 GB), then the ULNO-CCSD(T)/cc-pVDZ price of each (three points).
# Markers on stdout (the wrapper log): SMOKES OK | CATIONS FAILED: <step> | CATION ROWS DONE | CATIONS DONE.
set -u
cd /root/cations || exit 1
QC=/root/miniforge3/envs/qc/bin/python; QL=/root/miniforge3/envs/qclno/bin/python
export LD_LIBRARY_PATH=/root/miniforge3/envs/qclno/lib PYSCF_TMPDIR=/root/qc_tmp TMPDIR=/root/qc_tmp; mkdir -p /root/qc_tmp
t() { date '+%F %T'; }
echo "[$(t)] waiting for the environments"
until grep -q "PREP DONE" /root/prep_cation_envs.log 2>/dev/null; do sleep 60; done
grep -q "qclno ulno ok" /root/prep_cation_envs.log || { echo "CATIONS FAILED: env qclno has no working ULNO (see /root/prep_cation_envs.log)"; exit 1; }
echo "[$(t)] smokes (water cation, 4 threads, niced)"
nice -n 10 $QC cation_rows.py --smoke --out smoke_rows --worker psi4_worker.py --deck deck_v1_cation.json --threads 4 --memory-gb 4 || { echo "CATIONS FAILED: rows smoke"; exit 1; }
nice -n 10 $QL l3_ulno_price.py --smoke smoke_price --threads 4 --max-memory 4000 || { echo "CATIONS FAILED: price smoke"; exit 1; }
echo "SMOKES OK"
echo "[$(t)] waiting for route 2"
R2=/root/probes/results_m1/route2/route2_naphthalene.log
until grep -q "ROUTE 2 NAPHTHALENE DONE" $R2 2>/dev/null || ! pgrep -f "[r]oute2_naphthalene.sh" > /dev/null; do sleep 300; done
grep -q "ROUTE 2 NAPHTHALENE DONE" $R2 || echo "[$(t)] route 2 ended without its DONE marker — the machine is free, cations start"
for m in benzene naphthalene; do
  echo "[$(t)] cation rows: $m+"
  $QC cation_rows.py --name $m --geometry in/$m/geometry.json --out rows/$m --worker psi4_worker.py --deck deck_v1_cation.json --threads 16 --memory-gb 24 || { echo "CATIONS FAILED: rows $m"; exit 1; }
done
echo "CATION ROWS DONE"
for m in benzene naphthalene; do
  echo "[$(t)] ULNO price: $m+"
  $QL l3_ulno_price.py rows/$m price/$m --threads 16 --max-memory 24000 || { echo "CATIONS FAILED: price $m"; exit 1; }
done
echo "CATIONS DONE"
