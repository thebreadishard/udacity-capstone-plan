"""The DF-MP2 gradient we drafted for pyscf (TASKS 321), at a corpus geometry, for the comparison with psi4's.

Runs in WSL with the draft's pyscf worktree first on PYTHONPATH (run_vs_psi4.sh sets it; another pyscf is refused). The
reference is a density-fitted RHF in <jkfit set>, the correlation part is fitted in <ri set> (set on `mp.with_df`), as psi4
does it. The file keeps the level it was made at, which compare_grad.py checks against psi4's.

    python pyscf_grad.py <geometry.json> <basis name> <basis name or NWChem file> <jkfit set> <ri set> <frozen> <max_memory MB> <out.npz>
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

USAGE = "pyscf_grad.py <geometry.json> <basis name> <basis name or NWChem file> <jkfit set> <ri set> <frozen> <max_memory MB> <out.npz>"
KIB_PER_GIB = 1024 ** 2


def level_text(basis: str, jkfit: str, ri: str, frozen: int) -> str:
    """The level of a gradient file, written the same way by both programs' scripts."""
    return f"{basis.lower()} / {jkfit.lower()} / {ri.lower()} / frozen {frozen}"


def load_geometry(path: Path) -> tuple[list[str], np.ndarray]:
    """Element symbols and coordinates in bohr of a corpus geometry.json."""
    record = json.loads(path.read_text(encoding="utf-8"))
    return [s.capitalize() for s in record["symbols"]], np.asarray(record["coords_bohr"], float).reshape(-1, 3)


def save_npz(out: str, **arrays: object) -> None:
    """np.savez through a temp file moved over the target: a file that exists is a finished one."""
    tmp = Path(out).with_name(Path(out).name + ".tmp.npz")
    np.savez(tmp, **arrays)
    os.replace(tmp, out)


def main(argv: list[str]) -> int:
    if len(argv) != 8:
        raise SystemExit(USAGE)
    import resource  # Linux only; the helpers above are imported on Windows too

    import pyscf
    from pyscf import df, gto, lib, mp, scf

    geometry, basis_name, basis, jkfit, ri, frozen, max_memory, out = argv
    draft = Path(os.environ.get("PYTHONPATH", "").split(os.pathsep)[0]).resolve()
    if draft not in Path(pyscf.__file__).resolve().parents:
        raise SystemExit(f"pyscf was imported from {pyscf.__file__}, not from the draft's worktree {draft}")
    symbols, coords = load_geometry(Path(geometry))
    if Path(basis).is_file():
        basis = {s: gto.basis.load(basis, s) for s in sorted(set(symbols))}
    mol = gto.M(atom=list(zip(symbols, coords, strict=True)), basis=basis, unit="Bohr", verbose=4, max_memory=float(max_memory))
    print(f"nao {mol.nao}, threads {lib.num_threads()}, max_memory {mol.max_memory} MB, pyscf at {pyscf.__file__}", flush=True)
    stamps = [time.time()]
    mf = scf.RHF(mol).density_fit(auxbasis=jkfit)
    mf.conv_tol = 1e-12
    mf.kernel()
    stamps.append(time.time())
    pt = mp.dfmp2.DFMP2(mf, frozen=int(frozen))
    pt.with_df = df.DF(mol, auxbasis=ri)
    pt.kernel()
    stamps.append(time.time())
    gradient = pt.nuc_grad_method().kernel()
    stamps.append(time.time())
    seconds = np.diff(stamps)
    peak_gib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / KIB_PER_GIB
    save_npz(out, gradient=gradient, e_scf=mf.e_tot, e_tot=pt.e_tot, coords_bohr=coords, seconds=seconds, peak_gib=peak_gib,
             level=level_text(basis_name, jkfit, ri, int(frozen)))
    print(f"=== PYSCF GRAD DONE e_tot {pt.e_tot:.10f}; scf {seconds[0]:.0f} s, mp2 {seconds[1]:.0f} s, gradient {seconds[2]:.0f} s; "
          f"peak RSS {peak_gib:.2f} GiB", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
