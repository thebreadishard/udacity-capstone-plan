#!/usr/bin/env bash
# composite_pipeline_1007.sh (7 Oct 2026; TASKS 28, chain 33c registered 07:1x). Runs on the laptop (Git Bash) once the CCX53's MP2 rows queue ends:
#   (P1) wait for "=== QUEUE DONE|FAILED" in ~/e8/composite/queue.log (every 15 min);
#   (P2) fetch the merged rows, the queue and worker logs into probes/results_m1/composite_rows_2026-10-07/;
#   (P3) start the analytic-labels server on the same CCX53 (probes/bootstrap_labels_ccx53.sh — the user's yes of 5 Oct), so the machine is not idle;
#   (P4) build the five composites (cc_composite_full_check.py build; anthracene in its plane frame) and apply the registered promotion rule
#        (probes/composite_promote.py) — the anchor registry decides what is carried;
#   (P5) chain 33c: T3 on every carried TZ-tier anchor with chain 34's three models; seed means beside the cc-pVDZ control.
# Markers in probes/results_m1/afternoon_2026-10-04.log; the read against the lines is mine, by hand. Restartable: every step skips what is done
# (rows on disk, the labels lanes' marker, a registered composite, a seed's T3 record), so the watch may relaunch it after an app restart.
#   nohup bash probes/composite_pipeline_1007.sh >> probes/results_m1/afternoon_2026-10-04.log 2>&1 &
set -uo pipefail
# no-set-e: every step writes its own marker; a failed step stops what depends on it
P=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
IP=157.180.32.149
SSH="ssh -i $HOME/.ssh/hetzner_g_measure -o ConnectTimeout=25 -o BatchMode=yes root@$IP"
D=$P/probes/results_m1/composite_rows_2026-10-07
R=$P/probes/results_m1
OUT=$P/modules/05_support_predictor/out
DATE=2026-10-07   # fixed: a relaunch on a later day must find today's files
LOG=$R/afternoon_2026-10-04.log
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
t() { date '+%F %T'; }
cd "$P" || exit 1
echo "=== (P1) composite pipeline armed: waiting for the CCX53 queue $(t)"
# only the lines after the last "=== QUEUE start" count (the log keeps the failed starts of 7 Oct morning)
until $SSH 'tac ~/e8/composite/queue.log | sed "/=== QUEUE start/q" | grep -qE "=== QUEUE (DONE|FAILED|REFUSED)"' < /dev/null 2>/dev/null; do sleep 900; done
if ! $SSH 'tac ~/e8/composite/queue.log | sed "/=== QUEUE start/q" | grep -q "=== QUEUE DONE"' < /dev/null; then
  echo "=== (P1) QUEUE FAILED on the CCX53 — see ~/e8/composite/queue.log; pipeline stops $(t)"; exit 1
fi
echo "=== (P2) queue done; fetching rows $(t)"
mkdir -p "$D"
[ "$(ls "$D"/mp2_rows_*_ccpv?z.npz 2>/dev/null | wc -l)" -ge 10 ] && echo "=== (P2) rows already on disk $(t)" || $SSH 'cd ~/e8/composite && tar czf - mp2_rows_*_ccpv?z.npz queue.log worker_*.log jobs.txt rows' < /dev/null > "$D/rows.tgz" && (cd "$D" && tar xzf rows.tgz) \
  || { echo "=== (P2) FETCH FAILED $(t)"; exit 1; }
echo "=== (P2) fetched $(ls "$D"/mp2_rows_*_ccpv?z.npz | wc -l) merged row files, $(ls "$D"/rows | wc -l) job files $(t)"

if grep -q "(P3) labels server running" "$LOG"; then echo "=== (P3) labels server already started $(t)"; else
echo "=== (P3) labels server bootstrap on $IP $(t)"
bash probes/bootstrap_labels_ccx53.sh "$IP" > "$R/labels_bootstrap_$DATE.log" 2>&1 \
  && echo "=== (P3) labels server running (four lanes) $(t)" || echo "=== (P3) LABELS BOOTSTRAP FAILED — see $R/labels_bootstrap_$DATE.log $(t)"
