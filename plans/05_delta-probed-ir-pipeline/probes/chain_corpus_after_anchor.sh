#!/usr/bin/env bash
# Chain: start the Module 05 corpus (layer A) when the M3 TZ anchor run has FINISHED, and only then.
# Written 2026-09-17 after the label-count note: the corpus is the cheapest path to the first learning
# curve (39 layer-A molecules, ~40 h), and it is the next thing the machine should do.
#
# It refuses to start the corpus over a crashed anchor. The completion test is the sealed result:
# REPORT.md in the TZ output directory, which m1_frozen_spaces.py writes only at the end.
# (Corrected 18 Sep 07:3x: the first version watched m1_sealed_energies.sha256, but dump_state() rewrites
# that file after EVERY point, so the chain would have fired after the first displaced point, ~9 days early.)
# If the anchor python disappears WITHOUT that file, the anchor was stopped (guard, reboot, crash) and
# this chain exits without starting anything - resuming the anchor is then the first job, not the corpus.
#
# Usage: setsid nohup ./chain_corpus_after_anchor.sh >> <log> 2>&1 &
set -u
P=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
SEAL=$P/probes/results_m1/naphthalene_cc-pvtz_tight_m3/m1_sealed_energies.sha256
SEAL=$P/probes/results_m1/naphthalene_cc-pvtz_tight_m3/REPORT.md   # the true end marker; the sha256 above is per-point
CORPUS=$P/modules/05_support_predictor/corpus
PY=/mnt/c/Users/thebr/.conda/envs/qc/python.exe
CORPUS_LOG=$CORPUS/run_corpus_layerA_chained.log
MAX_DAYS=${MAX_DAYS:-12}

echo "CHAIN armed $(date '+%F %T'): waiting for the anchor run to write REPORT.md (its last action) (max ${MAX_DAYS} days)"
end=$(( $(date +%s) + MAX_DAYS * 86400 ))
while : ; do
  if [ -f "$SEAL" ]; then
    echo "CHAIN $(date '+%F %T'): the anchor wrote REPORT.md ($(grep -o '"mode":' "${SEAL%REPORT.md}m1_sealed_energies.json" | wc -l) points sealed); starting corpus layer A"
    break
  fi
  if ! pgrep -f 'm1_frozen_spaces.py.*cc-pvtz' > /dev/null 2>&1; then
    # give a relaunch a minute to appear before concluding the run is gone
    sleep 90
    if ! pgrep -f 'm1_frozen_spaces.py.*cc-pvtz' > /dev/null 2>&1 && [ ! -f "$SEAL" ]; then
      echo "CHAIN ENDS $(date '+%F %T'): the anchor is gone and nothing is sealed - it was stopped, not finished."
      echo "CHAIN ENDS: resume the anchor first; the corpus is NOT started."
      exit 1
    fi
  fi
  [ "$(date +%s)" -ge "$end" ] && { echo "CHAIN ENDS $(date '+%F %T'): ${MAX_DAYS} days elapsed, nothing sealed"; exit 1; }
  sleep 600
done

cd "$CORPUS" || exit 1
echo "CHAIN $(date '+%F %T'): launching run_corpus.py --layer A (its own lock, its own hourly progress line)" >> "$CORPUS_LOG"
"$PY" run_corpus.py --layer A >> "$CORPUS_LOG" 2>&1
rc=$?
echo "CHAIN ENDS $(date '+%F %T'): run_corpus.py exited with $rc" | tee -a "$CORPUS_LOG"
exit $rc
