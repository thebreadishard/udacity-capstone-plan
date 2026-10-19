"""Pack the psi4 logs that the data mirror leaves out into one compressed archive with a sha256 list, for a release asset of capstone-data
(the user, 19 Oct 2026: 'optie 1: een gecomprimeerd archief als release-bijlage in capstone-data op GitHub'). The logs hold the only copy
of every displaced geometry's energy and gradient that a corpus Hessian was built from (the .npz files keep the assembled Hessian only), so
a label can be re-checked or re-assembled without recomputing it.

Which files: those tools/backup_data.py excludes by name (PSI4_LOGS) under its sources — one definition, imported. The archive holds the
files at their plan-relative paths plus the sha256 list; after writing, the archive is read back and every member checked against the list.

    python tools/archive_psi4_logs.py --out C:\\Users\\thebr\\Documents\\CapstoneData_archives [--date 2026-10-19]

Writes <out>/psi4_logs_<date>.tar.xz and <out>/psi4_logs_<date>.sha256.tsv (path, bytes, sha256). Progress lines '[hh:mm:ss] packed k/N'
every PROGRESS_EVERY files; the end line '=== ARCHIVE VERIFIED …'.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import sys
import tarfile
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup_data import PLAN, PSI4_LOGS, SOURCES

PROGRESS_EVERY = 25
XZ_PRESET = 6
CHUNK = 1 << 20


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def collect(plan: Path, sources: list[tuple[str, set[str] | frozenset[str]]], names: frozenset[str]) -> list[str]:
    """Plan-relative paths of the files named in `names` under every source that excludes them, sorted."""
    out = set()
    for rel, excluded in sources:
        if not names & set(excluded):
            continue
        root = plan / rel
        if root.is_dir():
            out |= {p.relative_to(plan).as_posix() for p in root.rglob("*") if p.name in names and p.is_file()}
    return sorted(out)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def manifest_text(plan: Path, files: list[str]) -> str:
    return "".join(f"{f}\t{(plan / f).stat().st_size}\t{sha256_of(plan / f)}\n" for f in files)


def build(plan: Path, files: list[str], manifest: str, archive: Path) -> None:
    """The archive through a temp file moved over the target: the sha256 list first, then every file at its plan-relative path."""
    tmp = archive.with_name(archive.name + ".tmp")
    with tarfile.open(tmp, "w:xz", preset=XZ_PRESET) as tar:
        data = manifest.encode("utf-8")
        info = tarfile.TarInfo("SHA256SUMS.tsv")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
        for k, f in enumerate(files, 1):
            tar.add(plan / f, arcname=f, recursive=False)
            if k % PROGRESS_EVERY == 0 or k == len(files):
                log(f"packed {k}/{len(files)}")
    os.replace(tmp, archive)


def verify(archive: Path, manifest: str) -> int:
    """Every listed file is in the archive with its size and sha256, and nothing else is; returns the file count."""
    expected = {path: (int(size), digest) for path, size, digest in (line.split("\t") for line in manifest.splitlines())}
    seen = {}
    with tarfile.open(archive, "r:xz") as tar:
        for member in tar:
            if member.name == "SHA256SUMS.tsv" or not member.isfile():
                continue
            h = hashlib.sha256()
            fh = tar.extractfile(member)
            for block in iter(lambda fh=fh: fh.read(CHUNK), b""):
                h.update(block)
            seen[member.name] = (member.size, h.hexdigest())
    if seen != expected:
        missing, extra = sorted(set(expected) - set(seen)), sorted(set(seen) - set(expected))
        changed = sorted(p for p in set(seen) & set(expected) if seen[p] != expected[p])
        raise SystemExit(f"archive does not match its list: missing {missing[:5]}, extra {extra[:5]}, changed {changed[:5]}")
    return len(seen)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.resolve().is_relative_to(PLAN.resolve()):
        raise SystemExit(f"--out {out} lies inside the plan: the archive must stay out of the code repository")
    archive, listing = out / f"psi4_logs_{a.date}.tar.xz", out / f"psi4_logs_{a.date}.sha256.tsv"
    if archive.exists() or listing.exists():
        raise SystemExit(f"{archive} or its list exists - not overwritten")
    files = collect(PLAN, SOURCES, PSI4_LOGS)
    if not files:
        raise SystemExit("no psi4 logs found under the mirror's sources")
    log(f"{len(files)} logs, {sum((PLAN / f).stat().st_size for f in files) / 1e9:.2f} GB; hashing")
    manifest = manifest_text(PLAN, files)
    out.mkdir(parents=True, exist_ok=True)
    with open(listing.with_name(listing.name + ".tmp"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(manifest)
    os.replace(listing.with_name(listing.name + ".tmp"), listing)
    build(PLAN, files, manifest, archive)
    log("reading the archive back")
    n = verify(archive, manifest)
    raw = sum(int(line.split("\t")[1]) for line in manifest.splitlines())
    print(f"=== ARCHIVE VERIFIED {archive} {n} files {raw} bytes -> {archive.stat().st_size} bytes {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
