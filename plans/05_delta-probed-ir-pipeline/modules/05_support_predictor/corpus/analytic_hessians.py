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
from constants import AMU2AU
from grid_response_blocked import blocked_grid_response
from library_log import PYSCF_LOG_NAME, pyscf_mole
from vibrations import (
    LABEL_TAGS,
    LOW_MODE_CM,
    STEP_BOHR,
    column,
    displacement,
    low_mode_directions,
    mass_weights,
    patched_hessian,
    rigid_basis,
    signed_cm,
    vibrational_modes,
)

APT_FILE = "dipole_b3lyp_cphf.npz"     # the name the export and module 08 read; route B writes it too
XC_BY_TAG = {"b3lyp": "b3lyp", "wb97x": "wb97x"}        # the label tags' functionals; the tags themselves are vibrations.LABEL_TAGS
FUNCTIONALS = tuple((tag, XC_BY_TAG[tag]) for tag in LABEL_TAGS)
IMAGINARY_BELOW = 0.0                  # cm⁻¹: every negative mode, as pyscf and module 05 count it (TASKS 188; psi4_worker's FD count: −10)
SPIN_CONTAMINATION = 0.05              # |<S²> − S(S+1)| above which a warning is printed
MAX_MEMORY_MB = 20000                  # pyscf's max_memory (its blocking target); a run under a memory cap passes a smaller one
NEWTON_MAX_CYCLE = 50                  # the second-order finish's macro iterations (pyscf's SCF default)
FD_CONV_TOL_GRAD = 1e-8                # a displaced point's DIIS threshold: a gradient error of 1e-8 over 2h = 0.01 bohr is
                                       # 1e-6 hartree/bohr^2, against translation residuals of about 1e-4 (TASKS 201 step 2)


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
    newton_finish: bool = False

    def __post_init__(self) -> None:
        known = tuple(tag for tag, _xc in FUNCTIONALS)
        if not self.functionals or len(set(self.functionals)) != len(self.functionals) or set(self.functionals) - set(known):
            raise ValueError(f"functionals {self.functionals}: one or more of {known}, each once")
        if self.reuse_existing and self.compare_only:
            raise ValueError("--reuse-existing and --compare-only do not combine: --compare-only reads both Hessians already")
        if self.newton_finish and self.compare_only:
            raise ValueError("--newton-finish and --compare-only do not combine: --compare-only runs no SCF")
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
    sm = mass_weights(masses)
    q = rigid_basis(masses, x)
    P = np.eye(3 * n) - q @ q.T
    Hp = P @ (H / np.outer(sm, sm)) @ P
    return Hp * np.outer(sm, sm)


def freqs_cm(Hp, masses):
    """Harmonic frequencies (cm-1, 3N long, imaginary negative) of a Cartesian Hessian in hartree/bohr^2 with masses in amu — the corpus convention."""
    sm = np.sqrt(np.repeat(masses, 3))
    return np.asarray(signed_cm(np.linalg.eigvalsh(Hp / np.outer(sm, sm)) / AMU2AU), float)


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


def labels_ks(mol, xc, grid):
    """The labels route's RKS (UKS when mol.spin > 0) at an unpruned (radial, angular) grid, not yet run."""
    mf = dft.UKS(mol) if mol.spin else dft.RKS(mol)
    mf.xc = xc
    mf.grids.atom_grid = tuple(grid)
    mf.grids.prune = None
    mf.conv_tol = 1e-11
    return mf


