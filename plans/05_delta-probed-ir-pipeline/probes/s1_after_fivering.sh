#!/usr/bin/env bash
# S1 (TASKS 53, 13 Oct 2026) on benzene, started when the five-ring pool's laptop runner (F5) has ended, so that it takes no threads from it.
# Registration: GoalGathering/notes/PreRegistration_2026-10-13_S1_Anharmonic_Level.md. Run from the plan folder (WSL):
#   bash probes/s1_after_fivering.sh >> probes/results_m1/s1_anharmonic_2026-10-13.log 2>&1
set -euo pipefail
export WAIT_LOG=probes/results_m1/fivering_laptop_2026-10-10.log
export WAIT_RE='^=== \(F5\) (laptop runner finished|STOP file|COPY FAILED|NO CANDIDATE)'
exec bash probes/s1_anharmonic_level.sh modules/05_support_predictor/corpus/molecules/A_8448043181/geometry.json \
  /home/thebreadishard/s1_benzene_2026-10-13 4 R:6-31g*:99,590 G:6-31g*:75,302 B:6-31g:99,590
