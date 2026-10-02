"""Lever 5 (2 Oct 2026, 07:4x): dipole derivatives (atomic polar tensors) from the coupled-perturbed SCF response, at the corpus's DFT settings — the
finite-difference route (probes/dipole_derivs_fd.py) costs 6N SCFs (≈ 11 h for a 22-atom molecule at 4 threads); this one costs one CPHF solve, the
same solve the analytic Hessian needs.

∂μ_t/∂R_{A,x} = Z_A δ_tx − Tr(∂D/∂R_{A,x} · r_t) − Tr(D · ∂r_t/∂R_{A,x}), with ∂C_occ/∂R from `hessian.rhf.solve_mo1` (the occupied block included, as
pyscf's own `hess_elec` uses it: pyscf/hessian/rhf.py, exercised by pyscf/hessian/test/test_rks.py) and ∂r/∂R from the derivative dipole integrals
(`int1e_irp`, the basis functions on atom A). Second routes on every molecule: the translation sum rule Σ_A ∂μ/∂R_A = q·I, and — where
dipole_<xc>_fd.npz exists — the finite-difference APT (water, 2 Oct: the two routes agree to the number printed). The index convention of `int1e_irp`
was fixed against the FD route on water and is asserted here, not assumed.

    python probes/dipole_derivs_cphf.py <dir with geometry.json> [--xc b3lyp] [--hessian hessian_b3lyp_analytic.npz] [--threads 8] [--check-fd dipole_b3lyp_fd.npz]
"""
import argparse
import json
import sys
import time

import numpy as np
from pyscf import dft, gto, lib

sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
from dipole_derivs_fd import intensities  # noqa: E402  (same intensity formula as the FD route)


def apt_cphf(mf, log=print):
    """Atomic polar tensor P[3, 3N] (∂μ_t/∂R_{A,x}, a.u.) from the CPHF response of a converged RKS object."""
    mol = mf.mol
    t0 = time.time()
    hobj = mf.Hessian()
    mo_coeff, mo_occ, mo_energy = mf.mo_coeff, mf.mo_occ, mf.mo_energy
    h1ao = hobj.make_h1(mo_coeff, mo_occ)                       # (natm, 3, nao, nao): the Fock derivative incl. the xc response
    mo1s, _ = hobj.solve_mo1(mo_energy, mo_coeff, mo_occ, h1ao)  # mo1s[A]: (3, nao, nocc) = ∂C_occ/∂R_{A,x} in the AO basis
    log(f"  CPHF solved: {time.time() - t0:.0f} s")
    mocc = mo_coeff[:, mo_occ > 0]
    dm = mf.make_rdm1()
    r = mol.intor("int1e_r", comp=3)                              # ⟨μ|r_t|ν⟩
    irp = mol.intor("int1e_irp", comp=9).reshape(3, 3, mol.nao, mol.nao)   # derivative dipole integrals, two index orders possible → fixed below
    Z = mol.atom_charges()
    n = mol.natm
    P = np.zeros((3, 3 * n))
    aoslices = mol.aoslice_by_atom()
    for A in range(n):
        p0, p1 = aoslices[A, 2:]
        for x in range(3):
            dD = 2.0 * (mo1s[A][x] @ mocc.T)
            dD = dD + dD.T
            P[:, 3 * A + x] -= np.einsum("pq,tpq->t", dD, r)      # −Tr(∂D r)
            # −Tr(D ∂r/∂R): the functions on A move; ∂⟨μ|r|ν⟩/∂R_A = −⟨∂μ|r|ν⟩ − ⟨μ|r|∂ν⟩ for μ, ν on A.  int1e_irp[t, x] = ⟨μ| r_t ∂_x |ν⟩ (checked on water)
            blk = irp[:, x, :, p0:p1]                              # (3, nao, nA): ⟨μ| r_t ∂_x |ν⟩, ν on A
            P[:, 3 * A + x] -= -2.0 * np.einsum("pq,tpq->t", dm[:, p0:p1], blk)   # both ⟨∂μ|r|ν⟩ and ⟨μ|r|∂ν⟩ by symmetry of D
        P[:, 3 * A:3 * A + 3] += Z[A] * np.eye(3)
    return P


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir")
    ap.add_argument("--xc", default="b3lyp")
    ap.add_argument("--hessian", default="hessian_b3lyp_analytic.npz")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--grid", default="99,590")
    ap.add_argument("--charge", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--check-fd", default=None, help="an FD APT file (dipole_<xc>_fd.npz) to compare with")
    ap.add_argument("--sum-rule-limit", type=float, default=5e-4,
                    help="2 Oct 2026 17:0x: set by the benzene two-route measurement — CPHF vs FD APT differ by 4.4e-4 e at most (intensities within 0.07 km/mol), "
                         "so the 1e-4 first guess refused a correct benzene (1.1e-4); the FD route itself holds the sum rule to 3e-6")
    ap.add_argument("--fd-limit", type=float, default=1e-3, help="max |P_cphf − P_fd| allowed (e); the FD route itself is good to ≈ 3e-6 on water")
    a = ap.parse_args()
    lib.num_threads(a.threads)
    grid = tuple(int(v) for v in a.grid.split(","))
    g = json.load(open(f"{a.dir}/geometry.json"))
    x0 = np.asarray(g["coords_bohr"], float)
    masses = np.asarray(g["masses_amu"], float)
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], x0, strict=True)], unit="Bohr", basis="6-31g*", cart=True, symmetry=False,
                verbose=0, max_memory=20000, charge=a.charge)
    t0 = time.time()
    mf = dft.RKS(mol)
    mf.xc = a.xc
    mf.grids.atom_grid = grid
    mf.grids.prune = None
    mf.conv_tol = 1e-11
    mf.conv_tol_grad = 1e-8
    mf.kernel()
    if not mf.converged:
        raise SystemExit("SCF not converged")
    P = apt_cphf(mf)
    n = len(x0)
    sr = float(np.abs(P.reshape(3, n, 3).sum(axis=1) - a.charge * np.eye(3)).max())
    fd_diff = float("nan")
    if a.check_fd:
        fd_diff = float(np.abs(P - np.load(a.check_fd)["apt"]).max())
    H = np.load(f"{a.dir}/{a.hessian}")["H_projected"]
    freq, inten = intensities(P, H, masses)
    passed = sr <= a.sum_rule_limit and (not a.check_fd or fd_diff <= a.fd_limit)
    out = a.out or f"{a.dir}/dipole_{a.xc}_cphf.npz"
    np.savez_compressed(out, apt=P, sum_rule_max=sr, fd_max_diff=fd_diff, freq_cm=freq, intensity_km_mol=inten, xc=a.xc, basis="6-31g*", grid=np.array(grid),
                        passed=passed, route="cphf", seconds=round(time.time() - t0))
    print(f"{a.dir}: APT by CPHF; sum rule max |Σ P − qI| = {sr:.1e} (limit {a.sum_rule_limit:g}); "
          + (f"vs FD max |ΔP| = {fd_diff:.1e} (limit {a.fd_limit:g}); " if a.check_fd else "") + f"→ {'PASS' if passed else 'FAIL'}; {time.time() - t0:.0f} s")
    for f, i in zip(freq, inten, strict=True):
        print(f"  {f:8.1f} cm-1  {i:8.2f} km/mol")
    return 0 if passed else 3


if __name__ == "__main__":
    sys.exit(main())
