"""S1 of the spectral-shape design (13 Oct 2026, TASKS 53; `GoalGathering/notes/PreRegistration_2026-10-13_S1_Anharmonic_Level.md`): does the
anharmonic shift Δ_anh = ν − ω move when the anharmonic step runs at a cheaper DFT setting?

Two helpers for `probes/s1_anharmonic_level.sh`, which chains the existing QFF tools (make_qff_displacements.py → pyscf_hessians_for_qff.py →
python -m dpir.qff):

    python s1_anharmonic_level.py optimise <geometry.json> <ref_stub.json> --basis 6-31g* --grid 99,590 [--threads 4]
        the minimum at the setting itself (VPT2 assumes a stationary point; the corpus geometry is psi4's, and pyscf's B3LYP and grids move
        it): BFGS on the analytic RKS gradient to max |g| ≤ 1e-4, then Newton steps on the analytic Hessian until ≤ 1e-6 E_h/bohr (BFGS alone
        stalled at 3e-6 on water: line-search precision against a 1e-11 energy), written as a stub json for pyscf_hessians_for_qff.py.
    python s1_anharmonic_level.py gate <ref.json> <ref_finer_grid.json> [--window 550,2000] [--line 1.0]
        S1-TZ's grid gate (14 Oct 2026): exit 0 when the largest |Δω| over the window is within the line, 3 when not.
    python s1_anharmonic_level.py compare <ref_dir> <test_dir> [<test_dir> ...] [--window 550,2000]
        each directory holds a setting's reference Hessian (ref.json) and its dpir.qff report (qff_report.npz); modes are matched to the
        reference setting's by eigenvector overlap; prints and writes Δ_anh per mode and the rms / max difference over the window.

No pyscf import at module level, so `compare` and the tests run without it.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import linear_sum_assignment, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
GTOL = 1e-6                     # E_h/bohr, max component: tighter than geomeTRIC's default (4.5e-4) by design — VPT2 reads the cubic terms


BFGS_GTOL = 1e-4                # hand-over to the Newton polish


def external_basis(x: np.ndarray) -> np.ndarray:
    """Orthonormal basis (3n × k, k = 6 or 5) of the rigid translations and rotations at geometry x (bohr), unweighted Cartesian."""
    c = x - x.mean(axis=0)
    vecs = [np.tile(e, len(x)) for e in np.eye(3)] + [np.cross(e, c).reshape(-1) for e in np.eye(3)]
    u, s, _ = np.linalg.svd(np.array(vecs).T, full_matrices=False)
    return u[:, s > 1e-8 * s.max()]


def internal_gradient(x: np.ndarray, g: np.ndarray) -> np.ndarray:
    """The gradient with its translation/rotation components removed (what a geometry step can lower and VPT2 reads)."""
    T = external_basis(x)
    gf = np.asarray(g, float).reshape(-1)
    return gf - T @ (T.T @ gf)


def newton_polish(x, energy_gradient_hessian, gtol=GTOL, max_steps=6, log=print):
    """Newton steps in the internal space only: x ← x − W (Wᵀ H W)⁻¹ Wᵀ g, W an orthonormal basis of the complement of the rigid translations
    and rotations. (A pseudo-inverse of the full H does not do: without grid response the external eigenvalues are ~1e-4, not 0, and the net
    force divided by them gave 0.024-bohr translations on water while the internal gradient stayed.)"""
    n = len(x)
    for k in range(max_steps):
        e, g, H = energy_gradient_hessian(x)
        gmax = float(np.abs(internal_gradient(x, g)).max())
        log(f"  Newton {k}: E = {e:.10f}, max |g_internal| = {gmax:.1e}, net force {np.abs(np.asarray(g).sum(axis=0)).max():.1e}")
        if gmax <= gtol:
            return x, float(e), gmax, k
        T = external_basis(x)
        W = np.linalg.svd(np.eye(3 * n) - T @ T.T)[0][:, : 3 * n - T.shape[1]]
        Hi = W.T @ (0.5 * (H + H.T)) @ W
        step = -W @ np.linalg.solve(Hi, W.T @ np.asarray(g, float).reshape(-1))
        x = x + step.reshape(n, 3)
    e, g, _ = energy_gradient_hessian(x)
    return x, float(e), float(np.abs(internal_gradient(x, g)).max()), max_steps


def optimise(symbols, x0, energy_and_gradient, gtol=BFGS_GTOL, max_iter=200, log=print):
    """BFGS on Cartesian coordinates (bohr) to gtol (max component). energy_and_gradient(x (n, 3)) → (E, g (n, 3)).
    Returns (x, E, max |g|, evaluations)."""
    n = len(symbols)
    hist = []

    def f(flat):
        e, g = energy_and_gradient(flat.reshape(n, 3))
        gi = internal_gradient(flat.reshape(n, 3), g)
        hist.append((e, float(np.abs(gi).max())))
        return e, gi

    def stop(flat):
        if hist and hist[-1][1] <= gtol:
            raise StopIteration

    flat = np.asarray(x0, float).reshape(-1)
    try:
        res = minimize(f, flat, jac=True, method="BFGS", options={"gtol": gtol, "maxiter": max_iter, "norm": np.inf}, callback=stop)
        flat = res.x
    except StopIteration:
        pass
    e, g = energy_and_gradient(flat.reshape(n, 3))
    gmax = float(np.abs(internal_gradient(flat.reshape(n, 3), g)).max())
    log(f"BFGS: E = {e:.10f}, max |g_internal| = {gmax:.1e} after {len(hist)} evaluations")
    return flat.reshape(n, 3), float(e), gmax, len(hist)


def pyscf_energy_and_gradient(symbols, basis, grid, threads, hessian=False):
    """eg(x) → (E, g), or (E, g, H) with hessian=True (Cartesian, E_h/bohr²), at the S1 setting."""
    from pyscf import dft, gto, lib
    from pyscf.hessian import rks as rks_hess
    lib.num_threads(threads)
    rad, ang = (int(v) for v in grid.split(","))

    def eg(x):
        mol = gto.M(atom=[(s, tuple(p)) for s, p in zip(symbols, x, strict=True)], unit="Bohr", basis=basis, symmetry=False, verbose=0)
        mf = dft.RKS(mol)
        mf.xc = "b3lyp"
        mf.grids.atom_grid = (rad, ang)
        mf.grids.prune = None
        mf.conv_tol = 1e-11
        mf.conv_tol_grad = 1e-8
        mf.max_cycle = 200
        e = mf.kernel()
        if not mf.converged:
            raise SystemExit("SCF not converged during the optimisation")
        g = mf.nuc_grad_method().kernel()
        if not hessian:
            return e, g
        H = rks_hess.Hessian(mf).kernel()
        return e, g, H.transpose(0, 2, 1, 3).reshape(3 * mol.natm, 3 * mol.natm)
    return eg


def harmonic_modes(ref_json: str):
    """(ω cm⁻¹, mass-weighted eigenvectors) of a reference Hessian record, in dpir.qff's own order and convention."""
    from dpir.qff import harmonic
    d = json.load(open(ref_json, encoding="utf-8"))
    sym = d["molecule"]["symbols"]
    geom = np.array(d["molecule"]["geometry"], float).reshape(-1, 3)
    H = np.array(d["return_result"], float).reshape(3 * len(sym), 3 * len(sym))
    h = harmonic(H, sym, geom)
    return np.asarray(h.omega_cm), np.asarray(h.q)


