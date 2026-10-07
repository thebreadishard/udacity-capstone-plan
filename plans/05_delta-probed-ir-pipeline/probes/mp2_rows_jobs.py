"""Job list for probes/mp2_rows_queue_ccx53.sh (7 Oct 2026; TASKS 28): one line per (molecule, basis, symmetry-unique displacement), largest first.

The composites need MP2 rows at cc-pVDZ and cc-pVTZ for every symmetry-unique displacement of each cc-pVDZ anchor, in the frame its rows will be
assembled in: the corpus geometry for naphthalene, pyridine, fluorobenzene and benzonitrile; anthracene's plane frame (test 3 already has its seven
out-of-plane rows, so only the fourteen in-plane displacements are queued). Order: estimated cost (atoms⁵, cc-pVTZ ≈ 20 × cc-pVDZ), largest first,
so the long jobs start while every worker is free.

    python probes/mp2_rows_jobs.py <out_dir>     → <out_dir>/jobs.txt and <out_dir>/geom_<name>.json (the files to copy to ~/e8/composite)
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_symmetry as SYM  # noqa: E402

MOLS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
CORPUS_FRAME = {"naphthalene": "A_01f3186607", "pyridine": "A_6e858b26e5", "fluorobenzene": "B_8b12a55d3a", "benzonitrile": "A_3100da3761"}
ANTHRACENE_PF = PLAN / "probes" / "results_m1" / "e8_anthracene_ccpvdz_2026-10-06_partial" / "geometry_planeframe.json"
BASES = (("cc-pvtz", 20.0), ("cc-pvdz", 1.0))


def unique_ks(geom: dict) -> list[int]:
    sym = [s.capitalize() for s in geom["symbols"]]
    x = np.asarray(geom["coords_bohr"], float)
    return SYM.unique_displacements(SYM.point_group_ops(sym, x), len(sym))[0]


def jobs() -> tuple[list[tuple], dict[str, Path]]:
    out, geoms = [], {}
    for name, mol in CORPUS_FRAME.items():
        g = json.loads((MOLS / mol / "geometry.json").read_text(encoding="utf-8"))
        geoms[f"geom_{name}.json"] = MOLS / mol / "geometry.json"
        for basis, w in BASES:
            out += [(w * len(g["symbols"]) ** 5, name, mol, basis, k, f"geom_{name}.json") for k in unique_ks(g)]
    pf = json.loads(ANTHRACENE_PF.read_text(encoding="utf-8"))
    geoms["geometry_planeframe.json"] = ANTHRACENE_PF
    ip = [k for k in pf["unique_ks"] if k not in pf["oop_ks"]]
    for basis, w in BASES:
        out += [(w * len(pf["symbols"]) ** 5, "anthracene", "A_a1e6ec1862", basis, k, "geometry_planeframe.json") for k in ip]
    out.sort(key=lambda j: (-j[0], j[1], j[3], j[4]))
    return out, geoms


def main() -> int:
    d = Path(sys.argv[1])
    d.mkdir(parents=True, exist_ok=True)
    js, geoms = jobs()
    with open(d / "jobs.txt", "w", encoding="utf-8", newline="\n") as f:   # LF: the server reads it (7 Oct: CR endings broke every job)
        f.write("".join(f"{n}|{m}|{b}|{k}|{g}\n" for _, n, m, b, k, g in js))
    for dst, src in geoms.items():
        shutil.copy(src, d / dst)
    per = {}
    for _, n, _, b, _, _ in js:
        per[(n, b)] = per.get((n, b), 0) + 1
    print(f"{len(js)} jobs → {d / 'jobs.txt'}; " + ", ".join(f"{n} {b} {c}" for (n, b), c in sorted(per.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
