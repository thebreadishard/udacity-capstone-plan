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
       Residual-checked response (12 Oct 2026, TASKS 44 (a)): pyscf's Krylov CPHF stops early for DFT (pyscf #2702), which the Hessian does not
       feel and the APT does; the APT is contracted from the response after `refine_response` (apt.py), route "hessian_response_refined", and the
       file carries cphf_residual_before/after, cphf_refine_rounds and cphf_fallback_columns (13 Oct 2026: columns still above the bound after
       the batched rounds, solved one by one). A residual above apt.CPHF_BOUND fails the APT as a sum rule does.
       The Hessian keeps pyscf's own response.
       Provenance (11 Oct 2026, TASKS 47): every file written carries `software` — the pyscf, numpy and Python versions, pyscf's source
       commit when it is imported from a git checkout, and the sha256 of this script and apt.py — as a JSON string in the npz files and as a
       field inside each functional's entry of analytic_check.json (its readers iterate the entries).
       Analytic-only folders (12 Oct 2026, chain 42, TASKS 49): a folder whose result.json says labels "analytic_only" (psi4_worker with
       "hessians": false) gets n_imaginary_b3lyp/wb97x written into that result.json from these frequencies (below −10 cm⁻¹, psi4_worker's own
       count), because the trainer's loader reads its imaginary flag there.
       pyscf's own log (19 Oct 2026, `probes/library_log.py`): every SCF cycle and the Hessian's step timers are appended to <molecule dir>/pyscf.log,
       so an hours-long Hessian shows whether it computes. `library_log.py` is found next to this script (a server copy) or in the plan's probes/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any, TextIO

import numpy as np
import pyscf
from apt import (
    CPHF_BOUND,
    SUM_RULE_LIMIT,
    apt_from_mo1,
    hessian_with_response,
    intensities,
    refine_response,
    solve_response,
    sum_rule,
)
from pyscf import dft, lib

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "probes"))
from library_log import PYSCF_LOG_NAME, pyscf_mole

AMU2AU = 1822.888486209
AU2CM = 219474.6313705
APT_FILE = "dipole_b3lyp_cphf.npz"     # the name the export and module 08 read; route B writes it too
FUNCTIONALS = (("b3lyp", "b3lyp"), ("wb97x", "wb97x"))
IMAGINARY_BELOW = -10.0                # cm⁻¹, psi4_worker's own count
SPIN_CONTAMINATION = 0.05              # |<S²> − S(S+1)| above which a warning is printed
MAX_MEMORY_MB = 20000                  # pyscf's max_memory (its blocking target); a run under a memory cap passes a smaller one


@dataclass(frozen=True)
class LabelsRun:
    """One call's settings, checked before any molecule is read."""
    grid: tuple[int, int]
    charge: int
    spin: int
    compare_only: bool
    apt: bool
    stamp: dict
    max_memory_mb: int = MAX_MEMORY_MB
    reuse_existing: bool = False
    functionals: tuple[str, ...] = tuple(tag for tag, _xc in FUNCTIONALS)

    def __post_init__(self) -> None:
        known = tuple(tag for tag, _xc in FUNCTIONALS)
        if not self.functionals or len(set(self.functionals)) != len(self.functionals) or set(self.functionals) - set(known):
            raise ValueError(f"functionals {self.functionals}: one or more of {known}, each once")
        if self.reuse_existing and self.compare_only:
            raise ValueError("--reuse-existing and --compare-only do not combine: --compare-only reads both Hessians already")
        if len(self.grid) != 2 or min(self.grid) < 1:
            raise ValueError(f"grid {self.grid} is not two positive integers (radial, angular)")
        if self.spin < 0:
            raise ValueError(f"spin (2S) {self.spin} is negative")
        if self.max_memory_mb < 1:
            raise ValueError(f"max_memory {self.max_memory_mb} MB is not positive")


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
    sha = {}
    for f in ("analytic_hessians.py", "apt.py"):
        with open(os.path.join(here, f), "rb") as fh:
            sha[f] = hashlib.sha256(fh.read()).hexdigest()[:12]
    return {"pyscf": pyscf.__version__, "pyscf_git": git, "numpy": np.__version__, "python": platform.python_version(), "sha256": sha}


