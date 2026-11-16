"""Analytic labels fetched from a label server, merged into the corpus by a checked copy (TASKS 171).

The merges of 8 and 10 Nov 2026 were made by hand with these checks; this is the same procedure as one script, so that 222 molecules
get the checks 60 got. For every molecule folder of the source: the corpus must hold the folder, and its `geometry.json` must equal the
source's byte for byte — a label belongs to the geometry it was computed at. Each label file is then planned: absent in the corpus
(copy), present and identical (nothing to do), present and different (refused); a leftover `<file>.tmp` of an earlier, interrupted
copy is refused too. Nothing is written unless every molecule passes and the source holds exactly the expected number of molecules.
A copy goes to a temp file, which is compared with the source before it is moved onto a target that must still be absent. The record
names every label file with its sha256, copied or already there, and is written even when a copy fails. The finite-difference labels
in the corpus (`hessian_b3lyp.npz`, `hessian_wb97x.npz`) and every other file of the source are not touched.

    python probes/labels_merge_checked.py <source molecules dir> <corpus molecules dir> <record.json> --expect-molecules N [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

GEOMETRY = "geometry.json"
LABEL_FILES = ("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz", "dipole_b3lyp_cphf.npz", "analytic_check.json")
TMP_SUFFIX = ".tmp"


@dataclass(frozen=True)
class Plan:
    """What a merge will do: the source's molecule ids, the files to copy and the ones already there as (id, file name), and the
    reasons to refuse."""

    molecule_ids: tuple[str, ...]
    copies: tuple[tuple[str, str], ...]
    identical: tuple[tuple[str, str], ...]
    refusals: tuple[str, ...]


def sha256(path: Path) -> str:
    """The file's sha256 as hex."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_molecule(molecule_id: str, source: Path, corpus: Path) -> tuple[list[str], list[str], list[str]]:
    """(files to copy, files already identical, reasons to refuse) for one molecule."""
    src, dst = source / molecule_id, corpus / molecule_id
    if not dst.is_dir():
        return [], [], [f"{molecule_id}: no such folder in the corpus"]
    if not (src / GEOMETRY).is_file() or not (dst / GEOMETRY).is_file():
        return [], [], [f"{molecule_id}: {GEOMETRY} missing in the source or the corpus"]
    if (src / GEOMETRY).read_bytes() != (dst / GEOMETRY).read_bytes():
        return [], [], [f"{molecule_id}: {GEOMETRY} differs between the source and the corpus"]
    copies, identical, refusals = [], [], []
    for name in LABEL_FILES:
        if not (src / name).is_file():
            refusals.append(f"{molecule_id}: the source has no {name}")
        elif (dst / (name + TMP_SUFFIX)).exists():
            refusals.append(f"{molecule_id}: a leftover {name + TMP_SUFFIX} of an interrupted copy is in the corpus; look at it and remove it")
        elif not (dst / name).exists():
            copies.append(name)
        elif sha256(src / name) == sha256(dst / name):
            identical.append(name)
        else:
            refusals.append(f"{molecule_id}: the corpus already holds another {name}")
    return copies, identical, refusals


def plan(source: Path, corpus: Path, expect_molecules: int) -> Plan:
    """The plan for every molecule folder of the source; refused when their number is not the expected one."""
    ids = tuple(sorted(p.name for p in source.iterdir() if p.is_dir()))
    copies, identical, refusals = [], [], []
    if len(ids) != expect_molecules:
        refusals.append(f"{source}: {len(ids)} molecule folders, {expect_molecules} expected")
    for molecule_id in ids:
        c, i, r = plan_molecule(molecule_id, source, corpus)
        copies += [(molecule_id, name) for name in c]
        identical += [(molecule_id, name) for name in i]
        refusals += r
    return Plan(ids, tuple(copies), tuple(identical), tuple(refusals))


def copy_checked(src: Path, dst: Path) -> str:
    """Copy one file to a temp file, compare that with the source, and move it onto a target that is still absent; its sha256."""
    tmp = dst.with_name(dst.name + TMP_SUFFIX)
    shutil.copyfile(src, tmp)
    digest = sha256(tmp)
    if digest != sha256(src):
        tmp.unlink()
        raise RuntimeError(f"{tmp}: the copy differs from {src}; nothing was put in its place")
    if dst.exists():
        tmp.unlink()
        raise RuntimeError(f"{dst} appeared after the merge was planned; it is left as it is")
    os.replace(tmp, dst)
    return digest


def new_record(planned: Plan, source: Path, corpus: Path, *, dry_run: bool) -> dict:
    """The record before any copy: the plan's counts, the refusals and the sha256 of every file already in the corpus."""
    return {"source": str(source), "corpus": str(corpus), "dry_run": dry_run, "label_files": list(LABEL_FILES),
            "source_molecules": len(planned.molecule_ids), "to_copy": len(planned.copies), "refusals": list(planned.refusals),
            "identical": {f"{m}/{name}": sha256(corpus / m / name) for m, name in planned.identical}, "copied": {}, "error": None}


def merge(source: Path, corpus: Path, expect_molecules: int, *, dry_run: bool) -> dict:
    """Plan, then refuse or copy. The record says what was done; a copy that fails stops the merge and is named in `error`."""
    planned = plan(source, corpus, expect_molecules)
    record = new_record(planned, source, corpus, dry_run=dry_run)
    if planned.refusals or dry_run:
        return record
    for molecule_id, name in planned.copies:
        try:
            record["copied"][f"{molecule_id}/{name}"] = copy_checked(source / molecule_id / name, corpus / molecule_id / name)
        except (OSError, RuntimeError) as err:
            record["error"] = f"{molecule_id}/{name}: {type(err).__name__}: {err}"
            break
    return record


def write_record(path: Path, record: dict) -> None:
    """The record through a temp file moved over the target."""
    tmp = path.with_name(path.name + TMP_SUFFIX)
    tmp.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("corpus", type=Path)
    ap.add_argument("record", type=Path)
    ap.add_argument("--expect-molecules", type=int, required=True, help="the number of molecule folders the source must hold")
    ap.add_argument("--dry-run", action="store_true", help="plan and report; copy nothing")
    a = ap.parse_args()
    for folder in (a.source, a.corpus):
        if not folder.is_dir():
            raise SystemExit(f"{folder}: no such folder")
    if a.record.exists():
        raise SystemExit(f"{a.record} exists: a record is evidence and is not overwritten; name another")
    record = merge(a.source, a.corpus, a.expect_molecules, dry_run=a.dry_run)
    write_record(a.record, record)
    print(f"{record['source_molecules']} molecules: {record['to_copy']} files to copy, {len(record['identical'])} already identical, "
          f"{len(record['refusals'])} refusals; {'DRY RUN' if a.dry_run else f'{len(record['copied'])} copied'}", flush=True)
    if record["refusals"]:
        raise SystemExit("REFUSED, nothing copied:\n  " + "\n  ".join(record["refusals"][:20]))
    if record["error"]:
        raise SystemExit(f"STOPPED after {len(record['copied'])} copies: {record['error']} (the record is in {a.record}; run again)")


if __name__ == "__main__":
    main()
