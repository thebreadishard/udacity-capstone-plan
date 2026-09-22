"""Geometry hypothesis for the R0 diagonal reading (22 Sep 2026): the deck measures every method's curvature at the B3LYP/6-31G*
geometry, the literature harmonics are at each method's own minimum. Test with HF/cc-pVTZ, where the effect should be largest:
  (1) HF energies on a 3 x 3 grid over the two a1g coordinates (deck modes 11 = ring breathing, 29 = C-H stretch), q in {-1, 0, +1};
      quadratic fit -> the HF minimum (q11*, q29*) within the a1g space (the other coordinates cannot shift by symmetry);
  (2) curvature along mode 29 at that relaxed point (q29* +- 0.5, +- 1.0) -> omega'_HF(relaxed), against 3224.8 at the B3LYP geometry;
  (3) control: the same with B3LYP/6-31G* (must give q* ~ 0 and omega' ~ 3210).
Usage: python r0_geometry_check.py <dir with stageA.json and stageA_hessians.npz>
"""
import json, os, sys, time
import numpy as np
from pyscf import gto, scf, dft

HARTREE_CM = 219474.6313632
d = sys.argv[1]
a = json.load(open(os.path.join(d, "stageA.json"))); z = np.load(os.path.join(d, "stageA_hessians.npz"))
L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
symbols = a["symbols"]
I_BR, I_CH = 11, 29


def geom(qv):
    return coords0 + ((L @ (qv / np.sqrt(omega))) * Minv).reshape(-1, 3)


def e_hf(x):
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, x)], unit="Bohr", basis="cc-pvtz", verbose=0, symmetry=False)
    mf = scf.RHF(mol).density_fit(); mf.conv_tol = 1e-11; return mf.kernel()


def e_b3(x):
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, x)], unit="Bohr", basis="6-31g*", verbose=0, symmetry=False)
    mf = dft.RKS(mol, xc="b3lyp"); mf.grids.atom_grid = (99, 590); mf.conv_tol = 1e-11; return mf.kernel()


def qvec(q11, q29):
    v = np.zeros(len(omega)); v[I_BR] = q11; v[I_CH] = q29; return v


def study(name, efun):
    t0 = time.time()
    grid = [(i, j) for i in (-1.0, 0.0, 1.0) for j in (-1.0, 0.0, 1.0)]
    E = {g: efun(geom(qvec(*g))) for g in grid}
    E0 = E[(0.0, 0.0)]
    # quadratic fit E = E0 + g1 q1 + g2 q2 + 1/2 k11 q1^2 + k12 q1 q2 + 1/2 k22 q2^2
    A = np.array([[1, g[0], g[1], 0.5 * g[0] ** 2, g[0] * g[1], 0.5 * g[1] ** 2] for g in grid]); y = np.array([E[g] - E0 for g in grid])
    c = np.linalg.lstsq(A, y, rcond=None)[0]; g_ = c[1:3]; K = np.array([[c[3], c[4]], [c[4], c[5]]])
    qstar = -np.linalg.solve(K, g_)
    print(f"[{name}] gradient at B3LYP geometry (µE_h/q): breathing {g_[0]*1e6:+.1f}, CH {g_[1]*1e6:+.1f}; a1g minimum at q11* {qstar[0]:+.3f}, q29* {qstar[1]:+.3f} "
          f"(E drop {(0.5 * g_ @ np.linalg.solve(K, g_))*1e6:.1f} µE_h); {time.time()-t0:.0f} s", flush=True)
    # displacement of the C-H bond implied by q29*: compare geometries
    x0 = geom(qvec(0, 0)); xs = geom(qvec(*qstar))
    dr = [np.linalg.norm(xs[i] - xs[j]) - np.linalg.norm(x0[i] - x0[j]) for i in range(len(symbols)) for j in range(len(symbols)) if symbols[i] == "C" and symbols[j] == "H" and np.linalg.norm(x0[i] - x0[j]) < 2.2]
    print(f"[{name}] implied C-H bond change at the relaxed point: {np.mean(dr)*0.529177:+.4f} Å", flush=True)
    # curvature along mode 29 at the relaxed point vs at the B3LYP geometry
    w = omega[I_CH] * HARTREE_CM; k_dft = omega[I_CH] * 1e6
    out = {}
    for label, base in (("B3LYP geometry", np.zeros(2)), ("relaxed a1g point", qstar)):
        Eb = efun(geom(qvec(*base)))
        ev = []
        for q in (0.5, 1.0):
            ep = efun(geom(qvec(base[0], base[1] + q))); em = efun(geom(qvec(base[0], base[1] - q)))
            ev.append(0.5 * (ep + em) - Eb)
        ev = np.array(ev) * 1e6; qa = np.array([0.5, 1.0]); Afit = np.stack([0.5 * qa**2, 0.25 * qa**4], 1); k, c4 = np.linalg.lstsq(Afit, ev, rcond=None)[0]
        out[label] = w * np.sqrt(k / k_dft)
        print(f"[{name}] omega' along mode 29 at the {label}: {out[label]:.1f} cm-1 (k {k:+.1f}, c4 {c4:+.1f} µE_h)", flush=True)
    print(f"[{name}] geometry effect on the C-H stretch curvature: {out['relaxed a1g point'] - out['B3LYP geometry']:+.1f} cm-1; total {time.time()-t0:.0f} s", flush=True)
    return dict(gradient=g_.tolist(), qstar=qstar.tolist(), dr_CH_A=float(np.mean(dr) * 0.529177), omega_prime=out)


res = {"HF/cc-pVTZ": study("HF/cc-pVTZ", e_hf), "B3LYP/6-31G*": study("B3LYP/6-31G*", e_b3)}
json.dump(res, open("r0_geometry_check.json", "w"), indent=1)
print("done")
