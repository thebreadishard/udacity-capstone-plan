"""Does the corpus hold any mode like coronene's 24 and 36 — and could we label one if it did? (TASKS 210.)

    python probes/anharmonic_coverage_screen.py <sets.json> <out dir> [--strain-min 0.08]

Coronene's two broken fundamentals carry solved shifts of +38.5 and +162.3 cm⁻¹ while the network predicts about −10, because nothing
in the training set resembles them. A candidate is only useful if its fundamental can be stated, so it needs both a large shift and a
breakdown a pair block covers (TASKS 209). The two conditions pull against each other, and this measures which modes satisfy both.

Modes are ranked by **strain**, |ν − ω| / ω, the diagnostic that marks a mode (`dpir.vpt2_domain`), not by the absolute shift: an
X–H stretch shifts −170 cm⁻¹ as perfectly sound VPT2 and would swamp any list ordered by size, while coronene's modes are a fifth of
their own frequency. The signature wanted here is a *large strain on a mode below the stretches*, which is the 11.2 µm region.

Per mode, from the label's ν(GVPT2) and the force field's own quartic constants:

    strain     |ν − ω| / ω
    shift      ν − ω
    diagonal   φ_iiii/8, the mode's own quartic contribution to its fundamental
    partner    the mode carrying the largest |x_ij|, as the solve chooses it, and the ½·φ_iijj/4 it contributes to the block
    outside    shift − (diagonal + partner): what a block of those two would leave to perturbation theory
    coverable  |outside| ≤ vpt2_domain.STRAIN_MAX × ω, the same tenth that marks a mode

The block's part is taken from the block's **own** constants, not from χ's x_ii: x_ii also holds the terms that run through other
modes, which are exactly what the block does not contain, and using it hid the whole effect — it called every strained mode coverable
where the real solve covers only coronene's.

This is a screen, not a reading. It leaves out the block's cubic contributions, which are second order where the quartic ones are
first, so `outside` is an estimate of what `probes/solve_marked_modes.py --block pair` would find — exact for coronene, whose block
    partner    the mode carrying the largest |x_ij|, as the solve chooses it, and the ½·φ_iijj/4 it adds to the block
which candidates are worth labelling, cheaply enough to run over every force field in hand.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))
from s2_read import write_atomic  # noqa: E402
from s2b_read import read_sets  # noqa: E402

from dpir.vpt2_domain import STRAIN_MAX  # noqa: E402

PLAN = HERE.parent
STRETCH_FLOOR_CM = 2000.0   # above this are the X-H stretches, whose large shifts are sound VPT2


def mode_rows(label: dict[str, Any], phi4: np.ndarray, chi: np.ndarray, source: str) -> list[dict[str, Any]]:
    """Every mode of one force field with its strain, the partner carrying its largest x_ij, and what a pair block of the two would
    leave outside."""
    omega, nu = np.asarray(label["omega"], float), np.asarray(label["nu_gvpt2"], float)
    for name, array in (("phi_iijj", phi4), ("chi", chi)):
        if array.shape != (omega.size, omega.size):
            raise ValueError(f"{label['id']}: {name} {array.shape} against {omega.size} modes")
    off = chi - np.diag(np.diag(chi))
    rows = []
    for i in range(omega.size):
        partner = int(np.abs(off[i]).argmax())
        diagonal = float(phi4[i, i]) / 8.0
        partner_half = 0.5 * float(phi4[i, partner]) / 4.0
        outside = float(nu[i] - omega[i]) - (diagonal + partner_half)
        rows.append({"id": label["id"], "source": source, "mode": i, "omega_cm": float(omega[i]),
                     "strain": abs(float(nu[i] - omega[i])) / max(float(omega[i]), 1.0),
                     "shift_cm": float(nu[i] - omega[i]), "diagonal_cm": diagonal, "partner": partner,
                     "partner_half_cm": partner_half, "outside_cm": outside,
                     "coverable": abs(outside) <= STRAIN_MAX * float(omega[i])})
    return rows


def screen(sets_path: str) -> list[dict[str, Any]]:
    """Every mode of every force field the sets file names, on both the DFT and the xtb side."""
    rows: list[dict[str, Any]] = []
    for s in read_sets(sets_path):
        for source, label_dir, root in (("G", s.gvpt2_dir, s.root), ("X", s.xtb_gvpt2_dir, s.xtb_root)):
            setting = "G" if source == "G" else "X"
            for name in sorted(os.listdir(PLAN / label_dir)):
                if not name.endswith(".json"):
                    continue
                label = json.loads((PLAN / label_dir / name).read_text(encoding="utf-8"))
                report = PLAN / root / label["id"] / setting / "qff_report.npz"
                if not report.is_file():
                    continue
                with np.load(report) as z:
                    if not {"phi_iijj_sym", "chi_sym"} <= set(z.files):
                        continue
                    phi4, chi = np.asarray(z["phi_iijj_sym"]), np.asarray(z["chi_sym"])
                rows.extend(mode_rows(label, phi4, chi, source))
    return rows


def report_lines(rows: list[dict[str, Any]], strain_min: float) -> list[str]:
    """How many strained modes there are, how many a pair block could cover, and the most strained of them."""
    strained = [r for r in rows if r["strain"] >= strain_min]
    coverable = [r for r in strained if r["coverable"]]
    below = [r for r in strained if r["omega_cm"] < STRETCH_FLOOR_CM]
    fields = {(r["id"], r["source"]) for r in rows}
    lines = [f"# Strained modes in the corpus (TASKS 210), strain at least {strain_min:g}", "",
             f"{len(rows)} modes over {len(fields)} force fields; {len(strained)} reach a strain of {strain_min:g}, of which "
             f"**{len(coverable)}** would be covered by a block of the mode and its largest partner, and {len(below)} sit below "
             f"{STRETCH_FLOOR_CM:g} cm⁻¹ — the region coronene's two broken modes are in, and the mandate's 11.2 µm band.", "",
             "| molecule | side | mode | ω | strain | shift | φ_iiii/8 | ½x_ij (partner) | outside | coverable |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(strained, key=lambda r: -r["strain"])[:20]:
        lines.append(f"| {r['id']} | {r['source']} | {r['mode']} | {r['omega_cm']:.1f} | {r['strain']:.3f} | "
                     f"{r['shift_cm']:+.1f} | {r['diagonal_cm']:+.1f} | {r['partner_half_cm']:+.1f} ({r['partner']}) | "
                     f"{r['outside_cm']:+.1f} | {'yes' if r['coverable'] else 'no'} |")
    wanted = [r for r in coverable if r["omega_cm"] < STRETCH_FLOOR_CM]
    lines += ["", f"Strained, below {STRETCH_FLOOR_CM:g} cm⁻¹ and coverable: "
                  + (", ".join(f"{r['id']} {r['source']} mode {r['mode']} ({r['omega_cm']:.0f} cm⁻¹, {r['shift_cm']:+.0f})"
                               for r in sorted(wanted, key=lambda r: -r["strain"])) if wanted else "none.")]
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sets", help="a sets.json naming the label folders and force-field roots")
    ap.add_argument("out", type=Path)
    ap.add_argument("--strain-min", type=float, default=0.08, help="|nu - omega| / omega a mode must reach to count as a candidate")
    a = ap.parse_args(argv)
    rows = screen(a.sets)
    os.makedirs(a.out, exist_ok=True)
    write_atomic(str(a.out / "coverage_screen.json"), json.dumps({"strain_min": a.strain_min, "modes": rows}, indent=1))
    lines = report_lines(rows, a.strain_min)
    write_atomic(str(a.out / "coverage_screen.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
