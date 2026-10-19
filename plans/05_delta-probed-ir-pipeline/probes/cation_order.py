"""The order of the cation analytic run (19 Oct 2026; the user: 'stoppen na huidig molecuul en gesorteerd herstarten'): runner a's finished
cations still without both analytic Hessians, smallest first by their number of basis functions (6-31G*, Cartesian d — the labels route's
basis), so the per-molecule max RSS the run logs grows along the list and the first molecule that needs more than the cap marks where the
larger cap begins. Prints one line per molecule: id, basis functions, atoms.

    python probes/cation_order.py <shard dir with pool3_a.log and molecules/>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# 6-31G* with Cartesian d: H 2s; B–F 3s 2p(×3) + 6 d = 15; Al–Cl 4s 3p(×3) + 6 d = 19 (checked against pyscf's mol.nao, 19 Oct)
BASIS_FUNCTIONS = {"H": 2, "B": 15, "C": 15, "N": 15, "O": 15, "F": 15, "Si": 19, "P": 19, "S": 19, "Cl": 19}
FUNCTIONALS = ("b3lyp", "wb97x")


def basis_functions(symbols: list[str]) -> int:
    """The 6-31G* Cartesian basis size of a molecule; refuses an element outside the table."""
    missing = sorted({s.capitalize() for s in symbols} - set(BASIS_FUNCTIONS))
    if missing:
        raise ValueError(f"no 6-31G* basis-function count for {', '.join(missing)}")
    return sum(BASIS_FUNCTIONS[s.capitalize()] for s in symbols)


def pending(shard: Path) -> list[tuple[int, int, str]]:
    """(basis functions, atoms, id) of every finished cation without both analytic Hessians, smallest first."""
    log = shard / "pool3_a.log"
    if not log.is_file():
        raise FileNotFoundError(f"{log} missing")
    done = [line.split()[3] for line in log.read_text(encoding="utf-8").splitlines() if "] done P3c_" in line]
    out = []
    for mid in done:
        d = shard / "molecules" / mid
        if all((d / f"hessian_{f}_analytic.npz").exists() for f in FUNCTIONALS):
            continue
        symbols = json.loads((d / "geometry.json").read_text(encoding="utf-8"))["symbols"]
        out.append((basis_functions(symbols), len(symbols), mid))
    return sorted(out)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    for nbf, natoms, mid in pending(Path(argv[0])):
        print(f"{mid}\t{nbf}\t{natoms}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
