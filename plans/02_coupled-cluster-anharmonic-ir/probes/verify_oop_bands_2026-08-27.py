"""Check the solo/duo/trio/quartet band positions against measured spectra.

Uitleg chapter 01 quoted 890 / 833 / 787 / 745 cm-1 for the CH out-of-plane bands
of solo, duo, trio and quartet hydrogens. Those numbers were written from recall.
The repository rule is that nothing is cited from recall, so this measures them.

METHOD

  Download the raw JCAMP-DX spectra from the NIST Chemistry WebBook, parse them,
  and locate the peaks directly. No intermediate source, no summary table, no
  textbook correlation chart -- the digitised experimental spectrum itself.

  Each molecule's CH adjacency classes are known from its structure, so a molecule
  containing only one class assigns that class unambiguously.

WHAT A PEAK POSITION IS WORTH HERE

  The NIST gas-phase grids are 4 cm-1; the solution grids are 1 cm-1. A parabolic
  fit through the three points around each maximum recovers a little below the grid
  spacing, but no position here is better than about +/- 2 cm-1, and gas and
  solution differ by a few cm-1 anyway because the solvent presses on the molecule.

  That is fine for the question being asked. We are checking whether a quoted value
  is right to within a few wavenumbers or wrong by tens.

Run:  python verify_oop_bands_2026-08-27.py
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import numpy as np

CACHE = Path(__file__).parent / "nist_cache"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36"}

# NIST uses "C" + CAS without punctuation.
# adjacency classes are counted from the structure: how many runs of k adjacent CH.
MOLECULES = [
    ("benzene",      "C71432",  {6: 1}),
    ("naphthalene",  "C91203",  {4: 2}),
    ("anthracene",   "C120127", {4: 2, 1: 2}),
    ("phenanthrene", "C85018",  {4: 2, 2: 1}),
    ("pyrene",       "C129000", {3: 2, 2: 2}),
    ("triphenylene", "C217594", {4: 3}),
    ("chrysene",     "C218019", {4: 2, 2: 2}),
]

CLAIMED = {1: 890.0, 2: 833.0, 3: 787.0, 4: 745.0}
CLASS_NAME = {1: "solo", 2: "duo", 3: "trio", 4: "quartet", 5: "quintet", 6: "sextet"}

OOP_WINDOW = (650.0, 950.0)


def fetch(nist_id, index):
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"{nist_id}_{index}.jdx"
    if path.exists():
        return path.read_text(encoding="utf-8")
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP={nist_id}&Index={index}&Type=IR"
    try:
        text = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)
        text = text.read().decode("utf-8", "replace")
    except Exception:
        return None
    if "##XYDATA" not in text:
        return None
    path.write_text(text, encoding="utf-8")
    return text


def parse(text):
    """JCAMP (X++(Y..Y)) in plain AFFN, which is what the WebBook serves.

    Each line carries its own starting X, so the axis is rebuilt from those rather
    than from FIRSTX/LASTX: several WebBook spectra are stitched from two segments
    and have a gap in the middle.
    """
    meta, rows, in_data = {}, [], False
    for line in text.splitlines():
        line = line.rstrip()
        if line.startswith("##"):
            in_data = line.startswith("##XYDATA")
            if "=" in line:
                key, val = line[2:].split("=", 1)
                meta[key.strip()] = val.strip()
            continue
        if in_data and line.strip():
            try:
                rows.append([float(t) for t in line.split()])
            except ValueError:
                pass

    n = int(meta["NPOINTS"])
    step = (float(meta["LASTX"]) - float(meta["FIRSTX"])) / (n - 1)
    yfactor = float(meta.get("YFACTOR", 1))

    xs, ys = [], []
    for row in rows:
        x0, vals = row[0], row[1:]
        xs.extend(x0 + j * step for j in range(len(vals)))
        ys.extend(v * yfactor for v in vals)

    order = np.argsort(xs)
    return meta, np.array(xs)[order], np.array(ys)[order]


def peaks_in_window(x, y, absorbance):
    """Return (position, relative height) for maxima, strongest first.

    A spectrum where several peaks tie at full height is a flat or noisy stretch,
    not a band, and is rejected: one WebBook benzene entry is exactly that and
    would otherwise contribute a fictitious 772 cm-1 line.
    """
    signal = y if absorbance else -y
    mask = (x >= OOP_WINDOW[0]) & (x <= OOP_WINDOW[1])
    if mask.sum() < 5:
        return [], 0.0
    xs, ys = x[mask], signal[mask]
    span = ys.max() - ys.min()
    if span <= 0:
        return [], 0.0
    step = xs[1] - xs[0]
    found = []
    for i in range(1, len(ys) - 1):
        if ys[i] > ys[i - 1] and ys[i] >= ys[i + 1]:
            a, b, c = ys[i - 1], ys[i], ys[i + 1]
            denom = a - 2 * b + c
            shift = 0.5 * (a - c) / denom if denom else 0.0
            found.append((float(xs[i] + shift * step), float((b - ys.min()) / span)))
    found.sort(key=lambda t: -t[1])
    if sum(1 for _, rel in found if rel > 0.95) >= 3:
        return [], float(step)
    return found, float(step)


def main():
    print("Measured CH out-of-plane bands, from NIST digitised spectra")
    print("=" * 74)

    observed = {}
    for name, nist_id, classes in MOLECULES:
        label = " + ".join(f"{n}x{CLASS_NAME[k]}" for k, n in sorted(classes.items(), reverse=True))
        print(f"\n{name}  ({label})")

        any_data = False
        for index in range(4):
            text = fetch(nist_id, index)
            if text is None:
                continue
            meta, x, y = parse(text)
            state = meta.get("STATE", "?")
            absorbance = "ABS" in meta.get("YUNITS", "").upper()
            found, step = peaks_in_window(x, y, absorbance)
            if not found:
                continue
            any_data = True
            strong = [p for p in found if p[1] > 0.15][:4]
            listed = "  ".join(f"{pos:.0f}({rel:.2f})" for pos, rel in strong)
            print(f"   {state[:38]:<38} grid {step:.0f} cm-1 : {listed}")

            # Assign only when the band count matches the class count. Ordering rule:
            # more adjacent hydrogens push the in-phase mode DOWN, so the class with
            # the fewest H takes the highest band. That is an assumption, not a
            # measurement, and it is the only one in this file.
            if len(strong) == len(classes):
                by_freq = sorted(strong, key=lambda t: -t[0])
                by_size = sorted(classes, reverse=False)
                for size, (pos, _) in zip(by_size, by_freq):
                    observed.setdefault(size, []).append((name, pos))
        if not any_data:
            print("   no usable spectrum")

    print("\n" + "=" * 74)
    print("MEASURED AGAINST CLAIMED")
    print("=" * 74)
    print(f"{'class':>9}{'molecule':>15}{'measured':>11}{'claimed':>10}{'difference':>13}")
    print("-" * 58)
    for size in sorted(observed):
        claimed = CLAIMED.get(size)
        for mol, pos in observed[size]:
            diff = f"{pos - claimed:+.0f}" if claimed else "-"
            print(f"{CLASS_NAME[size]:>9}{mol:>15}{pos:>11.1f}"
                  f"{(f'{claimed:.0f}' if claimed else '-'):>10}{diff:>13}")

    print("\nSPREAD OF ONE CLASS ACROSS MOLECULES")
    print("-" * 58)
    for size in sorted(observed):
        vals = [p for _, p in observed[size]]
        if len(vals) < 2:
            print(f"{CLASS_NAME[size]:>9}   only one molecule, no spread measurable")
            continue
        print(f"{CLASS_NAME[size]:>9}   {min(vals):.0f} to {max(vals):.0f} cm-1"
              f"   spread {max(vals)-min(vals):.0f}")

    print("\nCheck: are the claimed values just round wavelengths turned around?")
    for size, claimed in sorted(CLAIMED.items()):
        micron = 1e4 / claimed
        print(f"   {CLASS_NAME[size]:>7} {claimed:.0f} cm-1  <->  {micron:.2f} um")


if __name__ == "__main__":
    main()
