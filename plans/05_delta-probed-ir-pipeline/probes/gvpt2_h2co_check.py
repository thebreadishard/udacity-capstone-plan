"""Validation (c) of S2 amendment 2 (18 Oct 2026): our GVPT2 path against pyVPT2's own, end to end on H₂CO — runs in the WSL env `vpt2`.

    python gvpt2_h2co_check.py --out <dir>

pyVPT2 computes H₂CO exactly as its tests/test_h2co.py does (SCF/6-31G*, Hessian finite differences, step 0.05, FERMI and GVPT2 on), and
its own result must pass that test's references first (0.1 cm⁻¹). Its force constants, rotational constants and Coriolis ζ then go through
probes/gvpt2_labels.gvpt2 (dpir.qff.vpt2 at Martin's threshold + our overtones and bands + pyVPT2's polyad solver). Pass: our deperturbed
and our GVPT2 fundamentals equal pyVPT2's to 0.1 cm⁻¹, the test's tolerance. Writes <dir>/gvpt2_h2co_check.json and prints PASS or FAIL.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gvpt2_labels import gvpt2  # noqa: E402

TOL = 0.1  # cm⁻¹, tests/test_h2co.py's tolerance
# tests/test_h2co.py's references (pyVPT2 commit 2eae571): ν − ω after GVPT2, and deperturbed ν − ω
REF_ANHARMONIC = [-17.4496, -18.9212, -33.1555, -25.5869, -142.8295, -129.2199]
REF_DEPERTURBED = [-17.4496, -18.9212, -33.1555, -25.5869, -142.8295, -184.5589]


def run_pyvpt2():
    """pyVPT2 on H₂CO with test_h2co's geometry, model and options; returns its VPTResult."""
    import psi4
    import pyvpt2
    mol = psi4.geometry("""
    C
    O 1 R1
    H 1 R2 2 A1
    H 1 R3 2 A2 3 D

    A1 =  122.1401534366
    A2 =  122.1401534366
    D  = -179.9999893363
    R1 =    1.1843393306
    R2 =    1.0915309601
    R3 =    1.0915309601
    """)
    inp = {"molecule": mol.to_schema(dtype=2),
           "keywords": {"FD": "HESSIAN", "DISP_SIZE": 0.05, "FERMI": True, "GVPT2": True},
           "input_specification": [{"model": {"method": "scf", "basis": "6-31g*"},
                                    "keywords": {"d_convergence": 1e-12, "e_convergence": 1e-12, "scf_type": "direct", "puream": True,
                                                 "points": 5}}]}
    return pyvpt2.vpt2_from_schema(inp)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run_pyvpt2()
    omega = np.asarray(res.omega)
    v = np.argsort(omega)[-6:]
    v.sort()
    theirs_gvpt2 = np.asarray(res.nu)[v] - omega[v]
    theirs_dep = np.asarray(res.extras["Deperturbed Freq"])[v] - omega[v]
    upstream_ok = bool(np.abs(theirs_gvpt2 - REF_ANHARMONIC).max() <= TOL and np.abs(theirs_dep - REF_DEPERTURBED).max() <= TOL)
    ix3, ix2 = np.ix_(v, v, v), np.ix_(v, v)
    zeta = np.asarray(res.zeta)[:, v][:, :, v]
    ours = gvpt2(omega[v], np.asarray(res.phi_ijk)[ix3], np.asarray(res.phi_iijj)[ix2], np.asarray(res.rotational_constants), zeta)
    ours_dep, ours_gvpt2 = ours["nu_dvpt2"] - omega[v], ours["nu_gvpt2"] - omega[v]
    d_dep, d_gvpt2 = float(np.abs(ours_dep - theirs_dep).max()), float(np.abs(ours_gvpt2 - theirs_gvpt2).max())
    passed = upstream_ok and d_dep <= TOL and d_gvpt2 <= TOL
    out = {"upstream_matches_its_test": upstream_ok, "omega": omega[v].tolist(), "pyvpt2_deperturbed": theirs_dep.tolist(),
           "ours_deperturbed": ours_dep.tolist(), "pyvpt2_gvpt2": theirs_gvpt2.tolist(), "ours_gvpt2": ours_gvpt2.tolist(),
           "max_diff_deperturbed": d_dep, "max_diff_gvpt2": d_gvpt2, "moved": ours["moved"], "tolerance": TOL, "pass": passed}
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "gvpt2_h2co_check.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("upstream_matches_its_test", "max_diff_deperturbed", "max_diff_gvpt2", "moved")}))
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