def compare(ref_dir: str, test_dirs: list, window=(550.0, 2000.0)) -> dict:
    if os.path.exists(os.path.join(ref_dir, "NOISY")):
        raise SystemExit(f"{ref_dir}: the reference setting itself failed the noise guard; no comparison")
    wr, qr = harmonic_modes(os.path.join(ref_dir, "ref.json"))
    zr = np.load(os.path.join(ref_dir, "qff_report.npz"))
    dr = zr["nu_sym"] - zr["omega_cm"]
    inwin = (wr >= window[0]) & (wr <= window[1])
    out = {"window": list(window), "reference": ref_dir, "omega_ref": wr.tolist(), "d_anh_ref": dr.tolist(), "tests": {}}
    for t in test_dirs:
        wt, qt = harmonic_modes(os.path.join(t, "ref.json"))
        zt = np.load(os.path.join(t, "qff_report.npz"))
        dt = zt["nu_sym"] - zt["omega_cm"]
        m = linear_sum_assignment(-(qr.T @ qt) ** 2)[1]                 # test mode matched to each reference mode
        diff = dt[m] - dr
        out["tests"][t] = {"noisy": os.path.exists(os.path.join(t, "NOISY")),
                           "d_anh": dt[m].tolist(), "diff": diff.tolist(), "rms_window": float(np.sqrt(np.mean(diff[inwin] ** 2))),
                           "max_window": float(np.abs(diff[inwin]).max()), "n_window": int(inwin.sum()),
                           "min_overlap": float(((qr.T @ qt) ** 2)[np.arange(len(m)), m].min())}
    return out


