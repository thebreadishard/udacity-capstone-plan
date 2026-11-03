#!/usr/bin/env bash
# The Atlas's pipeline show (TASKS 146): module 08's default runs without the 0.4 benzene of 30 Oct, the show batch's 30, hold-out (a)'s
# seven besides benzene, and one benzene on pipeline 0.9 (the user, 3 Nov: one benzene in the show, under that name). Every Atlas link is
# asked for after the build; website/deploy.sh then copies the page.
#
#   bash probes/build_pipeline_show.sh
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"
R=$P/probes/results_m1
BENZENE=$R/pipeline_benzene_reuse_2026-11-03/benzene
runs=("$BENZENE" "$R/pipeline_demo_v04_2026-10-30/phenanthrene" "$R/pipeline_demo_v04_2026-10-30/candidate06"
      "$R/pipeline_rehearsal_2026-10-30/cinnoline" "$R/pipeline_reuse_demo_2026-10-31/carbazole")
for d in "$R"/pipeline_show_batch_2026-11-01/*/ "$R"/pipeline_holdout_a_2026-11-02/*/; do
  case "$d" in */benzene_*) continue ;; esac
  runs+=("${d%/}")
done
for d in "${runs[@]}"; do [ -f "$d/pipeline.json" ] || { echo "no pipeline.json in $d" >&2; exit 1; }; done
echo "runs: ${#runs[@]}"
cd "$P/modules/08_industry_synthesis"
PYTHONUTF8=1 python -m m08.show --runs "${runs[@]}" --check-links
