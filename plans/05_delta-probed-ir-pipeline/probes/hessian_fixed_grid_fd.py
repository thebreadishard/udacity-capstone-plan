"""pyscf's analytic DFT Hessian against central differences of its analytic gradient on a frozen grid (12 Oct 2026; registration
`probes/results_m1/hessian_xc_check_2026-10-12/REGISTRATION.md`).

The analytic Hessian has no grid response, so its exact counterpart is the finite difference of the gradient without grid response with the
integration grid of the reference geometry kept for every displaced geometry (points and weights frozen; the screening mask rebuilt for the
moved basis functions with `gen_grid.make_mask`). Gradient calls as pyscf's grad/test/test_rks.py (`nuc_grad_method()`); the grid is reused
through `mf.grids`, which pyscf's DFT code builds only when `coords is None` (`dft/rks.py` get_veff).

    python probes/hessian_fixed_grid_fd.py <dir with geometry.json> --out <file.npz> [--xc b3lyp] [--hessian hessian_b3lyp_analytic.npz]
                                           [--step 0.005] [--threads 4] [--charge 0 --spin 0]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from pyscf import dft, gto, lib
from pyscf.dft import gen_grid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus"))
from analytic_hessians import freqs_cm, project_tr, vib_only  # noqa: E402  (the labels route's own conventions)


def make_mf(mol, xc, grids=None, grid=(99, 590)):
    mf = dft.UKS(mol) if mol.spin else dft.RKS(mol)
    mf.xc = xc
    if grids is None:
        mf.grids.atom_grid = grid
        mf.grids.prune = None
    else:
        mf.grids = grids
    mf.conv_tol = 1e-11
    mf.conv_tol_grad = 1e-8
    mf.verbose = 0
    return mf


def frozen_grids(ref_grids, mol):
    """A copy of the reference grid (points, weights) for a displaced molecule; the screening mask is rebuilt for its basis."""
    g = gen_grid.Grids(mol)
    g.atom_grid = ref_grids.atom_grid
    g.prune = ref_grids.prune
    g.coords = ref_grids.coords
    g.weights = ref_grids.weights
    g.non0tab = gen_grid.make_mask(mol, g.coords)
    return g


def gradient(mf):
    gobj = mf.nuc_grad_method()
    gobj.grid_response = False
    gobj.verbose = 0
    return gobj.kernel()


def fd_hessian(mol0, xc, grid, h, log=print):
    ref = make_mf(mol0, xc, grid=grid)
    ref.kernel()
    if not ref.converged:
        raise RuntimeError("reference SCF not converged")
    dm0 = ref.make_rdm1()
    x0 = mol0.atom_coords(unit="Bohr")
    n = mol0.natm
    H = np.zeros((3 * n, 3 * n))
    t0 = time.time()
    for A in range(n):
        for d in range(3):
            g = []
            for s in (+1, -1):
                x = x0.copy()
                x[A, d] += s * h
                m = mol0.set_geom_(x, unit="Bohr", inplace=False)
                mf = make_mf(m, xc, grids=frozen_grids(ref.grids, m))
                mf.kernel(dm0)
                if not mf.converged:
                    raise RuntimeError(f"SCF not converged at atom {A} coordinate {d} sign {s}")
                g.append(gradient(mf).ravel())
            H[3 * A + d] = (g[0] - g[1]) / (2 * h)
        log(f"  atom {A + 1}/{n} done, {time.time() - t0:.0f} s", flush=True)
    return H


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--xc", default="b3lyp")
    ap.add_argument("--hessian", default=None, help="a saved labels-route Hessian (H_raw) to compare with; else pyscf's analytic Hessian is computed")
    ap.add_argument("--step", type=float, default=0.005)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--grid", default="99,590")
    ap.add_argument("--charge", type=int, default=0)
    ap.add_argument("--spin", type=int, default=0)
    a = ap.parse_args()
    lib.num_threads(a.threads)
    grid = tuple(int(v) for v in a.grid.split(","))
    geo = json.load(open(os.path.join(a.dir, "geometry.json")))
    x = np.asarray(geo["coords_bohr"], float)
    masses = np.asarray(geo["masses_amu"], float)
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(geo["symbols"], x, strict=True)], unit="Bohr", basis="6-31g*", cart=True,
                symmetry=False, verbose=0, max_memory=4000, charge=a.charge, spin=a.spin)
    t0 = time.time()
    if a.hessian:
        Ha = np.load(os.path.join(a.dir, a.hessian))["H_raw"]
    else:
        mf = make_mf(mol, a.xc, grid=grid)
        mf.kernel()
        Ha = mf.Hessian().kernel().transpose(0, 2, 1, 3).reshape(3 * mol.natm, 3 * mol.natm)
        Ha = 0.5 * (Ha + Ha.T)
    Hf = fd_hessian(mol, a.xc, grid, a.step)
    Hf_s = 0.5 * (Hf + Hf.T)
    fa = vib_only(freqs_cm(project_tr(Ha, masses, x), masses))
    ff = vib_only(freqs_cm(project_tr(Hf_s, masses, x), masses))
    dw = ff - fa
    np.savez_compressed(a.out, H_analytic=Ha, H_fd=Hf, freq_analytic=fa, freq_fd=ff, step=a.step, xc=a.xc, grid=np.array(grid),
                        seconds=round(time.time() - t0))
    print(f"{a.dir} ({a.xc}): max |H_analytic − H_FD,frozen grid| {np.abs(Ha - Hf_s).max():.2e}, FD asymmetry {np.abs(Hf - Hf.T).max():.2e}; "
          f"max |Δω| {np.abs(dw).max():.2f} cm-1 (mode at {fa[np.argmax(np.abs(dw))]:.1f}); {time.time() - t0:.0f} s", flush=True)
    for f, d in zip(fa, dw, strict=True):
        print(f"  {f:8.1f} cm-1  Δω {d:+.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
