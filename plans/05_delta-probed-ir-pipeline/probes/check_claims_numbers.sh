#!/usr/bin/env bash
# probes/check_claims_numbers.sh (13 Nov 2026, TASKS 140) — the number audit of the four claims' page against every source behind it.
# Each read that lands on the page before 25 November adds its own source file here, so the audit keeps covering the whole page.
# Zero unplaced tokens is the bar: a number nobody can trace is a claim nobody can defend.
#   bash probes/check_claims_numbers.sh
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd)
cd "$P"
PAGE=GoalGathering/notes/Claims_2026-11-13_Four_Claims_For_25_November.md
SOURCES=(
  modules/05_support_predictor/out/read_chain42.md
  modules/05_support_predictor/out/read_chain42.json
  modules/05_support_predictor/out/read_chain42_beside.json
  modules/05_support_predictor/out/anchor_count_2026-10-29/anchor_count_read.md
  modules/05_support_predictor/out/anchor_plan/count_n167.md
  GoalGathering/notes/Design_2026-11-13_VPT2_Domain_Marks.md
  GoalGathering/notes/Mandate_2026-09-13_Affordable_Plan_Obstacle_Ledger.md
  probes/results_m1/labels_domain_2026-11-13/s3_read_exclude/s3_read.md
  probes/results_m1/labels_domain_2026-11-13/route_rule/route_rule.md
  probes/results_m1/low_mode_patch_2026-11-13/corpus/D_ac28161d06/report.json
  probes/results_m1/coverage_screen_2026-11-13/coverage_screen.md
  probes/results_m1/solved_modes_2026-11-13/coronene/solved_modes_pair.md
)
for f in "$PAGE" "${SOURCES[@]}"; do [ -f "$f" ] || { echo "check_claims_numbers.sh: $f missing" >&2; exit 2; }; done
out=$(PYTHONUTF8=1 python probes/check_reading_copy_numbers.py "$PAGE" "${SOURCES[@]}")
echo "$out"
echo "$out" | grep -q "not found in any source: 0$" || { echo "check_claims_numbers.sh: a number on the page is in no source" >&2; exit 1; }
