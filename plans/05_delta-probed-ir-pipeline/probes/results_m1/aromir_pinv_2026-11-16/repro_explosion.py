"""One corpus molecule through aromir's bundled release: the Wilson B's singular values and what B⁺ and ΔH come out as (TASKS 236).

Read-only. Run before and after the fix of aromir's pseudo-inverse, on each platform:

    python repro_explosion.py <plan folder> <corpus id> [<out.npz>]

Prints the float64 singular values of B around index 3N-6 (the last real and the first null one), numpy's default pinv cutoff and
how many values it keeps, max|B⁺| from `np.linalg.pinv(B)` and from aromir's own internal force constants, and each seed's ΔH.
With an output path the B matrix, the default-cutoff B⁺ and the seeds' ΔH are saved for a comparison across platforms.
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import torch
from aromir import __version__ as aromir_version
from aromir import release as aromir_release
from aromir.molecule import Geometry
from aromir.network import primitives

LOW_HESSIAN = "hessian_b3lyp_analytic.npz"   # the file module 05's inference path reads (rungC_infer.LOW_HESSIAN)
WINDOW = 4                                   # singular values printed on each side of the rank


def load(plan: Path, molecule_id: str) -> tuple[Geometry, np.ndarray]:
    """The corpus molecule's geometry in aromir's form and its projected low-level Hessian."""
    folder = plan / "modules" / "05_support_predictor" / "corpus" / "molecules" / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    symbols = tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"])
    with np.load(folder / LOW_HESSIAN) as low:
        hessian = np.array(low["H_projected"], float)
    return Geometry(symbols, np.array(stored["coords_bohr"], float)), hessian


def main() -> None:
    plan, molecule_id = Path(sys.argv[1]).resolve(), sys.argv[2]
    geometry, hessian = load(plan, molecule_id)
    release = aromir_release.load(aromir_release.bundled())
    print(f"{platform.system()} python {platform.python_version()} numpy {np.__version__} torch {torch.__version__} "
          f"aromir {aromir_version} release v{release.network_version}; {molecule_id}, {geometry.n_atoms} atoms")
    b = primitives.build(geometry, release.recipes[0].inputs.primitives).wilson_b
    rank = 3 * geometry.n_atoms - 6
    s = np.linalg.svd(b, compute_uv=False)
    cutoff = 1e-15 * s[0]
    print(f"  B {b.shape} {b.dtype}, 3N-6 = {rank}; singular values (1-based) {rank - WINDOW + 1}..{rank + WINDOW}:")
    print("   ", " ".join(f"{v:.3e}" for v in s[rank - WINDOW:rank + WINDOW]))
    print(f"  s_max {s[0]:.6e}; last real s[{rank}] {s[rank - 1]:.6e}; first null s[{rank + 1}] {s[rank]:.3e}; "
          f"ratio null/real {s[rank] / s[rank - 1]:.3e}; null/s_max {s[rank] / s[0]:.3e}")
    print(f"  numpy's default cutoff 1e-15 * s_max = {cutoff:.3e}: keeps {int((s > cutoff).sum())} values (the rank is {rank})")
    default_pinv = np.linalg.pinv(b)
    print(f"  np.linalg.pinv(B): max|B+| {np.abs(default_pinv).max():.6g}")
    f = primitives.internal_force_constants(hessian, b)
    print(f"  aromir internal_force_constants: max|F| {np.abs(f).max():.6g}, finite {bool(np.isfinite(f).all())}")
    corrections = release.corrections(geometry, hessian)
    for seed, dh in enumerate(corrections.per_seed):
        print(f"  seed {seed}: max|dH| {np.abs(dh).max():.6g}, finite {bool(np.isfinite(dh).all())}")
    if len(sys.argv) > 3:
        np.savez(sys.argv[3], B=b, singular_values=s, pinv_default=default_pinv, F=f, delta_h=np.array(corrections.per_seed))


if __name__ == "__main__":
    main()