def project_tr(H, masses, x):
    """Project translations and rotations out of a Cartesian Hessian (mass-weighted projector, then back), as psi4 does for H_projected."""
    n = len(masses)
    sm = np.sqrt(np.repeat(masses * AMU2AU, 3))
    r = x - (x * masses[:, None]).sum(0) / masses.sum()
    D = []
    for k in range(3):
        v = np.zeros((n, 3))
        v[:, k] = 1.0
        D.append((v * np.sqrt(masses)[:, None]).ravel())
    for k in range(3):
        e = np.zeros(3)
        e[k] = 1.0
        v = np.cross(np.tile(e, (n, 1)), r)
        D.append((v * np.sqrt(masses)[:, None]).ravel())
    q, _ = np.linalg.qr(np.array(D).T)
    P = np.eye(3 * n) - q @ q.T
    Hp = P @ (H / np.outer(sm, sm)) @ P
    return Hp * np.outer(sm, sm)


def freqs_cm(Hp, masses):
    """Harmonic frequencies (cm-1, 3N long, imaginary negative) of a Cartesian Hessian in hartree/bohr^2 with masses in amu — the corpus convention."""
    sm = np.sqrt(np.repeat(masses, 3))
    w = np.linalg.eigvalsh(Hp / np.outer(sm, sm))
    f = np.sqrt(np.abs(w) / AMU2AU) * AU2CM
    return np.where(w < 0, -f, f)


def vib_only(f):
    """The 3N-6 vibrational entries of a 3N-long frequency list: drop the six entries closest to zero, keep imaginary modes as negative numbers, sorted."""
    f = np.asarray(f, dtype=float)
    keep = np.argsort(np.abs(f))[6:]
    return np.sort(f[keep])


def mark_imaginary(d, counts):
    """n_imaginary_<tag> into an analytic-only folder's result.json (atomic replace); other folders keep the psi4 worker's own counts."""
    path = os.path.join(d, "result.json")
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as fh:
        r = json.load(fh)
    if r.get("labels") != "analytic_only":
        return False
    r.update({f"n_imaginary_{tag}": int(n) for tag, n in counts.items()})
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1)
    os.replace(path + ".tmp", path)
    return True


def labels_mol(geometry, log_stream: TextIO, charge=0, spin=0, max_memory=MAX_MEMORY_MB):
    """The labels route's molecule from a geometry.json dict: 6-31G* with Cartesian d (as psi4), no symmetry. pyscf's own log (every SCF
    cycle, the Hessian's step timers) goes to log_stream (`probes/library_log.py`)."""
    atoms = [(s.capitalize(), tuple(c)) for s, c in zip(geometry["symbols"], geometry["coords_bohr"], strict=True)]
    return pyscf_mole(log_stream, atom=atoms, unit="Bohr", basis="6-31g*", cart=True, symmetry=False, max_memory=max_memory, charge=charge,
                      spin=spin)


def labels_scf(mol, xc, grid):
    """The labels route's converged SCF (RKS, or UKS when mol.spin > 0) at an unpruned (radial, angular) grid; raises when it does not converge."""
    mf = dft.UKS(mol) if mol.spin else dft.RKS(mol)
    mf.xc = xc
    mf.grids.atom_grid = tuple(grid)
    mf.grids.prune = None
    mf.conv_tol = 1e-11
    e = mf.kernel()
    if not mf.converged:
        raise RuntimeError(f"{xc}: SCF not converged")
    return mf, e


def write_apt(d, hobj, response, Hp, masses, grid, stamp):  # noqa: PLR0913  (the APT record's inputs; called from one place)
    """The APT from the Hessian's own response after `refine_response`, its sum rule and band heights, written as route B writes them (the file
    carries the summary; analytic_check.json keeps one entry per functional, as its readers expect). Raises ValueError when the sum rule or the
    response's residual fails (the file is written all the same, marked passed=False)."""
    t0 = time.time()
    mf = hobj.base
    mo1, info = refine_response(hobj, response.mo1, response.h1ao, bound=CPHF_BOUND)
    P = apt_from_mo1(mf, mo1)
    sr = sum_rule(P, mf.mol.charge)
    freq, km = intensities(P, Hp, masses)
    fails = [f"APT sum rule {sr:.1e} > {SUM_RULE_LIMIT:g}"] if sr > SUM_RULE_LIMIT else []
    if info["residual_after"] > CPHF_BOUND:
        fails.append(f"CPHF residual {info['residual_after']:.1e} > {CPHF_BOUND:g} after {info['rounds']} rounds and "
                     f"{info.get('columns_fallback', 0)} single-column solves")
    np.savez_compressed(f"{d}/{APT_FILE}", apt=P, sum_rule_max=sr, fd_max_diff=float("nan"), freq_cm=freq, intensity_km_mol=km, xc="b3lyp",
                        basis="6-31g*", grid=np.array(grid), passed=not fails, route="hessian_response_refined",
                        cphf_residual_before=info["residual_before"], cphf_residual_after=info["residual_after"],
                        cphf_refine_rounds=info["rounds"], cphf_fallback_columns=info.get("columns_fallback", 0),
                        seconds=round(time.time() - t0, 3), software=json.dumps(stamp, sort_keys=True))
    if fails:
        raise ValueError("; ".join(fails))
    return (f"APT from the Hessian's response: CPHF residual {info['residual_before']:.1e} -> {info['residual_after']:.1e} in {info['rounds']} "
            f"rounds, sum rule {sr:.1e}, {time.time() - t0:.1f} s")


