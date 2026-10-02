"""Lever 5 (2 Oct 2026): dipole derivatives (atomic polar tensors) by central finite differences of the analytic SCF dipole moment, at the corpus's
DFT settings (6-31G* cartesian, grid 99/590, conv 1e-11), so that IR intensities can join the read-outs.

Routes checked on every molecule (noise principle, 21 Sep 2026): (i) the translation sum rule Σ_A ∂μ/∂R_A = q·I (the atomic polar tensors of a
neutral molecule sum to zero, charge q·identity otherwise); (ii) two step sizes (h and h/2) — Richardson pair, the O(h²) error read directly.
Intensities: A_k = (N_A π / 3c²) |∂μ/∂Q_k|² in km/mol with ∂μ/∂Q from the APT and the mass-weighted normal modes of the Hessian file given.

pyscf calls: `mf.dip_moment(unit='AU')` as in pyscf/scf/test/test_rhf.py (test_dip_moment) and examples/scf/18-dipole_moment.py (cited per the
29 Sep 2026 rule); the Hessian comes from a stored npz (corpus/analytic_hessians.py), not recomputed here.

    python probes/dipole_derivs_fd.py <dir with geometry.json> --xc b3lyp [--hessian hessian_b3lyp_analytic.npz] [--step 0.005] [--threads 8] [--out dipole_b3lyp_fd.npz]
"""
import argparse
import json
import sys
import time

import numpy as np
from pyscf import dft, gto, lib

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705
# A_k [km/mol] = 974.8802 · |∂μ/∂Q_k|² with μ in e·bohr... the usual constant for (D/Å)²/amu is 42.2561 km/mol; in atomic units (e² bohr² / bohr² amu⁻¹
# → e²/amu) the factor is 42.2561 × (2.541746 D/e·Å ... ) — written out: 1 e/√amu → (2.541746 D / 0.529177 Å)² × 42.2561 = 974.88 km/mol.
KM_PER_MOL = 974.8802


def dipole(mol, xc, grid, x, conv=1e-11, dm0=None):
    """Analytic dipole (a.u.) of the converged RKS at geometry x; `dm0` seeds the SCF (the equilibrium density halves the displaced SCF cost)."""
    m = mol.copy()
    m.set_geom_(x, unit="Bohr")
    mf = dft.RKS(m)
    mf.xc = xc
    mf.grids.atom_grid = grid
    mf.grids.prune = None
    mf.conv_tol = conv
    mf.conv_tol_grad = 1e-8          # 2 Oct 07:0x: with the default 3e-6 the seeded SCFs left 1.5e-4 e in the APT (sum rule failed on water); 1e-8 restores 1e-6
    mf.verbose = 0
    mf.kernel(dm0)
    if not mf.converged:
        raise RuntimeError("SCF not converged at a displaced geometry")
    return mf.dip_moment(unit="AU", verbose=0), mf.make_rdm1()


def apt_fd(mol, xc, grid, x0, h, log=print):
    """Atomic polar tensor P[3, 3N]: P[c, A*3+d] = ∂μ_c / ∂R_{A,d} by central differences; every displaced SCF starts from the equilibrium density."""
    n = len(x0)
    P = np.zeros((3, 3 * n))
    t0 = time.time()
    _, dm0 = dipole(mol, xc, grid, x0)
    for A in range(n):
        for d in range(3):
            xp, xm = x0.copy(), x0.copy()
            xp[A, d] += h
            xm[A, d] -= h
            P[:, 3 * A + d] = (dipole(mol, xc, grid, xp, dm0=dm0)[0] - dipole(mol, xc, grid, xm, dm0=dm0)[0]) / (2 * h)
        log(f"  atom {A + 1}/{n} done, {time.time() - t0:.0f} s")
    return P


def intensities(P, H_projected, masses):
    """IR intensities (km/mol) of the vibrational modes of the projected Hessian from the APT."""
    mm = np.repeat(masses * AMU2AU, 3)
    Hm = H_projected / np.sqrt(np.outer(mm, mm))
    w, L = np.linalg.eigh(Hm)
    freq = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    vib = np.abs(freq) > 20.0
    dmu_dQ = P @ (L[:, vib] / np.sqrt(np.repeat(masses, 3))[:, None])          # e / √amu
    return freq[vib], KM_PER_MOL * (dmu_dQ ** 2).sum(axis=0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir")
    ap.add_argument("--xc", default="b3lyp")
    ap.add_argument("--hessian", default="hessian_b3lyp_analytic.npz")
    ap.add_argument("--step", type=float, default=0.005)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--grid", default="99,590")
    ap.add_argument("--charge", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--sum-rule-limit", type=float, default=1e-4, help="max |Σ_A P_A − q·I| allowed (e)")
    ap.add_argument("--no-half-step", action="store_true", help="skip the h/2 repeat (the sum rule stays as the second route; water: |P(h) − P(h/2)| 3e-6 e)")
    a = ap.parse_args()
    lib.num_threads(a.threads)
    grid = tuple(int(v) for v in a.grid.split(","))
    g = json.load(open(f"{a.dir}/geometry.json"))
    x0 = np.asarray(g["coords_bohr"], float)
    masses = np.asarray(g["masses_amu"], float)
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], x0, strict=True)], unit="Bohr", basis="6-31g*", cart=True, symmetry=False,
                verbose=0, max_memory=20000, charge=a.charge)
    t0 = time.time()
    P = apt_fd(mol, a.xc, grid, x0, a.step)
    P2 = P if a.no_half_step else apt_fd(mol, a.xc, grid, x0, a.step / 2)
    n = len(x0)
    sum_rule = P.reshape(3, n, 3).sum(axis=1) - a.charge * np.eye(3)
    sr = float(np.abs(sum_rule).max())
    rich = float("nan") if a.no_half_step else float(np.abs(P - P2).max())
    H = np.load(f"{a.dir}/{a.hessian}")["H_projected"]
    freq, I = intensities(P2, H, masses)
    _, I1 = intensities(P, H, masses)
    out = a.out or f"{a.dir}/dipole_{a.xc}_fd.npz"
    passed = sr <= a.sum_rule_limit
    np.savez_compressed(out, apt=P2, apt_h=P, step=a.step, sum_rule_max=sr, richardson_max=rich, freq_cm=freq, intensity_km_mol=I, intensity_km_mol_h=I1,
                        xc=a.xc, basis="6-31g*", grid=np.array(grid), passed=passed, seconds=round(time.time() - t0))
    print(f"{a.dir}: APT by FD (h = {a.step:g} and {a.step / 2:g}); sum rule max |Σ P − qI| = {sr:.1e} (limit {a.sum_rule_limit:g}) → {'PASS' if passed else 'FAIL'}; "
          f"|P(h) − P(h/2)| max {rich:.1e} e; {time.time() - t0:.0f} s")
    for f, i, i1 in zip(freq, I, I1, strict=True):
        print(f"  {f:8.1f} cm-1  {i:8.2f} km/mol  (h: {i1:8.2f})")
    return 0 if passed else 3


if __name__ == "__main__":
    sys.exit(main())
