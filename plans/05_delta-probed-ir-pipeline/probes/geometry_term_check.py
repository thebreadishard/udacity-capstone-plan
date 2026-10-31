"""Does the first-order geometry term hold beyond benzene? (TASKS 156 (d); `GoalGathering/notes/PreRegistration_2026-10-31_Geometry_Term.md`)

An anchor's Hessian is computed at the B3LYP geometry, not at its own level's minimum. To first order the band then moves by
Δω_i = ½ Σ_k φ_iik Δq_k, with φ the B3LYP cubic constants and Δq the displacement to the higher level's minimum in reduced coordinates
(validated on benzene, 22 Sep 2026: C–H stretches 52 → 14 cm⁻¹ against CCSD(T)). This check repeats it at DFT scale on the 18 molecules
whose force fields exist at the anharmonic level G (S2, B3LYP/6-31G*, grid 75/302): the higher level is ωB97X/6-31G* (the proxy's).

    run  <s2 molecule dir>/G <out dir> [--xc wb97x --basis 6-31g* --grid 99,590 --threads 8]   (WSL, pyscf)
         ωB97X's analytic Hessian at G's minimum x0, Newton steps (S1's `newton_step`) with that Hessian held to its own minimum x_T,
         and its Hessian at x_T. One line per evaluation; pyscf's log beside it.
    read <s2 root> <runs root> [--out <dir>]                                                     (no pyscf)
         per molecule: measured Δω (ωB97X at x_T minus at x0, modes paired by overlap, then to G's modes) against the term with Δq from
         the true displacement and from the first Newton step at x0 (what a product could compute), and the registered lines.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE))
from dpir.qff import harmonic  # noqa: E402

RUN_FILE = "geometry_term_run.npz"
MIN_SHIFT_CM = 1.0                 # modes the geometry moves by less are below what the lines read
WINDOWS = (("below 1000", 0.0, 1000.0), ("1000-1900", 1000.0, 1900.0), ("1900-2700", 1900.0, 2700.0), ("X-H stretch", 2700.0, 1e9))
MIN_WINDOW_MODES = 10
LINE_A, LINE_B, LINE_D = 0.30, 0.35, 16      # residual / shift (true Δq), (Newton Δq); molecules where the term helps
OMEGA_CHECK_CM = 0.01              # the reference Hessian's ω against the force field's own
MAX_STEPS = 12                     # Newton steps on the held Hessian before the run is refused


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_reference(g_dir: Path) -> tuple[list[str], np.ndarray, np.ndarray]:
    """(symbols, x0 (n, 3) bohr, H (3n, 3n)) of a force field's reference Hessian record."""
    d = json.loads((g_dir / "ref.json").read_text(encoding="utf-8"))
    sym = d["molecule"]["symbols"]
    x0 = np.asarray(d["molecule"]["geometry"], float).reshape(-1, 3)
    return sym, x0, np.asarray(d["return_result"], float).reshape(3 * len(sym), 3 * len(sym))


# ---------------------------------------------------------------- run (WSL, pyscf)

def run(g_dir: Path, out: Path, xc: str, basis: str, grid: str, threads: int) -> None:
    """ωB97X's Hessian at x0, Newton steps with that Hessian held (gradients only: x0 is a few thousandths of an ångström from x_T, so the
    steps converge in a few and a Hessian per step would triple the cost), and the Hessian again at x_T."""
    from library_log import PYSCF_LOG_NAME
    from s1_anharmonic_level import GTOL, PyscfSetting, internal_gradient, log_line, newton_step, pyscf_energy_and_gradient

    name = g_dir.parent.name
    sym, x0, _ = read_reference(g_dir)
    out.mkdir(parents=True, exist_ok=True)
    seconds: list[float] = []
    t_start = time.time()

    def timed(f, x, what):
        t0 = time.time()
        res = f(x)
        seconds.append(time.time() - t0)
        gmax = float(np.abs(internal_gradient(x, res[1])).max())
        log_line(f"  [geometry term] {name} {what}: {xc} E = {res[0]:.10f}, max |g_internal| = {gmax:.1e}, {seconds[-1]:.0f} s")
        return res, gmax

    with (out / PYSCF_LOG_NAME).open("a", encoding="utf-8") as lib_log:
        setting = PyscfSetting(basis, grid, threads, lib_log, xc=xc)
        eg, egh = pyscf_energy_and_gradient(sym, setting), pyscf_energy_and_gradient(sym, setting, hessian=True)
        (e0, g0, H0), gmax = timed(egh, x0, "Hessian at G's minimum")
        x, g, steps = x0.copy(), g0, 0
        while gmax > GTOL:
            if steps == MAX_STEPS:
                raise SystemExit(f"{name}: not converged, max |g| {gmax:.1e} > {GTOL:g} after {steps} steps on the held Hessian")
            x = x + newton_step(x, g, H0)
            steps += 1
            (_, g), gmax = timed(eg, x, f"gradient after step {steps}")
        (e_t, g_t, H_t), gmax = timed(egh, x, "Hessian at its own minimum")
    tmp = out / (RUN_FILE + ".tmp.npz")
    np.savez(tmp, symbols=np.array(sym), x0=x0, g0=g0, H0=H0, e0=e0, x_t=x, g_t=g_t, H_t=H_t, e_t=e_t, max_gradient=gmax,
             newton_steps=steps, evaluation_seconds=np.array(seconds), xc=xc, basis=basis, grid=grid, seconds=time.time() - t_start,
             ref_sha256=sha256(g_dir / "ref.json"), qff_sha256=sha256(g_dir / "qff_report.npz"))
    os.replace(tmp, out / RUN_FILE)
    log_line(f"  [geometry term] {name} done: {steps} steps, max |g| {gmax:.1e}, {time.time() - t_start:.0f} s")


