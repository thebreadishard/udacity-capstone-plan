#!/usr/bin/env bash
# probes/plan_paths.sh — sourced by a wrapper that starts a WSL job from Git Bash:  . "$(dirname "$0")/plan_paths.sh"; plan_paths "$0"
# Sets PLAN_DIR (the plan folder the calling script lies in, as this shell names it) and PLAN_WSL (the same folder as WSL names
# it), so a worktree's copy of a wrapper reads and writes that worktree.
# Physical paths (-P): a shell started by another program can inherit PWD in Windows form ('C:/Users/…'), and the logical `pwd`
# then answers in it — tools/runspec.py starts a run that way, and '/mnt' + 'C:/…' is no path (20 Nov 2026, the dry run of
# probes/low_mode_patch.sh, which carries the same lines of its own until its running measurement has ended).
# Git Bash names drive C as /c/… (or, from an inherited PWD, C:/…), WSL as /mnt/c/…; on Linux or inside WSL a path is its own,
# also one that starts with a one-letter folder. PLAN_HOST_KERNEL stands in for `uname -s` in the test.
# no-set-e: a sourced file of one function; the options are the calling wrapper's (set -euo pipefail there), and setting them here would change them
plan_paths() {   # $1 = the calling script's own path ($0), which lies in <plan>/probes
  PLAN_DIR=$(cd -P "$(dirname "$1")/.." && pwd -P) || return 2
  case "${PLAN_HOST_KERNEL:-$(uname -s)}" in
    MINGW*|MSYS*|CYGWIN*)
      case "$PLAN_DIR" in
        [A-Za-z]:/*) PLAN_WSL=/mnt/$(printf '%s' "${PLAN_DIR:0:1}" | tr 'A-Z' 'a-z')${PLAN_DIR:2} ;;
        /[A-Za-z]/*) PLAN_WSL=/mnt$PLAN_DIR ;;
        *) echo "plan_paths.sh: cannot turn '$PLAN_DIR' into a WSL path"; return 2 ;;
      esac ;;
    *) PLAN_WSL=$PLAN_DIR ;;
  esac
}
