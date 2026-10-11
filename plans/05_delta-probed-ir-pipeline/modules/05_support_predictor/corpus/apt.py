"""Dipole derivatives (atomic polar tensors, APT) and IR band heights — one implementation for the labels route (`analytic_hessians.py`, which
takes the APT from the response its own Hessian solves: TASKS 44 route C, 11 Oct 2026) and the probes (`probes/dipole_derivs_cphf.py`, route B,
a second CPHF solve; `probes/dipole_derivs_fd.py`, finite differences). It sits beside `analytic_hessians.py` because the labels server runs that
script from a folder of its own, with this file copied next to it.

∂μ_t/∂R_{A,x} = Z_A δ_tx − Tr(∂D/∂R_{A,x} · r_t) − Tr(D · ∂r_t/∂R_{A,x}), with ∂C_occ/∂R from pyscf's `hessian.rhf.solve_mo1` (the occupied block
included, as pyscf's own `hess_elec` uses it: pyscf/hessian/rhf.py, exercised by pyscf/hessian/test/test_rks.py) and ∂r/∂R from the derivative
dipole integrals (`int1e_irp`, the basis functions on atom A); the index convention of `int1e_irp` was fixed against the FD route on water (2 Oct).
Measured (11 Oct, `probes/apt_route_c_probe.py`): the captured response gives route B's APT to 4.8e-7 e on benzene, the contraction costs < 0.01 s
against a 465 s Hessian; against finite differences 4.4e-4 e (benzene), 1.2e-5 e (water).
"""
import numpy as np

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705
# A_k [km/mol] = 974.8802 · |∂μ/∂Q_k|² with ∂μ/∂Q in e/√amu: 1 e/√amu → (2.541746 D / 0.529177 Å)² × 42.2561 km/mol per (D/Å)²/amu = 974.88 km/mol.
KM_PER_MOL = 974.8802


def capture_mo1(hobj):
    """Keep the CPHF response a Hessian object solves: returns a dict that holds 'mo1' (as `solve_mo1` returns it) once `hobj.kernel()` has run.
    pyscf 2.14's `hessian/rhf.py` `hess_elec` calls `hessobj.solve_mo1(...)` on the instance (line 59), so an instance attribute takes the call.
    Closed shell only: a UKS Hessian returns an (alpha, beta) pair, which `apt_from_mo1` does not take."""
    store = {}
    solve = hobj.solve_mo1

    def keep(*args, **kwargs):
        mo1, e1 = solve(*args, **kwargs)
        store["mo1"] = mo1
        return mo1, e1

    hobj.solve_mo1 = keep
    return store


def apt_from_mo1(mf, mo1s):
    """Atomic polar tensor P[3, 3N] (∂μ_t/∂R_{A,x}, a.u.) of a converged RKS object from a solved response: mo1s[A] (3, nao, nocc) =
    ∂C_occ/∂R_{A,x} in the AO basis, as pyscf's RHF/RKS `solve_mo1` returns it."""
    mol = mf.mol
    mocc = mf.mo_coeff[:, mf.mo_occ > 0]
    dm = mf.make_rdm1()
    r = mol.intor("int1e_r", comp=3)                                          # ⟨μ|r_t|ν⟩
    irp = mol.intor("int1e_irp", comp=9).reshape(3, 3, mol.nao, mol.nao)      # int1e_irp[t, x] = ⟨μ| r_t ∂_x |ν⟩ (checked on water)
    Z = mol.atom_charges()
    n = mol.natm
    P = np.zeros((3, 3 * n))
    aoslices = mol.aoslice_by_atom()
    for A in range(n):
        p0, p1 = aoslices[A, 2:]
        for x in range(3):
            dD = 2.0 * (mo1s[A][x] @ mocc.T)
            dD = dD + dD.T
            P[:, 3 * A + x] -= np.einsum("pq,tpq->t", dD, r)                  # −Tr(∂D r)
            # −Tr(D ∂r/∂R): the functions on A move; ∂⟨μ|r|ν⟩/∂R_A = −⟨∂μ|r|ν⟩ − ⟨μ|r|∂ν⟩ for μ, ν on A
            blk = irp[:, x, :, p0:p1]                                          # (3, nao, nA): ⟨μ| r_t ∂_x |ν⟩, ν on A
            P[:, 3 * A + x] -= -2.0 * np.einsum("pq,tpq->t", dm[:, p0:p1], blk)   # both ⟨∂μ|r|ν⟩ and ⟨μ|r|∂ν⟩ by symmetry of D
        P[:, 3 * A:3 * A + 3] += Z[A] * np.eye(3)
    return P


def sum_rule(P, charge=0):
    """The translation sum rule's residual max |Σ_A ∂μ/∂R_A − q·I| (e): a second route on every APT."""
    n = P.shape[1] // 3
    return float(np.abs(P.reshape(3, n, 3).sum(axis=1) - charge * np.eye(3)).max())


def intensities(P, H_projected, masses):
    """IR intensities (km/mol) of the vibrational modes of the projected Hessian from the APT."""
    mm = np.repeat(masses * AMU2AU, 3)
    Hm = H_projected / np.sqrt(np.outer(mm, mm))
    w, L = np.linalg.eigh(Hm)
    freq = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    vib = np.abs(freq) > 20.0
    dmu_dQ = P @ (L[:, vib] / np.sqrt(np.repeat(masses, 3))[:, None])          # e / √amu
    return freq[vib], KM_PER_MOL * (dmu_dQ ** 2).sum(axis=0)
