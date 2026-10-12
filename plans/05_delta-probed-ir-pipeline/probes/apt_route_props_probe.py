"""TASKS 44, third route (11 Oct 2026): pyscf-properties' infrared module against our band heights, closed and open shell.

Registration (lines L1–L5, written before the runs): `probes/results_m1/apt_route_props_2026-10-11/REGISTRATION.md`. Per molecule, at the labels
route's settings (`corpus/analytic_hessians.py`: B3LYP/6-31G* Cartesian, grid unpruned, conv_tol 1e-11; RKS, or UKS for 2S > 0):
  - upstream `infrared.rks/uks.Infrared(mf)`: `kernel_dipderiv` (the Hessian and the APT from its response, upstream's `proc_hessian_`), then
    `kernel_ir` on normal modes from `hessian.thermo.harmonic_analysis` with the corpus's masses (upstream's default is isotope averages);
  - L1 the APT against route B's saved file, L2 the Hessian against the saved analytic one, L3 upstream's heights against
    `corpus/apt.intensities` on the same APT, Hessian and masses, L4 the translation sum rule, L5 the APT against finite differences.
Nothing is written into the molecule folders; one JSON per run goes to --out.
An FD file with two steps (dipole_derivs_fd.py without --no-half-step) adds the Richardson reading of
`probes/results_m1/uks_apt_margin_2026-10-11/REGISTRATION.md` (M3): the gap at h, at h/2 and to P* = (4 P(h/2) − P(h)) / 3.

    python probes/apt_route_props_probe.py <dir with geometry.json> [more dirs] --out <file.json> [--threads 4] [--grid 99,590]
                                           [--charge 1 --spin 1] [--fd <FD npz, one dir only>]
"""
import argparse
import json
import os
import resource
import sys
import time

import numpy as np
from pyscf import dft, gto, lib
from pyscf.hessian import thermo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus"))
from analytic_hessians import project_tr  # noqa: E402  (the labels route's own projector)
from apt import intensities, sum_rule  # noqa: E402
from upstream_infrared import load  # noqa: E402

LIMITS = {"vs_route_b": 1e-4, "hessian": 1e-5, "freq": 0.1, "height_rel": 1e-3, "sum_rule": 5e-4, "vs_fd": 1e-3}   # REGISTRATION.md L1–L5
HEIGHT_FLOOR = 1.0       # km/mol: L3 compares the groups at least this strong
DEGENERATE = 1.0         # cm⁻¹: modes this close form one group (their split of the intensity is arbitrary)


def maxdiff(a, b):
    return float(np.abs(np.asarray(a) - np.asarray(b)).max())


def apt_from_upstream(de):
    """Upstream's dipole derivative de[A, x, t] = ∂μ_t/∂R_{A,x} as our P[t, 3A + x]."""
    de = np.asarray(de)
    return de.transpose(2, 0, 1).reshape(3, -1)


def band_groups(freq, km, tol=DEGENERATE):
    """(mean frequency, summed intensity) per group of modes whose sorted frequencies lie within `tol` of the previous one."""
    order = np.argsort(freq)
    f, k = np.asarray(freq)[order], np.asarray(km)[order]
    groups, start = [], 0
    for i in range(1, len(f) + 1):
        if i == len(f) or f[i] - f[i - 1] > tol:
            groups.append((float(f[start:i].mean()), float(k[start:i].sum())))
            start = i
    return groups


def compare_heights(freq_a, km_a, freq_b, km_b):
    """L3: max frequency difference over sorted modes, and max relative intensity difference over groups of ≥ HEIGHT_FLOOR km/mol."""
    fa, fb = np.sort(freq_a), np.sort(freq_b)
    if fa.shape != fb.shape:
        raise ValueError(f"mode counts differ: {fa.size} vs {fb.size}")
    ga, gb = band_groups(freq_a, km_a), band_groups(freq_b, km_b)
    if len(ga) != len(gb):
        raise ValueError(f"degenerate groups differ: {len(ga)} vs {len(gb)}")
    rel = [abs(a[1] - b[1]) / max(a[1], b[1]) for a, b in zip(ga, gb, strict=True) if max(a[1], b[1]) >= HEIGHT_FLOOR]
    return maxdiff(fa, fb), max(rel) if rel else 0.0


