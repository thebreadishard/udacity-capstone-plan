#!/usr/bin/env bash
# night_1007_lno.sh (7 Oct 2026, 22:xx). The LNO follow-up's extra coordinate, as registered (rung C pre-registration, outcome of 7 Oct 10:1x: "the
# cells disagree → one more (out-of-plane) coordinate, both cells"): naphthalene's k 2 = atom 0 z (out-of-plane share 0.99; k 0/1 were 0.10/0.12),
# cell (a) xtight thresholds, cell (b) the reference's localisation reused at tight, then the plain tight cell at k 2 for context (not read against the
# lines). Reference energies are cached in the anchor directory, so each cell is two LNO energies (≈ 2.4 h each at xtight, ≈ 1.7 h at tight, 8 threads).
# Runs INSIDE WSL (setsid nohup); the VM is held by the scheduled task CapstoneWSLKeepalive. Markers "=== (N3) ..." in the log below.
#   wsl -e bash -c "setsid nohup bash /mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/night_1007_lno.sh \
#     >> /mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/results_m1/lno_extra_k2_2026-10-07.log 2>&1 < /dev/null &"
set -uo pipefail
# no-set-e: each cell writes its own marker; a failed cell does not stop the next
export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp
mkdir -p "$HOME/qc_tmp"
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
R=$PW/probes/results_m1
ANCHOR=$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02
GEOM=$PW/modules/05_support_predictor/corpus/molecules/A_01f3186607/geometry.json
PY=$HOME/qc05/bin/python
t() { date '+%F %T'; }
echo "=== (N3) LNO extra coordinate k 2 armed inside WSL (pid $$) $(t)"
cd "$PW" || exit 1
for cell in xtight reuse tight; do
  case $cell in
    xtight) flag="--xtight" ;;
    reuse) flag="--reuse-localisation" ;;
    tight) flag="" ;;
  esac
  # shellcheck disable=SC2086
  OMP_NUM_THREADS=8 $PY probes/lno_curvature_check.py "$ANCHOR" "$GEOM" --ks 2 --threads 8 --max-memory 6000 $flag \
    --out "$R/lno_curvature_${cell}_k2_2026-10-07.json" > "$R/lno_curvature_${cell}_k2_2026-10-07.log" 2>&1 \
    && echo "=== (N3) LNO k2 cell $cell done $(t)" || echo "=== (N3) LNO K2 CELL $cell FAILED $(t)"
done
echo "=== (N3) LNO extra coordinate finished $(t)"
