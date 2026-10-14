"""Why do two CC APT routes of one anchor disagree? (14 Oct 2026, azulene of anchor set three: the field route against the FD-dipole route,
max |ΔP| 2.39e-3 e against the cross-check's line 1e-3.)

For the field-route APT and the FD-dipole APT of one molecule (same geometry): the geometry's own deviation from its point group (largest
atom displacement under the operations `e8_symmetry.point_group_ops` finds), each APT's deviation from that group's symmetry
(max |R P Dᵀ − P|, D the displacement representation of `qff_symmetry_rebuild.rep`), each APT's translation sum rule, the largest difference
as stored and after both are symmetrised (group average), and the per-atom largest difference. The FD-dipole route symmetrises its APT; at a
geometry that is not exactly symmetric the true APT is not either, so the stored difference contains that asymmetry.

    python probes/apt_symmetry_diagnosis.py <apt_ccsd_t_field.npz> <apt_ccsd_t.npz> [--out diagnosis.json]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e8_symmetry import point_group_ops  # noqa: E402
from qff_symmetry_rebuild import rep  # noqa: E402


def geometry_residual(x, ops) -> float:
    """Largest |R x_i − x_perm[i]| over the operations, coordinates about their mean — point_group_ops' own convention."""
    c = np.asarray(x, float) - np.asarray(x, float).mean(0)
    return float(max(np.abs(c @ R.T - c[perm]).max() for R, perm in ops))


def diagnose(field_npz: str, fd_npz: str) -> dict:
    F, R = np.load(field_npz, allow_pickle=True), np.load(fd_npz, allow_pickle=True)
    x = np.asarray(F["coords_bohr"], float)
    if np.abs(x - np.asarray(R["coords_bohr"], float)).max() > 1e-10:
        raise SystemExit("the two APTs are not at the same geometry")
    sym = [str(s) for s in F["symbols"]]
    n = len(sym)
    ops = point_group_ops(sym, x)
    reps = [(Rm, rep(Rm, perm, n)) for Rm, perm in ops]

    def sym_dev(P):
        return float(max(np.abs(Rm @ P @ D.T - P).max() for Rm, D in reps))

    def sym_avg(P):
        return sum(Rm.T @ P @ D for Rm, D in reps) / len(reps)

    def sum_rule(P):
        return float(np.abs(P.reshape(3, n, 3).sum(1)).max())

    Pf, Pr = np.asarray(F["apt"], float), np.asarray(R["apt"], float)
    d = (Pf - Pr).reshape(3, n, 3)
    return {"field": field_npz, "fd_dipole": fd_npz, "operations": len(ops),
            "geometry_symmetry_residual_bohr": geometry_residual(x, ops),
            "symmetry_deviation": {"field": sym_dev(Pf), "fd_dipole": sym_dev(Pr)},
            "translation_sum_rule": {"field": sum_rule(Pf), "fd_dipole": sum_rule(Pr)},
            "max_abs_diff": float(np.abs(d).max()), "max_abs_diff_both_symmetrised": float(np.abs(sym_avg(Pf) - sym_avg(Pr)).max()),
            "per_atom_max_abs_diff": {f"{s}{i}": float(v) for i, (s, v) in enumerate(zip(sym, np.abs(d).max(axis=(0, 2)), strict=True))}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("field_npz")
    ap.add_argument("fd_npz")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = diagnose(a.field_npz, a.fd_npz)
    print(json.dumps({k: v for k, v in res.items() if k != "per_atom_max_abs_diff"}, indent=1))
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
