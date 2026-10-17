#!/usr/bin/env bash
# tools/make_module_repo.sh <module dir> <dev branch> <target dir> [<main ref>] (17 Oct 2026; module 02's review, the user: 'Ja, goed idee') —
# a Udacity module as its own repository with its own history. The rubrics ask for a named repository with multiple commits and at least one
# development branch; a copy of the folder would have one commit. `git subtree split` keeps every commit that touched the module, with the
# module folder as the new root: <main ref> (default master) becomes `main`, <dev branch> keeps its name. Nothing is pushed: the user creates
# the repository on GitHub and pushes both branches (the commands are printed at the end).
#   bash tools/make_module_repo.sh plans/05_delta-probed-ir-pipeline/modules/02_opponent_atlas module-02-opponent-atlas /c/tmp/ai-programming-foundations-project
# Run from anywhere inside the plan repository; the temporary split branches are removed again.
set -euo pipefail
MODULE=${1:?module dir, relative to the repository root}
DEV=${2:?development branch}
TARGET=${3:?target dir (must not exist)}
MAIN_REF=${4:-master}
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
[ -d "$MODULE" ] || { echo "no module dir $MODULE" >&2; exit 2; }
[ -e "$TARGET" ] && { echo "target $TARGET exists; refusing to overwrite" >&2; exit 2; }
dev_ref=$DEV
git rev-parse --verify -q "$dev_ref" > /dev/null || dev_ref="origin/$DEV"
git rev-parse --verify -q "$dev_ref" > /dev/null || { echo "no branch $DEV (local or origin)" >&2; exit 2; }

tag=$(date +%s)
split_main="split-main-$tag"
split_dev="split-dev-$tag"
cleanup() { git branch -D -q "$split_main" "$split_dev" 2> /dev/null || true; }
trap cleanup EXIT
git subtree split -q --prefix="$MODULE" "$MAIN_REF" -b "$split_main"
git subtree split -q --prefix="$MODULE" "$dev_ref" -b "$split_dev"

git init -q -b main "$TARGET"
git -C "$TARGET" fetch -q "$ROOT" "$split_main:refs/heads/main-tmp" "$split_dev:refs/heads/$DEV"   # git refuses to fetch into the unborn current branch
git -C "$TARGET" branch -m main-tmp main
git -C "$TARGET" checkout -q main

echo "repository at $TARGET"
for b in main "$DEV"; do echo "  $b: $(git -C "$TARGET" rev-list --count "$b") commits"; done
echo "  files on main: $(git -C "$TARGET" ls-files | wc -l)"
echo "  largest file in history: $(git -C "$TARGET" rev-list --objects --all | git -C "$TARGET" cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | awk '$1 == "blob" {print $2, $3}' | sort -n | tail -1)"
echo "to publish (the user): create the empty GitHub repository, then"
echo "  git -C $TARGET remote add origin <url> && git -C $TARGET push -u origin main $DEV"
