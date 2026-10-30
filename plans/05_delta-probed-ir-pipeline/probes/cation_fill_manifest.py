"""The cation fill into the corpus manifest (TASKS 121; decision 52's 30 per cell over the cation twins; the user approved the CSV on 30 Oct
2026): every row of `compute_prices.py cations`' CSV becomes a pending P3c row — the layer `run_corpus.py` runs with the cation deck, the
neutral parent's SMILES and `parent <id>` in the note, as pool 3's 60 cations are written. Checked before anything is written: the id is
the parent's hash under P3c, the parent is a done row of the manifest or a fetched shard's molecule, the atom count is RDKit's. A cation
whose parent is computed but not merged yet (no geometry.json under corpus/molecules, which `run_corpus.py` starts a cation from) is held
and named; run the script again after the merge. A row already written identically is skipped, a different one stops the fill. The
manifest is copied beside itself first and replaced through a temp file.

    python probes/cation_fill_manifest.py <cation_candidates.csv>            # checks and counts only
    python probes/cation_fill_manifest.py <cation_candidates.csv> --write    # appends the ready rows (after the user's review)
"""
from __future__ import annotations

import argparse
import csv
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import anchor_plan as AP  # noqa: E402
import pool3_candidates as P3  # noqa: E402

BM = P3.BM                                     # the corpus's manifest code, on the path through pool3_candidates
import run_corpus as RC  # noqa: E402

MANIFEST = P3.M05 / "corpus" / "manifest.csv"
NOTE = "cation fill (decision 52); parent {parent}; charge {charge} mult {mult}"


@dataclass(frozen=True)
class Fill:
    """The rows to append, the cations held until their parent is merged, and the ids already written identically."""
    rows: list[dict]
    held: list[str]
    written: list[str]


def check_candidate(c: dict, by_id: dict[str, dict], computed: set[str]) -> dict:
    """A candidate's manifest row after its checks; any failure raises."""
    parent = by_id.get(c["parent_id"])
    if c["parent_id"] not in computed or parent is None:
        raise ValueError(f"{c['id']}: parent {c['parent_id']} is neither done in the manifest nor in a fetched shard")
    if parent["smiles"] != c["parent_smiles"]:
        raise ValueError(f"{c['id']}: the CSV's parent SMILES differs from the manifest's")
    if c["id"] != "P3c_" + P3.sha(c["parent_smiles"])[:10]:
        raise ValueError(f"{c['id']}: not the parent's hash under P3c")
    n_heavy, n_atoms = P3.atom_counts(c["parent_smiles"])
    if n_atoms != int(c["n_atoms"]):
        raise ValueError(f"{c['id']}: {c['n_atoms']} atoms in the CSV, {n_atoms} by RDKit")
    note = NOTE.format(parent=c["parent_id"], charge=c["charge"], mult=c["multiplicity"])
    return P3.manifest_row({"id": c["id"], "layer": "P3c", "name": c["name"], "smiles": c["parent_smiles"], "n_heavy": n_heavy,
                            "n_atoms": n_atoms, "note": note})


def _merged(row: dict) -> bool:
    try:
        RC.parent_geometry_path(row)
    except RuntimeError:
        return False
    return True


def fill(candidates: list[dict], manifest: list[dict], computed: set[str]) -> Fill:
    """Every candidate checked; the ready rows, the held ids and the already written ids apart."""
    if len({c["id"] for c in candidates}) != len(candidates):
        raise ValueError("the CSV names an id twice")
    by_id = {r["id"]: r for r in manifest}
    rows, held, written = [], [], []
    for c in candidates:
        row = check_candidate(c, by_id, computed)
        if c["id"] in by_id:
            if {k: str(v) for k, v in row.items()} != by_id[c["id"]]:
                raise ValueError(f"{c['id']}: in the manifest with other values")
            written.append(c["id"])
        elif _merged(row):
            rows.append(row)
        else:
            held.append(c["id"])
    return Fill(rows, held, written)


def write(rows: list[dict], manifest_path: Path) -> Path:
    """The manifest with the rows appended, in its own line ending; a dated copy is kept beside it."""
    backup = manifest_path.with_name(f"{manifest_path.name}.pre_cation_fill_{time.strftime('%Y-%m-%d_%H%M')}")
    shutil.copy2(manifest_path, backup)
    term = "\r\n" if b"\r\n" in manifest_path.read_bytes()[:4096] else "\n"
    tmp = manifest_path.with_suffix(".csv.tmp")
    with manifest_path.open(newline="", encoding="utf-8") as src, tmp.open("w", newline="", encoding="utf-8") as dst:
        existing = list(csv.DictReader(src))
        w = csv.DictWriter(dst, fieldnames=BM.FIELDS, lineterminator=term)
        w.writeheader()
        w.writerows(existing)
        w.writerows(rows)
    tmp.replace(manifest_path)
    return backup


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidates", type=Path)
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--write", action="store_true", help="append the ready rows (after the user's review of the CSV)")
    a = ap.parse_args(argv)
    with a.candidates.open(newline="", encoding="utf-8") as f:
        candidates = list(csv.DictReader(f))
    manifest = P3.manifest_rows(a.manifest)
    f = fill(candidates, manifest, AP.computed_ids(manifest))
    print(f"{len(candidates)} candidates: {len(f.rows)} ready (P3c, pending), {len(f.written)} already written, "
          f"{len(f.held)} held until their parent is merged" + (f" (first: {', '.join(f.held[:3])})" if f.held else ""))
    if a.write and f.rows:
        backup = write(f.rows, a.manifest)
        print(f"appended {len(f.rows)} rows to {a.manifest}; the previous manifest kept as {backup.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