def richardson(P, P_h, P_h2):
    """M3 of the margin registration: max |P − P_FD| at h, at h/2, and against P* = (4 P(h/2) − P(h)) / 3, plus |P(h) − P(h/2)|."""
    star = (4.0 * np.asarray(P_h2) - np.asarray(P_h)) / 3.0
    return {"g_h": maxdiff(P, P_h), "g_h2": maxdiff(P, P_h2), "g_richardson": maxdiff(P, star), "fd_pair": maxdiff(P_h, P_h2)}


def upstream_heights(ir, H, masses):
    """Upstream's `kernel_ir` on normal modes of H with the corpus's masses: (frequencies, heights). Imaginary modes as negative numbers."""
    ir.vib_dict = thermo.harmonic_analysis(ir.mol, H, mass=np.asarray(masses, float))   # upstream reads vib_dict when it is set (rhf.kernel_ir)
    ir.kernel_ir()
    freq = np.asarray(ir.vib_dict["freq_wavenumber"])
    if np.iscomplexobj(freq):
        freq = np.where(np.abs(freq.imag) > 1e-10, -np.abs(freq.imag), freq.real)
    return freq, np.asarray(ir.ir_inten)


def upstream_route(mf, masses, infrared):
    """Run upstream's module on a converged RKS/UKS: (P[3, 3N], Hessian (natm, natm, 3, 3), frequencies, heights, seconds, the heights on
    the symmetrised Hessian). `harmonic_analysis` passes the Hessian to `numpy.linalg.eigh`, which reads one triangle; the labels route
    symmetrises first (analytic_hessians.py), so the second set of heights shows how much of an L3 difference the asymmetry carries."""
    ir = (infrared.uks if mf.mol.spin else infrared.rks).Infrared(mf)
    t0 = time.time()
    ir.kernel_dipderiv()
    t1 = time.time()
    H = ir.mf_hess.de
    sym = upstream_heights(ir, 0.5 * (H + H.transpose(1, 0, 3, 2)), masses)
    freq, km = upstream_heights(ir, H, masses)                                        # upstream as it runs: the registered L3
    return apt_from_upstream(ir.de), H, freq, km, t1 - t0, sym


