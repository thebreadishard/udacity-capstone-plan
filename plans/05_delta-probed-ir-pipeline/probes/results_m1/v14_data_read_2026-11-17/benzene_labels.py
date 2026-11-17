"""Is the benzene v1.4 is tested on the benzene v1.3 was tested on? The label files now against the superseded ones (read-only).

Usage: benzene_labels.py <module 05 folder>
"""
from __future__ import annotations

import datetime
import hashlib
import sys
from pathlib import Path

import numpy as np

m05 = Path(sys.argv[1])
sys.path.insert(0, str(m05 / "m05"))
from learning_curve_layerA import normal_modes  # noqa: E402  module 05's code is not a package

BENZENE = "A_8448043181"
now = m05 / "corpus" / "molecules" / BENZENE
for folder in [*sorted(m05.glob(f"corpus/superseded_*/{BENZENE}")), now]:
    print(f"--- {folder.parent.name}/{folder.name}")
    for path in sorted(folder.glob("*.npz")) + sorted(folder.glob("geometry.json")):
        stamp = datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"    {path.name:<32}{stamp}  sha16 {hashlib.sha256(path.read_bytes()).hexdigest()[:16]}")

import json  # noqa: E402

masses = np.array(json.loads((now / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
for name in ("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"):
    with np.load(now / name) as z:
        current = np.array(z["H_projected"], float)
    for old_folder in sorted(m05.glob(f"corpus/superseded_*/{BENZENE}")):
        if not (old_folder / name).is_file():
            print(f"{name}: no superseded copy in {old_folder.parent.name} (the file was not replaced then)")
            continue
        with np.load(old_folder / name) as z:
            old = np.array(z["H_projected"], float)
        f_now, f_old = np.sort(normal_modes(current, masses)[1]), np.sort(normal_modes(old, masses)[1])
        print(f"{name}: against {old_folder.parent.name}: largest |ΔH| {np.abs(current - old).max():.3e} hartree/bohr² "
              f"(largest element {np.abs(current).max():.3f}); largest change of a frequency {np.abs(f_now - f_old).max():.3e} cm⁻¹")
