#!/usr/bin/env bash
# no-set-e: a library of functions to be sourced; each function returns its own status
# tools/hosts.sh (10 Oct 2026) — rented servers by name, with the machine pinned (tools/hosts.tsv). Source it:
#   . tools/hosts.sh
#   host_ip labels                 → 157.180.32.149
#   host_ssh labels 'uptime'       → runs the command only on the pinned machine; prints its output
# host_ssh returns 3 and prints 'WRONG MACHINE …' on stderr when the IP answers with another machine-id (a re-used IP), 255 when unreachable,
# 4 when the name is not in the table. HOSTS_FILE and HOSTS_SSH (the ssh command, for tests) can be overridden.
HOSTS_FILE=${HOSTS_FILE:-$(dirname "${BASH_SOURCE[0]}")/hosts.tsv}
HOSTS_SSH=${HOSTS_SSH:-ssh -o BatchMode=yes -o ConnectTimeout=20 -i $HOME/.ssh/hetzner_g_measure}

_host_row() { grep -v '^#' "$HOSTS_FILE" 2>/dev/null | awk -F'\t' -v n="$1" '$1 == n'; }

host_ip() {
  local row; row=$(_host_row "$1")
  [ -n "$row" ] || { echo "host '$1' not in $HOSTS_FILE" >&2; return 4; }
  echo "$row" | cut -f2
}

host_ssh() {   # $1 = name, $2 = remote command
  local row ip mid out rc first
  row=$(_host_row "$1")
  [ -n "$row" ] || { echo "host '$1' not in $HOSTS_FILE" >&2; return 4; }
  ip=$(echo "$row" | cut -f2); mid=$(echo "$row" | cut -f3)
  out=$($HOSTS_SSH "root@$ip" "cat /etc/machine-id; $2" 2>/dev/null); rc=$?
  first=$(echo "$out" | head -1)
  if [ -z "$first" ]; then return 255; fi
  if [ "$first" != "$mid" ]; then echo "WRONG MACHINE at $ip for '$1': machine-id $first, pinned $mid" >&2; return 3; fi
  echo "$out" | tail -n +2
  return "$rc"
}