def finish_by_newton(mf) -> float:
    """Finish a DIIS SCF that stalled near its threshold with pyscf's second-order solver from its own orbitals, as pyscf's
    examples/scf/22-newton.py does (`newton().kernel(mo_coeff, mo_occ)`), then restart the plain SCF from that density: the Hessian is
    built on the usual RKS/UKS object, and `mf.converged` stays that object's own verdict. HBC's ωB97X (1 Nov 2026) stalled at |g| 1.5e-8
    with the energy still falling 1.3e-10 a cycle against conv_tol 1e-11."""
    second = mf.newton()
    second.max_cycle = NEWTON_MAX_CYCLE                   # its own budget: the stalled run's max_cycle is copied into it
    # and its own threshold: pyscf's SecondOrderSCF.kernel passes self.conv_tol_grad (soscf/newton_ah.py), so the caller's tight value
    # is copied in too, and the solver stalls above it -- T_76dfc434db spent 50 macro iterations at |g| 1.83e-8 against 1e-8 on
    # 14 Nov 2026 and the run failed. None leaves it pyscf's own sqrt(conv_tol) (newton_ah.py:526); the restart below keeps the
    # caller's threshold as the verdict, which is the recipe probes/scf_converge.py follows for the S1/S2 paths.
    second.conv_tol_grad = None
    second.kernel(mf.mo_coeff, mf.mo_occ)
    if not second.converged:
        return mf.e_tot
    return mf.kernel(dm0=second.make_rdm1())


def labels_scf(mol, xc, grid, newton_finish=False, *, conv_tol_grad: float | None = None, dm0: Any = None):
    """The labels route's converged SCF; with newton_finish a stalled DIIS run gets `finish_by_newton`; raises when it does not converge.

    conv_tol_grad and dm0 are the two settings a displaced point of the low-mode repair needs: its gradient must be tighter than a
    label's (FD_CONV_TOL_GRAD), and it starts from the previous point's density. The second-order finish never inherits the tight
    threshold, which is what `finish_by_newton` guards.
    """
    mf = labels_ks(mol, xc, grid)
    if conv_tol_grad is not None:
        mf.conv_tol_grad = conv_tol_grad
    e = mf.kernel(dm0=dm0)
    if not mf.converged and newton_finish:
        print(f"{xc}: DIIS stopped unconverged at E = {e:.12f}; finishing by the second-order solver", flush=True)
        e = finish_by_newton(mf)
    if not mf.converged:
        raise RuntimeError(f"{xc}: SCF not converged")
    return mf, e


def displaced_gradient(geometry: dict, coords: np.ndarray, xc: str, run: LabelsRun, lib_log: TextIO,
                       dm0: Any = None) -> tuple[np.ndarray, Any]:
    """The grid-response gradient at a displaced geometry, and its density for the next point.

    The grid is built at the displaced coordinates, so it moves with the atoms; `blocked_grid_response` is pyscf's response of the
    quadrature weights, evaluated block by block. The charge and spin come from the run, so a cation's point is a cation's.
    """
    mol = labels_mol({**geometry, "coords_bohr": np.asarray(coords, float).tolist()}, lib_log, run.charge, run.spin, run.max_memory_mb)
    mf, _e = labels_scf(mol, xc, run.grid, newton_finish=True, conv_tol_grad=FD_CONV_TOL_GRAD, dm0=dm0)
    with blocked_grid_response():
        gradient = mf.nuc_grad_method().set(grid_response=True).kernel()
    return np.asarray(gradient, float), mf.make_rdm1()


def measured_columns(geometry: dict, directions: np.ndarray, xc: str, run: LabelsRun, lib_log: TextIO) -> np.ndarray:
    """The Hessian's columns along each direction (3N, k), from central differences of grid-response gradients: two points each."""
    masses = np.array(geometry["masses_amu"])
    coords = np.array(geometry["coords_bohr"])
    columns = []
    dm0 = None
    for j in range(directions.shape[1]):
        step, q = displacement(directions[:, j], masses)
        gradients = []
        for sign in (1, -1):
            t0 = time.time()
            gradient, dm0 = displaced_gradient(geometry, coords + sign * step, xc, run, lib_log, dm0)
            gradients.append(gradient)
            print(f"  low-mode point {xc} dir {j} {'plus' if sign > 0 else 'minus'}: {time.time() - t0:.0f} s", flush=True)
        columns.append(column(gradients[0], gradients[1], q, masses))
    return np.column_stack(columns)


