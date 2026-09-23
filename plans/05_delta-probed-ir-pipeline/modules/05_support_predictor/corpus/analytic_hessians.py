"""Second route for a corpus molecule's Hessians (23 September 2026, noise principle): pyscf analytic Hessians of both functionals at the
corpus geometry, 6-31G* with Cartesian d (as psi4), grid (99,590), written next to the psi4 finite-difference files as
hessian_<tag>_analytic.npz (H_raw, H_projected with translations/rotations projected out, freq_cm, energy) plus analytic_check.json with the
side-by-side frequencies. Found on benzene: the corpus ωB97X FD Hessian was wrong by up to 133 cm⁻¹ (degenerate pairs split 563/605).

Usage: python analytic_hessians.py <molecule dir> [more dirs...] [--threads 16] [--grid 99,590]
"""
import argparse
import json
import time

import numpy as np
from pyscf import dft, gto, lib
from pyscf.hessian import thermo

AMU2AU = 1822.888486209


def project_tr(H, masses, x):
    """Project translations and rotations out of a Cartesian Hessian (mass-weighted projector, then back), as psi4 does for H_projected."""
    n = len(masses); m = np.repeat(masses * AMU2AU, 3); sm = np.sqrt(m)
    com = (x * masses[:, None]).sum(0) / masses.sum(); r = x - com
    D = []
    for k in range(3):
        v = np.zeros((n, 3)); v[:, k] = 1.0; D.append((v * np.sqrt(masses)[:, None]).ravel())
    for k in range(3):
        e = np.zeros(3); e[k] = 1.0; v = np.cross(np.tile(e, (n, 1)), r); D.append((v * np.sqrt(masses)[:, None]).ravel())
    D = np.array(D).T; q, _ = np.linalg.qr(D); P = np.eye(3 * n) - q @ q.T
    Hmw = H / np.outer(sm, sm); Hp = P @ Hmw @ P
    return Hp * np.outer(sm, sm)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--threads", type=int, default=16); ap.add_argument("--grid", default="99,590")
    a = ap.parse_args(); lib.num_threads(a.threads); rad, ang = (int(v) for v in a.grid.split(","))
    for d in a.dirs:
        g = json.load(open(d + "/geometry.json")); sym = g["symbols"]; x = np.array(g["coords_bohr"]); masses = np.array(g["masses_amu"])
        mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(sym, x)], unit="Bohr", basis="6-31g*", cart=True, symmetry=False, verbose=0, max_memory=20000)
        out = {}
        for tag, xc in (("b3lyp", "b3lyp"), ("wb97x", "wb97x")):
            t0 = time.time(); mf = dft.RKS(mol); mf.xc = xc; mf.grids.atom_grid = (rad, ang); mf.grids.prune = None; mf.conv_tol = 1e-11; e = mf.kernel()
            H = mf.Hessian().kernel(); n = len(sym); Hc = H.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n); Hc = 0.5 * (Hc + Hc.T)
            res = thermo.harmonic_analysis(mol, H, exclude_trans=True, exclude_rot=True, imaginary_freq=False); fr = np.sort(res["freq_wavenumber"].real)
            Hp = project_tr(Hc, masses, x)
            np.savez_compressed(f"{d}/hessian_{tag}_analytic.npz", H_raw=Hc, H_projected=Hp, freq_cm=fr, energy=float(e), grid=np.array([rad, ang]))
            corpus = np.load(f"{d}/hessian_{tag}.npz"); fc = np.sort(corpus["freq_cm"][corpus["freq_cm"] > 10])
            out[tag] = dict(freq_analytic=fr.tolist(), freq_corpus=fc.tolist(), dH_max=float(np.abs(Hc - corpus["H_raw"]).max()),
                            dH_rms=float(np.sqrt(np.mean((Hc - corpus["H_raw"]) ** 2))), energy=float(e), energy_corpus=float(corpus["energy"]), seconds=round(time.time() - t0))
            print(f"{d} {tag}: {out[tag]['seconds']} s; |H_analytic − H_corpus| max {out[tag]['dH_max']:.2e} rms {out[tag]['dH_rms']:.2e}; max |Δfreq| {np.abs(fr - fc).max():.0f} cm-1", flush=True)
        json.dump(out, open(d + "/analytic_check.json", "w"), indent=1)


if __name__ == "__main__":
    main()
