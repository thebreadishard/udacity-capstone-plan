"""Dipole derivatives (atomic polar tensors, APT) and IR band heights — one implementation for the labels route (`analytic_hessians.py`, which
takes the APT from the response its own Hessian solves: TASKS 44 route C, 11 Oct 2026) and the probes (`probes/dipole_derivs_cphf.py`, route B,
a second CPHF solve; `probes/dipole_derivs_fd.py`, finite differences). It sits beside `analytic_hessians.py` because the labels server runs that
script from a folder of its own, with this file copied next to it.

∂μ_t/∂R_{A,x} = Z_A δ_tx − Tr(∂D/∂R_{A,x} · r_t) − Tr(D · ∂r_t/∂R_{A,x}), with ∂C_occ/∂R from pyscf's `hessian.rhf.solve_mo1` (the occupied block
included, as pyscf's own `hess_elec` uses it: pyscf/hessian/rhf.py, exercised by pyscf/hessian/test/test_rks.py) and ∂r/∂R from the derivative
dipole integrals (`int1e_irp`, the basis functions on atom A); the index convention of `int1e_irp` was fixed against the FD route on water (2 Oct).
The Hessian with its response kept (`hessian_with_response`) follows pyscf-properties' `pyscf/prop/infrared/rhf.py` (`proc_hessian_`): solve
the response once and hand it to `hess_elec(mo1=, mo_e1=, h1ao=)`, the arguments pyscf's `hessian/rhf.py` `hess_elec` takes for this (2.14).
Measured (11 Oct, `probes/apt_route_c_probe.py`): the kept response gives route B's APT to 4.8e-7 e on benzene, the contraction costs < 0.01 s
against a 465 s Hessian; against finite differences 4.4e-4 e (benzene), 1.2e-5 e (water).
The response checked against its own equations (`refine_response`, 12 Oct 2026, TASKS 44 (a); design note
GoalGathering/notes/Design_2026-10-12_Residual_Checked_APT.md): pyscf 2.14's `lib.krylov` stops the Hessian's CPHF 7e-5 to 1e-4 off its own
system for DFT, whatever `tol` says (pyscf issue #2702; `probes/results_m1/krylov_report_2026-10-12/`). The Hessian is insensitive (benzene
0.06 cm⁻¹), the APT is not (4.3e-4 e against the field route). One round of batched defect correction brought benzene's residual from 1.3e-4
to 7.8e-8 and its APT to the field route's to 3.75e-5 e, for ≈ 120 s on a 780 s Hessian. The Hessian keeps pyscf's own response; only the
APT takes the refined one.
"""
import time
from typing import NamedTuple

import numpy as np

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705
# A_k [km/mol] = 974.8802 · |∂μ/∂Q_k|² with ∂μ/∂Q in e/√amu: 1 e/√amu → (2.541746 D / 0.529177 Å)² × 42.2561 km/mol per (D/Å)²/amu = 974.88 km/mol.
KM_PER_MOL = 974.8802
SUM_RULE_LIMIT = 5e-4  # e; route B's limit (benzene: CPHF vs FD differ by 4.4e-4 e at most)
CPHF_BOUND = 1e-6   # max |residual| of the refined response; 3.75e-5 e on benzene's APT was reached at 7.8e-8 (design note, 12 Oct 2026)


class Response(NamedTuple):
    """The CPHF response of a Hessian as pyscf's `solve_mo1` returns it (lists indexed by atom), with the derivative Fock matrices it solves."""
    mo1: list
    mo_e1: list
    h1ao: object


def solve_response(hobj):
    """`make_h1` and `solve_mo1`, the first two steps of pyscf's `HessianBase.kernel` (2.14), as pyscf-properties' infrared module calls them."""
    mf = hobj.base
    h1ao = hobj.make_h1(mf.mo_coeff, mf.mo_occ, None, hobj.atmlst)
    mo1, mo_e1 = hobj.solve_mo1(mf.mo_energy, mf.mo_coeff, mf.mo_occ, h1ao, None, hobj.atmlst)
    return Response(mo1, mo_e1, h1ao)


def hessian_with_response(hobj, response=None):
    """`hobj.kernel()` with the CPHF response solved once and returned: (de (natm, natm, 3, 3) as `kernel` returns it, mo1). The steps of pyscf's
    `HessianBase.kernel` (2.14) with `make_h1` and `solve_mo1` called here (or taken from `response`, a `solve_response` result, when the caller
    keeps h1ao for `refine_response`), as pyscf-properties' infrared module does; `hobj.de` is set as `kernel` sets it. Closed shell only: a UKS
    Hessian's response is an (alpha, beta) pair, which `apt_from_mo1` does not take."""
    mf = hobj.base
    mo_energy, mo_coeff, mo_occ, atmlst = mf.mo_energy, mf.mo_coeff, mf.mo_occ, hobj.atmlst
    mo1, mo_e1, h1ao = solve_response(hobj) if response is None else response
    de = hobj.hess_elec(mo_energy, mo_coeff, mo_occ, mo1=mo1, mo_e1=mo_e1, h1ao=h1ao, atmlst=atmlst)
    hobj.de = de + hobj.hess_nuc(hobj.mol, atmlst=atmlst)
    if mf.do_disp():
        hobj.de += hobj.get_dispersion()
    return hobj.de, mo1


