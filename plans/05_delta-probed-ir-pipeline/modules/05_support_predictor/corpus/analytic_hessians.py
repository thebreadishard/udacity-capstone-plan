"""Second route for a corpus molecule's Hessians (23 September 2026, noise principle): pyscf analytic Hessians of both functionals at the
corpus geometry, 6-31G* with Cartesian d (as psi4), grid (99,590), written next to the psi4 finite-difference files as
hessian_<tag>_analytic.npz (H_raw, H_projected with translations/rotations projected out, freq_cm, energy) plus analytic_check.json with the
side-by-side frequencies. Found on benzene: the corpus ωB97X FD Hessian was wrong by up to 133 cm⁻¹ (degenerate pairs split 563/605).

Usage: python analytic_hessians.py <molecule dir> [more dirs...] [--threads 16] [--grid 99,590] [--charge 0 --spin 0]
       --charge/--spin (29 Sep 2026, anchor set two R4): UKS for an open-shell molecule (spin = 2S, as pyscf); a folder without the corpus psi4 file
       of a functional (the cation has no corpus row) gets the analytic file and no comparison for it.
       APT (11 Oct 2026, TASKS 44 route C): a closed-shell molecule's B3LYP pass also writes dipole_b3lyp_cphf.npz (route "hessian_response"),
       contracted from the CPHF response the Hessian solves anyway (apt.py, next to this file; < 0.01 s against a 465 s Hessian on benzene, equal
       to the separate CPHF route to 4.8e-7 e). An existing APT file is kept. A failed APT (or a sum rule above 5e-4 e) is reported after the
       molecule's two Hessians are written, and the exit status is 3, so the lane logs the molecule as FAILED. --no-apt turns it off.
       Provenance (11 Oct 2026, TASKS 47): every file written carries `software` — the pyscf, numpy and Python versions, pyscf's source
       commit when it is imported from a git checkout, and the sha256 of this script and apt.py — as a JSON string in the npz files and as a
       field inside each functional's entry of analytic_check.json (its readers iterate the entries).
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import time

import numpy as np
import pyscf
from apt import apt_from_mo1, hessian_with_response, intensities, sum_rule
from pyscf import dft, gto, lib

AMU2AU = 1822.888486209
APT_FILE = "dipole_b3lyp_cphf.npz"     # the name the export and module 08 read; route B writes it too
SUM_RULE_LIMIT = 5e-4                  # e; route B's limit (benzene: CPHF vs FD differ by 4.4e-4 e at most)


def software():
    """What made a file: versions, pyscf's commit when it comes from a git checkout (its parent folder the checkout's root, so an unrelated
    repository around site-packages is not reported), and the sha256 (first 12) of this script and apt.py."""
    here = os.path.dirname(os.path.abspath(__file__))
    pdir = os.path.dirname(os.path.abspath(pyscf.__file__))
    git = None
    try:
        top = subprocess.run(["git", "-C", pdir, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10,
                             check=False).stdout.strip()
        if top and os.path.samefile(top, os.path.dirname(pdir)):
            git = subprocess.run(["git", "-C", top, "describe", "--always", "--dirty"], capture_output=True, text=True,
                                 timeout=10, check=False).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    sha = {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()[:12] for f in ("analytic_hessians.py", "apt.py")}
    return {"pyscf": pyscf.__version__, "pyscf_git": git, "numpy": np.__version__, "python": platform.python_version(), "sha256": sha}


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


def write_apt(d, mf, mo1, Hp, masses, grid, stamp):
    """The APT from the Hessian's own response, its sum rule and band heights, written as route B writes them (the file carries the summary;
    analytic_check.json keeps one entry per functional, as its readers expect). Raises ValueError when the sum rule fails (the file is written
    all the same, marked passed=False)."""
    t0 = time.time()
    P = apt_from_mo1(mf, mo1)
    sr = sum_rule(P, mf.mol.charge)
    freq, km = intensities(P, Hp, masses)
    passed = sr <= SUM_RULE_LIMIT
    np.savez_compressed(f"{d}/{APT_FILE}", apt=P, sum_rule_max=sr, fd_max_diff=float("nan"), freq_cm=freq, intensity_km_mol=km, xc="b3lyp",
                        basis="6-31g*", grid=np.array(grid), passed=passed, route="hessian_response", seconds=round(time.time() - t0, 3),
                        software=json.dumps(stamp, sort_keys=True))
    if not passed:
        raise ValueError(f"APT sum rule {sr:.1e} > {SUM_RULE_LIMIT:g}")
    return f"APT from the Hessian's response: sum rule {sr:.1e}, {time.time() - t0:.2f} s"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--threads", type=int, default=16); ap.add_argument("--grid", default="99,590"); ap.add_argument("--compare-only", action="store_true", help="rebuild analytic_check.json from the saved *_analytic.npz files (no DFT)")
    ap.add_argument("--charge", type=int, default=0); ap.add_argument("--spin", type=int, default=0, help="2S; > 0 selects UKS (the E8 open-shell path uses the same convention)")
    ap.add_argument("--no-apt", action="store_true", help="skip the B3LYP APT from the Hessian's response (closed shell only; on by default since 11 Oct 2026)")
    a = ap.parse_args(); lib.num_threads(a.threads); rad, ang = (int(v) for v in a.grid.split(","))
    apt_errors = []
    stamp = software()
    for d in a.dirs:
        g = json.load(open(d + "/geometry.json")); sym = g["symbols"]; x = np.array(g["coords_bohr"]); masses = np.array(g["masses_amu"])
        mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(sym, x, strict=True)], unit="Bohr", basis="6-31g*", cart=True, symmetry=False, verbose=0, max_memory=20000,
                    charge=a.charge, spin=a.spin)
        out = {}
        for tag, xc in (("b3lyp", "b3lyp"), ("wb97x", "wb97x")):
            n = len(sym); t0 = time.time()
            if a.compare_only:
                z = np.load(f"{d}/hessian_{tag}_analytic.npz"); Hc = z["H_raw"]; Hp = z["H_projected"]; e = float(z["energy"])
            else:
                mf = dft.UKS(mol) if a.spin else dft.RKS(mol); mf.xc = xc; mf.grids.atom_grid = (rad, ang); mf.grids.prune = None; mf.conv_tol = 1e-11; e = mf.kernel()
                if not mf.converged: raise RuntimeError(f"{d} {tag}: SCF not converged")
                if a.spin:
                    s2 = float(mf.spin_square()[0]); s = a.spin / 2
                    if abs(s2 - s * (s + 1)) > 0.05: print(f"{d} {tag}: WARNING <S^2> = {s2:.3f}, expected {s * (s + 1):.3f} (spin contamination)", flush=True)
                hobj = mf.Hessian()
                want_apt = tag == "b3lyp" and not a.spin and not a.no_apt and not os.path.exists(f"{d}/{APT_FILE}")
                H, mo1 = hessian_with_response(hobj) if want_apt else (hobj.kernel(), None)
                Hc = H.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n); Hc = 0.5 * (Hc + Hc.T)
                Hp = project_tr(Hc, masses, x)
            # frequencies from the projected Hessian by the corpus's own convention: a 3N-long list, imaginary modes negative, six ~0 entries.
            # (pyscf's harmonic_analysis drops a mode when an imaginary one falls in its trans/rot window — 62 instead of 63 entries on A2_3a2982dd85, 23 Sep.)
            fr = freqs_cm(Hp, masses)
            if not a.compare_only:
                np.savez_compressed(f"{d}/hessian_{tag}_analytic.npz", H_raw=Hc, H_projected=Hp, freq_cm=fr, energy=float(e), grid=np.array([rad, ang]),
                                    charge=a.charge, spin=a.spin, reference="UKS" if a.spin else "RKS", software=json.dumps(stamp, sort_keys=True))
                if mo1 is not None:           # after the Hessian is on disk: an APT failure never costs the Hessian
                    try:
                        print(f"{d} b3lyp: {write_apt(d, mf, mo1, Hp, masses, (rad, ang), stamp)}", flush=True)
                    except Exception as exc:  # noqa: BLE001 — reported and turned into exit status 3 after both functionals
                        apt_errors.append(f"{d}: {exc}")
                        print(f"{d} b3lyp: APT FAILED: {exc}", flush=True)
            if not os.path.exists(f"{d}/hessian_{tag}.npz"):
                out[tag] = dict(freq_analytic=vib_only(fr).tolist(), energy=float(e), seconds=round(time.time() - t0), corpus_file="absent", software=stamp)
                print(f"{d} {tag}: {out[tag]['seconds']} s; no corpus psi4 file to compare with; lowest vib {vib_only(fr)[:3].round(1).tolist()} cm-1", flush=True)
                continue
            corpus = np.load(f"{d}/hessian_{tag}.npz")
            fr = vib_only(fr); fc = vib_only(corpus["freq_cm"])     # drop the six trans/rot entries (smallest |value|) from both lists; imaginary modes stay, negative
            out[tag] = dict(freq_analytic=fr.tolist(), freq_corpus=fc.tolist(), dH_max=float(np.abs(Hc - corpus["H_raw"]).max()),
                            dH_rms=float(np.sqrt(np.mean((Hc - corpus["H_raw"]) ** 2))), energy=float(e), energy_corpus=float(corpus["energy"]), seconds=round(time.time() - t0), software=stamp)
            print(f"{d} {tag}: {out[tag]['seconds']} s; |H_analytic − H_corpus| max {out[tag]['dH_max']:.2e} rms {out[tag]['dH_rms']:.2e}; max |Δfreq| {np.abs(fr - fc).max():.0f} cm-1", flush=True)
        json.dump(out, open(d + "/analytic_check.json", "w"), indent=1)
    if apt_errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
