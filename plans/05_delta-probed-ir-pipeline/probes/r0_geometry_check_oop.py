"""Second part of the geometry test (22 Sep 2026): do the out-of-plane modes move under the same a1g relaxation?
HF/cc-pVTZ curvature along deck modes 4 (nu11 a2u), 5 (nu4 b2g), 10 (nu5 b2g), 6 (nu10 e1g) and the in-plane control 18 (nu14 b2u),
one-sided (+0.5, +1.0; the potential is even in these coordinates), at the B3LYP geometry and at HF's own a1g minimum
(q11* = +0.733, q29* = -0.255 from r0_geometry_check). Prints omega' at both points and the shift.
Usage: python r0_geometry_check_oop.py <dir with stageA.json and stageA_hessians.npz>
"""
import json, os, sys, time
import numpy as np
from pyscf import gto, scf

HARTREE_CM = 219474.6313632
d = sys.argv[1]
a = json.load(open(os.path.join(d, "stageA.json"))); z = np.load(os.path.join(d, "stageA_hessians.npz"))
L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
symbols = a["symbols"]
QSTAR = {11: 0.733, 29: -0.255}
MODES = [4, 5, 10, 6, 18]


def geom(qv):
    return coords0 + ((L @ (qv / np.sqrt(omega))) * Minv).reshape(-1, 3)


def e_hf(x):
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, x)], unit="Bohr", basis="cc-pvtz", verbose=0, symmetry=False)
    mf = scf.RHF(mol).density_fit(); mf.conv_tol = 1e-11; return mf.kernel()


def base_vec(relaxed):
    v = np.zeros(len(omega))
    if relaxed:
        for k, q in QSTAR.items(): v[k] = q
    return v


t0 = time.time(); out = {}
for relaxed in (False, True):
    b = base_vec(relaxed); E0 = e_hf(geom(b)); label = "relaxed a1g point" if relaxed else "B3LYP geometry"
    for m in MODES:
        ev = []
        for q in (0.5, 1.0):
            v = b.copy(); v[m] += q; ev.append(e_hf(geom(v)) - E0)
        ev = np.array(ev) * 1e6; qa = np.array([0.5, 1.0]); A = np.stack([0.5 * qa**2, 0.25 * qa**4], 1); k, c4 = np.linalg.lstsq(A, ev, rcond=None)[0]
        w = omega[m] * HARTREE_CM; wp = w * np.sqrt(k / (omega[m] * 1e6))
        out.setdefault(m, {})[label] = float(wp)
        print(f"mode {m:2d} (omega_B3LYP {w:7.1f}) at the {label}: omega'_HF {wp:7.1f} (k {k:+.1f}, c4 {c4:+.1f})", flush=True)
print("--- geometry effect (relaxed - B3LYP geometry), cm-1:")
for m in MODES:
    print(f"mode {m:2d}: {out[m]['relaxed a1g point'] - out[m]['B3LYP geometry']:+.1f}")
json.dump(out, open("r0_geometry_check_oop.json", "w"), indent=1)
print(f"done in {time.time()-t0:.0f} s")
