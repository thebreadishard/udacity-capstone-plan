#!/bin/bash
set -euo pipefail
# Run network_spreads.py in WSL with the aromir_dev interpreter, carried and with the invariant axis.
cd /mnt/c/Users/thebr/AppData/Local/Temp/claude/6e282d7a6878e314/a98f6ae6-a06a-4b5a-ac48-06ddd4d42d17/scratchpad/probe_287 || exit 1
export OMP_NUM_THREADS=2 PYTHONUNBUFFERED=1
C=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/corpus
PY=~/aromir_dev/bin/python
/usr/bin/time -f "RSS %M kB wall %e s" timeout 900 $PY network_spreads.py $C 2>&1 | tail -10
/usr/bin/time -f "RSS %M kB wall %e s" timeout 900 $PY network_spreads.py $C fix 2>&1 | tail -10
