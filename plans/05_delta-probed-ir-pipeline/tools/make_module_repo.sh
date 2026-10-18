#!/usr/bin/env bash
# tools/make_module_repo.sh <module dir> <dev branch> <target dir> [<main ref>] [--no-run] (17 Oct 2026; module 02's review) — a Udacity
# module as its own repository with its own history. The rubrics ask for a named repository with multiple commits and at least one
# development branch; a copy of the folder would have one commit. `git subtree split` keeps every commit that touched the module, with the
# module folder as the new root: <main ref> (default master) becomes `main`, <dev branch> keeps its name. Nothing is pushed: the user creates
# the repository on GitHub and pushes both branches (the commands are printed at the end).
#   bash tools/make_module_repo.sh plans/05_delta-probed-ir-pipeline/modules/02_opponent_atlas module-02-opponent-atlas /c/tmp/ai-programming-foundations-project
# 18 Oct 2026 (the user: a submitted module must run standalone — other modules' folders do not exist then; builders stay in the plan
# repository, option 1): when the module holds a SUBMISSION.txt (one path or 'dir/' per line, '#' comments, 'run: <notebook> [VAR=value …]'
# lines, the assignments set for that notebook's execution only — module 05's labelled pipeline check M05_QUICK=1), `main`
# gets one more commit that keeps only those files, and the repository is then checked in a fresh clone: every listed path exists, no README
# link leaves the repository, and every 'run:' notebook executes there with no error and no unexecuted cell (tools/notebook_ran.py).
# Any failure stops with exit 1. --no-run skips the execution (a notebook that trains for hours), not the other checks.
# Run from anywhere inside the plan repository; the temporary split branches are removed again.
set -euo pipefail
NO_RUN=0
ARGS=()
for a in "$@"; do [ "$a" = --no-run ] && NO_RUN=1 || ARGS+=("$a"); done
MODULE=${ARGS[0]:?module dir, relative to the repository root}
DEV=${ARGS[1]:?development branch}
TARGET=${ARGS[2]:?target dir (must not exist)}
MAIN_REF=${ARGS[3]:-master}
TOOLS=$(cd "$(dirname "$0")" && pwd)
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
[ -d "$MODULE" ] || { echo "no module dir $MODULE" >&2; exit 2; }
[ -e "$TARGET" ] && { echo "target $TARGET exists; refusing to overwrite" >&2; exit 2; }
dev_ref=$DEV
git rev-parse --verify -q "$dev_ref" > /dev/null || dev_ref="origin/$DEV"
git rev-parse --verify -q "$dev_ref" > /dev/null || { echo "no branch $DEV (local or origin)" >&2; exit 2; }
AUTHOR_NAME=$(git config user.name || true)
AUTHOR_EMAIL=$(git config user.email || true)
[ -n "$AUTHOR_NAME" ] && [ -n "$AUTHOR_EMAIL" ] || { echo "no git user.name/user.email for the submission commit" >&2; exit 2; }

tag=$(date +%s)
split_main="split-main-$tag"
split_dev="split-dev-$tag"
CHECK=""
cleanup() { git branch -D -q "$split_main" "$split_dev" 2> /dev/null || true; [ -z "$CHECK" ] || rm -rf "$CHECK"; }
trap cleanup EXIT
git subtree split -q --prefix="$MODULE" "$MAIN_REF" -b "$split_main" > /dev/null
git subtree split -q --prefix="$MODULE" "$dev_ref" -b "$split_dev" > /dev/null

git init -q -b main "$TARGET"
git -C "$TARGET" fetch -q "$ROOT" "$split_main:refs/heads/main-tmp" "$split_dev:refs/heads/$DEV"   # git refuses to fetch into the unborn current branch
git -C "$TARGET" branch -m main-tmp main
git -C "$TARGET" checkout -q main

# ---- deliverables only (SUBMISSION.txt)
MANIFEST="$TARGET/SUBMISSION.txt"
runs=()
if [ -f "$MANIFEST" ]; then
  keep=()
  while IFS= read -r line; do
    line=${line%$'\r'}; line=${line%%#*}; line=$(echo "$line" | sed 's/[[:space:]]*$//')
    [ -z "$line" ] && continue
    case "$line" in run:*) runs+=("$(echo "${line#run:}" | sed 's/^[[:space:]]*//')") ;; *) keep+=("$line") ;; esac
  done < "$MANIFEST"
  for k in "${keep[@]}"; do [ -e "$TARGET/$k" ] || { echo "SUBMISSION.txt lists $k, which the module does not hold" >&2; exit 1; }; done
  for spec in "${runs[@]}"; do
    read -r -a words <<< "$spec"
    for w in "${words[@]:1}"; do [[ "$w" =~ ^[A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*$ ]] || { echo "run line '$spec': '$w' is not a VAR=value assignment" >&2; exit 1; }; done
  done
  drop=()
  while IFS= read -r f; do
    hit=0
    for k in "${keep[@]}"; do case "$k" in */) [[ "$f" == "$k"* ]] && hit=1 ;; *) [ "$f" = "$k" ] && hit=1 ;; esac; done
    [ "$hit" = 0 ] && drop+=("$f")
  done < <(git -C "$TARGET" ls-files)
  if [ "${#drop[@]}" -gt 0 ]; then
    printf '%s\0' "${drop[@]}" | git -C "$TARGET" rm -q --pathspec-from-file=- --pathspec-file-nul
    git -C "$TARGET" -c user.name="$AUTHOR_NAME" -c user.email="$AUTHOR_EMAIL" commit -q \
      -m "Submission: the deliverables and the data the notebook reads; the scripts that made them stay in the plan repository"
  fi
  echo "  kept ${#keep[@]} entries of SUBMISSION.txt, removed ${#drop[@]} files"
fi

# ---- standalone check in a fresh clone
CHECK=$(mktemp -d)
git clone -q "$TARGET" "$CHECK/repo"
if grep -nE '\]\(\.\./' "$CHECK/repo/README.md" 2> /dev/null; then echo "README links outside the repository (above)" >&2; exit 1; fi
if [ "$NO_RUN" = 0 ]; then
  for spec in "${runs[@]}"; do
    read -r -a words <<< "$spec"
    nb=${words[0]}
    d=$(dirname "$CHECK/repo/$nb")
    (cd "$d" && env "${words[@]:1}" jupyter nbconvert --to notebook --execute "$(basename "$nb")" --output-dir "$CHECK/out" --output ran.ipynb \
      --ExecutePreprocessor.timeout=1800 > "$CHECK/nbconvert.log" 2>&1) || { tail -5 "$CHECK/nbconvert.log" >&2; echo "notebook $nb fails in a fresh clone" >&2; exit 1; }
    python "$TOOLS/notebook_ran.py" "$CHECK/out/ran.ipynb" || exit 1
  done
fi

echo "repository at $TARGET"
for b in main "$DEV"; do echo "  $b: $(git -C "$TARGET" rev-list --count "$b") commits"; done
echo "  files on main: $(git -C "$TARGET" ls-files | wc -l)"
echo "  largest file in history: $(git -C "$TARGET" rev-list --objects --all | git -C "$TARGET" cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | awk '$1 == "blob" {print $2, $3}' | sort -n | tail -1)"
echo "  standalone check: $([ "$NO_RUN" = 1 ] && echo 'files and links only (--no-run)' || echo "passed (${#runs[@]} notebook(s) executed in a fresh clone)")"
echo "to publish (the user): create the empty GitHub repository, then"
echo "  git -C $TARGET remote add origin <url> && git -C $TARGET push -u origin main $DEV"