def repair_low_modes(geometry: dict, hessians: dict[str, np.ndarray], run: LabelsRun, lib_log: TextIO,
                     below_cm: float = LOW_MODE_CM) -> tuple[dict[str, np.ndarray], dict]:
    """The label Hessians with their soft modes recomputed from grid-response curvature, and the record of what was done.

    pyscf's CPU DFT Hessian leaves out the derivative of the quadrature weights, which moves a mode below LOW_MODE_CM by up to 6
    cm-1 and one above it by less than 0.5 (TASKS 201 step 2). The directions are the modes below the threshold in either label,
    merged, so both functionals are repaired along the same ones. Returns ({}, {}) when the molecule has no soft mode.

    below_cm is the registered threshold; only a test passes another, to make a stiff mode 'low' and exercise the measurement on a
    molecule where the analytic Hessian is already right.
    """
    masses = np.array(geometry["masses_amu"])
    coords = np.array(geometry["coords_bohr"])
    modes = {tag: vibrational_modes(hessians[tag], masses, coords) for tag in sorted(hessians)}
    U = low_mode_directions([modes[tag] for tag in sorted(modes)], below_cm)
    if U.shape[1] == 0:
        return {}, {}
    repaired, record = {}, {"below_cm": below_cm, "directions": int(U.shape[1]), "step_bohr": STEP_BOHR, "per_functional": {}}
    for tag in sorted(hessians):
        C = measured_columns(geometry, U, XC_BY_TAG[tag], run, lib_log)
        repaired[tag] = patched_hessian(hessians[tag], masses, U, C)
        before = modes[tag].omega_cm
        after = vibrational_modes(repaired[tag], masses, coords).omega_cm
        record["per_functional"][tag] = {"lowest_label_cm": float(min(before)), "lowest_repaired_cm": float(min(after)),
                                         "max_change_cm": float(np.abs(np.sort(after) - np.sort(before)).max())}
        print(f"  low-mode repair {tag}: lowest {min(before):.2f} -> {min(after):.2f} cm-1 along {U.shape[1]} direction(s)", flush=True)
    return repaired, record


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
        mf, e = labels_scf(mol, xc, run.grid, newton_finish=run.newton_finish)
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


def save_hessian(d: str, tag: str, Hc: np.ndarray, Hp: np.ndarray, fr: np.ndarray, e: float,  # noqa: PLR0913  (one record's fields)
                 run: LabelsRun, *, unrepaired: np.ndarray | None = None, repair: dict | None = None, pending: bool = False) -> None:
    """hessian_<tag>_analytic.npz (one record's fields).

    `unrepaired` and `repair` are given once the low-mode repair has run: the label is then the repaired Hessian, the analytic one
    stays beside it as `H_raw_unrepaired`, and `low_mode_patch` records the threshold, the step and what moved — the same key
    `probes/low_mode_swap.py` writes, so a reader cannot tell the two sources apart and an auditor can. `pending` marks the file
    written before the repair: the Hessian reaches the disk ahead of the APT, as it always has, but such a file is not a finished
    label and `--reuse-existing` refuses it.
    """
    fields = dict(H_raw=Hc, H_projected=Hp, freq_cm=fr, energy=float(e), grid=np.array(run.grid), charge=run.charge, spin=run.spin,
                  reference="UKS" if run.spin else "RKS", software=json.dumps(run.stamp, sort_keys=True))
    if unrepaired is not None:
        fields["H_raw_unrepaired"] = unrepaired
        fields["low_mode_patch"] = json.dumps({"route": "analytic_hessians.repair_low_modes", **(repair or {})}, sort_keys=True)
    if pending:
        fields["low_mode_pending"] = True
    np.savez_compressed(f"{d}/hessian_{tag}_analytic.npz", **fields)