def probe(d, grid, charge, spin, fd_file, infrared, log=print, save_apt=None):
    g = json.load(open(os.path.join(d, "geometry.json")))
    x = np.asarray(g["coords_bohr"], float)
    masses = np.asarray(g["masses_amu"], float)
    n = len(x)
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], x, strict=True)], unit="Bohr", basis="6-31g*", cart=True,
                symmetry=False, verbose=0, max_memory=4000, charge=charge, spin=spin)
    t0 = time.time()
    mf = dft.UKS(mol) if spin else dft.RKS(mol)
    mf.xc = "b3lyp"
    mf.grids.atom_grid = grid
    mf.grids.prune = None
    mf.conv_tol = 1e-11
    mf.kernel()
    if not mf.converged:
        raise RuntimeError(f"{d}: SCF not converged")
    scf_s = time.time() - t0
    r = {"dir": d, "atoms": n, "charge": charge, "spin": spin, "reference": "UKS" if spin else "RKS"}
    if spin:
        r["s2"] = round(float(mf.spin_square()[0]), 4)
    P, H, freq_up, km_up, hess_s, (freq_sym, km_sym) = upstream_route(mf, masses, infrared)
    Hc = H.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
    r_asym = float(np.abs(Hc - Hc.T).max())
    if save_apt:
        np.savez_compressed(save_apt, apt=P, charge=charge, spin=spin, grid=np.array(grid))
    Hc = 0.5 * (Hc + Hc.T)
    freq, km = intensities(P, project_tr(Hc, masses, x), masses)
    r["seconds"] = {"scf": round(scf_s, 1), "upstream_hessian_and_apt": round(hess_s, 1)}
    r["sum_rule"] = sum_rule(P, charge)
    r["freq_maxdiff"], r["height_maxrel"] = compare_heights(freq_up, km_up, freq, km)
    r["diagnostic"] = {"hessian_asymmetry_max": r_asym,                                     # not a registered line (L3 diagnosis, 11 Oct)
                       "symmetrised": dict(zip(("freq_maxdiff", "height_maxrel"), compare_heights(freq_sym, km_sym, freq, km), strict=True))}
    saved = {k: os.path.join(d, f) for k, f in (("b", "dipole_b3lyp_cphf.npz"), ("fd", "dipole_b3lyp_fd.npz"), ("h", "hessian_b3lyp_analytic.npz"))}
    if fd_file:
        saved["fd"] = fd_file
    if os.path.exists(saved["b"]):
        r["vs_route_b"] = maxdiff(P, np.load(saved["b"])["apt"])
    if os.path.exists(saved["fd"]):
        zf = np.load(saved["fd"])
        r["vs_fd"] = maxdiff(P, zf["apt"])
        r["fd_file"] = saved["fd"]
        r["fd_sum_rule"] = float(zf["sum_rule_max"])
        if "apt_h" in zf.files and not np.array_equal(zf["apt_h"], zf["apt"]):
            r["richardson"] = richardson(P, zf["apt_h"], zf["apt"])
    if os.path.exists(saved["h"]):
        zh = np.load(saved["h"])
        if "spin" in zh.files and int(zh["spin"]) != spin:
            raise ValueError(f"{saved['h']} was computed at 2S = {int(zh['spin'])}, not {spin}")
        r["hessian_vs_saved"] = maxdiff(Hc, zh["H_raw"])
    measured = {"vs_route_b": "vs_route_b", "hessian": "hessian_vs_saved", "freq": "freq_maxdiff", "height_rel": "height_maxrel",
                "sum_rule": "sum_rule", "vs_fd": "vs_fd"}
    r["checks"] = {k: r[m] <= LIMITS[k] for k, m in measured.items() if m in r}
    r["passed"] = all(r["checks"].values())
    r["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)
    r["bands"] = [[round(f, 1), round(k, 2)] for f, k in band_groups(freq_up, km_up) if k >= HEIGHT_FLOOR]
    log(f"{d}: {n} atoms, {r['reference']}{' <S²> ' + str(r['s2']) if spin else ''}; SCF {r['seconds']['scf']} s, upstream Hessian + APT "
        f"{r['seconds']['upstream_hessian_and_apt']} s, peak {r['peak_rss_gb']} GB; sum rule {r['sum_rule']:.1e}"
        + (f"; vs route B {r['vs_route_b']:.1e} e" if "vs_route_b" in r else "")
        + (f"; vs FD {r['vs_fd']:.1e} e" if "vs_fd" in r else "")
        + (f"; Hessian vs saved {r['hessian_vs_saved']:.1e}" if "hessian_vs_saved" in r else "")
        + f"; heights: freq {r['freq_maxdiff']:.1e} cm-1, rel {r['height_maxrel']:.1e}"
        + f" → {'PASS' if r['passed'] else 'FAIL ' + str([k for k, v in r['checks'].items() if not v])}", flush=True)
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--grid", default="99,590")
    ap.add_argument("--charge", type=int, default=0)
    ap.add_argument("--spin", type=int, default=0, help="2S; > 0 selects UKS (as analytic_hessians.py)")
    ap.add_argument("--fd", default=None, help="an FD APT file (dipole_derivs_fd.py --out) for a single molecule")
    ap.add_argument("--save-apt", default=None, help="write the upstream APT (P[3, 3N]) of a single molecule to this npz (12 Oct: per-element reads)")
    a = ap.parse_args()
    if (a.fd or a.save_apt) and len(a.dirs) != 1:
        ap.error("--fd and --save-apt name the files of one molecule")
    lib.num_threads(a.threads)
    infrared, commit = load()
    grid = tuple(int(v) for v in a.grid.split(","))
    rows = [probe(d, grid, a.charge, a.spin, a.fd, infrared, save_apt=a.save_apt) for d in a.dirs]
    with open(a.out, "w") as f:
        json.dump({"probe": "TASKS 44 third route (pyscf-properties infrared)", "pyscf_properties_commit": commit, "limits": LIMITS,
                   "threads": a.threads, "grid": list(grid), "molecules": rows}, f, indent=1)
    return 0 if all(r["passed"] for r in rows) else 3


if __name__ == "__main__":
    sys.exit(main())
