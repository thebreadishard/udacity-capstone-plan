#!/bin/bash
# labels_lane_switch.sh <lane> <pid in progress> <new list> — runs ON the labels server (8 Oct 2026; the user: "Ja, doe maar" to the smallest-first
# order). The old lane's bash is killed by the caller and its analytic_hessians.py child finishes as an orphan; this waits for that pid so the lane never
# runs two molecules at once (lanes × threads ≤ cores), then runs labels_lane.sh on the smallest-first list (the molecule that was in progress sits at
# its end: skipped if the orphan wrote its files, retried if not).
#   setsid nohup bash /root/labels/labels_lane_switch.sh 0 448381 /root/labels/small_ids_0.txt >> /root/labels/lane_0.log 2>&1 < /dev/null &
set -u
# no-set-e: the wait loop ends on a dead pid; labels_lane.sh keeps its own per-molecule status
LANE=$1; OLDPY=$2; LIST=$3
cd /root/labels || exit 1
echo "[$(date '+%F %T')] lane $LANE switch: waiting for pid $OLDPY (the molecule in progress), then the smallest-first list $LIST"
while kill -0 "$OLDPY" 2>/dev/null; do sleep 30; done
echo "[$(date '+%F %T')] lane $LANE switch: pid $OLDPY ended; smallest-first list starts"
exec bash labels_lane.sh "$LANE" "$LIST"