fi

echo "=== (P4) building composites $(t)"
build() {   # name mol anchor [planeframe]
  local name=$1 mol=$2 anchor=$3 pf=${4:-}
  grep -q "composite_full_${name}_$DATE.npz" modules/05_support_predictor/out/ANCHORS_STATUS.json && { echo "--- $name already built and registered"; return 0; }
  python probes/cc_composite_full_check.py build "$anchor" "$mol" "$D/mp2_rows_${name}_ccpvdz.npz" "$D/mp2_rows_${name}_ccpvtz.npz" \
    "$OUT/composite_full_${name}_$DATE" ${pf:+--planeframe "$pf"} > "$OUT/composite_full_${name}_$DATE.log" 2>&1 \
    && python probes/composite_promote.py promote "modules/05_support_predictor/out/composite_full_${name}_$DATE.npz" "$mol" "$name" "$DATE" \
    || echo "=== (P4) BUILD OR PROMOTION FAILED: $name $(t)"
}
build naphthalene A_01f3186607 "$R/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz"
build pyridine A_6e858b26e5 "$R/e8_pyridine_ccpvdz_2026-09-30/hessian_ccsd_t.npz"
build fluorobenzene B_8b12a55d3a "$R/e8_fluorobenzene_ccpvdz_2026-09-30/hessian_ccsd_t.npz"
build benzonitrile A_3100da3761 "$R/e8_benzonitrile_ccpvdz_2026-09-30/hessian_ccsd_t_INVALID.npz"
build anthracene A_a1e6ec1862 "$R/e8_anthracene_ccpvdz_2026-10-06_partial/hessian_ccsd_t_IMAGINARY.npz" "$R/e8_anthracene_ccpvdz_2026-10-06_partial/geometry_planeframe.json"
python modules/05_support_predictor/m05/anchor_registry.py --check --write-overview
echo "=== (P4) composites built and registered $(t)"

ARGS=$(python probes/composite_promote.py t3-args TZ)
N=$(echo "$ARGS" | grep -o -- "--anchor" | wc -l)
if [ "$N" -lt 4 ]; then echo "=== (P5) CHAIN 33c NOT STARTED: only $N carried TZ-tier anchors $(t)"; exit 1; fi
echo "=== (P5) chain 33c: T3 on $N TZ-tier anchors start $(t)"
cd "$P/modules/05_support_predictor" || exit 1
for s in 0 1 2; do
  [ -f "out/T3_tz_anchors_c34_seed${s}_$DATE.json" ] && { echo "--- seed $s already done"; continue; }
  # shellcheck disable=SC2086   # ARGS is a list of --anchor arguments
  python m05/rungC_cc_transfer.py corpus/molecules out/E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed$s.pt out/T3_tz_anchors_c34_seed${s}_$DATE \
    --threads 8 --epochs 300 --lr 1e-3 --head-l2 1 $ARGS > out/T3_tz_anchors_c34_seed${s}_$DATE.log 2>&1 \
    && echo "=== (P5) chain 33c seed $s done $(t)" || echo "=== (P5) CHAIN 33c seed $s FAILED $(t)"
done
cd "$P" || exit 1
python probes/t3_seed_means.py "modules/05_support_predictor/out/T3_tz_anchors_c34_seed*_$DATE.json" "modules/05_support_predictor/out/T3_four_anchors_c34_seed*_2026-10-07.json" \
  --json "$OUT/T3_seed_means_tz_vs_dz_c34_$DATE.json" > "$OUT/T3_seed_means_tz_vs_dz_c34_$DATE.md" 2>&1
echo "=== (P5) chain 33c finished — read $OUT/T3_seed_means_tz_vs_dz_c34_$DATE.md against the lines $(t)"
