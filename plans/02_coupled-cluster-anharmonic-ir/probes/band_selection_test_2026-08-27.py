"""Does using the whole molecule instead of a frozen ring recover the missing 56 cm-1?

verify_oop_bands_2026-08-27.py measured, from NIST gas-phase spectra, that the
quartet CH out-of-plane band sits at 781.5 cm-1 in naphthalene and 725.6 in
anthracene: a 56 cm-1 gap between two molecules carrying the same edge motif.

The locality probe's frozen local basis reproduced that gap as 6 cm-1. Nine times
too small. The suspicion is that freezing every atom outside the CH run throws away
exactly the ring participation that carries the difference.

This tests that suspicion on the three cases where a measured value exists, using
stored Hessians so nothing is recomputed.

Run:  & "$env:USERPROFILE\\.conda\\envs\\qc\\python.exe" band_selection_test_2026-08-27.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
EXPERIMENT = {
    ("benzene", 6): 673.0,
    ("naphthalene", 4): 781.5,
    ("anthracene", 4): 725.6,
    ("anthracene", 1): 875.2,
}


def load_probe():
    spec = importlib.util.spec_from_file_location("dft", HERE / "dft_locality_2026-08-26.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    d = load_probe()
    from rdkit import Chem

    rows = []
    for name, smiles, expect, _ in d.MOLECULES:
        raw = d.RESULTS / f"{name}.npz"
        if not raw.exists():
            continue
        store = np.load(raw)
        hess = store["hessian_au"]
        coords_bohr = store["coords_bohr"]
        masses = store["masses_amu"]
        coords_ang = coords_bohr * d.BOHR_TO_ANG

        mol = d.rdkit_molecule(name, smiles, expect)
        pairs = d.ch_pairs(mol)
        hmw = d.mass_weighted(hess, masses, coords_bohr)

        centred = coords_ang - coords_ang.mean(axis=0)
        normal = np.linalg.svd(centred)[2][2]
        v_oop = d.local_basis(pairs, coords_ang, masses, lambda c, h: normal)
        w_oop = v_oop.T @ hmw @ v_oop
        nu_oop = d.K_AU * np.sqrt(np.abs(np.diag(w_oop)))

        for run in d.adjacency_runs(mol, pairs):
            exp = EXPERIMENT.get((name, len(run)))
            if exp is None:
                continue
            block = w_oop[np.ix_(run, run)]
            eigvals, eigvecs = np.linalg.eigh(block)
            frozen = d.K_AU * np.sqrt(abs(eigvals[int(np.argmax(np.abs(eigvecs.sum(axis=0))))]))
            band = d.band_from_normal_modes(run, v_oop, hmw)
            rows.append((name, len(run), frozen, band, exp))

    if not rows:
        print("No stored Hessians yet. Run dft_locality_2026-08-26.py first.")
        return

    print("Band position against measured NIST gas-phase spectra")
    print("=" * 78)
    print(f"{'molecule':<14}{'class':>9}{'frozen':>9}{'best mode':>11}{'centroid':>10}"
          f"{'overlap':>9}{'measured':>10}")
    print("-" * 78)
    seen, errs = set(), {"frozen": [], "best": [], "centroid": []}
    for name, size, frozen, band, exp in rows:
        if (name, size) in seen:
            continue
        seen.add((name, size))
        errs["frozen"].append(frozen - exp)
        errs["best"].append(band["band_best_mode"] - exp)
        errs["centroid"].append(band["band_centroid"] - exp)
        print(f"{name:<14}{d.CLASS_NAME[size]:>9}{frozen:>9.1f}"
              f"{band['band_best_mode']:>11.1f}{band['band_centroid']:>10.1f}"
              f"{band['max_overlap']:>9.2f}{exp:>10.1f}")

    print("\nERRORS AGAINST EXPERIMENT")
    print(f"{'method':<22}{'mean |error|':>14}{'range':>22}")
    print("-" * 58)
    for key, label in (("frozen", "frozen local basis"), ("best", "best normal mode"),
                       ("centroid", "overlap centroid")):
        e = np.array(errs[key])
        print(f"{label:<22}{np.abs(e).mean():>13.1f} {f'{e.min():+.1f} to {e.max():+.1f}':>22}")

    quartets = {n: b for n, s, f, b, _ in rows if s == 4 for _ in [0]}
    frozen_q = {n: f for n, s, f, b, _ in rows if s == 4}
    if {"naphthalene", "anthracene"} <= set(frozen_q):
        print("\nTHE GAP THAT STARTED THIS: quartet, naphthalene minus anthracene")
        print(f"  measured                {781.5 - 725.6:+.1f} cm^-1")
        print(f"  frozen local basis      {frozen_q['naphthalene'] - frozen_q['anthracene']:+.1f}")
        for key, label in (("band_best_mode", "best normal mode"),
                           ("band_centroid", "overlap centroid")):
            gap = quartets["naphthalene"][key] - quartets["anthracene"][key]
            print(f"  {label:<22}{gap:+.1f}")
        print("\nRecovering the gap matters more than matching any single position:")
        print("a transfer law lives or dies on differences between host molecules.")


if __name__ == "__main__":
    main()
