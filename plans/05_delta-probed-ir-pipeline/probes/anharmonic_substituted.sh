#!/usr/bin/env bash
# probes/anharmonic_substituted.sh <part> <id> <start> <out dir> [--dry-run] [--show-command] (20 Nov 2026, TASKS 211;
# GoalGathering/notes/PreRegistration_2026-11-20_Anharmonic_Step_Substituted_Molecule.md) — the two force fields of the
# measurement of the anharmonic step on a substituted molecule, each by an existing runner in WSL under probes/wsl_capped.sh:
#   second-field   part A: a second GFN2-xTB force field with its label, probes/xtb_field_for_step.sh <id> <start> <out dir>;
#                  <start> is a folder holding ref.json, a stored B3LYP minimum other than the pipeline's;
#   g-label        part B: the B3LYP/6-31G* force field with its label, probes/g_label_for_step.sh <id> <start> <out dir> THREADS;
#                  <start> is a geometry.json.
# <start> and <out dir> are relative to the plan folder this script lies in, so a worktree's copy reads and writes that
# worktree. CAP_MB is the cgroup cap (default: second-field 1536, g-label 4096); THREADS the g-label's OpenMP threads (4);
# the second field runs SHARDS × OMP_NUM_THREADS = 2 × 2 as the pipeline does. For g-label pyscf's max_memory is half the cap
# (PYSCF_MAX_MEMORY, read by pyscf/__config__.py), as probes/low_mode_patch.sh sets it: block sizes only, no number changes.
# --dry-run is the runner's own; --show-command prints what would be started inside WSL and starts nothing.
# Markers "=== (ASM) …"; the runners' own are "=== (ANH) …" and "=== (GLB) …".
set -euo pipefail
USAGE="usage: anharmonic_substituted.sh second-field|g-label <id> <start> <out dir> [--dry-run] [--show-command]"
[ $# -ge 4 ] || { echo "$USAGE"; exit 2; }
PART=$1; ID=$2; START=$3; OUT=$4
shift 4
DRY=""
SHOW=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=--dry-run; shift ;;
    --show-command) SHOW=1; shift ;;
    *) echo "unknown argument '$1'; $USAGE"; exit 2 ;;
  esac
done
case "$ID" in ''|*[!A-Za-z0-9_]*) echo "id '$ID' must be letters, digits and '_'; $USAGE"; exit 2 ;; esac
# an option where a path belongs means a path was left out: without this, '--show-command' as <out dir> would start the run
for path in "$START" "$OUT"; do
  case "$path" in ''|-*) echo "'$path' is not a path; $USAGE"; exit 2 ;; esac
done
. "$(dirname "$0")/plan_paths.sh"
plan_paths "$0"
say() { echo "=== (ASM) $* $(date '+%F %T')"; }
THREADS=${THREADS:-4}
case "$PART" in
  second-field)
    CAP_MB=${CAP_MB:-1536}
    [ -f "$PLAN_DIR/$START/ref.json" ] || { say "STOPPED: $START/ref.json missing"; exit 1; }
    ENVIRONMENT="PYTHONUNBUFFERED=1"
    ARGS=(probes/xtb_field_for_step.sh "$ID" "$START" "$OUT") ;;
  g-label)
    CAP_MB=${CAP_MB:-4096}
    [ -f "$PLAN_DIR/$START" ] || { say "STOPPED: $START missing"; exit 1; }
    ENVIRONMENT="PYTHONUNBUFFERED=1 PYSCF_MAX_MEMORY=$((CAP_MB / 2))"
    ARGS=(probes/g_label_for_step.sh "$ID" "$START" "$OUT" "$THREADS") ;;
  *) echo "unknown part '$PART'; $USAGE"; exit 2 ;;
esac
case "$CAP_MB$THREADS" in *[!0-9]*) echo "CAP_MB '$CAP_MB' and THREADS '$THREADS' must be whole numbers; $USAGE"; exit 2 ;; esac
[ -z "$DRY" ] || ARGS+=("$DRY")
QUOTED=$(printf '%q ' "${ARGS[@]}")     # each argument quoted for the shell inside WSL, so a path with a space stays one argument
INSIDE="export $ENVIRONMENT; cd $(printf '%q' "$PLAN_WSL") && bash probes/wsl_capped.sh $CAP_MB -- bash ${QUOTED% }"
if [ -n "$SHOW" ]; then echo "(ASM) cap $CAP_MB MB: $INSIDE"; exit 0; fi
[ -n "$DRY" ] || say "start: $PART of $ID from $START into $OUT, cap $CAP_MB MB"
MSYS_NO_PATHCONV=1 wsl -e bash -c "$INSIDE" || { say "RUN FAILED: $PART of $ID (exit $?)"; exit 1; }
[ -n "$DRY" ] || say "done: $PART of $ID"
