#!/usr/bin/env bash
# probes/fetch_s1tz.sh MOLECULE (18 Oct 2026, TASKS 60) — the full fetch of one S1-TZ molecule from s1 once its run has ended with rc 0:
# the molecule's folder (every Hessian, the QFF report, the grid gate), its run log, exit and pid files, the server's fetched.log and the
# conda listings. One molecule at a time, as each finishes (the fetch-per-anchor rule), so a later server loss costs one molecule at most.
# FINAL=1 also takes the code folders /root/dpir_s1tz{,_d,_e,_n} and /root/scf_guess_test (for the last molecule). The copy, the sha256 check and the FETCHED line are
# tools/fetch_server_full.sh's (VERIFY_ONLY=1 and NO_RECORD=1 pass through).
#   bash probes/fetch_s1tz.sh benzene              → probes/results_m1/s1tz_2026-10-18/benzene/
set -euo pipefail
MOL=${1:?usage: fetch_s1tz.sh benzene|naphthalene|acenaphthylene}
EXTRA=()
case "$MOL" in
  benzene) WORK=s1tz; RUN=dpir_s1tz/s1tz_benzene ;;              # phase 1 ran in /root/s1tz (s1tz_run.sh's first target)
  naphthalene) WORK=s1tz_naphthalene; RUN=dpir_s1tz_n/s1tz_naphthalene2                          # 21 Oct 19:55 resume (s1tz_naphthalene2)
    EXTRA=(dpir_s1tz/s1tz_naphthalene.log dpir_s1tz/s1tz_naphthalene.exit dpir_s1tz/s1tz_naphthalene.pid) ;;   # the first run's stop at 17:17
  acenaphthylene) WORK=s1tz_acenaphthylene; RUN=dpir_s1tz_e/s1tz_acenaphthylene3 ;;   # 19 Oct 20:03 relaunch (run spec s1tz_acenaphthylene3)
  *) echo "unknown molecule '$MOL' (benzene, naphthalene, acenaphthylene)"; exit 2 ;;
esac
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PARTS=("$WORK" "$RUN.log" "$RUN.exit" "$RUN.pid" "${EXTRA[@]}")
[ -n "${FINAL:-}" ] && PARTS=("$WORK" dpir_s1tz dpir_s1tz_d dpir_s1tz_e dpir_s1tz_n scf_guess_test)   # every S1-TZ code folder and the SCF-start test
export READY="grep -q '^=== (S2) all done' /root/$RUN.log && [ \"\$(cat /root/$RUN.exit 2>/dev/null)\" = 0 ]"
exec bash "$HERE/../tools/fetch_server_full.sh" s1 "s1tz $MOL" "$HERE/results_m1/s1tz_2026-10-18/$MOL" "${PARTS[@]}"
