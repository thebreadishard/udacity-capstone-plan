"""Anchor set three, pricing (12 Oct 2026): the wall time and peak memory of one CCSD(T)/cc-pVDZ gradient — the unit of both an FD Hessian (2 × the
symmetry-unique displacements) and a CC APT by the field route (6) — measured on the server that will run them, before any price is quoted
(the lesson of 12 Oct: '5 min' per APT recompute was 2.2 h). The production chain: `cc_apt_field.cc_gradient_in_field` at zero field
(RHF → CCSD → (T) → (T) lambda → gradient, frozen core by the E8 rule), with the (T) C kernels as the anchors run them.

    python probes/anchor_gradient_timing.py <geometry.json> --threads 5 [--max-memory 8000]   → one JSON line
"""
import argparse
import json
import os
import resource
import sys
import time

import numpy as np
from pyscf import gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "t_density_kernel"))
from cc_apt_field import cc_gradient_in_field  # noqa: E402
from e8_cc_hessian_fd import core_orbital_count  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("geometry")
    ap.add_argument("--threads", type=int, default=5)
    ap.add_argument("--max-memory", type=int, default=8000)
    a = ap.parse_args()
    lib.num_threads(a.threads)
    import t_density_fast as fast
    if not fast.available():
        raise SystemExit("the (T) C kernel is not available here")
    fast.install()
    fast.install_lambda()
    g = json.load(open(a.geometry))
    symbols = [s.capitalize() for s in g["symbols"]]
    mol = gto.M(atom=list(zip(symbols, map(tuple, np.array(g["coords_bohr"])), strict=True)), unit="Bohr", basis="cc-pvdz", symmetry=False,
                verbose=0, max_memory=a.max_memory)
    t0 = time.time()
    grad, mu, e = cc_gradient_in_field(mol, core_orbital_count(symbols), np.zeros(3))
    print(json.dumps({"geometry": a.geometry, "atoms": len(symbols), "nao": mol.nao, "threads": a.threads, "seconds": round(time.time() - t0, 1),
                      "peak_rss_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2), "energy": e,
                      "max_abs_gradient": float(np.abs(grad).max())}), flush=True)


if __name__ == "__main__":
    main()
