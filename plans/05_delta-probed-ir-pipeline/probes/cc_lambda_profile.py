"""Lever 3, design input (2 Oct 2026): where does pyscf's CCSD Λ solve spend its time? cProfile around `mycc.solve_lambda()` on a small molecule at the
anchor settings (CCSD, cc-pVDZ, frozen core derived as the E8 probe does), top entries by cumulative time, plus the per-iteration wall time. The (T) part of
the lambda is our own C kernel and is not profiled here; this is the CCSD Λ update (`pyscf/cc/ccsd_lambda.py`, `update_lambda`) whose contractions are
the candidate for a kernel. pyscf usage as in pyscf/cc/test/test_ccsd_lambda.py.

    python probes/cc_lambda_profile.py <geometry.json> [--threads 4] [--basis cc-pvdz] [--top 18]
"""
import argparse
import cProfile
import json
import pstats
import sys
import time

import numpy as np
from pyscf import cc, gto, lib, scf

FIRST_ROW = {"B", "C", "N", "O", "F"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("geometry")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--top", type=int, default=18)
    a = ap.parse_args()
    lib.num_threads(a.threads)
    g = json.load(open(a.geometry))
    sym = [s.capitalize() for s in g["symbols"]]
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(sym, np.asarray(g["coords_bohr"], float), strict=True)], unit="Bohr", basis=a.basis, verbose=0, max_memory=8000)
    frozen = sum(1 for s in sym if s in FIRST_ROW)                      # the E8 probe's rule: the 1s of every first-row atom
    t0 = time.time()
    mf = scf.RHF(mol).run(conv_tol=1e-10)
    t1 = time.time()
    mycc = cc.CCSD(mf, frozen=frozen).run(conv_tol=1e-8, conv_tol_normt=1e-6)
    t2 = time.time()
    print(f"{mol.natm} atoms, {mol.nao} basis functions, frozen {frozen}; SCF {t1 - t0:.0f} s, CCSD {t2 - t1:.0f} s ({a.threads} threads)")
    pr = cProfile.Profile()
    pr.enable()
    mycc.solve_lambda()
    pr.disable()
    t3 = time.time()
    print(f"CCSD lambda: {t3 - t2:.0f} s")
    st = pstats.Stats(pr)
    st.sort_stats("cumulative")
    print(f"\ntop {a.top} by cumulative time (functions inside pyscf.cc and numpy einsum / dot):")
    rows = []
    for (fn, ln, name), (_cc, nc, tt, ct, _callers) in st.stats.items():
        if ("pyscf" in fn and ("/cc/" in fn or "\\cc\\" in fn or "lib" in fn)) or name in ("einsum", "dot", "ddot", "_contract"):
            rows.append((ct, tt, nc, f"{fn.split('pyscf')[-1] if 'pyscf' in fn else fn}:{ln} {name}"))
    for ct, tt, nc, label in sorted(rows, reverse=True)[: a.top]:
        print(f"  cum {ct:7.1f} s  own {tt:7.1f} s  calls {nc:6d}  {label[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
