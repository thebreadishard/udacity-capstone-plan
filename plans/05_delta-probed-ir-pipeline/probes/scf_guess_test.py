"""Does a displaced SCF converge under DIIS when it starts from a neighbouring geometry's converged density? (19 Oct 2026, TASKS 80 brought
forward; the user: 'Ja, doe (b)'.) Acenaphthylene at B3LYP/def2-TZVP stalls under DIIS at every geometry and takes the second-order
fallback, about 2.5 h per displaced Hessian in all.

    python scf_guess_test.py <stub_a.json> <stub_b.json> --basis def2-tzvp --grid 75,302 --threads 5 --out <result.json>

A: stub_a's SCF from pyscf's default guess (with scf_converge's fallback when DIIS stalls). B1: stub_b's the same way. B2: stub_b's SCF
from A's converged density, DIIS only, its cycles counted. The record: per SCF the energy, whether the fallback ran, DIIS cycles and wall
seconds; |E(B2) − E(B1)| shows that the start does not change the answer. SCF only, no Hessian. The settings are pyscf_hessians_for_qff's.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from library_log import PYSCF_LOG_NAME, pyscf_mole  # noqa: E402
from pyscf_hessians_for_qff import displaced_geometry, rks_setup  # noqa: E402
from scf_converge import converged_scf  # noqa: E402


def one_scf(stub: str, a: argparse.Namespace, lib_log, dm0=None) -> tuple[dict, object]:
    """One SCF at a stub's geometry; returns its record and the converged density."""
    import numpy as np
    d = displaced_geometry(stub)
    if d is None:
        raise ValueError(f"{stub} is not a Hessian stub")
    sym, geom = d["molecule"]["symbols"], np.array(d["molecule"]["geometry"], float).reshape(-1, 3)
    mol = pyscf_mole(lib_log, atom=[(s, tuple(x)) for s, x in zip(sym, geom, strict=True)], unit="Bohr", basis=a.basis, symmetry=False)
    mf = rks_setup(mol, a.xc, a.grid, a.conv)
    lines = []
    t0 = time.time()
    if dm0 is None:
        mf, e = converged_scf(mf, 200, log=lines.append)
        rec = {"start": "default guess", "fallback": bool(lines), "converged": True}
    else:
        mf.max_cycle = 200
        e = mf.kernel(dm0=dm0)
        rec = {"start": "neighbour's density", "fallback": False, "converged": bool(mf.converged)}
    rec.update({"stub": os.path.basename(stub), "energy": float(e), "seconds": round(time.time() - t0, 1),
                "diis_cycles": int(getattr(mf, "cycles", -1))})
    print(f"{rec['stub']}: {rec['start']}, converged {rec['converged']}, fallback {rec['fallback']}, {rec['diis_cycles']} cycles, "
          f"{rec['seconds']} s, E = {rec['energy']:.10f}", flush=True)
    return rec, mf.make_rdm1()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("stub_a")
    ap.add_argument("stub_b")
    ap.add_argument("--xc", default="b3lyp")
    ap.add_argument("--basis", required=True)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--conv", type=float, default=1e-11)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from pyscf import lib
    lib.num_threads(a.threads)
    out_dir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, PYSCF_LOG_NAME), "a", encoding="utf-8") as lib_log:
        rec_a, dm_a = one_scf(a.stub_a, a, lib_log)
        rec_b1, _ = one_scf(a.stub_b, a, lib_log)
        rec_b2, _ = one_scf(a.stub_b, a, lib_log, dm0=dm_a)
    result = {"A": rec_a, "B1": rec_b1, "B2": rec_b2, "energy_difference_B2_B1": abs(rec_b2["energy"] - rec_b1["energy"]),
              "settings": {"basis": a.basis, "grid": a.grid, "conv_tol": a.conv, "threads": a.threads}}
    with open(a.out + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    os.replace(a.out + ".tmp", a.out)
    print(f"|E(B2) - E(B1)| = {result['energy_difference_B2_B1']:.1e}; B2 {'converged under DIIS' if rec_b2['converged'] else 'did NOT converge'} "
          f"in {rec_b2['diis_cycles']} cycles, {rec_b2['seconds']} s against B1's {rec_b1['seconds']} s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
