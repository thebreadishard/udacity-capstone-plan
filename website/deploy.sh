#!/bin/bash
# Spectrum Atlas — publish the built site to github.com/thebreadishard/spectrum-atlas (branch gh-pages → GitHub Pages).
# The source of truth stays in this monorepo (website/export → website/site); the public repository holds the built static site only.
# Steps: export (unless --no-export) → astro build with base /spectrum-atlas → .nojekyll (Astro's _astro/ folder) → force-push dist/ to gh-pages.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_URL="https://github.com/thebreadishard/spectrum-atlas.git"
if [ "${1:-}" != "--no-export" ]; then
  (cd "$HERE/export" && PYTHONIOENCODING=utf-8 python build_catalog.py > /dev/null && PYTHONIOENCODING=utf-8 python depict.py > /dev/null)
fi
(cd "$HERE/site" && npm run build > /dev/null)
touch "$HERE/site/dist/.nojekyll"
cp "$HERE/site/public/README.md" "$HERE/site/dist/README.md" 2>/dev/null || true
TMP="$(mktemp -d)"
git clone -q --depth 1 --branch gh-pages "$REPO_URL" "$TMP/pages" 2>/dev/null || { git init -q "$TMP/pages" && (cd "$TMP/pages" && git checkout -q -b gh-pages && git remote add origin "$REPO_URL"); }
(cd "$TMP/pages" && git rm -rq . 2>/dev/null || true)
cp -r "$HERE/site/dist/." "$TMP/pages/"
(cd "$TMP/pages" && git add -A && git -c user.name="Frederic Petrignani" -c user.email="frederic.petrignani@gmail.com" commit -qm "Publish Spectrum Atlas $(date -u +%Y-%m-%dT%H:%MZ) (built from the CapstonePlan monorepo, $(cd "$HERE" && git rev-parse --short HEAD))" && git push -q -f origin gh-pages)
echo "published: https://thebreadishard.github.io/spectrum-atlas/  (size: $(du -sh "$HERE/site/dist" | cut -f1))"
rm -rf "$TMP"
