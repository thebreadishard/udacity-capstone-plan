"""L3 diagnosis (11 Oct 2026): why upstream's heights differ from ours by 3.2e-3 on the cation P3c_02d75f732a and by 1.5e-6 on benzene.

Hypothesis: pyscf's `hessian.thermo.harmonic_analysis` hands the raw (slightly asymmetric) analytic Hessian to `numpy.linalg.eigh`, which reads
only one triangle; our probe symmetrises it first. Test: from the saved analytic Hessian (equal to upstream's to 1.8e-11) and one fixed APT,
heights by (a) ours on the symmetrised Hessian, (b) `harmonic_analysis` on the raw Hessian, (c) `harmonic_analysis` on the symmetrised one.
If (c) matches (a) and (b) reproduces the 3.2e-3, the asymmetry is the cause. No SCF; seconds.

    python probes/results_m1/apt_route_props_2026-10-11/diagnose_l3.py   (WSL, qc05)
"""
import json
import os
import sys

import numpy as np
from pyscf import gto
from pyscf.hessian import thermo

PLAN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from analytic_hessians import project_tr  # noqa: E402
from apt import KM_PER_MOL, intensities  # noqa: E402
from apt_route_props_probe import compare_heights  # noqa: E402

CASES = {
    "cation P3c_02d75f732a": ("modules/05_support_predictor/corpus/shards_pool3/a/molecules/P3c_02d75f732a",
                              "probes/results_m1/apt_route_props_2026-10-11/P3c_02d75f732a_fd.npz", 1, 1),
    "benzene A_8448043181": ("modules/05_support_predictor/corpus/molecules/A_8448043181",
                             "modules/05_support_predictor/corpus/molecules/A_8448043181/dipole_b3lyp_cphf.npz", 0, 0),
}


def heights_upstream_modes(mol, H4, masses, P):
    """Heights with pyscf's normal modes (harmonic_analysis) and our unit constant: isolates the modes."""
    d = thermo.harmonic_analysis(mol, H4, mass=masses)
    q = d["norm_mode"].reshape(-1, mol.natm * 3)                 # (modes, 3N), amu^-1/2 per mode
    dmu = q @ P.T                                                 # (modes, 3)
    return np.real(d["freq_wavenumber"]), KM_PER_MOL * (dmu ** 2).sum(axis=1)


def to4(M):
    """3N×3N Cartesian Hessian → pyscf's (natm, natm, 3, 3)."""
    n = M.shape[0] // 3
    return M.reshape(n, 3, n, 3).transpose(0, 2, 1, 3)


out = {}
for name, (d, apt_file, charge, spin) in CASES.items():
    g = json.load(open(os.path.join(PLAN, d, "geometry.json")))
    x = np.asarray(g["coords_bohr"], float)
    masses = np.asarray(g["masses_amu"], float)
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], x, strict=True)], unit="Bohr", basis="sto-3g",
                charge=charge, spin=spin, verbose=0)                 # geometry and masses only; the basis is not used
    Hc = np.load(os.path.join(PLAN, d, "hessian_b3lyp_analytic.npz"))["H_raw"]
    P = np.load(os.path.join(PLAN, apt_file))["apt"]
    Hs = 0.5 * (Hc + Hc.T)
    fa, ka = intensities(P, project_tr(Hs, masses, x), masses)
    fb, kb = heights_upstream_modes(mol, to4(Hc), masses, P)
    fc, kc = heights_upstream_modes(mol, to4(Hs), masses, P)
    out[name] = {
        "asymmetry_max": float(np.abs(Hc - Hc.T).max()),
        "asymmetry_rel": float(np.abs(Hc - Hc.T).max() / np.abs(Hc).max()),
        "ours_vs_upstream_raw": compare_heights(fb, kb, fa, ka),
        "ours_vs_upstream_symmetrised": compare_heights(fc, kc, fa, ka),
    }
    print(name, json.dumps(out[name]), flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnose_l3.json"), "w"), indent=1)
