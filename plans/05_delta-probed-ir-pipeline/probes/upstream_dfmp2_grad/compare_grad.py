"""Compare the pyscf draft's DF-MP2 gradient with psi4's, element by element (TASKS 321).

Refused: two files of different levels (a psi4 file reused for another case), of different geometries, or whose energies
differ by more than ENERGY_LINE — equal energies are what shows that both programs computed the same thing (the same basis file,
fitting sets and frozen orbitals), so a gradient comparison is only printed when they hold.

    python compare_grad.py <pyscf.npz> <psi4.npz>
"""
from __future__ import annotations

import sys

import numpy as np

SAME_GEOMETRY_BOHR = 1e-10
ENERGY_LINE = 1e-6          # Eh; the runs of 26 Nov 2026 agree to 1e-9


def compare(ours: dict[str, np.ndarray], theirs: dict[str, np.ndarray]) -> list[str]:
    """The report's lines, or a refusal."""
    if str(ours["level"]) != str(theirs["level"]):
        raise SystemExit(f"the two gradients are of different levels: pyscf {ours['level']}, psi4 {theirs['level']}")
    if np.abs(ours["coords_bohr"] - theirs["coords_bohr"]).max() > SAME_GEOMETRY_BOHR:
        raise SystemExit("the two gradients are at different geometries")
    energies = {name: float(ours[key]) - float(theirs[key]) for name, key in (("E(SCF)", "e_scf"), ("E(total)", "e_tot"))}
    far = {name: d for name, d in energies.items() if abs(d) > ENERGY_LINE}
    if far:
        raise SystemExit(f"the energies differ by more than {ENERGY_LINE} Eh ({far}): not the same calculation")
    d = ours["gradient"] - theirs["gradient"]
    lines = [f"level: {ours['level']}"]
    lines += [f"{name}: difference pyscf minus psi4 {delta:+.2e} Eh" for name, delta in energies.items()]
    lines.append(f"gradient: largest element {np.abs(ours['gradient']).max():.6f}, max |difference| {np.abs(d).max():.2e}, "
                 f"rms {np.sqrt((d ** 2).mean()):.2e} Eh/bohr")
    lines.append(f"pyscf seconds (scf, mp2, gradient) {np.round(ours['seconds'], 1).tolist()}, sum {float(np.sum(ours['seconds'])):.0f}, "
                 f"peak RSS of its process {float(ours['peak_gib']):.2f} GiB; psi4 seconds (the whole gradient call) "
                 f"{float(theirs['seconds']):.0f}, its memory not measured here")
    return lines


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("compare_grad.py <pyscf.npz> <psi4.npz>")
    with np.load(argv[0]) as a, np.load(argv[1]) as b:
        lines = compare({k: a[k] for k in a.files}, {k: b[k] for k in b.files})
    print("\n".join(lines), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
