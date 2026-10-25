#!/usr/bin/env bash
# anthracene_oop_rows_ccx53.sh (6 Oct 2026, 19:0x). Test 3 of the composite anchor level (design note of 4 Oct, amendment of 6 Oct): the MP2 rows of
# anthracene's seven out-of-plane unique displacements at cc-pVDZ and cc-pVTZ, in the molecule's plane frame, on the anthracene CCX53 beside the
# still-running pyscf two-route lane (pid 60393, 8 threads). Two lanes of 8 threads: lane A = the DZ rows (cheap) then TZ displacements 2,8,11,14;
# lane B = TZ displacements 44,50,53. Each `compute` prints a line per displacement (its own heartbeat); a watcher adds an hourly status line.
# Inputs on the server: ~/e8/composite/{cc_composite_full_check.py,cc_composite_basis_check.py,e8_symmetry.py,geometry_planeframe.json}; env qc05.
# Outputs: ~/e8/composite/mp2_rows_anthracene_oop_{ccpvdz,ccpvtz_a,ccpvtz_b}.npz → merged mp2_rows_anthracene_oop_ccpvtz.npz; markers in
# ~/e8/composite/oop_rows.log ("=== OOP ROWS DONE" / "FAILED"). The read (repair-oop) runs on the laptop after the fetch.
#   nohup bash anthracene_oop_rows_ccx53.sh >> ~/e8/composite/oop_rows.log 2>&1 &
set -uo pipefail
# no-set-e: each lane writes its own marker; the merge runs only when both lanes succeeded
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp
mkdir -p "$HOME/qc_tmp"
W=$HOME/e8/composite
PY=/root/miniforge3/envs/qc05/bin/python
G=$W/geometry_planeframe.json
t() { date -u '+%F %T UTC'; }
cd "$W" || exit 1
echo "=== OOP ROWS start: lanes A (DZ all, then TZ 2,8,11,14) and B (TZ 44,50,53), 8 threads each, max_memory 30000 $(t)"

( OMP_NUM_THREADS=8 $PY cc_composite_full_check.py compute "$G" mp2_rows_anthracene_oop_ccpvdz.npz --basis cc-pvdz --threads 8 --max-memory 30000 --ks 2,8,11,14,44,50,53 > lane_a_dz.log 2>&1 \
    && echo "=== lane A: DZ rows done $(t)" || { echo "=== lane A: DZ ROWS FAILED $(t)"; exit 1; }
  OMP_NUM_THREADS=8 $PY cc_composite_full_check.py compute "$G" mp2_rows_anthracene_oop_ccpvtz_a.npz --basis cc-pvtz --threads 8 --max-memory 30000 --ks 2,8,11,14 > lane_a_tz.log 2>&1 \
    && echo "=== lane A: TZ rows 2,8,11,14 done $(t)" || { echo "=== lane A: TZ ROWS FAILED $(t)"; exit 1; } ) &
A=$!
( OMP_NUM_THREADS=8 $PY cc_composite_full_check.py compute "$G" mp2_rows_anthracene_oop_ccpvtz_b.npz --basis cc-pvtz --threads 8 --max-memory 30000 --ks 44,50,53 > lane_b_tz.log 2>&1 \
    && echo "=== lane B: TZ rows 44,50,53 done $(t)" || { echo "=== lane B: TZ ROWS FAILED $(t)"; exit 1; } ) &
B=$!
( while kill -0 "$A" 2>/dev/null || kill -0 "$B" 2>/dev/null; do
    sleep 3600
    echo "--- heartbeat $(t): $(grep -c '] mp2' lane_a_dz.log lane_a_tz.log lane_b_tz.log 2>/dev/null | tr '\n' ' ') displacements done; $(free -g | awk '/Mem:/{print $7 " GB free"}')"
  done ) &
wait "$A"; ra=$?
wait "$B"; rb=$?
if [ "$ra" -eq 0 ] && [ "$rb" -eq 0 ]; then
  $PY cc_composite_full_check.py merge mp2_rows_anthracene_oop_ccpvtz.npz mp2_rows_anthracene_oop_ccpvtz_a.npz mp2_rows_anthracene_oop_ccpvtz_b.npz \
    && echo "=== OOP ROWS DONE — fetch mp2_rows_anthracene_oop_{ccpvdz,ccpvtz}.npz and run repair-oop $(t)" || echo "=== OOP ROWS MERGE FAILED $(t)"
else
  echo "=== OOP ROWS FAILED (lane A rc $ra, lane B rc $rb) $(t)"
fi
