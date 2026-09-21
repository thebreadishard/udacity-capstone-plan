"""Displaced geometries for a quartic force field from Hessians, in the convention of qff_from_hessians.py (21 September 2026, test T3).

Given one reference record (a qcschema-like json with driver = hessian, molecule geometry in bohr and the analytic Hessian), this
script does the harmonic analysis of qff_from_hessians.py and writes, for every vibrational mode i and sign s = ±1, a stub json
{driver: hessian, molecule: {symbols, geometry = x_ref + s · d · A[:, i]}} where A[:, i] is the Cartesian displacement per unit reduced
normal coordinate (M^-1/2 q_i / sqrt(ω_i)), plus a stub of the reference geometry itself. `pyscf_hessians_for_qff.py <stub_dir> <out_dir>`
then computes the analytic Hessian at each stub, and `qff_from_hessians.py <out_dir> --disp d` assembles the force field. Because the
displacement basis is the analysis basis, the degenerate-subspace residual seen on the pyVPT2-generated geometries (assignment residual
3.5e-2, route maximum 46.8 cm⁻¹ on the T2 set) should not appear.

Usage: python make_qff_displacements.py <reference_json> <stub_dir> --disp 0.10 [--copy-reference-result]
  --copy-reference-result  copies the reference json itself into <stub_dir>/../<out_dir> is NOT done here; instead the reference stub gets the
                           same basename as the reference json, so copying the reference result into out_dir under that name makes
                           pyscf_hessians_for_qff.py skip it (one Hessian saved).
Validation: --check <dir_with_cached_geometries> reports, per generated stub, the distance to the nearest cached geometry (bohr).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qff_from_hessians import harmonic, HARTREE_CM  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference_json"); ap.add_argument("stub_dir")
    ap.add_argument("--disp", type=float, default=0.10)
    ap.add_argument("--check", default=None, help="directory with cached geometries to compare against (validation)")
    a = ap.parse_args()
    d = json.load(open(a.reference_json))
    assert d.get("driver") == "hessian"
    symbols = d["molecule"]["symbols"]; geom = np.array(d["molecule"]["geometry"], float)
    H = np.array(d["return_result"], float).reshape(len(geom), len(geom))
    omega, q, A, _ = harmonic(H, symbols, geom)
    n_modes = A.shape[1]
    os.makedirs(a.stub_dir, exist_ok=True)
    stubs = []
    ref_name = os.path.basename(a.reference_json)
    json.dump({"driver": "hessian", "molecule": {"symbols": symbols, "geometry": geom.tolist()},
               "displacement": {"mode": None, "sign": 0, "disp": a.disp, "note": "reference geometry"}},
              open(os.path.join(a.stub_dir, ref_name), "w"))
    for i in range(n_modes):
        for s in (1, -1):
            x = geom + s * a.disp * A[:, i]
            name = f"mode{i:02d}_{'p' if s > 0 else 'm'}.json"
            json.dump({"driver": "hessian", "molecule": {"symbols": symbols, "geometry": x.tolist()},
                       "displacement": {"mode": i, "sign": s, "disp": a.disp, "omega_cm": float(omega[i] * HARTREE_CM)}},
                      open(os.path.join(a.stub_dir, name), "w"))
            stubs.append((i, s, x))
    print(f"{2 * n_modes + 1} stubs in {a.stub_dir}; step {a.disp}; omega (cm-1): " + ", ".join(f"{w * HARTREE_CM:.1f}" for w in omega))
    if a.check:
        cached = []
        for f in sorted(glob.glob(os.path.join(a.check, "*.json"))):
            c = json.load(open(f))
            if isinstance(c, dict) and c.get("driver") == "hessian" and "molecule" in c:
                cached.append(np.array(c["molecule"]["geometry"], float))
        cached = np.array(cached)
        worst = []
        for i, s, x in stubs:
            dist = np.abs(cached - x[None, :]).max(axis=1).min()
            worst.append((dist, i, s))
        worst.sort(reverse=True)
        degenerate = {i for i in range(n_modes) for j in range(n_modes) if i != j and abs(omega[i] - omega[j]) * HARTREE_CM < 1.0}
        nondeg = [w for w in worst if w[1] not in degenerate]
        print(f"validation against {len(cached)} cached geometries: largest distance over non-degenerate modes {nondeg[0][0]:.2e} bohr "
              f"(mode {nondeg[0][1]}); over degenerate modes {max(w[0] for w in worst if w[1] in degenerate):.2e} bohr "
              f"(a rotation inside a degenerate pair is allowed there)")


if __name__ == "__main__":
    main()
