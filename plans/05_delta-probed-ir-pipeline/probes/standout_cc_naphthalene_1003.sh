#!/usr/bin/env bash
# Standout CC-level test on naphthalene (the user, 3 Oct 2026 19:5x: "zet nummer 11 vanavond na keten 34 in de wachtrij"): the decisive second molecule of the
# 28 Sep pre-registration (Standout_CC_Level_Test, lines C1–C3 unchanged), with the (T)-lambda CCSD(T)/cc-pVDZ Hessian of 2 Oct and the analytic B3LYP low
# level, as benzene's corrected read of 29 Sep 23:4x. Two cells, as for benzene: the registered band deck, and the wide pool with the open prior (the cell that
# passed on benzene and that gate B of the paper plan rests on). Waits for chain 34 step 2 to free its 8 threads (night2 log); 4 threads, beside the TZ run.
set -uo pipefail
# no-set-e: each cell records its own line
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
N2=$P/probes/results_m1/night2_2026-10-03.log
CC=$P/probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz
t() { date '+%F %T'; }
until grep -q "chain 34 step 2 finished" "$N2" 2>/dev/null; do sleep 600; done
[ -f "$CC" ] || { echo "=== standout naphthalene not started: no CC Hessian at $CC $(t)"; exit 1; }
cd "$P/modules/standout_pattern_proposer" || exit 1
export PYTHONUTF8=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
[ -f out/exports_analytic/A_01f3186607.npz ] || python run_export.py "$P/modules/05_support_predictor/corpus/molecules" out/exports_analytic --use-analytic --only A_01f3186607
echo "=== standout naphthalene, cell 1 (registered band deck, analytic low level) start $(t)"
python cc_level_test.py A_01f3186607 "$CC" --use-analytic --tag analytic_tlambda \
  && echo "=== cell 1 done $(t)" || echo "=== CELL 1 FAILED $(t)"
echo "=== standout naphthalene, cell 2 (wide pool, open prior; exploratory as registered) start $(t)"
python cc_level_test.py A_01f3186607 "$CC" --use-analytic --pool all --w-cm 0 --tag analytic_tlambda_all_band0 \
  && echo "=== cell 2 done $(t)" || echo "=== CELL 2 FAILED $(t)"
ls out/cc | grep A_01f3186607 | tr '\n' ' '; echo
echo "=== standout naphthalene finished $(t)"