def refine_response(hobj, mo1, h1ao, bound=CPHF_BOUND, max_rounds=3, tol=1e-9, per_column=True):
    """The Hessian's CPHF response checked against the equations pyscf's `scf/cphf.py` `solve_withs1` solves, and corrected where it is off.

    The system, per right-hand side in the MO basis (x = C^T S mo1): x_ai + e_ai·fx(x)_ai = −e_ai (h1 − s1·e_i)_ai on the virtual rows, with
    e_ai = 1/(e_a − e_i), fx the induced potential of `hessian.rhf.gen_vind` (the operator `solve_mo1` uses), and x_ij = −s1_ij/2 on the
    occupied rows, which are set here as pyscf sets them. The residual of all 3N right-hand sides is formed in one batched `fx` call; while its largest element
    exceeds `bound` (at most `max_rounds` times), the correction equation (I + A) δ = r is solved by the same multi-root `lib.krylov` and x += δ.
    **Per-column fallback** (13 Oct 2026, `per_column`): every column still above `bound` after the batched rounds is solved alone by scipy GMRES
    (rtol 1e-10, ≤ 300 iterations, restart 60) from the refined solution. The batched solver can stall where a single right-hand side converges:
    B_127dd8c4ed stayed at 2.1e-6 through five batched rounds, and single-column GMRES reached 1.2e-11 (`probes/results_m1/
    apt_refine_install_2026-10-12/diagnose_floor.log`). A bound ≤ 0 (a measurement of the rounds alone) skips it.
    Returns (mo1 refined, in pyscf's layout, and info: residual_before, residual_after, rounds, columns_fallback, seconds). The caller decides
    what a residual above `bound` means; nothing is raised. Closed shell only, all atoms (the APT needs every column)."""
    from pyscf import lib
    from pyscf.hessian import rhf as rhf_hess
    t0 = time.time()
    mf = hobj.base
    mol = mf.mol
    C, e, occ = mf.mo_coeff, mf.mo_energy, mf.mo_occ
    if np.asarray(C).ndim != 2:
        raise ValueError("refine_response: closed shell only (an open-shell response is an (alpha, beta) pair)")
    if hobj.atmlst is not None and list(hobj.atmlst) != list(range(mol.natm)):
        raise ValueError("refine_response: the response of every atom is needed")
    o, v = occ > 0, occ == 0
    nmo, nocc = C.shape[1], int(o.sum())
    mocc = C[:, o]
    e_ai = 1.0 / (e[v][:, None] - e[o][None, :])
    S = mf.get_ovlp()
    s1a = -mol.intor("int1e_ipovlp", comp=3)
    b = []
    for A, (_, _, p0, p1) in enumerate(mol.aoslice_by_atom()):                  # the right-hand side as solve_withs1 builds it
        s1ao = np.zeros((3,) + S.shape)
        s1ao[:, p0:p1] += s1a[:, p0:p1]
        s1ao[:, :, p0:p1] += s1a[:, p0:p1].transpose(0, 2, 1)
        s1 = np.einsum("pq,xqr,ri->xpi", C.T, s1ao, mocc)
        bb = np.einsum("pq,xqr,ri->xpi", C.T, np.asarray(h1ao[A]), mocc) - s1 * e[o]
        bb[:, v] *= -e_ai
        bb[:, o] = -0.5 * s1[:, o]
        b.append(bb)
    b = np.concatenate(b)                                                        # (3N, nmo, nocc)
    x = np.concatenate([np.einsum("pq,qr,xri->xpi", C.T, S, mo1[A]) for A in range(mol.natm)])
    x[:, o] = b[:, o]                                                            # the occupied rows as solve_withs1 sets them
    fx = rhf_hess.gen_vind(mf, C, occ)

    def a_vo(xx):
        """A x on the virtual rows, zero on the occupied rows: lib.krylov's `a` in (1 + a) x = b."""
        w = fx(xx.reshape(-1, nmo, nocc)).reshape(-1, nmo, nocc)
        w[:, v] *= e_ai
        w[:, o] = 0.0
        return w.reshape(len(w), -1)

    def residual(xx):
        return b - xx - a_vo(xx).reshape(xx.shape)                               # zero on the occupied rows, which δ then leaves alone

    r = residual(x)
    before = after = float(np.abs(r).max())
    rounds = 0
    while after > bound and rounds < max_rounds:
        x = x + lib.krylov(a_vo, r.reshape(len(r), -1), tol=tol, max_cycle=50).reshape(r.shape)
        r = residual(x)
        after = float(np.abs(r).max())
        rounds += 1
    n_fallback = 0
    if per_column and bound > 0 and after > bound:
        from scipy.sparse.linalg import LinearOperator, gmres
        dim = nmo * nocc
        op = LinearOperator((dim, dim), matvec=lambda y: y + a_vo(y.reshape(1, nmo, nocc)).reshape(-1), dtype=float)
        for j in np.flatnonzero(np.abs(r.reshape(len(r), -1)).max(axis=1) > bound):
            d, _ = gmres(op, r[j].reshape(-1), rtol=1e-10, atol=0.0, maxiter=300, restart=60)
            x[j] = x[j] + d.reshape(nmo, nocc)
            n_fallback += 1
        r = residual(x)
        after = float(np.abs(r).max())
    mo1_refined = [np.einsum("pq,xqi->xpi", C, x[3 * A:3 * A + 3]) for A in range(mol.natm)]
    return mo1_refined, {"residual_before": before, "residual_after": after, "rounds": rounds, "columns_fallback": n_fallback,
                         "seconds": round(time.time() - t0, 1)}


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
