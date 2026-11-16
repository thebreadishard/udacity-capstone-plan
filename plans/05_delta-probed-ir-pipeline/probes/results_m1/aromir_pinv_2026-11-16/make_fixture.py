"""Write aromir's test fixture for the pseudo-inverse of the Wilson B (TASKS 236).

Run on Windows (numpy 2.5.1), where `np.linalg.pinv` at its default cutoff keeps the right 63 values for biphenyl+CN:

    python make_fixture.py <npz written in WSL by repro_explosion.py> <plan folder> <corpus id> <fixture.npz>

The fixture holds the molecule (symbols, coordinates in bohr), the B matrix exactly as the Linux build made it — the bits on
which that build's `np.linalg.pinv(B)` returns 1e13 — and the Windows build's default-cutoff B⁺ of that same matrix. The script
refuses to write when the Windows B⁺ is not the bounded one.
"""
from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

import numpy as np

LARGEST_SANE = 10.0   # bohr per unit of internal coordinate; the bounded B⁺ of this molecule has max 3.30


def main() -> None:
    saved, plan, molecule_id, target = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), sys.argv[3], Path(sys.argv[4])
    if platform.system() != "Windows":
        raise SystemExit("the fixture's B⁺ is the Windows build's: run this on Windows")
    with np.load(saved) as z:
        b = np.array(z["B"], float)
    folder = plan / "modules" / "05_support_predictor" / "corpus" / "molecules" / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    symbols = np.array([s[0].upper() + s[1:].lower() for s in stored["symbols"]])
    pinv = np.linalg.pinv(b)
    largest = float(np.abs(pinv).max())
    penrose = float(np.abs(b @ pinv @ b - b).max())
    print(f"Windows numpy {np.__version__}: B {b.shape}, max|B+| {largest:.6f}, max|B B+ B - B| {penrose:.3e}")
    if largest > LARGEST_SANE:
        raise SystemExit(f"max|B+| {largest:.3e}: this build's default pinv is not the bounded one; nothing written")
    tmp = target.with_name(target.name + ".tmp.npz")
    np.savez_compressed(tmp, symbols=symbols, coords_bohr=np.array(stored["coords_bohr"], float), wilson_b=b,
                        pseudo_inverse_windows=pinv)
    os.replace(tmp, target)
    print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
