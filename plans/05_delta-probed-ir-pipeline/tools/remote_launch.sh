#!/bin/bash
# remote_launch — the launch wrapper promised on 14 September 2026 (QUALITY_POLICY, incident → guard), shaped by the incidents of 23–24 September:
#   * an ssh that starts `nohup … &` and then keeps talking hangs until the job ends  → the job is started in a detached subshell; the ssh only checks the pid and returns
#   * `pgrep -f <pattern>` inside the ssh matches the remote shell's own command line → the job's PID comes from a pidfile, never from a pattern
#   * quoting through ssh mangles commands                                             → the command line is written verbatim to <name>.cmd.sh on the server and run from there
#   * a queued script's new branch was never dry-run                                  → --dry-run "<extra args>" runs the command with those arguments first and shows the exit code
# Usage:
#   remote_launch.sh <user@host> <workdir> <name> [--threads N] [--dry-run "<extra args>"] -- "<full command line, one string>"
#   remote_status.sh <user@host> <workdir> <name> [lines]
# Files on the server, in <workdir>: <name>.cmd.sh, <name>.log (stdout+stderr), <name>.pid, <name>.exit (written when the job ends), <name>.dryrun.log.
set -euo pipefail
KEY="${REMOTE_KEY:-$HOME/.ssh/hetzner_g_measure}"
HOST="$1"; WORKDIR="$2"; NAME="$3"; shift 3
THREADS=""; DRY=""; HAVE_DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --threads) THREADS="$2"; shift 2 ;;
    --dry-run) DRY="$2"; HAVE_DRY=1; shift 2 ;;
    --) shift; break ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
[ $# -eq 1 ] || { echo "give the command line as ONE quoted string after --" >&2; exit 2; }
CMD="$1"
SSH=(ssh -i "$KEY" -o ConnectTimeout=25 -o BatchMode=yes "$HOST")
ENVLINE=""; [ -n "$THREADS" ] && ENVLINE="export OMP_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS"
# 1. the command file, verbatim (stdin carries it; no quoting through the remote shell)
printf '#!/bin/bash\ncd %q || exit 1\n%s\n%s "$@"\n' "$WORKDIR" "$ENVLINE" "$CMD" | "${SSH[@]}" "cat > '$WORKDIR/$NAME.cmd.sh' && chmod +x '$WORKDIR/$NAME.cmd.sh' && echo 'command file written'"
# 2. optional dry run of the same file with extra arguments
if [ $HAVE_DRY -eq 1 ]; then
  echo "dry run: $CMD $DRY"
  "${SSH[@]}" "cd '$WORKDIR' && bash '$NAME.cmd.sh' $DRY > '$NAME.dryrun.log' 2>&1; echo \"dry-run exit \$?\"; tail -n 5 '$NAME.dryrun.log'" < /dev/null || true
fi
# 3. detached start: setsid + nohup in a subshell, pid and exit code to files; the ssh checks the pid after 2 s and returns
"${SSH[@]}" "cd '$WORKDIR' && rm -f '$NAME.exit' && ( setsid nohup bash -c \"bash '$NAME.cmd.sh'; echo \\\$? > '$NAME.exit'\" > '$NAME.log' 2>&1 < /dev/null & echo \$! > '$NAME.pid' ); sleep 2; P=\$(cat '$NAME.pid'); if kill -0 \$P 2>/dev/null; then echo \"launched $NAME (pid \$P) on $HOST:$WORKDIR\"; else echo \"NOT RUNNING after 2 s — exit \$(cat '$NAME.exit' 2>/dev/null)\"; tail -n 5 '$NAME.log'; exit 1; fi" < /dev/null
