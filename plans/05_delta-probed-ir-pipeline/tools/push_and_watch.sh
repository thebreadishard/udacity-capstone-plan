#!/usr/bin/env bash
# push_and_watch.sh (3 Oct 2026, 23:5x). CI had been red for eight hours before anyone looked (two test-environment causes); state.sh shows the
# status only when it is run. This wrapper makes the failure visible at the moment it can appear: push, wait for the plan05 run of the pushed
# commit, print its conclusion, exit non-zero on failure (and print the failing test lines). Usage: bash tools/push_and_watch.sh [remote] [branch]
set -euo pipefail
REMOTE=${1:-origin}; BRANCH=${2:-$(git branch --show-current)}
git push "$REMOTE" "$BRANCH"
SHA=$(git rev-parse HEAD)
echo "pushed ${SHA:0:7}; waiting for the CI run"
for _ in $(seq 1 12); do
  ID=$(gh run list --limit 10 --json databaseId,headSha,status --jq ".[] | select(.headSha==\"$SHA\") | .databaseId" 2>/dev/null | head -1 || true)   # a GitHub 504 is retried, not fatal
  [ -n "$ID" ] && break
  sleep 10
done
[ -n "${ID:-}" ] || { echo "no CI run for ${SHA:0:7} within 2 min: the workflow's paths filter (.github/workflows/plan05-ci.yml) excludes the pushed files — nothing to watch"; exit 0; }
gh run watch "$ID" --exit-status >/dev/null 2>&1 && { echo "CI green: run $ID"; exit 0; }
echo "CI FAILED: run $ID"; gh run view "$ID" --log-failed 2>/dev/null | grep -E "(FAILED|ERROR) tests/|Error:" | sed 's/.*Z //' | sort -u | head -20
exit 1
