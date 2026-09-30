"""Production gradient with the fused pass (qc05, both kernels installed): lambda solve + gradient, as e8_cc_hessian_fd.py does them.
Before the fusion (same script shape, 30 Sep 09:5x): lambda solve 66.4 s + gradient 62.2 s = 128.6 s on benzene/cc-pVDZ, 16 threads."""
import json
import sys
import time

import numpy as np
from pyscf import cc, gto, lib, scf
from pyscf.cc import ccsd_t_lambda

sys.path.insert(0, "/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/t_density_kernel")
import t_density_fast as F  # noqa: E402
from pyscf.grad import ccsd_t as ccsd_t_grad  # noqa: E402

lib.num_threads(16)
F.install()
F.install_lambda()
g = json.load(open(sys.argv[1]))
mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"])], unit="Bohr", basis="cc-pvdz", verbose=0, max_memory=12000)
mf = scf.RHF(mol); mf.conv_tol = 1e-11; mf.kernel()
mycc = cc.CCSD(mf, frozen=6); mycc.conv_tol, mycc.conv_tol_normt = 1e-9, 1e-7
eris = mycc.ao2mo(); mycc.kernel(eris=eris); mycc.ccsd_t(eris=eris)
t = time.perf_counter(); conv, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-8); t_lam = time.perf_counter() - t
t = time.perf_counter(); gf = ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris); t_grad = time.perf_counter() - t
print(f"fused: lambda solve {t_lam:.1f} s + gradient {t_grad:.1f} s = {t_lam + t_grad:.1f} s (before fusion 128.6 s)", flush=True)
# second route on the same amplitudes: pure pyscf lambda + densities
F.uninstall(); F.uninstall_lambda()
conv, l1p, l2p = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-8)
gp = ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1p, l2p, eris)
print(f"max |grad fused - grad pyscf| = {np.abs(np.asarray(gf) - np.asarray(gp)).max():.1e} a.u.; max |l1 - l1_pyscf| = {np.abs(l1 - l1p).max():.1e}", flush=True)
