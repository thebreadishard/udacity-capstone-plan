"""The energy route for a diagonal quartic (28 Oct 2026, TASKS 53; the user: 'Ja'). S1-TZ's benzene at B3LYP/def2-TZVP has φ_iiii of its
out-of-plane modes far above 6-31G*'s (mode 10: 907 cm⁻¹ at both 75/302 and 99/590), and the analytic Hessians those constants come from are
the only route that saw them. This reads the same constant from SCF energies alone: E at q = 0, ±q_k along mode i (reduced coordinates of the
reference Hessian, dpir.qff.harmonic), and the even part

    E(q) + E(−q) − 2 E(0) = ω q² + φ_iiii q⁴ / 12 + c₆ q⁶ + …

solved exactly through the largest q (and once with one step fewer, so the truncation shows). ω from the fit against the Hessian's ω checks
the coordinates; the odd part E(q) − E(−q) is reported too (zero by symmetry for a mode that some operation flips). Energies are checkpointed
in energies.json, so a second call resumes.

    python probes/qff_energy_route.py <dir with ref.json> <out_dir> --modes 10 11 [--steps 0.1 0.2 0.3 0.4] [--basis def2-tzvp] [--grid 75,302]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, TextIO

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from library_log import PYSCF_LOG_NAME, pyscf_mole
from pyscf_hessians_for_qff import rks_setup
from scf_converge import converged_scf

from dpir.qff import HARTREE_CM, harmonic, load_results, reference_index


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("ref_dir", help="directory holding the reference Hessian (ref.json) whose modes are followed")
    ap.add_argument("out_dir")
    ap.add_argument("--modes", type=int, nargs="+", required=True, help="0-based mode indices, as dpir.qff's cache names them")
    ap.add_argument("--steps", type=float, nargs="+", default=[0.1, 0.2, 0.3, 0.4])
    ap.add_argument("--xc", default="b3lyp")
    ap.add_argument("--basis", default="def2-tzvp")
    ap.add_argument("--grid", default="75,302")
    ap.add_argument("--conv", type=float, default=1e-11)
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    if len(a.steps) < 2 or sorted(a.steps) != a.steps or a.steps[0] <= 0:
        raise SystemExit(f"--steps must be at least two increasing positive values, got {a.steps}")
    return a


def even_fit(steps: list[float], even: list[float]) -> np.ndarray:
    """Coefficients of q², q⁴, … that reproduce E(q) + E(−q) − 2 E(0) exactly at the given steps."""
    q = np.asarray(steps)
    return np.linalg.solve(np.stack([q ** (2 * k) for k in range(1, len(q) + 1)], axis=1), np.asarray(even))


def read_curve(e0: float, plus: list[float], minus: list[float], steps: list[float]) -> dict[str, Any]:
    """ω and φ_iiii (cm⁻¹) from the full set of steps and from all but the largest; the largest odd part (cm⁻¹)."""
    even = [p + m - 2 * e0 for p, m in zip(plus, minus, strict=True)]
    fits = {}
    for name, n in (("all_steps", len(steps)), ("one_fewer", len(steps) - 1)):
        c = even_fit(steps[:n], even[:n]) * HARTREE_CM
        fits[name] = {"steps": steps[:n], "omega": float(c[0]), "phi_iiii": float(12 * c[1])}
    return {**fits, "odd_max": float(max(abs(p - m) for p, m in zip(plus, minus, strict=True)) * HARTREE_CM)}


def scf_energy(symbols: list[str], geom: np.ndarray, a: argparse.Namespace, lib_log: TextIO) -> float:
    atoms = [(s, tuple(x)) for s, x in zip(symbols, geom, strict=True)]
    mol = pyscf_mole(lib_log, atom=atoms, unit="Bohr", basis=a.basis, symmetry=False)
    _, e = converged_scf(rks_setup(mol, a.xc, a.grid, a.conv), 200, log=lambda m: print(m, flush=True))
    return float(e)


def write_json(path: str, obj: Any) -> None:
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1)
    os.replace(path + ".tmp", path)


def main() -> None:
    a = parse_args()
    from pyscf import lib
    lib.num_threads(a.threads)
    os.makedirs(a.out_dir, exist_ok=True)
    recs = load_results(a.ref_dir)
    ref = recs[reference_index(recs)]
    harm = harmonic(ref.H, ref.symbols, ref.geom)
    geom0 = ref.geom.reshape(-1, 3)
    ck = os.path.join(a.out_dir, "energies.json")
    E: dict[str, float] = {}
    if os.path.exists(ck):
        with open(ck, encoding="utf-8") as fh:
            E = json.load(fh)
    points = [("ref", 0, 0.0)] + [(f"mode{i:02d}_{'p' if s > 0 else 'm'}{q:.2f}", i, s * q) for i in a.modes for q in a.steps for s in (1, -1)]
    with open(os.path.join(a.out_dir, PYSCF_LOG_NAME), "a", encoding="utf-8") as lib_log:
        for n, (key, i, q) in enumerate(points, 1):
            if key in E:
                continue
            t0 = time.time()
            E[key] = scf_energy(ref.symbols, geom0 + q * harm.A[:, i].reshape(-1, 3), a, lib_log)
            write_json(ck, E)
            print(f"[{time.strftime('%H:%M:%S')}] {n}/{len(points)} {key} E = {E[key]:.12f} ({time.time() - t0:.0f} s)", flush=True)
    res = {"ref_file": ref.file, "xc": a.xc, "basis": a.basis, "grid": a.grid, "conv": a.conv, "steps": a.steps, "modes": {}}
    for i in a.modes:
        plus = [E[f"mode{i:02d}_p{q:.2f}"] for q in a.steps]
        minus = [E[f"mode{i:02d}_m{q:.2f}"] for q in a.steps]
        res["modes"][str(i)] = {"omega_hessian": float(harm.omega_cm[i]), **read_curve(E["ref"], plus, minus, a.steps)}
        r = res["modes"][str(i)]
        print(f"mode {i}: ω Hessian {r['omega_hessian']:.2f}, energies {r['all_steps']['omega']:.2f}; φ_iiii energies "
              f"{r['all_steps']['phi_iiii']:.1f} (one step fewer {r['one_fewer']['phi_iiii']:.1f}); odd part max {r['odd_max']:.2e} cm⁻¹")
    write_json(os.path.join(a.out_dir, "energy_route.json"), res)


if __name__ == "__main__":
    main()
