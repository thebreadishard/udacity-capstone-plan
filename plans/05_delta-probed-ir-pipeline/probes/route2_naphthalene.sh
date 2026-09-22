#!/bin/bash
# Route 2 on hel1-14 (22 September 2026): the two-route quartic-force-field diagnostic on naphthalene at Mackie's level
# (B97-1 / Dunning TZ2P, analytic pyscf Hessians, grid 99/590), step 0.10 in reduced coordinates.
# Chain: optimise -> reference Hessian -> 2n displacement stubs -> 2n Hessians (runner skips finished files; safe to relaunch).
# Reading afterwards: python -m dpir.qff results_m1/route2/naph_hessians_d010 --disp 0.10   (or qff_from_hessians.py, identical numbers)
set -u
PY=/root/miniforge3/envs/qc05/bin/python
export PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=16
cd /root/probes || exit 1
R=results_m1/route2
mkdir -p $R
LOG=$R/route2_naphthalene.log
XC=B97-1; BASIS=CADPAC-TZ2P; DISP=0.10
{
  echo "[$(date '+%F %T')] route 2 naphthalene: $XC / $BASIS, disp $DISP, 16 threads"
  if [ ! -f $R/naph_ref_stub/reference.json ]; then
    $PY route2_optimise.py route2/stageA.json $R/naph_ref_stub --threads 16 --xc $XC --basis $BASIS || { echo "OPTIMISATION FAILED"; exit 1; }
  fi
  echo "[$(date '+%F %T')] optimised; reference Hessian"
  $PY pyscf_hessians_for_qff.py $R/naph_ref_stub $R/naph_ref --xc $XC --basis $BASIS --grid 99,590 --threads 16 || { echo "REFERENCE HESSIAN FAILED"; exit 1; }
  echo "[$(date '+%F %T')] reference Hessian done; displacements"
  $PY make_qff_displacements.py $R/naph_ref/reference.json $R/naph_geoms_d010 --disp $DISP || { echo "DISPLACEMENTS FAILED"; exit 1; }
  mkdir -p $R/naph_hessians_d010
  cp -n $R/naph_ref/reference.json $R/naph_hessians_d010/reference.json   # the reference is not recomputed
  n=$(ls $R/naph_geoms_d010/*.json | wc -l)
  echo "[$(date '+%F %T')] $n stubs; Hessians start (expected ≈ 28 min each)"
  $PY pyscf_hessians_for_qff.py $R/naph_geoms_d010 $R/naph_hessians_d010 --xc $XC --basis $BASIS --grid 99,590 --threads 16 || { echo "HESSIANS FAILED"; exit 1; }
  echo "[$(date '+%F %T')] ROUTE 2 NAPHTHALENE DONE: $(ls $R/naph_hessians_d010/*.json | wc -l) Hessians in $R/naph_hessians_d010"
} >> $LOG 2>&1
