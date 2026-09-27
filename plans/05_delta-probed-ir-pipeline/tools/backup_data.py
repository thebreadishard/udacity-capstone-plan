"""Mirror the computed results that the code repository ignores into a separate data repository (the user, 27 September 2026: "gratis op GitHub
is prima"; the GB-scale psi4 logs stay on the laptop until the PC arrives).

What is mirrored (relative to the plan directory), and what is not:
  modules/05_support_predictor/corpus/molecules/   every file except psi4.out and worker_stdout.txt (the 1.9 GB of logs; reproducible)
  modules/05_support_predictor/corpus/{manifest,ledger}.csv, STATUS.md
  modules/05_support_predictor/data/corpus_release/, data/second_route/, data/e9/
  modules/05_support_predictor/out/                 run records incl. the *.pt checkpoints the code repo ignores
  modules/standout_pattern_proposer/out/
  probes/results_m1/                                (small; also in the code repo, kept here so the data repo stands alone)
Not mirrored: data/hessian_qm9 (8 GB, re-downloadable), notebook logs, anything under the scratchpad.

Files are copied when size or mtime differ; nothing is deleted in the mirror. Then one commit in the mirror with the clock's stamp and, unless
--no-push, a push to its remote. --dry-run lists counts and megabytes only.

Usage: python tools/backup_data.py [--mirror C:\\Users\\thebr\\Documents\\CapstoneData] [--dry-run] [--no-push]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
M05 = "modules/05_support_predictor"
SOURCES = [                                                   # (relative dir, excluded file names)
    (f"{M05}/corpus/molecules", {"psi4.out", "worker_stdout.txt"}),
    (f"{M05}/data/corpus_release", set()),
    (f"{M05}/data/second_route", set()),
    (f"{M05}/data/e9", set()),
    (f"{M05}/out", set()),
    ("modules/standout_pattern_proposer/out", set()),
    ("probes/results_m1", set()),
]
SINGLE_FILES = [f"{M05}/corpus/manifest.csv", f"{M05}/corpus/ledger.csv", f"{M05}/corpus/STATUS.md"]
EXCLUDED_SUFFIXES = {".tmp", ".lock", ".pid"}


def iter_files(rel_dir: str, excluded: set[str]):
    root = PLAN / rel_dir
    if not root.is_dir():
        return
    for p in root.rglob("*"):
        if p.is_file() and p.name not in excluded and p.suffix not in EXCLUDED_SUFFIXES:
            yield p


def needs_copy(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True
    s, d = src.stat(), dst.stat()
    return s.st_size != d.st_size or int(s.st_mtime) > int(d.st_mtime)


def plan_copies(mirror: Path) -> tuple[list[tuple[Path, Path]], int, int]:
    """(pairs to copy, files considered, bytes considered)."""
    pairs, n, total = [], 0, 0
    files = [(p, p.relative_to(PLAN)) for rel, ex in SOURCES for p in iter_files(rel, ex)]
    files += [(PLAN / f, Path(f)) for f in SINGLE_FILES if (PLAN / f).is_file()]
    for src, rel in files:
        n += 1
        total += src.stat().st_size
        dst = mirror / rel
        if needs_copy(src, dst):
            pairs.append((src, dst))
    return pairs, n, total


def git(mirror: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(mirror), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {mirror}: {r.stderr.strip()}")
    return r.stdout.strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mirror", default=str(Path.home() / "Documents" / "CapstoneData"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args(argv)
    mirror = Path(a.mirror)
    pairs, n, total = plan_copies(mirror)
    changed = sum(s.stat().st_size for s, _ in pairs)
    print(f"{n} files, {total / 2**20:.0f} MB considered; {len(pairs)} to copy ({changed / 2**20:.1f} MB) into {mirror}")
    if a.dry_run:
        for s, _ in pairs[:10]:
            print("  ", s.relative_to(PLAN))
        return 0
    if not (mirror / ".git").is_dir():
        raise SystemExit(f"{mirror} is not a git repository — clone the data repository there first (git clone <url> {mirror})")
    for src, dst in pairs:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"- {stamp}: {len(pairs)} files copied ({changed / 2**20:.1f} MB); {n} files, {total / 2**20:.0f} MB in the mirror\n"
    with (mirror / "BACKUP_LOG.md").open("a", encoding="utf-8") as fh:
        fh.write(line)
    git(mirror, "add", "-A", ".")                                       # the mirror holds data only; adding everything is its purpose
    if git(mirror, "status", "--porcelain"):
        git(mirror, "commit", "-q", "-m", f"backup {stamp}: {len(pairs)} files ({changed / 2**20:.1f} MB)")
        print(f"committed {len(pairs)} files")
    else:
        print("nothing new to commit")
    if not a.no_push:
        if git(mirror, "remote", check=False):
            git(mirror, "push", "-q")
            print("pushed")
        else:
            print("no remote configured — not pushed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
