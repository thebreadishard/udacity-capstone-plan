"""Before/after benchmark for the (T) intermediates PR: benzene/cc-pVDZ, frozen 6, RCCSD(T) lambda solve and nuclear gradient.
Run once with pyscf 2.14 (Python loops) and once with the branch (C kernels); results saved to <label>.npz for the element-wise comparison."""
import json
import sys
import time

import numpy as np
from pyscf import cc, gto, lib, scf
from pyscf.cc import ccsd_t_lambda
from pyscf.grad import ccsd_t as ccsd_t_grad

label, geom, nthreads = sys.argv[1], sys.argv[2], int(sys.argv[3])
lib.num_threads(nthreads)
g = json.load(open(geom))
mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"])], unit="Bohr", basis="cc-pvdz", verbose=0, max_memory=14000)
mf = scf.RHF(mol).run(conv_tol=1e-11)
mycc = cc.CCSD(mf, frozen=6)
mycc.conv_tol, mycc.conv_tol_normt = 1e-10, 1e-8
eris = mycc.ao2mo()
mycc.kernel(eris=eris)
out = {}
t0 = time.perf_counter()
imds = ccsd_t_lambda.make_intermediates(mycc, mycc.t1, mycc.t2, eris)
out["t_make_intermediates"] = time.perf_counter() - t0
out["l1_t"], out["l2_t"] = imds.l1_t, imds.l2_t
t0 = time.perf_counter()
conv, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-8)
out["t_lambda_solve"] = time.perf_counter() - t0
out["l1"], out["l2"] = l1, l2
t0 = time.perf_counter()
grad = ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris)
out["t_gradient"] = time.perf_counter() - t0
out["grad"] = grad
import pyscf  # noqa: E402
print(f"{label}: pyscf {pyscf.__file__}; threads {lib.num_threads()}; nocc {mycc.nocc} nvir {mycc.nmo - mycc.nocc}; "
      f"make_intermediates {out['t_make_intermediates']:.1f} s; lambda solve {out['t_lambda_solve']:.1f} s (conv {conv}); "
      f"gradient with given lambda {out['t_gradient']:.1f} s", flush=True)
np.savez(label + ".npz", **out)