def grid_gate(ref_json: str, gate_json: str, window=(550.0, 2000.0), line=1.0) -> dict:
    """S1-TZ's grid gate (14 Oct 2026): harmonic ω of the same minimum at the run's grid and at a finer one, compared in sorted order (as the
    0.33 cm⁻¹ between G and R at 6-31G* was measured); passes when the largest |Δω| over the window's modes is within the line."""
    w1, _ = harmonic_modes(ref_json)
    w2, _ = harmonic_modes(gate_json)
    w1, w2 = np.sort(w1), np.sort(w2)
    inwin = (w1 >= window[0]) & (w1 <= window[1])
    dmax = float(np.abs(w1 - w2)[inwin].max())
    return {"max_abs_domega_window": dmax, "n_window": int(inwin.sum()), "line": line, "passed": dmax <= line}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("optimise")
    o.add_argument("geometry")
    o.add_argument("stub")
    o.add_argument("--basis", default="6-31g*")
    o.add_argument("--grid", default="99,590")
    o.add_argument("--threads", type=int, default=4)
    c = sub.add_parser("compare")
    c.add_argument("ref_dir")
    c.add_argument("test_dirs", nargs="+")
    c.add_argument("--window", default="550,2000")
    c.add_argument("--out", default=None)
    gt = sub.add_parser("gate")
    gt.add_argument("ref_json")
    gt.add_argument("gate_json")
    gt.add_argument("--window", default="550,2000")
    gt.add_argument("--line", type=float, default=1.0)
    a = ap.parse_args()
    if a.cmd == "gate":
        lo, hi = (float(v) for v in a.window.split(","))
        g = grid_gate(a.ref_json, a.gate_json, (lo, hi), a.line)
        print(f"grid gate: max |Δω| {g['max_abs_domega_window']:.2f} cm⁻¹ over {g['n_window']} modes in {lo:g}–{hi:g} "
              f"(line {g['line']:g}) → {'PASS' if g['passed'] else 'FAIL'}")
        return 0 if g["passed"] else 3
    if a.cmd == "optimise":
        g = json.load(open(a.geometry, encoding="utf-8"))
        sym = [s.capitalize() for s in g["symbols"]]
        t0 = time.time()
        x, e, gmax, it = optimise(sym, np.asarray(g["coords_bohr"], float), pyscf_energy_and_gradient(sym, a.basis, a.grid, a.threads))
        x, e, gmax, nk = newton_polish(x, pyscf_energy_and_gradient(sym, a.basis, a.grid, a.threads, hessian=True))
        it = f"{it} BFGS evaluations + {nk} Newton steps"
        if gmax > GTOL:
            raise SystemExit(f"not converged: max |g| {gmax:.1e} > {GTOL:g}")
        json.dump({"driver": "hessian", "molecule": {"symbols": sym, "geometry": x.reshape(-1).tolist()},
                   "optimisation": {"basis": a.basis, "grid": a.grid, "energy": e, "max_gradient": gmax, "evaluations": it,
                                    "seconds": round(time.time() - t0), "start": os.path.abspath(a.geometry)}},
                  open(a.stub, "w", encoding="utf-8"))
        return 0
    lo, hi = (float(v) for v in a.window.split(","))
    res = compare(a.ref_dir, a.test_dirs, (lo, hi))
    for t, r in res["tests"].items():
        print(f"{t}: Δ_anh difference over {r['n_window']} modes in {lo:g}–{hi:g} cm⁻¹: rms {r['rms_window']:.2f}, max {r['max_window']:.2f} cm⁻¹ "
              f"(min mode overlap {r['min_overlap']:.3f})" + (" — NOISY: failed the force-field noise guard" if r["noisy"] else ""))
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
