#!/usr/bin/env bash
# probes/anchor_wave.sh <list file> (12 Oct 2026; anchor set three, GoalGathering/notes/PreRegistration_2026-10-12_Anchor_Set_Three.md) — runs ON an
# anchor server bootstrapped by probes/bootstrap_anchors_cpx62.sh. One line per molecule in the list: name|geometry.json|workers|threads|mem_mb.
# Per molecule, in order:
#   1. the CCSD(T)/cc-pVDZ FD Hessian, through probes/run_anchors_hel23_parallel.sh with that one entry (its own ANCHOR … lines go to the log);
#   2. if the Hessian is DONE, the CC APT by the field route (probes/cc_apt_field.py, 16 threads), checked by probes/cc_apt_field_check.py.
#      The sum rule must be ≤ 1e-6. The FD run writes its own CC APT from the captured relaxed dipoles (apt_ccsd_t.npz, since 3 Oct), so the
#      two routes are compared as F2 compared them on benzene: max |ΔP| ≤ 1e-3 e (water smoke on anchors3, 12 Oct).
# Results go to /root/dpir/probes/results/<name>_ccpvdz/. The log is /root/dpir/anchors.log. Its markers are lines starting
# "=== (AS3) ": "<name> hessian DONE|FAILED|IMAGINARY", "<name> apt PASS|FAIL", and "wave done" at the end. probes/watch.sh reports them
# (check_anchors3). A molecule whose Hessian file already exists is not recomputed, so a relaunch resumes the wave.
#   setsid nohup bash /root/dpir/probes/anchor_wave.sh /root/dpir/wave1.txt > /dev/null 2>&1 < /dev/null &
# TWO_ROUTE (default 'energy' since 13 Oct 2026) goes to the anchor runner: the reference gradient is checked by the energy route after the partial
# runs instead of pyscf's slow (T) route before them. WAIT_PGREP=<pattern>: wait while a process matching it runs (a run started by an earlier wave).
# no-set-e: one failing molecule is logged and the wave goes on to the next
set -u
LIST=${1:?list file}
ROOT=${ROOT:-/root/dpir/probes}
PY=${PY:-/root/miniforge3/envs/qc05/bin/python}
LOG=${LOG:-/root/dpir/anchors.log}
FAST=${FAST---fast-t-density --fast-t-lambda}
export TWO_ROUTE=${TWO_ROUTE:-energy}
cd "$ROOT" || exit 1
mark() { echo "=== (AS3) $* $(date '+%F %T')" >> "$LOG"; }
if [ -n "${WAIT_PGREP:-}" ]; then
  mark "waiting while '$WAIT_PGREP' runs"
  while pgrep -f "$WAIT_PGREP" > /dev/null; do sleep 300; done
fi
mark "wave start: $(grep -c . "$LIST") molecules from $LIST on $(hostname), two-route mode $TWO_ROUTE"
while IFS='|' read -r name geom W T M; do
  [ -z "$name" ] && continue
  out="results/${name}_ccpvdz"
  if [ -f "$out/hessian_ccsd_t.npz" ]; then
    mark "$name hessian DONE (found, not recomputed)"
  else
    ROOT="$ROOT" PY="$PY" LOG="$LOG" ANCHOR_LIST="$name|$geom|$out|$W|$T|$M|$FAST" bash "$ROOT/run_anchors_hel23_parallel.sh" < /dev/null
    if [ -f "$out/hessian_ccsd_t.npz" ]; then mark "$name hessian DONE"
    elif [ -f "$out/hessian_ccsd_t_IMAGINARY.npz" ]; then mark "$name hessian IMAGINARY"; continue
    else mark "$name hessian FAILED (see $out/e8_fd.log)"; continue; fi
  fi
  apt="$out/apt_ccsd_t_field.npz"
  if [ ! -f "$apt" ]; then
    OMP_NUM_THREADS=16 "$PY" cc_apt_field.py "$geom" --out "$apt" --basis cc-pvdz --threads 16 --max-memory 24000 --fast > "$out/apt_field.log" 2>&1 < /dev/null
  fi
  ref=(); [ -f "$out/apt_ccsd_t.npz" ] && ref=(--ref "$out/apt_ccsd_t.npz" --line 1e-3)
  if "$PY" cc_apt_field_check.py "$apt" "${ref[@]}" > "$out/apt_check.log" 2>&1 < /dev/null; then mark "$name apt PASS $(cut -c1-120 "$out/apt_check.log")"
  else mark "$name apt FAIL (see $out/apt_check.log)"; fi
done < "$LIST"
mark "wave done"
