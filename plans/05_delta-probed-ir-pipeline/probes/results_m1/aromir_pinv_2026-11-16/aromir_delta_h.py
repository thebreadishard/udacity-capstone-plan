"""aromir's bundled release on a list of corpus molecules: every seed's ΔH and the corrected bands, saved per platform (TASKS 236).

Read-only on the corpus. Run with the aromir under test on each platform, then compare the files with `compare_delta_h.py`:

    python aromir_delta_h.py <plan folder> <ids file> <out.npz>

A molecule without the low-level Hessian the networks read is skipped and named.
"""
from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

import numpy as np
import torch
from aromir import release as aromir_release
from aromir import vibrations
from aromir.molecule import Geometry

LOW_HESSIAN = "hessian_b3lyp_analytic.npz"   # the file module 05's inference path reads (rungC_infer.LOW_HESSIAN)


def bands_cm(hessian: np.ndarray, geometry: Geometry) -> np.ndarray:
    """Sorted harmonic wavenumbers of the 3N-6 vibrations of a Cartesian Hessian, imaginary ones negative.

    The six rigid motions are projected out and their six near-zero values dropped: a wavenumber is a square root, so single-
    precision noise of 1e-8 in ΔH moves a mode at 0 cm-1 by 0.05 cm-1 and a real band by less than 1e-3.
    """
    weights = vibrations.mass_weights(geometry.masses_amu)
    n_vibrations = len(weights) - vibrations.N_RIGID_MOTIONS
    if not np.isfinite(hessian).all():
        return np.full(n_vibrations, np.nan)
    try:
        projected = vibrations.project_rigid_motions(hessian, geometry)
        curvatures = np.linalg.eigvalsh(projected / np.outer(weights, weights))
    except np.linalg.LinAlgError:
        # an exploded ΔH (1e29) has no eigenvalues LAPACK can find; the bands are then recorded as missing
        return np.full(n_vibrations, np.nan)
    wavenumbers = np.asarray(vibrations.signed_wavenumber(curvatures))
    return np.sort(wavenumbers[np.argsort(np.abs(wavenumbers))[vibrations.N_RIGID_MOTIONS:]])


def main() -> None:
    plan, ids_file, target = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), Path(sys.argv[3])
    corpus = plan / "modules" / "05_support_predictor" / "corpus" / "molecules"
    release = aromir_release.load(aromir_release.bundled())
    source = Path(aromir_release.__file__).resolve().parents[2]
    print(f"{platform.system()} numpy {np.__version__} torch {torch.__version__}, aromir from {source}, release "
          f"v{release.network_version}", flush=True)
    saved: dict[str, np.ndarray] = {}
    skipped = []
    for molecule_id in ids_file.read_text(encoding="utf-8").split():
        folder = corpus / molecule_id
        if not (folder / LOW_HESSIAN).is_file():
            skipped.append(molecule_id)
            continue
        stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
        geometry = Geometry(tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
        with np.load(folder / LOW_HESSIAN) as low:
            hessian = np.array(low["H_projected"], float)
        corrections = release.corrections(geometry, hessian)
        saved[f"{molecule_id}/delta_h"] = np.array(corrections.per_seed)
        saved[f"{molecule_id}/bands_cm"] = bands_cm(hessian + corrections.mean, geometry)
        print(f"  {molecule_id} {geometry.n_atoms:>3} atoms: max|dH| per seed "
              + " ".join(f"{np.abs(dh).max():.6g}" for dh in corrections.per_seed), flush=True)
    tmp = target.with_name(target.name + ".tmp.npz")
    np.savez_compressed(tmp, **saved)
    os.replace(tmp, target)
    print(f"{len(saved) // 2} molecules written to {target.name}; skipped (no {LOW_HESSIAN}): {skipped}")


if __name__ == "__main__":
    main()
