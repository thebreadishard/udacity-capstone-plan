"""Spot-check anchors (TASKS 36, 9 Oct 2026): the Cartesian coordinates of a molecule drawn by the registered rule, before any prediction exists.

Rule (Design_2026-10-08_Top_Rung_Anchor_Prices.md §5): the first C and the first H by atom index (the lowest index of an orbit is always its
symmetry-unique representative, so no symmetry detection is needed); for each, the out-of-plane direction = the Cartesian axis with the largest share
of the molecular plane's normal (smallest principal axis of the centred coordinates), and the in-plane direction = the axis with the smallest share.
The geometries need not lie in a coordinate plane; the axis shares are recorded, and a molecule whose best out-of-plane axis carries less than
--min-oop of the normal is refused (the coordinate would mix in- and out-of-plane motion).

    python probes/spot_coordinates.py <geometry.json> [--min-oop 0.98] [--out spot_coords.json]

Prints the --ks argument for lno_curvature_check.py --spot and cc_composite_full_check.py compute --ks.
"""
import argparse
import json
import sys

import numpy as np


def plane_normal(coords: np.ndarray) -> np.ndarray:
    xc = coords - coords.mean(0)
    return np.linalg.eigh(xc.T @ xc)[1][:, 0]


def draw(symbols: list[str], coords: np.ndarray, min_oop: float = 0.98) -> list[dict]:
    share = np.abs(plane_normal(np.asarray(coords, float)))
    oop_ax, ip_ax = int(np.argmax(share)), int(np.argmin(share))
    if share[oop_ax] < min_oop:
        raise ValueError(f"no Cartesian axis carries ≥ {min_oop} of the plane normal (best {share[oop_ax]:.3f})")
    sym = [s.capitalize() for s in symbols]
    rows = []
    for el in ("C", "H"):
        if el not in sym:
            raise ValueError(f"no {el} atom")
        i = sym.index(el)
        for kind, ax in (("out-of-plane", oop_ax), ("in-plane", ip_ax)):
            rows.append(dict(k=3 * i + ax, atom=i, element=el, axis="xyz"[ax], kind=kind, oop_share=round(float(share[ax]), 4)))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("geometry")
    ap.add_argument("--min-oop", type=float, default=0.98)
    ap.add_argument("--out")
    a = ap.parse_args()
    g = json.load(open(a.geometry))
    rows = draw(g["symbols"], np.asarray(g["coords_bohr"], float), a.min_oop)
    for r in rows:
        print(f"k {r['k']:3d}: {r['element']}{r['atom']} {r['axis']} ({r['kind']}, normal share {r['oop_share']:.3f})")
    ks = ",".join(str(r["k"]) for r in rows)
    print(f"--ks {ks}")
    if a.out:
        json.dump(dict(geometry=a.geometry, rule="first C and first H by index; oop = max normal share, in-plane = min", ks=ks, rows=rows),
                  open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
