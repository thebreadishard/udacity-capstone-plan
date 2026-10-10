#!/bin/bash
# cations_after_fivering.sh (10 Oct 2026; the user: "Ja, laat de vijfringpool voorgaan") — the cation analytic route (probes/cation_analytic_all.sh)
# was stopped after its current molecule so that the five-ring pool runs first on the laptop (probes/fivering_laptop_1015.sh, PRIORITY=1). This
# waits for that runner's end (all candidates done, or the STOP hand-over to pool 3's box), then relaunches the
# cation route, which skips every cation that already carries both analytic Hessians. The two cannot run side by side: ≈ 12 GB each.
#
#   nohup bash probes/cations_after_fivering.sh >> probes/results_m1/cation_analytic_2026-10-09.log 2>&1 < /dev/null & disown
set -u
# no-set-e: a waiting loop; the relaunch is the last command
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
F5LOG=$P/probes/results_m1/fivering_laptop_2026-10-09.log
t() { date '+%F %T'; }
echo "=== (CA) paused for the five-ring pool (pid $$): waiting for (F5)'s end $(t)"
until grep -qE '^=== \(F5\) (laptop runner finished|STOP file)' "$F5LOG" 2>/dev/null; do sleep 900; done
# the runner prints its end marker after its last molecule has returned, so nothing of it is left running here
echo "=== (CA) resumed after the five-ring pool $(t)"
cd "$P" || exit 1
exec bash probes/cation_analytic_all.sh
