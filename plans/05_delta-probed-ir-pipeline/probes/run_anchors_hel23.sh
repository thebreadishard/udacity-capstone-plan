#!/bin/bash
# Anchor set two (pre-registration 2026-09-29, Anchor_Set_Two) on ubuntu-32gb-hel1-23 (CPX62, 16 shared vCPU, 30 GB): one CCSD(T)/cc-pVDZ
# finite-difference Hessian at a time with e8_cc_hessian_fd.py --symmetry (pyscf's CCSD(T) gradient does not scale past 16 threads, 24 Sep 2026).
# Order: smokes (water, water cation — the open-shell path of 29 Sep must run before the chain spends hours) → corpus steps for fluorobenzene and
# pyridine (psi4, minutes) → benzonitrile → fluorobenzene → pyridine → benzene cation (UHF-UCCSD(T)). Every step writes one ANCHOR … DONE/FAILED
# line to anchors.log for the poller; the pair check of every coordinate is in each run's e8_fd.log as it lands.
set -euo pipefail
cd /root/e8
PY=/root/miniforge3/envs/qc05/bin/python
QC=/root/miniforge3/envs/qc/bin/python
export CORPUS_QC_PYTHON=$QC     # run_corpus.py finds the psi4 worker's python through this variable (first launch of 29 Sep stopped here)
CORPUS=/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/corpus
LOG=/root/e8/anchors.log
T=16
say() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

anchor() {   # name geometry out [extra e8 args]; returns 1 on failure so that the chain stops (set -e) and the poller sees FAILED
  local name=$1 geom=$2 out=$3; shift 3
  say "ANCHOR $name START ($geom)"
  mkdir -p "$out"
  if OMP_NUM_THREADS=$T "$PY" e8_cc_hessian_fd.py "$geom" "$out" --threads $T --symmetry "$@" >> "$out/chain.log" 2>&1 && [ -f "$out/hessian_ccsd_t.npz" ]; then
    say "ANCHOR $name DONE: $(grep -o 'symmetry: .*' "$out/e8_fd.log" | tail -1); $(grep -o 'FD asymmetry max [^;]*' "$out/e8_fd.log" | tail -1)"
  else
    say "ANCHOR $name FAILED (see $out/e8_fd.log)"; return 1
  fi
}

say "chain start on $(hostname), $(nproc) threads"
anchor water_smoke smoke/water.json results/smoke_water
anchor water_cation_smoke smoke/water.json results/smoke_water_cation --charge 1 --spin 1
say "SMOKES OK"

say "corpus steps: fluorobenzene B_8b12a55d3a and pyridine A_6e858b26e5 (psi4 deck v1, B3LYP geometry + both Hessians)"
( cd "$CORPUS" && OMP_NUM_THREADS=$T "$QC" run_corpus.py --ids B_8b12a55d3a,A_6e858b26e5 --threads $T --memory-gb 24 >> /root/e8/corpus_steps.log 2>&1 ) \
  || { say "CORPUS STEP FAILED (run_corpus.py exit $?; see corpus_steps.log)"; exit 1; }
for id in B_8b12a55d3a A_6e858b26e5; do
  [ -f "$CORPUS/molecules/$id/geometry.json" ] || { say "CORPUS STEP FAILED for $id (no geometry.json)"; exit 1; }
done
say "CORPUS STEPS DONE"

anchor benzonitrile molecules/A_3100da3761/geometry.json results/benzonitrile_ccpvdz
anchor fluorobenzene "$CORPUS/molecules/B_8b12a55d3a/geometry.json" results/fluorobenzene_ccpvdz
anchor pyridine "$CORPUS/molecules/A_6e858b26e5/geometry.json" results/pyridine_ccpvdz
anchor benzene_cation cations/benzene/geometry.json results/benzene_cation_ccpvdz --charge 1 --spin 1
say "CHAIN FINISHED"
