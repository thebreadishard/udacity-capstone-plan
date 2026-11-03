"""Read TASKS 142(a): does turning pyscf's grid with the nuclear-charge frame make its energies miss the way psi4's do?

The reading rule, written before the energies (3 Nov 2026): the turn is the cause when, at B3LYP/STO-3G 99/590,
  (1) on modes 5 and 11 (frame turns 5-7 and 3 degrees at q = 0.4) the charge-frame φ_iiii moves from the laboratory-frame one by more than
      MOVE_FACTOR times the laboratory curve's own truncation (|all steps - one step fewer|) and by more than MOVE_FLOOR_CM, and
  (2) on mode 10 (turn 0.07 degrees) it moves by less than STILL_CM, and
  (3) the move is larger on mode 5 than on mode 11 (the turn's order).
Anything else: the lead is not shown by this test, and the psi4 numbers stay unread.

    python probes/frame_proof_142a_read.py <out_dir>        (reads <out_dir>/lab/energy_route.json and <out_dir>/charge/energy_route.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MOVE_FACTOR = 5.0
MOVE_FLOOR_CM = 5.0
STILL_CM = 1.0
TURNING, STILL = ("5", "11"), "10"


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def verdict(lab: dict, charge: dict) -> tuple[list[str], bool]:
    """The table lines and whether rules (1)-(3) all hold."""
    lines, move = [], {}
    for mode in (*TURNING, STILL):
        a, b = lab["modes"][mode], charge["modes"][mode]
        move[mode] = abs(b["all_steps"]["phi_iiii"] - a["all_steps"]["phi_iiii"])
        trunc = abs(a["all_steps"]["phi_iiii"] - a["one_fewer"]["phi_iiii"])
        lines.append(f"| {mode} | {a['all_steps']['omega']:.2f} | {b['all_steps']['omega']:.2f} | {a['all_steps']['phi_iiii']:.1f} | "
                     f"{b['all_steps']['phi_iiii']:.1f} | {move[mode]:.1f} | {trunc:.1f} | {b['odd_max']:.2e} |")
        move[mode, "trunc"] = trunc
    rule1 = all(move[m] > MOVE_FACTOR * move[m, "trunc"] and move[m] > MOVE_FLOOR_CM for m in TURNING)
    rule2 = move[STILL] < STILL_CM
    rule3 = move["5"] > move["11"]
    lines.append(f"\nrule 1 (modes 5 and 11 move): {rule1}; rule 2 (mode 10 still): {rule2}; rule 3 (mode 5 more than 11): {rule3}")
    return lines, rule1 and rule2 and rule3


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")   # the table's ω and φ on a cp1252 console
    out = Path(sys.argv[1])
    lab, charge = load(out / "lab" / "energy_route.json"), load(out / "charge" / "energy_route.json")
    for key in ("program", "xc", "basis", "grid", "steps"):
        if lab[key] != charge[key]:
            raise SystemExit(f"the two runs differ in {key}: {lab[key]} against {charge[key]}")
    if (lab.get("frame"), charge.get("frame")) != ("lab", "charge"):
        raise SystemExit(f"frames are {lab.get('frame')} and {charge.get('frame')}, not lab and charge")
    lines, holds = verdict(lab, charge)
    print(f"{lab['program']}, {lab['xc']}/{lab['basis']}, grid {lab['grid']}; reference energy lab {lab['e_ref']:.10f}, "
          f"charge frame {charge['e_ref']:.10f}")
    print("| mode | ω lab | ω charge | φ_iiii lab | φ_iiii charge | move | lab truncation | odd part, charge |")
    print("|---|---|---|---|---|---|---|---|")
    print("\n".join(lines))
    print("VERDICT:", "the grid's turn makes the misses (lead shown)" if holds else "not shown by this test")


if __name__ == "__main__":
    main()
