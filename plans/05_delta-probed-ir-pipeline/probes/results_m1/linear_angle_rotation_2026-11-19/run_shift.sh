#!/bin/bash
set -euo pipefail
# Band shift of v1.4 at the stored orientation, carried vs invariant linear-angle axis (WSL aromir_dev).
cd /mnt/c/Users/thebr/AppData/Local/Temp/claude/6e282d7a6878e314/a98f6ae6-a06a-4b5a-ac48-06ddd4d42d17/scratchpad/probe_287 || exit 1
export OMP_NUM_THREADS=2 PYTHONUNBUFFERED=1
C=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/corpus
/usr/bin/time -f "RSS %M kB wall %e s" timeout 900 ~/aromir_dev/bin/python band_shift.py $C 2>&1 | tail -9
