#!/usr/bin/env bash
# probes/anchor_apt_rerun.sh <name> [threads] [max_memory_mb] (14 Oct 2026) — re-run the CC APT by the field route for one anchor of set three whose Hessian is DONE
# and whose APT step failed, with the same two commands as probes/anchor_wave.sh (cc_apt_field.py, then cc_apt_field_check.py against the
# FD-dipole route at line 1e-3), beside a running wave (default 8 threads, nice 5, 6 GB: at 12 GB the first re-run met acenaphthylene's two
# 10.5 GB partial runs and the memory guard stopped it). Each field's gradient is kept (cc_apt_field.py --cache-dir), so a stopped re-run resumes. The failed attempt's log is kept as
# apt_field_failed_<time>.log; the marker '=== (AS3) <name> apt PASS|FAIL' goes to the wave's log, so the watch and probes/fetch_anchor.sh
# treat it as the wave's own. Run on the anchor server from /root/dpir/probes:
#   bash anchor_apt_rerun.sh azulene 8
# no-set-e: the check's exit decides the marker
set -u
NAME=${1:?anchor name}; THR=${2:-8}; MEM=${3:-6000}
PY=${PY:-/root/miniforge3/envs/qc05/bin/python}
LOG=${LOG:-/root/dpir/anchors.log}
out="results/${NAME}_ccpvdz"
geom="/root/dpir/geoms/${NAME}/geometry.json"
mark() { echo "=== (AS3) $* $(date '+%F %T')" | tee -a "$LOG"; }
[ -f "$out/hessian_ccsd_t.npz" ] || { echo "$NAME: no Hessian — the wave's job, not a re-run's"; exit 1; }
[ -f "$geom" ] || { echo "$NAME: no geometry at $geom"; exit 1; }
apt="$out/apt_ccsd_t_field.npz"
[ -f "$apt" ] && { echo "$apt exists — nothing to re-run"; exit 1; }
[ -f "$out/apt_field.log" ] && mv "$out/apt_field.log" "$out/apt_field_failed_$(date +%Y%m%d_%H%M%S).log"
mark "$NAME apt re-run started ($THR threads, $MEM MB, nice 5; cc_dipole_capture $(grep -o '^MAX_CYCLE = [0-9]*' cc_dipole_capture.py))"
OMP_NUM_THREADS=$THR nice -n 5 "$PY" cc_apt_field.py "$geom" --out "$apt" --basis cc-pvdz --threads "$THR" --max-memory "$MEM" --fast \
  > "$out/apt_field.log" 2>&1 < /dev/null
ref=(); [ -f "$out/apt_ccsd_t.npz" ] && ref=(--ref "$out/apt_ccsd_t.npz" --line 1e-3)
if "$PY" cc_apt_field_check.py "$apt" "${ref[@]}" > "$out/apt_check.log" 2>&1 < /dev/null; then mark "$NAME apt PASS $(cut -c1-120 "$out/apt_check.log")"
else mark "$NAME apt FAIL (see $out/apt_check.log)"; fi
