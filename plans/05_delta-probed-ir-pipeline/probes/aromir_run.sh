#!/usr/bin/env bash
# aromir_run.sh <run name> <spectrum|baseline> <SMILES | path.xyz> [--dry-run] — TASKS 73: one aromir command on the laptop, in WSL's
# ~/aromir_v13 (aromir, torch, pyscf 2.15.0) under probes/wsl_capped.sh (CAP_MB) and /usr/bin/time, through probes/aromir_run_wsl.sh.
# The result folder is probes/results_m1/<run name>; `spectrum` reads the release in RELEASE (default: v1.3's folder).
# Markers "=== (AROMIR) …"; a progress line every five minutes while the process's CPU time grows (aromir prints nothing while pyscf
# works). --dry-run: `aromir check` on the molecule and, for a spectrum, `aromir card` on the release — nothing is computed.
set -euo pipefail
[ $# -ge 3 ] || { echo "usage: aromir_run.sh <run name> <spectrum|baseline> <SMILES | path.xyz> [--dry-run]"; exit 2; }
NAME=$1
WHAT=$2
MOLECULE=$3
MODE=${4:-}
case "$WHAT" in spectrum|baseline) ;; *) echo "aromir_run.sh: '$WHAT' is not spectrum or baseline"; exit 2 ;; esac
case "$MODE" in ''|--dry-run) ;; *) echo "aromir_run.sh: '$MODE' is not --dry-run"; exit 2 ;; esac
# a backslash (a stereo bond in a SMILES) is not tested through wsl.exe: refused, give such a molecule as an xyz file
case "$MOLECULE" in *\\*) echo "aromir_run.sh: a backslash in the molecule is not passed on safely; use an xyz file"; exit 2 ;; esac
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
P=$(cd "$(dirname "$0")/.." && pwd)
CAP_MB=${CAP_MB:-4096}
THREADS=${THREADS:-8}
PYSCF_MB=${PYSCF_MB:-$((CAP_MB / 2))}   # half the cap, as cphf_check_215.sh: the Hessian holds arrays outside max_memory
RELEASE=${RELEASE:-modules/05_support_predictor/out/aromir_release_v1.3}
REL_OUT=probes/results_m1/$NAME
case "$WHAT" in spectrum) RESULT=certificate.json ;; baseline) RESULT=baseline.json ;; esac
say() { echo "=== (AROMIR) $* $(date '+%F %T')"; }

if [ "$WHAT" = spectrum ]; then
  for f in evaluation.json training.json seed-0.safetensors; do
    [ -f "$P/$RELEASE/$f" ] || { say "STOPPED: $RELEASE/$f missing"; exit 1; }
  done
fi
case "$MOLECULE" in *.xyz) [ -f "$P/$MOLECULE" ] || { say "STOPPED: $MOLECULE missing"; exit 1; } ;; esac
[ ! -e "$P/$REL_OUT" ] || { say "STOPPED: $REL_OUT exists; aromir writes into a new folder"; exit 1; }
if [ -z "$MODE" ]; then
  say "start: $NAME, aromir $WHAT '$MOLECULE', cap $CAP_MB MB (pyscf $PYSCF_MB MB), $THREADS threads"
fi
MSYS_NO_PATHCONV=1 wsl -e bash "$PW/probes/wsl_capped.sh" "$CAP_MB" -- bash "$PW/probes/aromir_run_wsl.sh" \
  "$PW" "$WHAT" "$MOLECULE" "$REL_OUT" "$RELEASE" "$THREADS" "$PYSCF_MB" "$MODE" || { say "RUN FAILED: aromir $WHAT of $NAME (exit $?)"; exit 1; }
[ -n "$MODE" ] && exit 0
[ -f "$P/$REL_OUT/$RESULT" ] || { say "RUN FAILED: $REL_OUT/$RESULT missing"; exit 1; }
say "done: $REL_OUT holds $(ls "$P/$REL_OUT" | tr '\n' ' ')"