def warn_spin_contamination(d: str, tag: str, mf: Any, spin: int) -> None:
    """Print a warning when an open-shell SCF's <S²> is off its pure-spin value."""
    s2 = float(mf.spin_square()[0])
    s = spin / 2
    if abs(s2 - s * (s + 1)) > SPIN_CONTAMINATION:
        print(f"{d} {tag}: WARNING <S^2> = {s2:.3f}, expected {s * (s + 1):.3f} (spin contamination)", flush=True)


def compute_hessian(d: str, mol: Any, tag: str, xc: str, run: LabelsRun) -> tuple[np.ndarray, float, Any, Any]:
    """One functional's analytic Hessian (3N × 3N, symmetrised) with its energy, Hessian object and CPHF response (None without an APT)."""
    try:
        mf, e = labels_scf(mol, xc, run.grid)
    except RuntimeError as exc:
        raise RuntimeError(f"{d} {tag}: SCF not converged") from exc
    if run.spin:
        warn_spin_contamination(d, tag, mf, run.spin)
    hobj = mf.Hessian()
    want_apt = tag == "b3lyp" and run.apt and not run.spin and not os.path.exists(f"{d}/{APT_FILE}")
    response = solve_response(hobj) if want_apt else None
    H = hessian_with_response(hobj, response)[0] if want_apt else hobj.kernel()
    n = mol.natm
    Hc = H.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
    return 0.5 * (Hc + Hc.T), e, hobj, response


def save_hessian(d: str, tag: str, Hc: np.ndarray, Hp: np.ndarray, fr: np.ndarray, e: float, run: LabelsRun) -> None:  # noqa: PLR0913
    """hessian_<tag>_analytic.npz (one record's fields)."""
    np.savez_compressed(f"{d}/hessian_{tag}_analytic.npz", H_raw=Hc, H_projected=Hp, freq_cm=fr, energy=float(e), grid=np.array(run.grid),
                        charge=run.charge, spin=run.spin, reference="UKS" if run.spin else "RKS", software=json.dumps(run.stamp, sort_keys=True))


def check_entry(d: str, tag: str, Hc: np.ndarray, fr: np.ndarray, e: float, t0: float, stamp: dict) -> dict:  # noqa: PLR0913
    """analytic_check.json's entry for one functional: against the corpus psi4 Hessian when the folder has one, else the analytic numbers alone."""
    if not os.path.exists(f"{d}/hessian_{tag}.npz"):
        entry = dict(freq_analytic=vib_only(fr).tolist(), energy=float(e), seconds=round(time.time() - t0), corpus_file="absent", software=stamp)
        print(f"{d} {tag}: {entry['seconds']} s; no corpus psi4 file to compare with; lowest vib {vib_only(fr)[:3].round(1).tolist()} cm-1",
              flush=True)
        return entry
    corpus = np.load(f"{d}/hessian_{tag}.npz")
    fa, fc = vib_only(fr), vib_only(corpus["freq_cm"])     # the six trans/rot entries (smallest |value|) dropped; imaginary modes stay, negative
    entry = dict(freq_analytic=fa.tolist(), freq_corpus=fc.tolist(), dH_max=float(np.abs(Hc - corpus["H_raw"]).max()),
                 dH_rms=float(np.sqrt(np.mean((Hc - corpus["H_raw"]) ** 2))), energy=float(e), energy_corpus=float(corpus["energy"]),
                 seconds=round(time.time() - t0), software=stamp)
    print(f"{d} {tag}: {entry['seconds']} s; |H_analytic − H_corpus| max {entry['dH_max']:.2e} rms {entry['dH_rms']:.2e}; "
          f"max |Δfreq| {np.abs(fa - fc).max():.0f} cm-1", flush=True)
    return entry


