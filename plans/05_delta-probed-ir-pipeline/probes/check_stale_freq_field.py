"""TASKS 147: the corpus analytic Hessian files whose stored `freq_cm` differs from the frequencies of their own `H_projected` (files written
before the software stamp of 11 Oct 2026), and whether any of them could change an imaginary-mode verdict: the second-route reader
(`corpus/read_imaginary_second_route.py`) calls a mode healed at ≥ 10 cm⁻¹ and genuine below 0, so a file is at risk when its lowest
frequency, stored or recomputed, lies within the two's difference of either bound, or the two fall on different sides of one.

    python probes/check_stale_freq_field.py [--out <prefix>]     # → <prefix>.md and .json (default modules/05_support_predictor/out/stale_freq_field)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
from rungC_intensities import mode_intensities  # noqa: E402  (after the sys.path insert)

CORPUS = M05 / "corpus" / "molecules"
VIB_MIN_CM = 20.0                      # mode_intensities' vibrational threshold
STALE_CM = 0.01                        # above this the stored field is not its own Hessian's (stamped files agree to 1e-10)
BOUNDS_CM = (0.0, 10.0)                # read_imaginary_second_route.py: genuine below 0, healed at ≥ 10


def own_frequencies(path: Path) -> tuple[np.ndarray, np.ndarray, bool]:
    """(stored vibrational freq_cm, recomputed from H_projected, both sorted; whether the file carries the software stamp)."""
    with np.load(path) as z:
        stored, H, stamped = np.asarray(z["freq_cm"], float), z["H_projected"], "software" in z.files
    masses = np.asarray(json.loads((path.parent / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    own = mode_intensities(H, masses, np.zeros((3, H.shape[0])))[0]
    return np.sort(stored[np.abs(stored) > VIB_MIN_CM]), np.sort(own), stamped


def at_risk(stored_low: float, own_low: float, gap: float) -> list[str]:
    """The bounds a file's lowest frequency could cross: within `gap` of the bound, or the stored and recomputed values on its two sides."""
    return [f"{b:g} cm⁻¹" for b in BOUNDS_CM if min(abs(stored_low - b), abs(own_low - b)) <= gap or (stored_low - b) * (own_low - b) < 0]


def survey(corpus: Path = CORPUS) -> dict:
    stale, counts = [], {"stamped": 0, "unstamped": 0, "count_mismatch": 0}
    for f in sorted(corpus.glob("*/hessian_*_analytic.npz")):
        stored, own, stamped = own_frequencies(f)
        counts["stamped" if stamped else "unstamped"] += 1
        if len(stored) != len(own):
            counts["count_mismatch"] += 1
            stale.append(dict(id=f.parent.name, file=f.name, stamped=stamped, max_abs_diff_cm=None, note=f"{len(stored)} stored, {len(own)} own"))
            continue
        d = float(np.abs(stored - own).max())
        if d > STALE_CM:
            stale.append(dict(id=f.parent.name, file=f.name, stamped=stamped, max_abs_diff_cm=round(d, 3),
                              stored_lowest_cm=round(float(stored[0]), 2), own_lowest_cm=round(float(own[0]), 2),
                              at_risk=at_risk(float(stored[0]), float(own[0]), d)))
    return {"counts": counts, "stale": stale}


def report(s: dict) -> str:
    c = s["counts"]
    risky = [r for r in s["stale"] if r.get("at_risk") or r["max_abs_diff_cm"] is None]
    lines = ["# Analytic Hessian files with a stale `freq_cm` field (TASKS 147)", "",
             f"{c['stamped'] + c['unstamped']} files: {c['stamped']} with the software stamp, {c['unstamped']} without; "
             f"{len(s['stale'])} store a `freq_cm` more than {STALE_CM} cm⁻¹ from their own `H_projected`; {c['count_mismatch']} differ in mode count. "
             f"Files whose lowest frequency could cross a verdict bound ({', '.join(f'{b:g}' for b in BOUNDS_CM)} cm⁻¹): {len(risky)}.", "",
             "| molecule | file | stamped | largest difference (cm⁻¹) | lowest, stored | lowest, own | bound at risk |", "|---|---|---|---|---|---|---|"]
    for r in s["stale"]:
        lines.append(f"| {r['id']} | {r['file']} | {'yes' if r['stamped'] else 'no'} | {r['max_abs_diff_cm']} | {r.get('stored_lowest_cm', '—')} | "
                     f"{r.get('own_lowest_cm', '—')} | {', '.join(r.get('at_risk', [])) or r.get('note') or 'none'} |")
    return "\n".join(lines) + "\n"


def write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=M05 / "out" / "stale_freq_field")
    a = ap.parse_args(argv)
    s = survey()
    text = report(s)
    write(a.out.with_suffix(".md"), text)
    write(a.out.with_suffix(".json"), json.dumps(s, indent=1, ensure_ascii=False))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