# ---------------------------------------------------------------- read (no pyscf)

def reduced(h, dx: np.ndarray) -> np.ndarray:
    """A Cartesian displacement (bohr) in the reduced normal coordinates of `h` (dpir.qff's convention: Δx = A Δq)."""
    return np.sqrt(h.omega) * (h.q.T @ (dx.reshape(-1) / h.Minvh))


def paired(qa: np.ndarray, qb: np.ndarray) -> tuple[np.ndarray, float]:
    """For every mode of a, the mode of b with the largest total overlap (an assignment); the smallest overlap² taken."""
    s = (qa.T @ qb) ** 2
    rows, cols = linear_sum_assignment(-s)
    order = np.empty(len(rows), int)
    order[rows] = cols
    return order, float(s[rows, cols].min())


def window_of(w: float) -> str:
    return next(name for name, lo, hi in WINDOWS if lo <= w < hi)


@dataclass(frozen=True)
class Molecule:
    """One molecule's measured and predicted shifts per G mode (cm⁻¹)."""

    id: str
    omega_g: np.ndarray
    measured: np.ndarray
    predicted_true: np.ndarray
    predicted_newton: np.ndarray
    predicted_g_curvature: np.ndarray
    min_overlap: float


def molecule(mol_id: str, g_dir: Path, run_file: Path) -> Molecule:
    from s1_anharmonic_level import newton_step

    sym, x_ref, H_g = read_reference(g_dir)
    with np.load(g_dir / "qff_report.npz") as z:
        omega_ff, phi = z["omega_cm"], z["phi_ijk"]
    with np.load(run_file) as r:
        x0, g0, H0, x_t, H_t = r["x0"], r["g0"], r["H0"], r["x_t"], r["H_t"]
        if str(r["ref_sha256"]) != sha256(g_dir / "ref.json") or str(r["qff_sha256"]) != sha256(g_dir / "qff_report.npz"):
            raise SystemExit(f"{mol_id}: the run was made on another force field than {g_dir}")
    if not np.allclose(x0, x_ref):
        raise SystemExit(f"{mol_id}: the run did not start at the force field's reference geometry")
    hg = harmonic(H_g, sym, x0)
    if np.abs(hg.omega_cm - omega_ff).max() > OMEGA_CHECK_CM:
        raise SystemExit(f"{mol_id}: the reference Hessian's ω differ from the force field's by {np.abs(hg.omega_cm - omega_ff).max():.3f} cm⁻¹")
    cubic = np.einsum("iik->ik", phi)
    h0, ht = harmonic(H0, sym, x0), harmonic(H_t, sym, x_t)
    t_of_t0, ov1 = paired(h0.q, ht.q)              # ωB97X's modes at x_T paired with its modes at x0 ...
    t0_of_g, ov2 = paired(hg.q, h0.q)              # ... and those with G's
    measured = (ht.omega_cm[t_of_t0] - h0.omega_cm)[t0_of_g]
    dq_true = reduced(hg, x_t - x0)
    dq_newton = reduced(hg, newton_step(x0, g0, H0))
    dq_curv = -(hg.A.T @ g0.reshape(-1)) / hg.omega
    return Molecule(mol_id, hg.omega_cm, measured, 0.5 * cubic @ dq_true, 0.5 * cubic @ dq_newton, 0.5 * cubic @ dq_curv, min(ov1, ov2))


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else float("nan")


