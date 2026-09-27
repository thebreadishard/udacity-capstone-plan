"""Proposed new order for the not-yet-computed part of layer B (dated amendment planned for 28 September 2026; the user, 27 Sep: "3: morgen").

The hashed order of 12 September put small heteroaromatic molecules first (of the first 290 finished: median 18 atoms, 80 % with a heteroatom).
The new order ranks the *pending* B rows by class first and keeps the hash inside each class, so the corpus stays pseudo-random within a class:

  class 0  all-carbon cores with two or more rings (naphthalene, azulene, biphenyl)      — the PAH-like part of B
  class 1  all-carbon one-ring cores (benzene, styrene)
  class 2  heteroaromatic cores with two rings (quinoline, isoquinoline, indole, benzofuran, benzothiophene)
  class 3  heteroaromatic one-ring cores (pyridine, pyrimidine, pyrazine, pyrrole, furan, thiophene, imidazole, oxazole, thiazole)

Inside a class: larger first by n_atoms in bands of 4 (26–23, 22–19, ...), hash order inside a band. Finished and failed rows keep their
position (they are not re-queued). The script only *shows* the new order and writes it to a proposal CSV; `--apply` rewrites the manifest's
`priority` column for the pending B rows (after a `manifest.csv.pre_rehash_<stamp>` copy), which is the step the user authorises tomorrow.

Usage: python rehash_layerB.py [--manifest manifest.csv] [--show 30] [--apply]
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALL_CARBON_MULTI = {"naphthalene", "azulene", "biphenyl"}
ALL_CARBON_ONE = {"benzene", "styrene"}
HETERO_MULTI = {"quinoline", "isoquinoline", "indole", "benzofuran", "benzothiophene"}
HETERO_ONE = {"pyridine", "pyrimidine", "pyrazine", "pyrrole", "furan", "thiophene", "imidazole", "oxazole", "thiazole"}
CLASSES = [ALL_CARBON_MULTI, ALL_CARBON_ONE, HETERO_MULTI, HETERO_ONE]
BAND = 4


def core_of(name: str) -> str:
    return name.split("+")[0]


def core_class(name: str) -> int:
    c = core_of(name)
    for k, s in enumerate(CLASSES):
        if c in s:
            return k
    raise KeyError(f"core {c!r} of {name!r} is in no class — extend the class table before applying")


def new_priority(row: dict) -> str:
    """A sortable string: class digit, size band (larger first), then the old hash. Sorting these strings is the new order."""
    n_atoms = int(row["n_atoms"]) if row.get("n_atoms") else 0
    band = (30 - n_atoms) // BAND                                   # 26 atoms → band 1, 22 → 2, 18 → 3 ...
    return f"{core_class(row['name'])}{band:02d}{row['priority']}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--manifest", default=str(HERE / "manifest.csv"))
    ap.add_argument("--show", type=int, default=30)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(a.manifest, encoding="utf-8")))
    pending = [r for r in rows if r["layer"] == "B" and r["status"] == "pending"]
    for r in pending:
        core_class(r["name"])                                        # every pending core must be classified
    ordered = sorted(pending, key=new_priority)
    print(f"{len(pending)} pending layer-B rows; classes: "
          + ", ".join(f"class {k}: {n}" for k, n in sorted(Counter(core_class(r['name']) for r in pending).items())))
    for r in ordered[: a.show]:
        print(f"  {new_priority(r)[:3]}  {r['n_atoms']:>2} atoms  {r['name']}")
    first = ordered[:300]
    hetero = sum(1 for r in first if core_class(r["name"]) >= 2)
    sizes = sorted(int(r["n_atoms"]) for r in first)
    print(f"first 300 in the new order: median {sizes[len(sizes) // 2]} atoms, {100 * hetero // 300} % heteroaromatic "
          f"(the finished 290 of the old order: median 18 atoms, 80 % heteroaromatic)")
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    proposal = HERE / f"rehash_layerB_proposal_{stamp}.csv"
    with open(proposal, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "new_priority", "n_atoms", "name"])
        for r in ordered:
            w.writerow([r["id"], new_priority(r), r["n_atoms"], r["name"]])
    print(f"proposal written: {proposal.name}")
    if not a.apply:
        return 0
    backup = Path(a.manifest + f".pre_rehash_{stamp}")
    shutil.copy2(a.manifest, backup)
    newp = {r["id"]: new_priority(r) for r in pending}
    for r in rows:
        if r["id"] in newp:
            r["priority"] = newp[r["id"]]
            r["note"] = (r.get("note", "") + " rehash-2026-09-28").strip()
    tmp = a.manifest + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, a.manifest)
    print(f"applied to {a.manifest} (copy at {backup.name}); the shards pick the new order up at their next queue read")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
