"""A third route to the APT: central differences of the analytic nuclear gradient in a small uniform electric field (12 Oct 2026, the UKS
margin's diagnosis, `probes/results_m1/uks_apt_margin_2026-10-11/REGISTRATION.md`).

P[t, 3A+x] = ∂μ_t/∂R_Ax = −∂²E/∂F_t∂R_Ax = −(g_Ax(+F e_t) − g_Ax(−F e_t)) / 2F, with the field in the one-electron Hamiltonian as +F·r per
electron and −Z_A F·R_A for the nuclei (μ = −dE/dF). The gradient is pyscf's analytic RKS/UKS gradient; its core-Hamiltonian derivative gets the
field term's derivative from `int1e_irp` (⟨μ| r_t ∂_x |ν⟩, the convention `corpus/apt.py` fixed against finite differences on water, 2 Oct), and
the nuclear term −Z_A F is added. Run twice — the gradient without and with grid response (pyscf's `grid_response`, which the UKS *Hessian* of
2.14 lacks): without, the field route answers the analytic CPHF APT (fixed grid); with, the finite differences of the dipole (moving grid).
Gradient calls as pyscf's grad/test/test_uks.py (`nuc_grad_method()`, `grid_response = True`).

    python probes/apt_field_route.py <dir with geometry.json> --out <file.npz> [--charge 1 --spin 1] [--field 1e-3] [--threads 4]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from pyscf import dft, gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus"))
from apt import sum_rule  # noqa: E402


def field_hcore_generator(g, F):
    """Wrap the gradient object's core-Hamiltonian derivative with the derivative of the field term Σ_t F_t ⟨μ|r_t|ν⟩."""
    mol = g.mol
    nao = mol.nao
    irp = mol.intor("int1e_irp", comp=9).reshape(3, 3, nao, nao)      # [t, x]: ⟨μ| r_t ∂_x |ν⟩
    aos = mol.aoslice_by_atom()
    base = type(g).hcore_generator

    def gen(mol_=None):
        h = base(g, mol_)

        def deriv(atm):
            out = np.array(h(atm))
            p0, p1 = aos[atm, 2:]
            for x in range(3):
                M = np.zeros((nao, nao))
                M[:, p0:p1] = np.einsum("t,tij->ij", F, irp[:, x, :, p0:p1])
                out[x] -= M + M.T                                       # ∂⟨μ|r|ν⟩/∂R_A = −⟨∂μ|r|ν⟩ − ⟨μ|r|∂ν⟩ for the functions on A
            return out
        return deriv
    return gen


def scf_in_field(mol, settings, F, dm0=None):
    mf = dft.UKS(mol) if mol.spin else dft.RKS(mol)
    mf.xc = settings["xc"]
    mf.grids.atom_grid = settings["grid"]
    mf.grids.prune = None
    mf.conv_tol = 1e-11
    mf.conv_tol_grad = 1e-8                       # as the FD route (2 Oct: the default left 1.5e-4 e in the APT)
    mf.verbose = 0
    h = mf.get_hcore() + np.einsum("t,tij->ij", F, mol.intor("int1e_r", comp=3))
    mf.get_hcore = lambda *a: h
    mf.kernel(dm0)
    if not mf.converged:
        raise RuntimeError(f"SCF in field {F} not converged")
    return mf


def gradient_in_field(mf, F, grid_response):
    g = mf.nuc_grad_method()
    g.grid_response = grid_response
    g.verbose = 0
    g.hcore_generator = field_hcore_generator(g, F)
    return g.kernel() - mf.mol.atom_charges()[:, None] * F[None, :]   # + ∂(−Σ Z_A F·R_A)/∂R_A


def apt_field(mol, settings, field=1e-3, log=print):
    """(P without grid response, P with grid response), each [3, 3N]; one SCF per field direction and sign, two gradients on it."""
    dm0 = scf_in_field(mol, settings, np.zeros(3)).make_rdm1()
    P = {False: np.zeros((3, 3 * mol.natm)), True: np.zeros((3, 3 * mol.natm))}
    t0 = time.time()
    for t in range(3):
        g = {}
        for s in (+1, -1):
            F = np.zeros(3)
            F[t] = s * field
            mf = scf_in_field(mol, settings, F, dm0)
            for gr in (False, True):
                g[(s, gr)] = gradient_in_field(mf, F, gr)
        for gr in (False, True):
            P[gr][t] = -(g[(+1, gr)] - g[(-1, gr)]).ravel() / (2 * field)
        log(f"  field component {t + 1}/3 done, {time.time() - t0:.0f} s", flush=True)
    return P[False], P[True]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--charge", type=int, default=0)
    ap.add_argument("--spin", type=int, default=0)
    ap.add_argument("--field", type=float, default=1e-3)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--grid", default="99,590")
    a = ap.parse_args()
    lib.num_threads(a.threads)
    g = json.load(open(os.path.join(a.dir, "geometry.json")))
    x = np.asarray(g["coords_bohr"], float)
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], x, strict=True)], unit="Bohr", basis="6-31g*", cart=True,
                symmetry=False, verbose=0, max_memory=4000, charge=a.charge, spin=a.spin)
    settings = {"xc": "b3lyp", "grid": tuple(int(v) for v in a.grid.split(","))}
    t0 = time.time()
    P0, P1 = apt_field(mol, settings, a.field)
    np.savez_compressed(a.out, apt_no_grid_response=P0, apt_grid_response=P1, field=a.field, charge=a.charge, spin=a.spin,
                        grid=np.array(settings["grid"]), seconds=round(time.time() - t0))
    print(f"{a.dir}: field route (F = {a.field:g}): sum rule without grid response {sum_rule(P0, a.charge):.1e}, with {sum_rule(P1, a.charge):.1e}; "
          f"|P_noGR − P_GR| max {np.abs(P0 - P1).max():.1e} e; {time.time() - t0:.0f} s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