def summary(mols: list[Molecule]) -> dict:
    """The registered lines over the modes the geometry moves by at least MIN_SHIFT_CM."""
    meas = np.concatenate([m.measured for m in mols])
    keep = np.abs(meas) >= MIN_SHIFT_CM
    pt, pn, pc = (np.concatenate([getattr(m, k) for m in mols]) for k in ("predicted_true", "predicted_newton", "predicted_g_curvature"))
    w = np.concatenate([m.omega_g for m in mols])
    shift = rms(meas[keep])
    windows = {}
    for name, _, _ in WINDOWS:
        sel = keep & np.array([window_of(x) == name for x in w])
        if sel.sum():
            windows[name] = {"modes": int(sel.sum()), "rms_shift": rms(meas[sel]), "rms_residual_true": rms((meas - pt)[sel]),
                             "rms_residual_newton": rms((meas - pn)[sel]), "read": bool(sel.sum() >= MIN_WINDOW_MODES)}
    per_mol = {}
    for m in mols:
        k = np.abs(m.measured) >= MIN_SHIFT_CM
        per_mol[m.id] = {"modes": int(k.sum()), "rms_shift": rms(m.measured[k]), "rms_residual_true": rms((m.measured - m.predicted_true)[k]),
                         "rms_residual_newton": rms((m.measured - m.predicted_newton)[k]), "min_overlap": m.min_overlap,
                         "max_shift": float(np.abs(m.measured).max())}
    helped = sum(1 for v in per_mol.values() if v["modes"] and v["rms_residual_true"] < v["rms_shift"])
    res_true, res_newton = rms((meas - pt)[keep]), rms((meas - pn)[keep])
    lines = {"A": res_true <= LINE_A * shift, "B": res_newton <= LINE_B * shift,
             "C": all(v["rms_residual_true"] <= v["rms_shift"] for v in windows.values() if v["read"]), "D": helped >= LINE_D}
    return {"molecules": len(mols), "modes_read": int(keep.sum()), "rms_shift": shift, "rms_residual_true": res_true,
            "rms_residual_newton": res_newton, "rms_residual_g_curvature": rms((meas - pc)[keep]), "molecules_helped": helped,
            "lines": lines, "passed": all(lines.values()), "windows": windows, "per_molecule": per_mol,
            "thresholds": {"min_shift_cm": MIN_SHIFT_CM, "A": LINE_A, "B": LINE_B, "D": LINE_D, "min_window_modes": MIN_WINDOW_MODES}}


def report(s: dict) -> str:
    ok = {True: "holds", False: "fails"}
    lines = [f"# Geometry term beyond benzene — {s['molecules']} molecules, {s['modes_read']} modes moved by ≥ {MIN_SHIFT_CM:g} cm⁻¹", "",
             f"rms shift {s['rms_shift']:.2f} cm⁻¹; rms residual after the term: true Δq {s['rms_residual_true']:.2f}, Newton Δq "
             f"{s['rms_residual_newton']:.2f}, G-curvature Δq {s['rms_residual_g_curvature']:.2f} cm⁻¹", "",
             f"- **A** (true Δq, residual ≤ {LINE_A} × shift): {ok[s['lines']['A']]}",
             f"- **B** (Newton Δq, residual ≤ {LINE_B} × shift): {ok[s['lines']['B']]}",
             f"- **C** (no window of ≥ {MIN_WINDOW_MODES} modes made worse): {ok[s['lines']['C']]}",
             f"- **D** (the term helps in ≥ {LINE_D} molecules): {ok[s['lines']['D']]} ({s['molecules_helped']})", "",
             "| window | modes | rms shift | residual (true) | residual (Newton) |", "|---|---|---|---|---|"]
    lines += [f"| {k} | {v['modes']} | {v['rms_shift']:.2f} | {v['rms_residual_true']:.2f} | {v['rms_residual_newton']:.2f} |"
              for k, v in s["windows"].items()]
    lines += ["", "| molecule | modes | rms shift | residual (true) | residual (Newton) | max shift | min overlap² |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {k} | {v['modes']} | {v['rms_shift']:.2f} | {v['rms_residual_true']:.2f} | {v['rms_residual_newton']:.2f} | "
              f"{v['max_shift']:.2f} | {v['min_overlap']:.3f} |" for k, v in s["per_molecule"].items()]
    return "\n".join(lines) + "\n"


def read(s2_root: Path, runs_root: Path, out: Path) -> dict:
    ids = sorted(p.parent.name for p in runs_root.glob(f"*/{RUN_FILE}"))
    missing = sorted(p.parent.parent.name for p in s2_root.glob("*/G/qff_report.npz") if p.parent.parent.name not in ids)
    if missing:
        raise SystemExit(f"no run for {', '.join(missing)}: the lines read all the force fields at G")
    mols = [molecule(i, s2_root / i / "G", runs_root / i / RUN_FILE) for i in ids]
    s = summary(mols)
    out.mkdir(parents=True, exist_ok=True)
    for name, text in (("geometry_term_read.json", json.dumps(s, indent=1)), ("geometry_term_read.md", report(s))):
        tmp = out / (name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, out / name)
    return s


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("g_dir", type=Path)
    r.add_argument("out", type=Path)
    r.add_argument("--xc", default="wb97x")
    r.add_argument("--basis", default="6-31g*")
    r.add_argument("--grid", default="99,590")
    r.add_argument("--threads", type=int, default=8)
    d = sub.add_parser("read")
    d.add_argument("s2_root", type=Path)
    d.add_argument("runs_root", type=Path)
    d.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run(a.g_dir, a.out, a.xc, a.basis, a.grid, a.threads)
        return 0
    s = read(a.s2_root, a.runs_root, a.out or a.runs_root)
    print(report(s))
    return 0 if s["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
