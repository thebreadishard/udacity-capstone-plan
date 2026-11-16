"""What aromir's end-to-end run on 3-vinylfuran left behind, against the corpus row B_1e0fa2d7f0 (TASKS 245).

    python read_vinylfuran.py <plan folder>

The run (aromir cb01c7c, run spec aromir_e2e_vinylfuran) found a saddle point, stepped off it and ended in an optimisation
that did not converge in 100 steps. This reads the saddle point's saved low level — the analytic Hessian and the one with its
soft modes measured — beside the corpus's two B3LYP Hessians at the corpus geometry, and from pyscf.log the second
optimisation's last steps, to say what did not converge.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from aromir import vibrations
from aromir.molecule import Geometry

LOWEST = 4
CORPUS_ID = "B_1e0fa2d7f0"
STEP = re.compile(r"Step +(\d+) : Displace = \S*?([\d.e+-]+)\S*/\S*?([\d.e+-]+)\S* \(rms/max\) Trust = ([\d.e+-]+) .*?"
                  r"Grad = \S*?([\d.e+-]+)\S*/\S*?([\d.e+-]+)\S* \(rms/max\) E \(change\) = ([\d.-]+) \(\S*?([\d.e+-]+)\S*\)")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def lowest(hessian: np.ndarray, geometry: Geometry) -> list[float]:
    return np.round(np.sort(vibrations.vibrational_modes(hessian, geometry).wavenumbers)[:LOWEST], 2).tolist()


def main() -> None:
    plan = Path(sys.argv[1]).resolve()
    here = Path(__file__).parent / "vinylfuran"
    stored = json.loads((here / "saddle_point_geometry.json").read_text(encoding="utf-8"))
    saddle = Geometry(tuple(stored["symbols"]), np.array(stored["coords_bohr"], float))
    print(f"aromir, first attempt: {stored['optimisation']['n_steps']} steps, energy {stored['optimisation']['energy']:.10f}")
    with np.load(here / "saddle_point_lowlevel.npz") as arrays:
        print(f"  analytic Hessian, lowest {LOWEST}:     {lowest(np.array(arrays['analytic_hessian']), saddle)}")
        print(f"  soft modes measured, lowest {LOWEST}:  {lowest(np.array(arrays['hessian']), saddle)}")
        print(f"  soft-mode record (directions, positions before and after): {np.round(arrays['soft_modes'], 2).tolist()}")
    folder = plan / "modules" / "05_support_predictor" / "corpus" / "molecules" / CORPUS_ID
    corpus = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    geometry = Geometry(tuple(s[0].upper() + s[1:].lower() for s in corpus["symbols"]), np.array(corpus["coords_bohr"], float))
    # The corpus's label after its own repair reads -11.95 (soft_mode_by_label_2026-11-16, 'now b3lyp'); the two files are
    # named here as they are stored, without saying which the trainer reads.
    for name in ("hessian_b3lyp_analytic.npz", "hessian_b3lyp.npz"):
        with np.load(folder / name) as arrays:
            print(f"corpus {CORPUS_ID}, {name}, lowest {LOWEST}: {lowest(np.array(arrays['H_projected'], float), geometry)}")
    log = ANSI.sub("", (here / "pyscf.log").read_text(encoding="utf-8"))
    second = [match.groups() for match in map(STEP.search, log[log.rindex("Step    0 :"):].splitlines()) if match]
    print(f"aromir, second attempt after {json.loads((here / 'run.json').read_text(encoding='utf-8'))['left_saddle_point']['imaginary_cm']:.2f}"
          f" cm-1 and a step of 0.1 bohr: {len(second)} steps, not converged")
    print("  step  displacement rms/max   trust     gradient rms/max     energy          change")
    for step in (*second[:2], *second[-4:]):
        print(f"  {step[0]:>4}  {step[1]:>9}/{step[2]:<9}  {step[3]:>9}  {step[4]:>9}/{step[5]:<9}  {step[6]}  {step[7]}")
    energies = np.array([float(step[6]) for step in second])
    print(f"  energy below the saddle point at the end: {(energies[-1] - stored['optimisation']['energy']) * 219474.63:.2f} cm-1; "
          f"over the last 50 steps the energy fell {(energies[-51] - energies[-1]) * 219474.63:.3f} cm-1")
    print("  geomeTRIC's GAU_TIGHT, which aromir asks for: energy 1e-6, gradient rms 1e-5 / max 1.5e-5, "
          "displacement rms 4e-5 / max 6e-5")


if __name__ == "__main__":
    main()
