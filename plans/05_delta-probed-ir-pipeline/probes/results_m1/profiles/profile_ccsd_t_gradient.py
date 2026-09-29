"""Profile of one CCSD(T)/cc-pVDZ gradient of benzene (corpus geometry) at a given thread count — task '(T)-gradient throughput', step 2
(29 Sep 2026): where does the wall time go (SCF, CCSD, (T) energy, lambda, density, gradient) and which pyscf functions carry it.
Usage: python profile_ccsd_t_gradient.py <geometry.json> <out.txt> --threads 4 [--max-memory 8000]
"""
import argparse
import cProfile
import io
import json
import pstats
import time

import numpy as np
from pyscf import cc, gto, lib, scf
from pyscf.grad import ccsd_t as ccsd_t_grad

ap = argparse.ArgumentParser(); ap.add_argument("geometry"); ap.add_argument("out"); ap.add_argument("--threads", type=int, default=4); ap.add_argument("--max-memory", type=int, default=8000)
a = ap.parse_args(); lib.num_threads(a.threads)
g = json.load(open(a.geometry)); sym = g["symbols"]; x = np.array(g["coords_bohr"], float)
mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(sym, x)], unit="Bohr", basis="cc-pvdz", symmetry=False, verbose=0, max_memory=a.max_memory)
lines = [f"benzene CCSD(T)/cc-pVDZ gradient, {a.threads} threads, max_memory {a.max_memory} MB, {mol.nao} basis functions"]
T = {}
t = time.time(); mf = scf.RHF(mol); mf.conv_tol = 1e-11; mf.kernel(); T["scf"] = time.time() - t
t = time.time(); mycc = cc.CCSD(mf, frozen=6); mycc.conv_tol = 1e-9; mycc.conv_tol_normt = 1e-7; mycc.kernel(); T["ccsd"] = time.time() - t
t = time.time(); mycc.ccsd_t(); T["(T) energy"] = time.time() - t
pr = cProfile.Profile(); t = time.time(); pr.enable(); grad = ccsd_t_grad.Gradients(mycc).kernel(); pr.disable(); T["(T) gradient (lambda + densities + gradient)"] = time.time() - t
lines += [f"{k}: {v:.0f} s" for k, v in T.items()] + [f"total {sum(T.values()):.0f} s; max|grad| {np.abs(grad).max():.2e}", "", "cumulative time, top 25 (gradient stage):"]
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(25); lines.append(s.getvalue())
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(20); lines += ["own time, top 20 (gradient stage):", s.getvalue()]
open(a.out, "w").write("\n".join(lines)); print("\n".join(lines[:9]))
