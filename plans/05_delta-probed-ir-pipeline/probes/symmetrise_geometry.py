"""Symmetrise a geometry over the point-group operations it approximately satisfies (2026-09-15; decision 37's prerequisite).

Reads results_dryrun/<molecule>/stageA.json (coords in bohr), moves to the centre of mass and the principal axes,
finds which of the D2h operations (inversion, the three C2 rotations about the principal axes, the three reflections
through the principal planes) map the atom set onto itself within --detect bohr, and replaces every coordinate by
its average over the orbit of that group:  x_sym = (1/|G|) Σ_g g⁻¹ x[π_g], with π_g the atom permutation of g.
Prints the largest deviation from symmetry before and after (the 02:52 finding at naphthalene: 4–7e-5 bohr before),
and writes <molecule>/geometry_symmetrised.json (bohr and Å, the group found, the deviations) for the dry run's
stage A, which must then be run with the point group on so that the normal modes are irrep-pure.

Usage: python symmetrise_geometry.py --molecule naphthalene [--detect 1e-3]
Pure NumPy; runs in seconds beside a live anchor job.
"""
import argparse
import itertools
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BOHR = 0.529177210903
OPS = {"E": np.diag([1, 1, 1]), "i": np.diag([-1, -1, -1]),
       "C2z": np.diag([-1, -1, 1]), "C2y": np.diag([-1, 1, -1]), "C2x": np.diag([1, -1, -1]),
       "s_xy": np.diag([1, 1, -1]), "s_xz": np.diag([1, -1, 1]), "s_yz": np.diag([-1, 1, 1])}


def principal_frame(x, m):
    com = (m[:, None] * x).sum(0) / m.sum()
    y = x - com
    I = np.zeros((3, 3))
    for yi, mi in zip(y, m):
        I += mi * (np.dot(yi, yi) * np.eye(3) - np.outer(yi, yi))
    w, V = np.linalg.eigh(I)
    if np.linalg.det(V) < 0:
        V[:, 0] *= -1
    return y @ V, w


def permutation(x, symbols, g, tol):
    """Atom permutation induced by g, or None if some image has no partner of the same element within tol."""
    img = x @ g.T
    perm = []
    for k, p in enumerate(img):
        d = np.linalg.norm(x - p, axis=1)
        j = int(np.argmin(d))
        if d[j] > tol or symbols[j] != symbols[k]:
            return None
        perm.append(j)
    return perm if len(set(perm)) == len(perm) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", required=True)
    ap.add_argument("--detect", type=float, default=1e-3, help="bohr; an operation counts if every atom maps within this")
    args = ap.parse_args()
    d = os.path.join(HERE, "results_dryrun", args.molecule)
    a = json.load(open(os.path.join(d, "stageA.json")))
    x0 = np.array(a["coords_bohr"], float).reshape(-1, 3)
    symbols, m = a["symbols"], np.array(a["masses_amu"], float)
    x, moments = principal_frame(x0, m)

    found = {}
    for name, g in OPS.items():
        perm = permutation(x, symbols, g, args.detect)
        if perm is not None:
            found[name] = perm
    dev_before = {n: float(np.abs(x @ OPS[n].T - x[found[n]]).max()) for n in found}
    x_sym = sum(OPS[n].T @ (x[found[n]]).T for n in found) / len(found)   # (1/|G|) Σ g^-1 x[π_g]; g^-1 = g^T here
    x_sym = np.asarray(x_sym).T
    # iterate twice: the permutations were found on x; re-check them on x_sym
    for _ in range(2):
        x_sym = np.asarray(sum(OPS[n].T @ (x_sym[found[n]]).T for n in found) / len(found)).T
    dev_after = {n: float(np.abs(x_sym @ OPS[n].T - x_sym[found[n]]).max()) for n in found}
    shift = float(np.abs(x_sym - x).max())
    order = len(found)
    group = {8: "D2h", 4: "C2v / C2h / D2 (four operations)", 2: "Cs / C2 / Ci", 1: "C1"}.get(order, f"{order} operations")

    print(f"{args.molecule}: {len(symbols)} atoms; principal moments {moments.round(1)} amu·bohr²")
    print(f"operations satisfied within {args.detect:g} bohr: {sorted(found)}  → {group}")
    print(f"largest deviation from symmetry before: {max(dev_before.values()):.2e} bohr  "
          f"({', '.join(f'{n} {v:.1e}' for n, v in dev_before.items() if n != 'E')})")
    print(f"largest deviation after averaging:      {max(dev_after.values()):.2e} bohr; largest atom shift {shift:.2e} bohr")
    out = {"molecule": args.molecule, "source": "stageA.json (factory geometry) in the principal-axes frame",
           "group_operations": sorted(found), "group": group, "detect_tol_bohr": args.detect,
           "max_deviation_before_bohr": max(dev_before.values()), "max_deviation_after_bohr": max(dev_after.values()),
           "max_atom_shift_bohr": shift, "symbols": symbols,
           "coords_bohr": x_sym.tolist(), "coords_angstrom": (x_sym * BOHR).tolist(),
           "psi4_geometry_block": "\n".join(f"{s} {c[0]*BOHR:.10f} {c[1]*BOHR:.10f} {c[2]*BOHR:.10f}" for s, c in zip(symbols, x_sym))}
    path = os.path.join(d, "geometry_symmetrised.json")
    json.dump(out, open(path, "w"), indent=1)
    print(f"written {os.path.relpath(path, HERE)}")


if __name__ == "__main__":
    main()
