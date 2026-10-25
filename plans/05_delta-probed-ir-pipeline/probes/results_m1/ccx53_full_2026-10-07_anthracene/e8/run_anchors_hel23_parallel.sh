#!/bin/bash
# Anchor set two, parallel form (the user, 29 Sep 2026 ≈ 07:1x: "Zet de keten maar aan na benzonitril"). pyscf's CCSD(T) gradient keeps ≈ 3.4 of 16
# cores busy, so one molecule is run as W partial runs in parallel (--ks slices of the symmetry-unique displacements, T threads and M MB each; the
# naphthalene pattern of 24 Sep), then one assembling run computes any gradient still missing and the Hessian. Memory guard: 31 GB on the CPX62;
# when available memory drops under GUARD_MB the youngest partial run is stopped by pid (its slice is finished by the assembling run).
# Sequence (30 Sep 2026 restart on the corrected route: explicit (T) lambda, gate-1 stamp, --fast-t-density on the RHF molecules, UHF dvvVV fix):
# benzonitrile (2 × 8 threads) → fluorobenzene (3 × 5) → pyridine (3 × 5) → benzene cation (2 × 8, UHF needs twice the memory) → CHAIN FINISHED.
# 30 Sep 08:3x: FAST also carries --fast-t-lambda (the (T)-lambda C kernel; benzene 44 s vs pyscf 373 s, agreement 1e-16).
# The 29 Sep benzonitrile gradients (CCSD lambda) were moved to results/benzonitrile_ccpvdz_INVALID_ccsd_lambda. FAST="" drops the C kernel.
# Every step writes one ANCHOR … line to anchors.log for the poller.
# 1 Oct 2026: ANCHOR_LIST (lines of `name|geometry|out|workers|threads|mem_mb|extra args`) replaces the default four anchors below; the naphthalene
# run on ubuntu-32gb-hel1-2 uses it with one entry. An entry's extra args come after $FAST; an empty field means none.
# Smoke (WSL, water): ROOT=<dir with e8_cc_hessian_fd.py, e8_symmetry.py> PY=<python> LOG=<file> SMOKE=<geometry.json> bash run_anchors_hel23_parallel.sh
set -euo pipefail
ROOT=${ROOT:-/root/e8}
PY=${PY:-/root/miniforge3/envs/qc05/bin/python}
LOG=${LOG:-/root/e8/anchors.log}
CORPUS=${CORPUS:-/root/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/corpus}
GUARD_MB=${GUARD_MB:-1500}
FAST=${FAST---fast-t-density --fast-t-lambda}
TWO_ROUTE=${TWO_ROUTE:-inline}   # 2 Oct 2026: 'separate' runs the kernel two-route checks in a lane beside the partial runs (CT threads, CM MB)
CT=${CT:-8}; CM=${CM:-16000}
SKIP=${SKIP:-}   # space-separated anchor names to leave out (30 Sep 2026: benzonitrile's Hessian awaits a verdict; the rest goes on)
skipped() { [[ " $SKIP " == *" $1 "* ]] && say "ANCHOR $1 SKIPPED (SKIP)"; }
SMOKE=${SMOKE:-}
cd "$ROOT"
say() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

finish() {   # name out rc: the DONE/IMAGINARY/FAILED line, from the assembling run's exit code (0 / 4 / other) and its file (review, 30 Sep)
  local name=$1 out=$2 rc=${3:-1}
  if [ "$rc" -eq 4 ] && [ -f "$out/hessian_ccsd_t_IMAGINARY.npz" ]; then   # computed correctly, not a minimum — excluded, the chain goes on
    say "ANCHOR $name IMAGINARY (excluded from read-outs; see $out/e8_fd.log)"; return 0
  elif [ "$rc" -eq 0 ] && [ -f "$out/hessian_ccsd_t.npz" ]; then
    say "ANCHOR $name DONE: $(grep -o 'symmetry: .*' "$out/e8_fd.log" | tail -1); $(grep -o 'FD asymmetry max [^;]*' "$out/e8_fd.log" | tail -1)"
  else
    say "ANCHOR $name FAILED (see $out/e8_fd.log)"; return 1
  fi
}

n_unique() {   # geometry -> number of symmetry-unique displacements, by the probe's own code
  "$PY" - "$1" <<'EOF'
import json, sys
import numpy as np
import e8_symmetry as S
g = json.load(open(sys.argv[1])); x = np.array(g["coords_bohr"], float)
ops = S.point_group_ops(g["symbols"], x); ks, _ = S.unique_displacements(ops, len(g["symbols"]))
print(len(ks))
EOF
}

