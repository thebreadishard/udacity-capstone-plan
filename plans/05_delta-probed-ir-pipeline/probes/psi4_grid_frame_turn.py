"""How far psi4's DFT grid turns against the atoms along benzene's modes (28 Oct 2026, TASKS 53).

psi4 1.10 orients every atomic grid by the principal axes of the nuclear-charge second moment (libfock/cubature.cc, OrientationMgr).
The s1tz reference benzene's two in-plane moments differ by 0.009 in 190, so its in-plane axes are ill-conditioned: a displacement
that barely moves the atoms can turn the frame, and with it the grid, by degrees. The molecule itself does not turn, so this is a
turn of the grid against the atoms, an orientation-dependent quadrature error added to E(q). Printed per mode and step of the
energy route (q = +-0.1 ... +-0.4); no psi4 needed.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PLAN / "probes"), str(PLAN / "src")]
from qff_energy_route import harmonic, load_results, reference_index  # noqa: E402

NUCLEAR_CHARGE = {"C": 6, "H": 1}
REF_DIR = PLAN / "probes/results_m1/s1tz_gridcheck_2026-10-28/s1tz_gridcheck/benzene/coarse"
MODES = (5, 10, 11)
STEPS = (0.1, 0.2, 0.3, 0.4)


def charge_frame(geom: np.ndarray, charges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Moments (ascending) and axes of the nuclear-charge second moment about the centre of charge, as OrientationMgr builds them."""
    d = geom - charges @ geom / charges.sum()
    return np.linalg.eigh((d * charges[:, None]).T @ d)


def turn_degrees(v0: np.ndarray, v1: np.ndarray) -> float:
    """Smallest proper rotation between two axis frames, over the sign of each axis (an eigenvector's sign is arbitrary)."""
    angles = []
    for signs in itertools.product((1, -1), repeat=3):
        r = v0.T @ (v1 * np.array(signs))
        if np.linalg.det(r) > 0:
            angles.append(float(np.degrees(np.arccos(np.clip((np.trace(r) - 1) / 2, -1, 1)))))
    return min(angles)


def main() -> None:
    recs = load_results(str(REF_DIR))
    ref = recs[reference_index(recs)]
    harm = harmonic(ref.H, ref.symbols, ref.geom)
    geom0 = ref.geom.reshape(-1, 3)
    charges = np.array([NUCLEAR_CHARGE[s] for s in ref.symbols], dtype=float)
    w0, v0 = charge_frame(geom0, charges)
    print("reference moments of charge", np.round(w0, 6))
    for i in MODES:
        turns = []
        for q, s in itertools.product(STEPS, (1, -1)):
            _, v = charge_frame(geom0 + s * q * harm.A[:, i].reshape(-1, 3), charges)
            turns.append(f"{s * q:+.1f}: {turn_degrees(v0, v):.3f}")
        print(f"mode {i}: grid turn in degrees  " + "  ".join(turns))


if __name__ == "__main__":
    main()
