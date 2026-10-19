#!/usr/bin/env bash
# probes/wsl_capped.sh <cap_MB> -- command … (19 Oct 2026; after the out-of-memory of 19 Oct 00:46) — runs the command inside WSL in a
# systemd user scope with MemoryMax=<cap_MB> and no swap, so the kernel stops the whole process tree at the cap instead of letting it take
# memory from the other jobs. The cap is what a run spec's memory.peak_gb may cite: a bound that holds, where a measured peak may not.
# Exit 137 with the line 'KILLED: over the cap of <cap> MB' when the cap was hit; otherwise the command's own exit code.
# Tested 19 Oct on WSL Ubuntu with systemd: 100 MB under a 300 MB cap passes, 600 MB is killed (exit 137).
#   bash probes/wsl_capped.sh 1536 -- bash probes/xtb_anharmonic.sh …
set -u
# no-set-e: the command's exit code is read and reported
CAP=${1:?cap in MB}; shift
[ "${1:-}" = "--" ] && shift
[ "$#" -gt 0 ] || { echo "wsl_capped.sh: no command"; exit 2; }
case "$CAP" in ''|*[!0-9]*) echo "wsl_capped.sh: cap '$CAP' is not a whole number of MB"; exit 2 ;; esac
command -v systemd-run > /dev/null || { echo "wsl_capped.sh: systemd-run missing - no cap, not run"; exit 2; }
systemd-run --user --scope --quiet -p MemoryMax="${CAP}M" -p MemorySwapMax=0 "$@"
rc=$?
[ "$rc" = 137 ] && echo "KILLED: over the cap of $CAP MB (or killed from outside)"
exit "$rc"
