"""The pipeline show on the Atlas (TASKS 161 (2), 2 Nov 2026): copies module 08's built show to site/public/pipeline/index.html (served as
/pipeline/) and its index of linked molecules to out/pipeline_show.json, which the molecule pages read for their 'see it go through the
pipeline' link. Run by deploy.sh before the site build; the show itself is built by `python -m m08.show … --check-links`.

    python pipeline_show.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOW = HERE.parents[1] / "plans" / "05_delta-probed-ir-pipeline" / "modules" / "08_industry_synthesis" / "out"
PAGE_OUT = HERE.parent / "site" / "public" / "pipeline" / "index.html"
INDEX_OUT = HERE / "out" / "pipeline_show.json"


def copy_atomic(src: Path, dst: Path) -> str:
    """Copy src over dst through a temporary file; return the sha256 of the bytes copied."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".tmp")
    shutil.copyfile(src, tmp)
    os.replace(tmp, dst)
    return hashlib.sha256(dst.read_bytes()).hexdigest()


def main() -> int:
    page, index = SHOW / "pipeline_show.html", SHOW / "pipeline_show_index.json"
    missing = [str(p) for p in (page, index) if not p.exists()]
    if missing:
        raise SystemExit(f"pipeline_show.py: build the show first (python -m m08.show … --check-links); missing {missing}")
    if page.stat().st_mtime > index.stat().st_mtime + 60:
        raise SystemExit("pipeline_show.py: the show page is newer than its index — rebuild the show so both come from one build")
    linked = json.loads(index.read_text(encoding="utf-8"))["molecules"]
    sha_page = copy_atomic(page, PAGE_OUT)
    copy_atomic(index, INDEX_OUT)
    print(f"pipeline show: {page.stat().st_size / 1024:.0f} KB to {PAGE_OUT.relative_to(HERE.parent)} (sha256 {sha_page[:12]}), "
          f"{len(linked)} linked molecules to {INDEX_OUT.relative_to(HERE.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
