#!/bin/bash
# remote_status — companion of remote_launch.sh: is <name> still running on <host>, for how long, and what were its last lines.
set -euo pipefail
KEY="${REMOTE_KEY:-$HOME/.ssh/hetzner_g_measure}"
HOST="$1"; WORKDIR="$2"; NAME="$3"; LINES="${4:-4}"
ssh -i "$KEY" -o ConnectTimeout=25 -o BatchMode=yes "$HOST" "cd '$WORKDIR' 2>/dev/null || { echo 'no such workdir'; exit 1; }; P=\$(cat '$NAME.pid' 2>/dev/null); if [ -n \"\$P\" ] && kill -0 \$P 2>/dev/null; then echo \"$NAME: running (pid \$P, elapsed \$(ps -o etime= -p \$P | tr -d ' '))\"; elif [ -f '$NAME.exit' ]; then echo \"$NAME: finished, exit \$(cat '$NAME.exit')\"; else echo \"$NAME: not running, no exit file (never started or killed)\"; fi; tail -n $LINES '$NAME.log' 2>/dev/null | cut -c1-200" < /dev/null