anchor_parallel() {   # name geom out workers threads mem_mb [extra e8 args]
  local name=$1 geom=$2 out=$3 W=$4 T=$5 M=$6; shift 6
  mkdir -p "$out"
  say "ANCHOR $name START (parallel: $W partial runs x $T threads x $M MB) ($geom)"
  OMP_NUM_THREADS=16 "$PY" e8_cc_hessian_fd.py "$geom" "$out" --threads 16 --symmetry --only-reference --two-route-check "$TWO_ROUTE" "$@" >> "$out/chain.log" 2>&1 \
    || { say "ANCHOR $name FAILED (reference gradient; see $out/e8_fd.log)"; return 1; }
  local nk; nk=$(n_unique "$geom")
  say "ANCHOR $name: $nk symmetry-unique displacements over $W partial runs"
  local pids=() lo hi i
  if [ "$TWO_ROUTE" = "separate" ]; then     # the slow-route comparison runs beside the partial runs; the assembly requires its passing file
    OMP_NUM_THREADS=$CT nohup "$PY" e8_cc_hessian_fd.py "$geom" "$out" --threads "$CT" --two-route-check only --max-memory "$CM" "$@" > "$out/two_route_check.log" 2>&1 &
    pids+=($!); say "ANCHOR $name: two-route check lane started (pid $!, $CT threads, $CM MB)"; sleep 5
  fi
  for ((i = 0; i < W; i++)); do
    lo=$((i * nk / W)); hi=$(((i + 1) * nk / W))
    [ "$lo" -ge "$hi" ] && continue
    OMP_NUM_THREADS=$T nohup "$PY" e8_cc_hessian_fd.py "$geom" "$out" --threads "$T" --symmetry --ks "$lo:$hi" --max-memory "$M" "$@" > "$out/partial_${lo}-${hi}.log" 2>&1 &
    pids+=($!); sleep 5
  done
  local alive avail victim
  while true; do
    alive=()
    for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive+=("$p"); done
    [ "${#alive[@]}" -eq 0 ] && break
    avail=$(free -m | awk '/Mem:/{print $7}')
    if [ "$avail" -lt "$GUARD_MB" ] && [ "${#alive[@]}" -gt 1 ]; then
      victim=${alive[$((${#alive[@]} - 1))]}
      say "ANCHOR $name: memory guard — ${avail} MB available, stopping partial run pid $victim (its slice is finished by the assembling run)"
      kill -TERM "$victim" 2>/dev/null || true; sleep 30
    fi
    sleep 30
  done
  for p in "${pids[@]}"; do wait "$p" 2>/dev/null || true; done
  if grep -q "PAIR CHECK FAILED" "$out/e8_fd.log"; then say "ANCHOR $name FAILED (pair check; see $out/e8_fd.log)"; return 1; fi
  say "ANCHOR $name: partial runs done ($(ls "$out"/grad_*.npy 2>/dev/null | wc -l) gradient files) -> assembling run"
  rm -f "$out/hessian_ccsd_t.npz" "$out/hessian_ccsd_t_INVALID.npz" "$out/hessian_ccsd_t_IMAGINARY.npz"   # no stale verdict (review, 30 Sep)
  local rc=0
  OMP_NUM_THREADS=16 "$PY" e8_cc_hessian_fd.py "$geom" "$out" --threads 16 --symmetry "$@" >> "$out/chain.log" 2>&1 || rc=$?
  finish "$name" "$out" "$rc"
}

if [ -n "$SMOKE" ]; then    # water: reference, two partial runs of one thread, assembly — the whole pattern in a few minutes
  anchor_parallel smoke_parallel "$SMOKE" results/smoke_parallel 2 1 1500 $FAST
  say "SMOKE PARALLEL OK"; exit 0
fi

DEFAULT_LIST="benzonitrile|molecules/A_3100da3761/geometry.json|results/benzonitrile_ccpvdz|2|8|12000|$FAST
fluorobenzene|$CORPUS/molecules/B_8b12a55d3a/geometry.json|results/fluorobenzene_ccpvdz|3|5|8000|$FAST
pyridine|$CORPUS/molecules/A_6e858b26e5/geometry.json|results/pyridine_ccpvdz|3|5|8000|$FAST
benzene_cation|cations/benzene/geometry.json|results/benzene_cation_ccpvdz|2|8|11000|--charge 1 --spin 1"
ANCHOR_LIST=${ANCHOR_LIST:-$DEFAULT_LIST}
say "chain (corrected route) start on $(hostname)"
while IFS='|' read -r name geom out W T M extra; do
  [ -z "$name" ] && continue
  # shellcheck disable=SC2086   # extra is a list of probe arguments, split on purpose
  skipped "$name" || anchor_parallel "$name" "$geom" "$out" "$W" "$T" "$M" $extra
done <<< "$ANCHOR_LIST"
say "CHAIN FINISHED"
