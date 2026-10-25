"""Odds lever 4 (3 Oct 2026): the relaxed CCSD(T) dipole from the gradient code's own density, validated against a finite-field derivative.

`pyscf.grad.ccsd.grad_elec` builds the fully relaxed one-particle density (orbital response included) and contracts it with the derivative integrals, but
does not return it. It calls `mycc._scf.get_veff(mol, dm1 + dm1.T)` once with the correlation part of that density (pyscf 2.14.0, grad/ccsd.py line 169)
before adding the Hartree–Fock density. `relaxed_dipole` records that argument through a thin wrapper around `get_veff` during `Gradients.kernel(...)` —
no copy of the gradient algebra — and forms μ = Σ_A Z_A R_A − Tr[(D_corr + D_HF) r].

Second route (noise principle, 21 Sep 2026): the finite-field derivative of the CCSD(T) energy, E(±F) with the field on electrons and nuclei
(H' = −μ·F), two field strengths (Richardson). The two must agree to 1e-5 a.u. on water before the capture goes into the E8 probe. pyscf usage: the
lambda path of the E8 probe (`ccsd_t_lambda.kernel`, then `grad.ccsd_t.Gradients(mycc).kernel(t1, t2, l1, l2, eris)`, as in pyscf/grad/test/test_ccsd_t.py).

    python probes/cc_dipole_capture.py <geometry.json> [--basis cc-pvdz] [--threads 4] [--field 1e-4]
"""
import argparse
import json
import sys
import time

import numpy as np
from pyscf import cc, gto, lib, scf
from pyscf.cc import ccsd_t_lambda
from pyscf.grad import ccsd_t as ccsd_t_grad

FIRST_ROW = {"B", "C", "N", "O", "F"}


def _cc_with_lambda(mol, frozen, hcore_shift=None):
    """RHF → CCSD → (T) → the (T) lambda, as the E8 probe does; returns (energy, mf, mycc, l1, l2, eris)."""
    mf = scf.RHF(mol)
    mf.conv_tol = 1e-12
    if hcore_shift is not None:
        h0 = scf.hf.get_hcore(mol)
        mf.get_hcore = lambda *args, **kwargs: h0 + hcore_shift
    e_hf = mf.kernel()
    mycc = cc.CCSD(mf, frozen=frozen)
    mycc.conv_tol, mycc.conv_tol_normt = 1e-10, 1e-8
    e_corr = mycc.kernel()[0]
    et = mycc.ccsd_t()
    eris = mycc.ao2mo()
    conv, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-8)
    if not (mf.converged and mycc.converged and conv):
        raise RuntimeError("SCF, CCSD or the (T) lambda did not converge")
    return float(e_hf + e_corr + et), mf, mycc, l1, l2, eris


def relaxed_dipole(mol, mf, mycc, l1, l2, eris):
    """(μ in a.u. (3,), gradient (natm, 3)) from one gradient evaluation; the relaxed density is captured from the gradient code's get_veff call."""
    captured = []
    orig = mf.get_veff

    def get_veff_recording(mol_, dm=None, *args, **kwargs):
        if dm is not None and np.ndim(dm) == 2 and dm.shape == (mol.nao, mol.nao):
            captured.append(np.array(dm))
        return orig(mol_, dm, *args, **kwargs)

    mf.get_veff = get_veff_recording
    try:
        grad = ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris)
    finally:
        mf.get_veff = orig
    if not captured:
        raise RuntimeError("no get_veff call with an AO density was seen during the gradient")
    # the Z-vector solve (`_response_dm1`) calls get_veff with trial densities first; grad_elec's own call with dm1 + dm1.T is the last one
    # (pyscf 2.14.0 grad/ccsd.py: `_response_dm1` on line 148, `get_veff(mol, dm1+dm1.T)` on line 169). The finite-field route below is what proves it.
    d_corr = 0.5 * captured[-1]
    relaxed_dipole.n_calls = len(captured)
    d_hf = mf.make_rdm1()
    r = mol.intor("int1e_r", comp=3)
    mu_el = -np.einsum("xij,ji->x", r, d_corr + d_hf)
    mu_nuc = np.einsum("a,ax->x", mol.atom_charges(), mol.atom_coords())
    return mu_el + mu_nuc, np.asarray(grad)


def finite_field_dipole(mol, frozen, field):
    """μ = −dE/dF by central differences, E(F) the CCSD(T) energy with H' = −μ·F = +F·Σ r_i − F·Σ Z_A R_A, per Cartesian component."""
    r = mol.intor("int1e_r", comp=3)
    mu = np.zeros(3)
    for c in range(3):
        e = []
        for sgn in (+1.0, -1.0):
            fvec = np.zeros(3)
            fvec[c] = sgn * field
            e_el = _cc_with_lambda(mol, frozen, hcore_shift=np.einsum("x,xij->ij", fvec, r))[0]
            e_nuc_field = -float(np.dot(fvec, np.einsum("a,ax->x", mol.atom_charges(), mol.atom_coords())))
            e.append(e_el + e_nuc_field)
        mu[c] = -(e[0] - e[1]) / (2 * field)
    return mu


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("geometry")
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--field", type=float, default=1e-4)
    ap.add_argument("--limit", type=float, default=1e-5, help="max |μ_capture − μ_field| allowed (a.u.)")
    a = ap.parse_args()
    lib.num_threads(a.threads)
    g = json.load(open(a.geometry))
    sym = [s.capitalize() for s in g["symbols"]]
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(sym, np.asarray(g["coords_bohr"], float), strict=True)], unit="Bohr", basis=a.basis, verbose=0, max_memory=8000)
    mol.set_common_orig((0.0, 0.0, 0.0))
    frozen = sum(1 for s in sym if s in FIRST_ROW)
    t0 = time.time()
    e, mf, mycc, l1, l2, eris = _cc_with_lambda(mol, frozen)
    mu_cap, grad = relaxed_dipole(mol, mf, mycc, l1, l2, eris)
    t1 = time.time()
    mu_ff = finite_field_dipole(mol, frozen, a.field)
    mu_ff2 = finite_field_dipole(mol, frozen, 2 * a.field)
    t2 = time.time()
    d = float(np.abs(mu_cap - mu_ff).max())
    rich = float(np.abs(mu_ff - mu_ff2).max())
    passed = d <= a.limit
    print(f"{mol.natm} atoms, {a.basis}, frozen {frozen}: E(CCSD(T)) = {e:.9f}; capture {t1 - t0:.0f} s ({relaxed_dipole.n_calls} get_veff calls seen, the last taken), "
          f"finite field (12 energies) {t2 - t1:.0f} s")
    print(f"  μ captured     = {np.array2string(mu_cap, precision=7)}")
    print(f"  μ finite field = {np.array2string(mu_ff, precision=7)}  (F = {a.field:g}; |Δ| vs 2F = {rich:.1e})")
    print(f"  max |μ_capture − μ_field| = {d:.1e} a.u. (limit {a.limit:g}) → {'PASS' if passed else 'FAIL'}; max |grad| {np.abs(grad).max():.2e}")
    return 0 if passed else 3


if __name__ == "__main__":
    sys.exit(main())