def check_entry(d: str, tag: str, Hc: np.ndarray, fr: np.ndarray, e: float, seconds: float, stamp: dict) -> dict:  # noqa: PLR0913
    """analytic_check.json's entry for one functional: against the corpus psi4 Hessian when the folder has one, else the analytic numbers alone."""
    if not os.path.exists(f"{d}/hessian_{tag}.npz"):
        entry = dict(freq_analytic=vib_only(fr).tolist(), energy=float(e), seconds=round(seconds), corpus_file="absent", software=stamp)
        print(f"{d} {tag}: {entry['seconds']} s; no corpus psi4 file to compare with; lowest vib {vib_only(fr)[:3].round(1).tolist()} cm-1",
              flush=True)
        return entry
    corpus = np.load(f"{d}/hessian_{tag}.npz")
    fa, fc = vib_only(fr), vib_only(corpus["freq_cm"])     # the six trans/rot entries (smallest |value|) dropped; imaginary modes stay, negative
    entry = dict(freq_analytic=fa.tolist(), freq_corpus=fc.tolist(), dH_max=float(np.abs(Hc - corpus["H_raw"]).max()),
                 dH_rms=float(np.sqrt(np.mean((Hc - corpus["H_raw"]) ** 2))), energy=float(e), energy_corpus=float(corpus["energy"]),
                 seconds=round(seconds), software=stamp)
    print(f"{d} {tag}: {entry['seconds']} s; |H_analytic − H_corpus| max {entry['dH_max']:.2e} rms {entry['dH_rms']:.2e}; "
          f"max |Δfreq| {np.abs(fa - fc).max():.0f} cm-1", flush=True)
    return entry


def refresh_apt_summary(d: str, Hp: np.ndarray, masses: np.ndarray) -> bool:
    """Recompute the APT file's frequency and intensity summary from the Hessian the folder ends up with; False when there is no file.

    `write_apt` has to run while the Hessian object is alive, so its summary is made with the analytic Hessian. When the low-mode
    repair then moves the soft modes, the stored polar tensors stay valid — they are Cartesian — but the summary does not, and one
    file should not carry two Hessians' worth of numbers.
    """
    path = f"{d}/{APT_FILE}"
    if not os.path.exists(path):
        return False
    with np.load(path, allow_pickle=False) as z:
        fields = {k: z[k] for k in z.files}
    fields["freq_cm"], fields["intensity_km_mol"] = intensities(fields["apt"], Hp, masses)
    np.savez_compressed(path, **fields)
    return True


def analytic_label(d: str, mol: Any, tag: str, xc: str, run: LabelsRun,  # noqa: PLR0913  (one functional's whole context)
                   geometry: dict, apt_errors: list[str]) -> tuple[np.ndarray, float, float, bool]:
    """One functional's analytic Hessian, its energy, its seconds, and whether the file it came from already carries a repair.

    It reaches the disk here, awaiting the repair.

    The APT is written here as well, because it needs the Hessian object alive. The finished label is written in `write_labels`,
    once the repair has had its say.
    """
    t0 = time.time()
    saved = f"{d}/hessian_{tag}_analytic.npz"
    if run.compare_only or (run.reuse_existing and os.path.exists(saved)):
        with np.load(saved, allow_pickle=False) as z:
            if "low_mode_pending" in z.files:
                raise RuntimeError(f"{d} {tag}: {os.path.basename(saved)} was written before its low-mode repair; delete it and rerun")
            Hc, e = np.asarray(z["H_raw"], float), float(z["energy"])
            repaired_already = "low_mode_patch" in z.files
        if not run.compare_only:
            print(f"{d} {tag}: analytic Hessian reused from {os.path.basename(saved)}"
                  f"{' (it carries a low-mode repair)' if repaired_already else ''}", flush=True)
        return Hc, e, time.time() - t0, repaired_already
    masses, x = np.array(geometry["masses_amu"]), np.array(geometry["coords_bohr"])
    Hc, e, hobj, response = compute_hessian(d, mol, tag, xc, run)
    Hp = project_tr(Hc, masses, x)
    save_hessian(d, tag, Hc, Hp, freqs_cm(Hp, masses), e, run, pending=True)   # on disk before the APT, as it has always been
    if response is not None:
        try:
            print(f"{d} b3lyp: {write_apt(d, hobj, response, Hp, masses, run.grid, run.stamp)}", flush=True)
        except Exception as exc:  # noqa: BLE001, RUF100 — reported, exit status 3 after both functionals (BLE001 is pre-commit's rule)
            apt_errors.append(f"{d}: {exc}")
            print(f"{d} b3lyp: APT FAILED: {exc}", flush=True)
    return Hc, e, time.time() - t0, False


