"""Check the calculations against the laboratory, using data this repository can reach.

The bay conclusion rested on B3LYP alone, and a chat then produced argon-matrix
numbers that appeared to contradict the route to it. Those numbers were third-hand.
The paper they came from - Hudgins & Sandford 1998, J. Phys. Chem. A 102, 329,
doi:10.1021/jp9834816 - is closed access with no repository copy.

The same measurements are open, however. The NASA Ames PAH IR Spectroscopic
Database carries the laboratory library, and every band below is read off the
experimental database, version 2.00, with the species uid recorded so anyone can
re-open the page:

    https://www.astrochemistry.org/pahdb/experimental/2.00/default/details/<uid>/transitions

Each of these species lists Hudgins & Sandford (1998) as its reference, so this is
the same experiment, obtained without the paywall. Argon matrix, CsI window at
10-15 K, neutral species.

WHAT IS COMPARED, AND WHY IT IS ALLOWED

  Only the quartet series carries a conclusion. Its assignment needs no judgement:
  for every quartet-bearing molecule the quartet band is the strongest band in the
  600-1000 cm-1 window, and the script REFUSES to proceed if that margin is thin -
  which is the mistake that produced a spurious -126.8 cm-1 earlier in this
  campaign, when two bands at 66.1 and 66.0 km/mol were separated by a coin flip.

  The remaining classes are printed for information with their assignment gap
  visible, and nothing is concluded from them here.

  Matrix data may sit 15 cm-1 from calculation under this project's frozen
  tolerances; gas-phase data 10. These are matrix numbers.

A CORRECTION THIS SCRIPT FORCED

  The commit of 2026-08-27 argued that the bay is not additive because two
  independent one-bay steps came out +6.5 and +16.8, "differing by 10.3 cm-1, the
  entire tolerance". That comparison is wrong. The claim being tested is that ONE
  constant serves every bay, and fitting one constant to two points absorbs half
  their difference: the residual is 5.2, not 10.3. Two points cannot refute a
  one-parameter law.

  The laboratory says the same thing: +9.4 and +18.1, one constant, residual 4.4.
  Additivity survives both, on two pairs.

  What breaks it is triphenylene, three bays and no shift - and triphenylene is not
  in the experimental database, so that half of the argument has no laboratory
  counterpart and is calculation-only.

Run:  python pahdb_experimental_2026-08-28.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
RESULTS = HERE / "batch_results"
SCALE = 673.0 / 694.9      # harmonic correction, fitted on benzene alone
WINDOW = (600.0, 1000.0)
MIN_MARGIN = 1.20          # strongest band must beat the runner-up by this factor
MATRIX_TOLERANCE = 15.0

# NASA Ames PAH IR Spectroscopic Database, experimental v2.00, read 2026-08-28.
# (uid, [(wavenumber cm-1, integrated absorbance km/mol), ...]) inside WINDOW only.
# Reference for every entry: Hudgins & Sandford 1998, doi:10.1021/jp9834816.
LAB = {
    "naphthalene": (330, [(785.8, 108.0), (957.6, 3.25), (620.3, 4.34)]),
    "anthracene": (265, [(725.6, 84.3), (878.3, 66.2), (906.8, 0.843),
                         (954.9, 5.9), (602.9, 7.83)]),
    "phenanthrene": (273, [(735.0, 84.3), (812.8, 58.4), (864.9, 10.2),
                           (877.6, 1.69), (833.0, 1.69), (948.2, 2.53),
                           (710.2, 3.37), (617.5, 5.06)]),
    "tetracene": (282, [(742.9, 102.0), (895.3, 84.3), (953.6, 8.43),
                        (933.4, 2.05), (997.1, 7.22), (766.7, 1.02), (627.7, 1.02)]),
    "chrysene": (291, [(761.0, 114.0), (812.6, 56.0), (861.8, 9.03),
                       (880.1, 3.43), (852.7, 1.14), (945.9, 2.29), (682.4, 12.6)]),
    "pyrene": (334, [(842.8, 108.0), (821.5, 5.42), (743.9, 18.7),
                     (711.8, 46.4), (964.1, 1.08)]),
    "coronene": (18, [(857.0, 175.0), (846.1, 1.75), (771.6, 19.3)]),
}

# Computed here, in the same repository. Absent from the experimental database:
# triphenylene, which is why the chat's "triphenylene 740.8 Ar-matrix" has no
# source and must not be used.
COMPUTED = {
    "naphthalene": HERE / "results_dft_locality" / "naphthalene",
    "anthracene": HERE / "results_dft_locality" / "anthracene",
    "phenanthrene": RESULTS / "02_freq_phenanthrene",
    "tetracene": RESULTS / "03_freq_tetracene",
    "chrysene": RESULTS / "04_freq_chrysene",
    "triphenylene": RESULTS / "05_freq_triphenylene",
    "pyrene": RESULTS / "06_freq_pyrene",
    "coronene": RESULTS / "07_freq_coronene",
}

# Two 0 -> 1 bay steps at fixed formula and fixed ring count.
ONE_BAY_PAIRS = [("anthracene", "phenanthrene", "C14H10"),
                 ("tetracene", "chrysene", "C18H12")]

CLASS_NAME = {1: "solo", 2: "duo", 3: "trio", 4: "quartet", 5: "quintet", 6: "sextet"}


def probe_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def strongest_in_window(bands):
    """The loudest band, and the factor by which it beats the runner-up."""
    ordered = sorted(bands, key=lambda b: -b[1])
    if len(ordered) == 1:
        return ordered[0], float("inf")
    return ordered[0], ordered[0][1] / max(ordered[1][1], 1e-9)


def main():
    bay = probe_module("bay", "bay_series_2026-08-27.py")
    dft = bay.probe_module()

    computed = {}
    for name, stem in COMPUTED.items():
        if not (stem.with_suffix(".json").exists() and stem.with_suffix(".npz").exists()):
            continue
        data = json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))
        bands = bay.class_bands(dft, data, stem.with_suffix(".npz"))
        computed[name] = {size: b["centre"] * SCALE for size, b in bands.items()}

    print("IS THE LOUDEST BAND UNAMBIGUOUS?")
    print("The quartet assignment is only allowed if the strongest band in the")
    print(f"600-1000 window beats the next one by at least {MIN_MARGIN:.2f}x.\n")
    print(f"{'molecule':<14}{'uid':>5}{'loudest':>10}{'km/mol':>9}{'margin':>9}")
    print("-" * 47)
    loudest = {}
    for name, (uid, bands) in LAB.items():
        (nu, inten), margin = strongest_in_window(bands)
        loudest[name] = (nu, inten, margin)
        flag = "" if margin >= MIN_MARGIN else "   REFUSED"
        shown = "inf" if margin == float("inf") else f"{margin:.2f}x"
        print(f"{name:<14}{uid:>5}{nu:>10.1f}{inten:>9.1f}{shown:>9}{flag}")

    quartets = [n for n in ("naphthalene", "anthracene", "phenanthrene",
                            "tetracene", "chrysene")
                if n in loudest and loudest[n][2] >= MIN_MARGIN and 4 in computed.get(n, {})]
    print(f"\n{len(quartets)} of 5 quartet molecules pass. Those are the comparison.")

    print("\n\nQUARTET BAND: CALCULATION AGAINST LABORATORY")
    print(f"B3LYP/6-31G* harmonic, one scale factor fitted on benzene, versus argon")
    print(f"matrix. This project allows {MATRIX_TOLERANCE:.0f} cm-1 against matrix data.\n")
    print(f"{'molecule':<14}{'bays':>5}{'computed':>10}{'lab':>9}{'diff':>8}   verdict")
    print("-" * 60)
    errors = []
    for name in quartets:
        ours = computed[name][4]
        lab = loudest[name][0]
        diff = ours - lab
        errors.append(abs(diff))
        bays = next(b for n, s, f, b in dft.MOLECULES if n == name)
        verdict = "within" if abs(diff) <= MATRIX_TOLERANCE else "OUTSIDE"
        print(f"{name:<14}{bays:>5}{ours:>10.1f}{lab:>9.1f}{diff:>+8.1f}   {verdict}")
    print(f"\n   mean |error| {np.mean(errors):.1f} cm-1, worst {max(errors):.1f} cm-1")

    print("\n\nTHE BAY STEP, MEASURED IN THE LABORATORY")
    print("The same two controlled pairs, now with lab numbers on both sides.\n")
    print(f"{'formula':<10}{'0 bays':>26}{'1 bay':>26}")
    print("-" * 64)
    lab_steps, our_steps = [], []
    for flat, bayed, formula in ONE_BAY_PAIRS:
        if not all(n in loudest and n in computed for n in (flat, bayed)):
            continue
        lab_step = loudest[bayed][0] - loudest[flat][0]
        our_step = computed[bayed][4] - computed[flat][4]
        lab_steps.append(lab_step)
        our_steps.append(our_step)
        print(f"{formula:<10}{flat + ' ' + format(loudest[flat][0], '.1f'):>26}"
              f"{bayed + ' ' + format(loudest[bayed][0], '.1f'):>26}")
        print(f"{'':<10}{'lab step':>18}{lab_step:>+8.1f}"
              f"{'computed step':>18}{our_step:>+8.1f}")

    # The claim under test is "one additive constant serves every bay". So fit that
    # one constant and look at what it leaves over. Comparing the two steps to each
    # other instead - as an earlier commit did - double counts, because a fitted
    # constant absorbs half of their difference.
    print("\n   TESTING THE CLAIM THAT WAS ACTUALLY MADE")
    print("   Fit a single additive bay constant to both pairs and see what is left.\n")
    for label, steps in (("laboratory", lab_steps), ("calculation", our_steps)):
        if len(steps) < 2:
            continue
        constant = float(np.mean(steps))
        residual = max(abs(s - constant) for s in steps)
        verdict = ("survives" if residual <= MATRIX_TOLERANCE else "fails")
        print(f"   {label:<12} constant {constant:+.1f} cm-1, worst residual "
              f"{residual:.1f} -> additivity {verdict} on these two pairs")

    print("\n   Two pairs cannot refute an additive constant: two points always fit")
    print("   one free parameter to within half their spread. What breaks additivity")
    print("   is triphenylene, where three bays move the band by -1.2 instead of")
    print("   three times anything - and triphenylene is NOT in the experimental")
    print("   database. That part of the argument has no laboratory counterpart here.")

    print("\n\nCLASS SPREAD: DOES ONE CLASS HAVE ONE BAND?")
    print("This is the claim an atlas keyed on adjacency class actually makes, and")
    print("unlike the bay step it needs no fitted parameter at all.\n")
    print(f"{'class':>9}{'n':>3}{'lab spread':>13}{'computed spread':>18}")
    print("-" * 45)
    for size in (4,):
        lab_vals = [loudest[n][0] for n in quartets]
        our_vals = [computed[n][size] for n in quartets]
        print(f"{CLASS_NAME[size]:>9}{len(lab_vals):>3}"
              f"{max(lab_vals) - min(lab_vals):>12.1f} "
              f"{max(our_vals) - min(our_vals):>17.1f}")
    print(f"\n   Against a tolerance of {MATRIX_TOLERANCE:.0f} cm-1. The laboratory spread is")
    print("   the one that matters, and it is not smaller than the calculated one.")

    print("\n\nEVERY CLASS, EVERY MOLECULE - information only, nothing concluded")
    print("Each computed class band is shown next to the nearest laboratory band and")
    print("the gap to it. A large gap means the assignment is a guess, not a match.\n")
    print(f"{'molecule':<14}{'class':>9}{'computed':>10}{'nearest lab':>13}"
          f"{'km/mol':>9}{'gap':>8}")
    print("-" * 63)
    for name in COMPUTED:
        if name not in computed:
            continue
        if name not in LAB:
            print(f"{name:<14}{'':>9}{'':>10}   not in the experimental database")
            continue
        bands = LAB[name][1]
        for size in sorted(computed[name], reverse=True):
            ours = computed[name][size]
            nu, inten = min(bands, key=lambda b: abs(b[0] - ours))
            print(f"{name:<14}{CLASS_NAME[size]:>9}{ours:>10.1f}{nu:>13.1f}"
                  f"{inten:>9.1f}{ours - nu:>+8.1f}")

    what_a_band_tells_you(dft, bay, loudest)


def what_a_band_tells_you(dft, bay, loudest):
    """Two different questions get two different answers, and both are in the data.

    Astronomy asks: given a band position, which EDGE TYPE is out there? This thesis
    asks: given an edge type, WHERE is the band, to ten wavenumbers? The first can
    succeed while the second fails, and the numbers below say that it does.
    """
    print("\n\n" + "=" * 66)
    print("WHAT A BAND POSITION CAN AND CANNOT TELL YOU")
    print("=" * 66)

    # Which class owns the loudest band is not decided by eye: it is the class the
    # calculation says carries the most infrared intensity. Edge counts are PAHdb's
    # own, not this repository's, so the classification is an independent source.
    print("\nAssigning the loudest laboratory band to a class. The owner is the class")
    print("carrying the most computed infrared intensity; edge counts are PAHdb's.\n")
    print(f"{'molecule':<14}{'PAHdb edges':>26}{'owner':>9}{'share':>7}{'lab band':>10}")
    print("-" * 68)

    owned = {}
    for name, (uid, _) in LAB.items():
        stem = COMPUTED.get(name)
        if stem is None or not stem.with_suffix(".npz").exists():
            continue
        data = json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))
        bands = bay.class_bands(dft, data, stem.with_suffix(".npz"))
        owner = max(bands, key=lambda s: bands[s]["share_of_total_intensity"])
        share = bands[owner]["share_of_total_intensity"]
        edges = ", ".join(f"{bands[s]['n_groups']} {CLASS_NAME[s]}"
                          for s in sorted(bands, reverse=True))
        owned.setdefault(owner, []).append((name, loudest[name][0]))
        print(f"{name:<14}{edges:>26}{CLASS_NAME[owner]:>9}{share:>6.0%}"
              f"{loudest[name][0]:>10.1f}")

    print("\n\nQUESTION 1 - can you read the EDGE TYPE off a band position?")
    print("This is what astronomers do with the 11-15 micron region.\n")
    print(f"{'class':>9}{'molecules':>11}{'window':>18}{'width':>8}")
    print("-" * 47)
    windows = {}
    for size in sorted(owned):
        vals = [v for _, v in owned[size]]
        lo, hi = min(vals), max(vals)
        windows[size] = (lo, hi)
        print(f"{CLASS_NAME[size]:>9}{len(vals):>11}{f'{lo:.1f} - {hi:.1f}':>18}{hi - lo:>8.1f}")

    sizes = sorted(windows, key=lambda s: windows[s][0])   # by position, not class number
    print()
    overlap = False
    gaps = []
    for a, b in zip(sizes, sizes[1:]):
        gap = windows[b][0] - windows[a][1]
        gaps.append(gap)
        if gap > 0:
            print(f"   {CLASS_NAME[a]} and {CLASS_NAME[b]} do not overlap: "
                  f"{gap:.1f} cm-1 of empty space between them")
        else:
            overlap = True
            print(f"   {CLASS_NAME[a]} and {CLASS_NAME[b]} OVERLAP by {-gap:.1f} cm-1")
    widest = max(hi - lo for lo, hi in windows.values())
    if not overlap:
        print(f"\n   So yes. A band in one window names the edge type. The smallest gap")
        print(f"   between windows is {min(gaps):.1f} cm-1 and the widest window is "
              f"{widest:.1f} cm-1,")
        print("   so the separation is about the size of the scatter inside a class -")
        print("   comfortable enough to classify, nowhere near clean.")

    print("\n\nQUESTION 2 - can you read the MOLECULE off a band position?\n")
    for size in sizes:
        names = ", ".join(n for n, _ in owned[size])
        print(f"   {CLASS_NAME[size]:>7} window holds {len(owned[size])} of the "
              f"{sum(len(v) for v in owned.values())} measured molecules: {names}")
    biggest = max(owned.values(), key=len)
    print(f"\n   No. {len(biggest)} different molecules put their loudest band inside one")
    print("   window, and those are only the ones somebody has measured. Every larger")
    print("   PAH with the same edge type lands there too. The band names a building")
    print("   block, never a species.")

    print("\n\nQUESTION 3 - is the class enough to PREDICT a band to this project's")
    print(f"tolerance of {MATRIX_TOLERANCE:.0f} cm-1?\n")
    for size in sizes:
        vals = [v for _, v in owned[size]]
        centre = float(np.mean(vals))
        worst = max(abs(v - centre) for v in vals)
        verdict = "passes" if worst <= MATRIX_TOLERANCE else "FAILS"
        print(f"   {CLASS_NAME[size]:>7}: best single guess {centre:.1f}, worst miss "
              f"{worst:.1f} cm-1 -> {verdict}")

    print("\n   Knowing nothing at all, a CH out-of-plane band could sit anywhere in")
    print("   the 600-1000 window, a range of 400 cm-1. Knowing the edge type narrows")
    print("   that to a few tens. That is a large gain and it is still an order of")
    print("   magnitude short of what this thesis promised.")

    print("\n\nBOTH ANSWERS AT ONCE")
    print("   The edge type is readable from the spectrum, and that is exactly why")
    print("   the molecule is not: many species share an edge type and pile into the")
    print("   same window. The same fact that makes the classification work makes")
    print("   identification impossible.")
    print("   And a window is not a prediction. A method that only reproduces the")
    print("   window has reproduced what the field already had in the 1980s.")


if __name__ == "__main__":
    main()
