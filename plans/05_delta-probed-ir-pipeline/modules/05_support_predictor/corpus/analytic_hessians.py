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


def freqs_cm(Hp, masses):
    """Harmonic frequencies (cm-1, 3N long, imaginary negative) of a Cartesian Hessian in hartree/bohr^2 with masses in amu — the corpus convention."""
    sm = np.sqrt(np.repeat(masses, 3)); w = np.linalg.eigvalsh(Hp / np.outer(sm, sm))
    au2cm = 219474.6313705; amu2au = 1822.888486209
    f = np.sqrt(np.abs(w) / amu2au) * au2cm
    return np.where(w < 0, -f, f)


def vib_only(f):
    """The 3N-6 vibrational entries of a 3N-long frequency list: drop the six entries closest to zero, keep imaginary modes as negative numbers, sorted."""
    f = np.asarray(f, dtype=float); keep = np.argsort(np.abs(f))[6:]
    return np.sort(f[keep])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--threads", type=int, default=16); ap.add_argument("--grid", default="99,590"); ap.add_argument("--compare-only", action="store_true", help="rebuild analytic_check.json from the saved *_analytic.npz files (no DFT)")
    a = ap.parse_args(); lib.num_threads(a.threads); rad, ang = (int(v) for v in a.grid.split(","))
    for d in a.dirs:
        g = json.load(open(d + "/geometry.json")); sym = g["symbols"]; x = np.array(g["coords_bohr"]); masses = np.array(g["masses_amu"])
        mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(sym, x)], unit="Bohr", basis="6-31g*", cart=True, symmetry=False, verbose=0, max_memory=20000)
        out = {}
        for tag, xc in (("b3lyp", "b3lyp"), ("wb97x", "wb97x")):
            n = len(sym); t0 = time.time()
            if a.compare_only:
                z = np.load(f"{d}/hessian_{tag}_analytic.npz"); Hc = z["H_raw"]; Hp = z["H_projected"]; e = float(z["energy"])
            else:
                mf = dft.RKS(mol); mf.xc = xc; mf.grids.atom_grid = (rad, ang); mf.grids.prune = None; mf.conv_tol = 1e-11; e = mf.kernel()
                H = mf.Hessian().kernel(); Hc = H.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n); Hc = 0.5 * (Hc + Hc.T)
                Hp = project_tr(Hc, masses, x)
            # frequencies from the projected Hessian by the corpus's own convention: a 3N-long list, imaginary modes negative, six ~0 entries.
            # (pyscf's harmonic_analysis drops a mode when an imaginary one falls in its trans/rot window — 62 instead of 63 entries on A2_3a2982dd85, 23 Sep.)
            fr = freqs_cm(Hp, masses)
            if not a.compare_only:
                np.savez_compressed(f"{d}/hessian_{tag}_analytic.npz", H_raw=Hc, H_projected=Hp, freq_cm=fr, energy=float(e), grid=np.array([rad, ang]))
            corpus = np.load(f"{d}/hessian_{tag}.npz")
            fr = vib_only(fr); fc = vib_only(corpus["freq_cm"])     # drop the six trans/rot entries (smallest |value|) from both lists; imaginary modes stay, negative
            out[tag] = dict(freq_analytic=fr.tolist(), freq_corpus=fc.tolist(), dH_max=float(np.abs(Hc - corpus["H_raw"]).max()),
                            dH_rms=float(np.sqrt(np.mean((Hc - corpus["H_raw"]) ** 2))), energy=float(e), energy_corpus=float(corpus["energy"]), seconds=round(time.time() - t0))
            print(f"{d} {tag}: {out[tag]['seconds']} s; |H_analytic − H_corpus| max {out[tag]['dH_max']:.2e} rms {out[tag]['dH_rms']:.2e}; max |Δfreq| {np.abs(fr - fc).max():.0f} cm-1", flush=True)
        json.dump(out, open(d + "/analytic_check.json", "w"), indent=1)


if __name__ == "__main__":
    main()