def process_molecule(d: str, run: LabelsRun, lib_log: TextIO) -> list[str]:
    """The run's functionals on one molecule folder; returns its APT errors (the Hessians are written whatever the APT does)."""
    with open(d + "/geometry.json", encoding="utf-8") as fh:
        g = json.load(fh)
    x, masses = np.array(g["coords_bohr"]), np.array(g["masses_amu"])
    mol = labels_mol(g, lib_log, run.charge, run.spin, run.max_memory_mb)
    out, imaginary, apt_errors = {}, {}, []
    for tag, xc in (f for f in FUNCTIONALS if f[0] in run.functionals):
        t0 = time.time()
        saved = f"{d}/hessian_{tag}_analytic.npz"
        load = run.compare_only or (run.reuse_existing and os.path.exists(saved))
        if load:
            z = np.load(saved)
            Hc, Hp, e, response = z["H_raw"], z["H_projected"], float(z["energy"]), None
            if not run.compare_only:
                print(f"{d} {tag}: analytic Hessian reused from {os.path.basename(saved)}", flush=True)
        else:
            Hc, e, hobj, response = compute_hessian(d, mol, tag, xc, run)
            Hp = project_tr(Hc, masses, x)
        # frequencies from the projected Hessian by the corpus's own convention: a 3N-long list, imaginary modes negative, six ~0 entries.
        # (pyscf's harmonic_analysis drops a mode when an imaginary one falls in its trans/rot window — 62 instead of 63 entries on A2_3a2982dd85.)
        fr = freqs_cm(Hp, masses)
        imaginary[tag] = int((vib_only(fr) < IMAGINARY_BELOW).sum())
        if not load:
            save_hessian(d, tag, Hc, Hp, fr, e, run)
        if response is not None:                  # after the Hessian is on disk: an APT failure never costs the Hessian
            try:
                print(f"{d} b3lyp: {write_apt(d, hobj, response, Hp, masses, run.grid, run.stamp)}", flush=True)
            except Exception as exc:  # noqa: BLE001, RUF100 — reported, exit status 3 after both functionals (BLE001 is pre-commit's rule)
                apt_errors.append(f"{d}: {exc}")
                print(f"{d} b3lyp: APT FAILED: {exc}", flush=True)
        out[tag] = check_entry(d, tag, Hc, fr, e, t0, run.stamp)
    with open(d + "/analytic_check.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    if not run.compare_only and mark_imaginary(d, imaginary):
        print(f"{d}: analytic-only folder, imaginary modes {imaginary} written to result.json", flush=True)
    return apt_errors


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--grid", default="99,590")
    ap.add_argument("--compare-only", action="store_true", help="rebuild analytic_check.json from the saved *_analytic.npz files (no DFT)")
    ap.add_argument("--charge", type=int, default=0)
    ap.add_argument("--spin", type=int, default=0, help="2S; > 0 selects UKS (the E8 open-shell path uses the same convention)")
    ap.add_argument("--max-memory", type=int, default=MAX_MEMORY_MB, help="pyscf's max_memory in MB (19 Oct 2026: below a run's memory cap)")
    ap.add_argument("--reuse-existing", action="store_true",
                    help="read a functional's saved hessian_<tag>_analytic.npz instead of recomputing it (19 Oct 2026: a retry after a stop)")
    ap.add_argument("--no-apt", action="store_true",
                    help="skip the B3LYP APT from the Hessian's response (closed shell only; on by default since 11 Oct 2026)")
    ap.add_argument("--functionals", default=",".join(tag for tag, _xc in FUNCTIONALS),
                    help="comma-separated, of b3lyp and wb97x (29 Oct 2026, the pipeline: a new molecule needs the low level alone)")
    return ap.parse_args()


def main():
    a = parse_args()
    rad, ang = (int(v) for v in a.grid.split(","))
    run = LabelsRun(grid=(rad, ang), charge=a.charge, spin=a.spin, compare_only=a.compare_only, apt=not a.no_apt, stamp=software(),
                    max_memory_mb=a.max_memory, reuse_existing=a.reuse_existing, functionals=tuple(a.functionals.split(",")))
    lib.num_threads(a.threads)
    apt_errors = []
    for d in a.dirs:
        with open(os.path.join(d, PYSCF_LOG_NAME), "a", encoding="utf-8") as lib_log:
            apt_errors += process_molecule(d, run, lib_log)
    if apt_errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
