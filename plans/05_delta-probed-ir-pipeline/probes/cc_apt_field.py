"""Lever 6 of the 12 Oct 2026 odds (the user: 'Doe 6 ook'): a CCSD(T) atomic polar tensor (APT) for an anchor whose finite-difference run
stored no dipoles (pyridine, fluorobenzene, benzonitrile ran on 30 Sep, before the dipole capture of 3 Oct), so that read-out (3) can test the
Hessian's part of the intensities on a molecule of low symmetry (benzene's symmetry fixes its mode shapes: TASKS 'CC-level dipole derivatives').

P[t, 3A+x] = ∂μ_t/∂R_{A,x} = −∂g_{A,x}/∂F_t, by central differences of the CCSD(T) gradient in a uniform field F (H' = −μ·F: F·r added to the
core Hamiltonian, −Z_A F·R_A for the nuclei). The gradient's core-Hamiltonian derivative carries the field term through
`apt_field_route.field_hcore_generator` (validated for DFT on 12 Oct: water, benzene). Six CCSD(T) gradients instead of the 6N of the
finite-difference route. The CC chain is `cc_dipole_capture`'s (RHF → CCSD → (T) → the (T) lambda → `grad.ccsd_t.Gradients(mycc).kernel(t1, t2,
l1, l2, eris)`, the call pyscf/grad/test/test_ccsd_t.py makes); pyscf's `grad/ccsd.py` `grad_elec` takes the core-Hamiltonian derivative from
`mycc._scf.nuc_grad_method()` (2.14.0, line 158), which is where the field term goes in. Frozen core as the E8 probe derives it.

Second routes (registration `probes/results_m1/cc_apt_field_2026-10-12/REGISTRATION.md`): on water against central differences of the relaxed
CCSD(T) dipole (`apt_fd_dipole` here, the E8 probe's route); on benzene against the E8 run's own FD APT (`e8_benzene_ccpvdz_dip_2026-10-03`).

    python probes/cc_apt_field.py <geometry.json> --out <apt.npz> [--basis cc-pvdz] [--field 1e-3] [--threads 8] [--fast] [--coords-from <npz>]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from pyscf import gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus"))
from apt import sum_rule  # noqa: E402
from apt_field_route import field_hcore_generator  # noqa: E402
from cc_dipole_capture import _cc_with_lambda, relaxed_dipole  # noqa: E402
from e8_cc_hessian_fd import core_orbital_count  # noqa: E402


def cc_gradient_in_field(mol, frozen, F):
    """(CCSD(T) gradient (natm, 3) in the field F, relaxed dipole (3,), energy) — the field on electrons and nuclei."""
    F = np.asarray(F, dtype=float)
    shift = np.einsum("t,tij->ij", F, mol.intor("int1e_r", comp=3))
    energy, mf, mycc, l1, l2, eris = _cc_with_lambda(mol, frozen, hcore_shift=shift)
    if np.any(F):
        make_grad = mf.nuc_grad_method

        def nuc_grad_method(*args, **kwargs):
            g = make_grad(*args, **kwargs)
            g.hcore_generator = field_hcore_generator(g, F)
            return g
        mf.nuc_grad_method = nuc_grad_method
    mu, grad = relaxed_dipole(mol, mf, mycc, l1, l2, eris)
    return grad - mol.atom_charges()[:, None] * F[None, :], mu, energy


def apt_cc_field(mol, frozen, field=1e-3, log=print, cache_dir=None):
    """The CCSD(T) APT [3, 3N] from six gradients in ±field along x, y, z. With cache_dir, each field's gradient is kept as
    <cache_dir>/grad_<x|y|z><p|m>.npy and reused on a re-run (14 Oct 2026: a stopped run had lost 4 of 6 fields); a cached gradient is used only
    when its stored field, coordinates and basis match."""
    P = np.zeros((3, 3 * mol.natm))
    t0 = time.time()
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
    for t in range(3):
        g = []
        for s in (+1.0, -1.0):
            F = np.zeros(3)
            F[t] = s * field
            tag = f"{'xyz'[t]}{'p' if s > 0 else 'm'}"
            path = os.path.join(cache_dir, f"grad_{tag}.npz") if cache_dir else None
            if path and os.path.exists(path):
                c = np.load(path)
                if np.allclose(c["field"], F) and np.allclose(c["coords_bohr"], mol.atom_coords()) and str(c["basis"]) == str(mol.basis):
                    g.append(c["grad"])
                    log(f"  field {'xyz'[t]}{'+' if s > 0 else '-'} reused from {path}", flush=True)
                    continue
                raise SystemExit(f"{path} belongs to another field, geometry or basis — not reused; remove it or choose another --cache-dir")
            g.append(cc_gradient_in_field(mol, frozen, F)[0])
            if path:
                np.savez(path + ".tmp.npz", grad=g[-1], field=F, coords_bohr=mol.atom_coords(), basis=str(mol.basis))
                os.replace(path + ".tmp.npz", path)
            log(f"  field {'xyz'[t]}{'+' if s > 0 else '-'} done, {time.time() - t0:.0f} s", flush=True)
        P[t] = -(g[0] - g[1]).ravel() / (2 * field)
    return P


def apt_fd_dipole(mol, frozen, step=5e-3, log=print):
    """The second route on small molecules: central differences of the relaxed CCSD(T) dipole over all 3N Cartesian coordinates (6N gradients)."""
    x0 = mol.atom_coords()
    P = np.zeros((3, 3 * mol.natm))
    for k in range(3 * mol.natm):
        mu = []
        for s in (+1.0, -1.0):
            x = x0.copy()
            x[k // 3, k % 3] += s * step
            mu.append(cc_gradient_in_field(mol.set_geom_(x, unit="Bohr", inplace=False), frozen, np.zeros(3))[1])
        P[:, k] = (mu[0] - mu[1]) / (2 * step)
        log(f"  coordinate {k + 1}/{3 * mol.natm} done", flush=True)
    return P


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("geometry")
    ap.add_argument("--out", required=True)
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--field", type=float, default=1e-3)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=8000)
    ap.add_argument("--coords-from", help="an E8 npz (reference.npz, apt_ccsd_t.npz) whose coords_bohr replace the geometry file's (same atom order)")
    ap.add_argument("--fast", action="store_true", help="the (T) density and lambda C kernels of probes/t_density_kernel (as the E8 probe's flags)")
    ap.add_argument("--cache-dir", default=None, help="keep each field's gradient here and reuse it on a re-run (default: <out>.fields)")
    a = ap.parse_args()
    lib.num_threads(a.threads)
    log = print
    g = json.load(open(a.geometry))
    symbols = [s.capitalize() for s in g["symbols"]]
    x = np.array(np.load(a.coords_from)["coords_bohr"] if a.coords_from else g["coords_bohr"], dtype=float)
    if x.shape != (len(symbols), 3):
        raise SystemExit(f"coordinates {x.shape} do not match {len(symbols)} atoms")
    if a.fast:
        sys.path.insert(0, os.path.join(HERE, "t_density_kernel"))
        import t_density_fast as fast
        if not fast.available():
            raise SystemExit("--fast: the C kernel is not available on this machine (build probes/t_density_kernel/build.sh)")
        fast.install()
        fast.install_lambda()
    frozen = core_orbital_count(symbols)
    mol = gto.M(atom=list(zip(symbols, map(tuple, x), strict=True)), unit="Bohr", basis=a.basis, symmetry=False, verbose=0,
                max_memory=a.max_memory)
    log(f"CC APT by the field route: {len(symbols)} atoms, {a.basis}, frozen {frozen}, field {a.field:g}, {a.threads} threads"
        f"{', fast (T) kernels' if a.fast else ''}", flush=True)
    t0 = time.time()
    P = apt_cc_field(mol, frozen, a.field, log, cache_dir=a.cache_dir or a.out + ".fields")
    sr = sum_rule(P, mol.charge)
    np.savez_compressed(a.out, apt=P, sum_rule_max=sr, field=a.field, basis=a.basis, frozen=frozen, coords_bohr=x, symbols=np.array(symbols),
                        route="cc_field", seconds=round(time.time() - t0))
    log(f"APT written ({a.out}): translation sum rule {sr:.1e} e, {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