def write_labels(d: str, run: LabelsRun, labels: dict[str, tuple[np.ndarray, float, float, bool]],
                 repaired: dict[str, np.ndarray], repair: dict, geometry: dict) -> tuple[dict, dict]:
    """The finished label files, and (analytic_check.json's entries, the imaginary count per functional)."""
    masses, x = np.array(geometry["masses_amu"]), np.array(geometry["coords_bohr"])
    out, imaginary = {}, {}
    for tag, (Hc, e, seconds, _repaired_already) in labels.items():
        final = repaired.get(tag, Hc)
        Hp = project_tr(final, masses, x)
        # frequencies from the projected Hessian by the corpus's own convention: a 3N-long list, imaginary modes negative, six ~0 entries.
        # (pyscf's harmonic_analysis drops a mode when an imaginary one falls in its trans/rot window — 62 instead of 63 entries on A2_3a2982dd85.)
        fr = freqs_cm(Hp, masses)
        imaginary[tag] = int((vib_only(fr) < IMAGINARY_BELOW).sum())
        if not run.compare_only:
            save_hessian(d, tag, final, Hp, fr, e, run,
                         unrepaired=Hc if tag in repaired else None, repair=repair if tag in repaired else None)
            if tag in repaired and refresh_apt_summary(d, Hp, masses):
                print(f"{d} {tag}: the APT's frequency summary refreshed on the repaired Hessian", flush=True)
        out[tag] = check_entry(d, tag, final, fr, e, seconds, run.stamp)
    return out, imaginary


def process_molecule(d: str, run: LabelsRun, lib_log: TextIO) -> list[str]:
    """The run's functionals on one molecule folder; returns its APT errors (the Hessians are written whatever the APT does).

    Three phases, because the repair's directions are the soft modes of *both* labels: the Hessians, then the repair, then the
    files (TASKS 216, `Design_2026-11-14_Low_Mode_Repair_In_The_Label_Route.md`).
    """
    with open(d + "/geometry.json", encoding="utf-8") as fh:
        g = json.load(fh)
    mol = labels_mol(g, lib_log, run.charge, run.spin, run.max_memory_mb)
    apt_errors: list[str] = []
    labels = {tag: analytic_label(d, mol, tag, xc, run, g, apt_errors)
              for tag, xc in (f for f in FUNCTIONALS if f[0] in run.functionals)}
    already = {tag for tag, label in labels.items() if label[3]}
    if already and already != set(labels):
        raise RuntimeError(f"{d}: {sorted(already)} carry a low-mode repair and {sorted(set(labels) - already)} do not; "
                           "the folder is half repaired, which no reader can tell apart from a whole one")
    repaired, repair = (({}, {}) if run.compare_only or already
                        else repair_low_modes(g, {t: v[0] for t, v in labels.items()}, run, lib_log))
    out, imaginary = write_labels(d, run, labels, repaired, repair, g)
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
    ap.add_argument("--newton-finish", action="store_true",
                    help="finish a DIIS SCF that stalls unconverged by the second-order solver, same thresholds (1 Nov 2026, HBC)")
    return ap.parse_args()


def main():
    a = parse_args()
    rad, ang = (int(v) for v in a.grid.split(","))
    run = LabelsRun(grid=(rad, ang), charge=a.charge, spin=a.spin, compare_only=a.compare_only, apt=not a.no_apt, stamp=software(),
                    max_memory_mb=a.max_memory, reuse_existing=a.reuse_existing, functionals=tuple(a.functionals.split(",")),
                    newton_finish=a.newton_finish)
    lib.num_threads(a.threads)
    apt_errors = []
    for d in a.dirs:
        with open(os.path.join(d, PYSCF_LOG_NAME), "a", encoding="utf-8") as lib_log:
            apt_errors += process_molecule(d, run, lib_log)
    if apt_errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
