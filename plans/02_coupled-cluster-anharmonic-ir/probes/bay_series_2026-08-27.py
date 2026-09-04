"""Assign each infrared band to an adjacency class, instead of guessing by intensity.

The controlled series - tetracene, chrysene, triphenylene, all C18H12 with four
rings and 0, 1 and 3 bays - was supposed to settle whether the bay is an additive
motif effect. Reading it off the strongest band gave -126.8 cm-1 for one bay and
-48.8 per bay for three, which is not a trend, it is nonsense.

The reason is visible in the intensities. Tetracene has two bands at 66.1 and 66.0
km/mol. One is its quartet edge and the other its solo edge, and "strongest" chose
between them on a difference of 0.1. A rule that decides a 127 cm-1 result by a coin
flip is not a rule.

WHAT THIS DOES INSTEAD

  For every adjacency class in a molecule, build the in-phase out-of-plane wag over
  all runs of that class. Project it onto the real normal modes. Weight by infrared
  intensity. The band of a class is then the intensity-weighted centre of the modes
  that actually carry that class's motion.

  No band is compared across molecules unless both sides are the same class, which
  is the whole point of a controlled series.

Everything comes from stored Hessians, so this costs seconds rather than hours.

Run:  & "$env:USERPROFILE\\.conda\\envs\\qc\\python.exe" bay_series_2026-08-27.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
RESULTS = HERE / "batch_results"
SCALE = 673.0 / 694.9          # harmonic correction, fitted on benzene alone
MIN_OVERLAP = 0.02             # ignore modes that barely touch the class

SERIES = [
    ("tetracene", "03_freq_tetracene", 0),
    ("chrysene", "04_freq_chrysene", 1),
    ("triphenylene", "05_freq_triphenylene", 3),
]

# Every molecule with a stored Hessian, whatever run produced it. Missing entries
# are skipped, so this stays runnable while the queue is still working.
SURVEY = [
    (HERE / "results_dft_locality" / "benzene", 0),
    (HERE / "results_dft_locality" / "naphthalene", 0),
    (HERE / "results_dft_locality" / "anthracene", 0),
    (RESULTS / "02_freq_phenanthrene", 1),
    (RESULTS / "03_freq_tetracene", 0),
    (RESULTS / "04_freq_chrysene", 1),
    (RESULTS / "05_freq_triphenylene", 3),
    (RESULTS / "06_freq_pyrene", 0),
    (RESULTS / "07_freq_coronene", 0),
]

# Two independent 0 -> 1 bay steps at fixed formula and fixed ring count.
ONE_BAY_PAIRS = [("anthracene", "phenanthrene", "C14H10"),
                 ("tetracene", "chrysene", "C18H12")]

TOLERANCE_CM = 10.0            # the accuracy the atlas would have to reach

CLASS_NAME = {1: "solo", 2: "duo", 3: "trio", 4: "quartet", 5: "quintet", 6: "sextet"}


def probe_module():
    spec = importlib.util.spec_from_file_location(
        "dft", HERE / "dft_locality_2026-08-26.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def class_bands(dft, data, npz):
    """Band centre per adjacency class, backfilled from a stored Hessian.

    Uses dft.class_band_centres, the same function the pipeline now calls, so the
    results committed before that function existed and the ones produced after it
    are the same quantity computed by the same code.
    """
    store = np.load(npz)
    coords_ang = store["coords_bohr"] * dft.BOHR_TO_ANG
    masses = store["masses_amu"]
    pairs = [tuple(p) for p in store["pairs"]]

    hmw = dft.mass_weighted(store["hessian_au"], masses, store["coords_bohr"])
    normal = np.linalg.svd(coords_ang - coords_ang.mean(axis=0))[2][2]
    basis = dft.local_basis(pairs, coords_ang, masses, lambda c, h: normal)

    smiles = next(s for n, s, f, b in dft.MOLECULES if n == data["molecule"])
    mol = dft.rdkit_molecule(data["molecule"], smiles, (data["n_c"], data["n_h"]))

    raw = dft.class_band_centres(mol, dft.ch_pairs(mol), basis, hmw, data["ir_spectrum"])
    return {int(k): dict(centre=v["centre_cm"],
                         share_of_total_intensity=v["ir_share"],
                         n_groups=v["n_groups"]) for k, v in raw.items()}


def main():
    dft = probe_module()

    print("CONTROLLED BAY SERIES - all C18H12, four rings")
    print("Band centre per adjacency class, intensity-weighted, scaled by %.5f" % SCALE)
    print()
    print(f"{'molecule':<14}{'bays':>5}{'class':>9}{'groups':>8}{'band':>10}{'IR share':>10}")
    print("-" * 56)

    table = {}
    for name, job, bays in SERIES:
        data = json.loads((RESULTS / f"{job}.json").read_text(encoding="utf-8"))
        bands = class_bands(dft, data, RESULTS / f"{job}.npz")
        table[name] = (bays, bands)
        for size in sorted(bands, reverse=True):
            b = bands[size]
            print(f"{name:<14}{bays:>5}{CLASS_NAME[size]:>9}{b['n_groups']:>8}"
                  f"{b['centre']*SCALE:>10.1f}{b['share_of_total_intensity']:>9.0%}")

    print("\n\nQUARTET AGAINST QUARTET - the only like-for-like comparison here")
    print("Every molecule in the series has quartet edges, so this is the test.\n")
    print(f"{'molecule':<14}{'bays':>6}{'quartet band':>14}{'vs 0 bays':>12}{'per bay':>10}")
    print("-" * 56)
    ref = table["tetracene"][1].get(4, {}).get("centre")
    if ref is None:
        print("  tetracene has no quartet band; the series cannot be compared.")
        return
    shifts = []
    for name, (bays, bands) in table.items():
        q = bands.get(4)
        if q is None:
            continue
        shift = (q["centre"] - ref) * SCALE
        per = shift / bays if bays else float("nan")
        shifts.append((bays, shift))
        print(f"{name:<14}{bays:>6}{q['centre']*SCALE:>14.1f}{shift:>+12.1f}"
              f"{(f'{per:+.1f}' if bays else '-'):>10}")

    print("\n\nVERDICT")
    print("The criterion was fixed before the calculations ran: a shift roughly")
    print("linear in bay count means the bay is an additive motif key; anything")
    print("else means it is not separable from shape.\n")
    nonzero = [(b, s) for b, s in shifts if b]
    if len(nonzero) >= 2:
        per_bay = [s / b for b, s in nonzero]
        spread = max(per_bay) - min(per_bay)
        for b, s in sorted(nonzero):
            print(f"   {b} bay(s): {s:+.1f} cm^-1  ->  {s/b:+.1f} per bay")
        print(f"\n   spread in per-bay shift: {spread:.1f} cm^-1")
        if spread < 5.0:
            print("   Linear. The bay is an additive motif effect and belongs in the atlas key.")
        else:
            print("   NOT linear, and not close. The shift does not scale with bay count,")
            print("   so the bay is not an additive motif property. An atlas keyed on")
            print("   adjacency class plus bay count cannot carry these band positions.")

    survey(dft)


def survey(dft):
    """Same class against same class across every molecule computed so far."""
    print("\n\nALL MOLECULES - what one adjacency class is worth on its own")
    print("An atlas keyed on class alone predicts one band per class. This is how")
    print(f"far apart that one band actually sits, against a {TOLERANCE_CM:.0f} cm^-1 tolerance.\n")
    print(f"{'molecule':<14}{'C':>4}{'H':>3}{'bays':>6}{'class':>9}{'groups':>8}"
          f"{'band':>10}{'IR share':>10}")
    print("-" * 64)

    seen = {}
    for stem, bays in SURVEY:
        if not (stem.with_suffix(".json").exists() and stem.with_suffix(".npz").exists()):
            continue
        data = json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))
        bands = class_bands(dft, data, stem.with_suffix(".npz"))
        for size in sorted(bands, reverse=True):
            b = bands[size]
            centre = b["centre"] * SCALE
            seen.setdefault(size, []).append((data["molecule"], centre))
            print(f"{data['molecule']:<14}{data['n_c']:>4}{data['n_h']:>3}{bays:>6}"
                  f"{CLASS_NAME[size]:>9}{b['n_groups']:>8}{centre:>10.1f}"
                  f"{b['share_of_total_intensity']:>9.0%}")

    print(f"\n{'class':>9}{'molecules':>11}{'spread':>9}   positions")
    print("-" * 64)
    for size in sorted(seen):
        vals = seen[size]
        if len(vals) < 2:
            continue
        spread = max(v for _, v in vals) - min(v for _, v in vals)
        listed = ", ".join(f"{n} {v:.1f}" for n, v in vals)
        print(f"{CLASS_NAME[size]:>9}{len(vals):>11}{spread:>8.1f}   {listed}")

    print("\n\nTHE SAME BAY STEP, MEASURED TWICE")
    print("Two pairs, each 0 -> 1 bay at fixed formula and fixed ring count. If the")
    print("bay were a motif property the two steps would agree.\n")
    quartets = dict(seen.get(4, []))
    steps = []
    for flat, bayed, formula in ONE_BAY_PAIRS:
        if flat in quartets and bayed in quartets:
            step = quartets[bayed] - quartets[flat]
            steps.append(step)
            print(f"   {formula}: {flat} {quartets[flat]:.1f} -> {bayed} "
                  f"{quartets[bayed]:.1f}   {step:+.1f} cm^-1 for one bay")
    if len(steps) >= 2:
        disagreement = max(steps) - min(steps)
        print(f"\n   the two measurements of one bay differ by {disagreement:.1f} cm^-1")
        if disagreement > TOLERANCE_CM:
            print("   The bay step does not reproduce between two controlled pairs, so it")
            print("   is not a transferable number at all - not even a wrong constant.")


if __name__ == "__main__":
    main()
