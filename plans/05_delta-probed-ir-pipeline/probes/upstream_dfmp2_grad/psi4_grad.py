"""psi4's DF-MP2 gradient at a corpus geometry, by the route our production rows use (probes/dfmp2_rows.py): the counterpart
of the pyscf draft's gradient (TASKS 321). Runs in WSL in the psi4 environment. The file keeps the level it was made at.

    python psi4_grad.py <geometry.json> <basis> <jkfit set> <ri set> <frozen> <threads> <memory GB> <out.npz>
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dfmp2_rows as D
from pyscf_grad import level_text, load_geometry, save_npz

USAGE = "psi4_grad.py <geometry.json> <basis> <jkfit set> <ri set> <frozen> <threads> <memory GB> <out.npz>"


def main(argv: list[str]) -> int:
    if len(argv) != 8:
        raise SystemExit(USAGE)
    import psi4

    geometry, basis, jkfit, ri, frozen, threads, memory, out = argv
    symbols, coords = load_geometry(Path(geometry))
    level = D.Level(basis, int(frozen), False, int(threads), float(memory), 0, 1, D.Fitting.named_after(basis, jkfit, ri), "mp2")
    D.configure(psi4, level, Path(out).with_suffix(".psi4.log"))
    t0 = time.time()
    gradient = np.asarray(D.gradient(psi4, symbols, coords.ravel(), state=(0, 1), theory="mp2")).reshape(-1, 3)
    seconds = time.time() - t0
    save_npz(out, gradient=gradient, e_tot=psi4.variable("CURRENT ENERGY"), e_scf=psi4.variable("SCF TOTAL ENERGY"),
             coords_bohr=coords, seconds=seconds, level=level_text(basis, jkfit, ri, int(frozen)))
    print(f"=== PSI4 GRAD DONE psi4 {psi4.__version__} e_tot {psi4.variable('CURRENT ENERGY'):.10f} in {seconds:.0f} s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
