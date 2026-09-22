"""Independent check of the R0 diagonal reading (22 Sep 2026): rebuild the deck's displaced geometries exactly as
m1_frozen_spaces.py does (x = coords0 + (L @ (v/sqrt(omega))) * Minv) and evaluate, with pyscf,
  (a) B3LYP/6-31G* energies — the same functional and basis the mode vectors came from, so the fitted curvature must give
      omega' = omega_B3LYP (validates the displacement convention and the k/c4 fit of r0_diagonal_reading.py);
  (b) RHF/cc-pVTZ (density-fitted, as the deck) — validates the deck's SCF-only column against an independent evaluation.
Modes: 29 (a1g C-H stretch, +-0.5, +-1.0), 24 (b1u C-H stretch, +0.5, +1.0), 0 (e2u C-H oop, +0.5, +1.0), 18 (b2u Kekule, +0.5, +1.0).
Usage: python r0_convention_check.py <dryrun_dir_with_stageA.json_and_npz>
"""
import json, os, sys, time
import numpy as np
from pyscf import gto, scf, dft

HARTREE_CM = 219474.6313632
d = sys.argv[1]
a = json.load(open(os.path.join(d, "stageA.json"))); z = np.load(os.path.join(d, "stageA_hessians.npz"))
L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
symbols = a["symbols"]
plan = {29: [-1.0, -0.5, 0.5, 1.0], 24: [0.5, 1.0], 0: [0.5, 1.0], 18: [0.5, 1.0]}


def geom(m, q):
    v = np.zeros(len(omega)); v[m] = q
    return coords0 + ((L @ (v / np.sqrt(omega))) * Minv).reshape(-1, 3)


def energies(x):
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, x)], unit="Bohr", basis="6-31g*", verbose=0, symmetry=False)
    mf = dft.RKS(mol, xc="b3lyp"); mf.grids.atom_grid = (99, 590); mf.conv_tol = 1e-11; e_b3 = mf.kernel()
    mol2 = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, x)], unit="Bohr", basis="cc-pvtz", verbose=0, symmetry=False)
    hf = scf.RHF(mol2).density_fit(); hf.conv_tol = 1e-11; e_hf = hf.kernel()
    return e_b3, e_hf


t0 = time.time()
E0 = energies(coords0); print(f"reference: B3LYP/6-31G* {E0[0]:.9f}  HF/cc-pVTZ {E0[1]:.9f}  ({time.time()-t0:.0f} s)", flush=True)
out = {}
for m, qs in plan.items():
    E = {q: energies(geom(m, q)) for q in qs}
    for q in qs:
        print(f"mode {m} q={q:+.1f}: dE_B3LYP {(E[q][0]-E0[0])*1e6:+.1f} µE_h  dE_HF {(E[q][1]-E0[1])*1e6:+.1f} µE_h", flush=True)
    w = omega[m] * HARTREE_CM; k_dft = omega[m] * 1e6
    res = {}
    for name, idx in (("B3LYP/6-31G*", 0), ("HF/cc-pVTZ", 1)):
        qpos = sorted(set(abs(q) for q in qs))
        ev = np.array([np.mean([E[s * q][idx] - E0[idx] for s in (1, -1) if s * q in E]) for q in qpos]) * 1e6
        qa = np.array(qpos); A = np.stack([0.5 * qa**2, 0.25 * qa**4], 1); k, c4 = np.linalg.lstsq(A, ev, rcond=None)[0]
        k1 = 2 * ev[0] / qa[0]**2  # from the |q| = 0.5 point alone (c4 = 0)
        res[name] = dict(k=k, c4=c4, omega_prime=w * np.sqrt(k / k_dft), omega_prime_q05_only=w * np.sqrt(k1 / k_dft))
        print(f"  {name:<13} k {k:+.1f} c4 {c4:+.1f} µE_h -> omega' {w*np.sqrt(k/k_dft):.1f} (omega_B3LYP {w:.1f}; from |q|=0.5 alone {w*np.sqrt(k1/k_dft):.1f})", flush=True)
    out[m] = dict(omega_b3lyp=w, **{k_: v for k_, v in res.items()})
json.dump(out, open("r0_convention_check.json", "w"), indent=1, default=float)
print(f"done in {time.time()-t0:.0f} s")
