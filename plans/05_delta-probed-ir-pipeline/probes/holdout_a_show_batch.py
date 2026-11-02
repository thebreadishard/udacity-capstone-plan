"""The clean hold-out (a)'s batch for the pipeline show (TASKS 146): the eight molecules of `holdout_a_apt`'s ids.tsv, whose refined APTs
`probes/holdout_a_apt_install.py` put into the corpus, written as `probes/show_batch_select.py` writes its batch.tsv, so that
`probes/show_batch_run.sh` (with OUT set to the new folder) runs them through the pipeline by reuse. Names and SMILES from the corpus
manifest; each molecule's role is read from the network's own record (`m08.seen`) and must be hold-out (a).

    python probes/holdout_a_show_batch.py --ids <holdout_a_apt ids.tsv> --out <new folder>
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
sys.path.insert(0, str(PLAN / "probes"))
from m08 import pipeline as P  # noqa: E402
from m08 import seen as S  # noqa: E402
from m08.show import carbon_count  # noqa: E402
from show_batch_select import formula, slug  # noqa: E402

HOLDOUT_A = "a"


def read_ids(path: Path) -> list[str]:
    """The molecule ids of an ids.tsv: the first column of every line that is not a comment."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.split("\t")[0] for line in lines if line.strip() and not line.startswith("#")]


def batch_rows(ids: list[str], manifest: dict[str, dict], seen: S.Seen) -> list[list]:
    """One batch.tsv row per id (folder name, SMILES, id, role, carbon count), smallest carbon count first; refuses an id the manifest
    lacks or one the network's record does not hold out as (a)."""
    rows = []
    for mol_id in ids:
        if mol_id not in manifest:
            raise SystemExit(f"{mol_id} is not in {S.MANIFEST}")
        smiles, name = manifest[mol_id]["smiles"], manifest[mol_id]["name"]
        role = S.status(smiles, seen, mol_id)["role"]
        if role != HOLDOUT_A:
            raise SystemExit(f"{mol_id} ({name}) has role {role!r} in the carried network's record, not hold-out (a)")
        rows.append([slug(name, mol_id), smiles, mol_id, role, carbon_count(formula(smiles))])
    return sorted(rows, key=lambda r: (r[4], r[2]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ids", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    if a.out.exists():
        raise SystemExit(f"{a.out} exists: a batch is never overwritten")
    with S.MANIFEST.open(newline="", encoding="utf-8") as f:
        manifest = {r["id"]: r for r in csv.DictReader(f)}
    rows = batch_rows(read_ids(a.ids), manifest, S.load(P.carried_models()))
    a.out.mkdir(parents=True)
    with open(a.out / "batch.tsv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f, delimiter="\t").writerows(rows)
    for r in rows:
        print("\t".join(map(str, r)))


if __name__ == "__main__":
    main()
