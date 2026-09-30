"""Production split of one RCCSD(T) gradient as e8_cc_hessian_fd.py runs it (qc05 = pyscf 2.14 wheel, both project kernels installed),
benzene/cc-pVDZ frozen 6, 16 threads: which parts would the 6x triple symmetry of the kernels touch?"""
import json
import sys
import time

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
T = {}
t = time.perf_counter(); mf = scf.RHF(mol); mf.conv_tol = 1e-11; mf.kernel(); T["SCF"] = time.perf_counter() - t
mycc = cc.CCSD(mf, frozen=6); mycc.conv_tol, mycc.conv_tol_normt = 1e-9, 1e-7
t = time.perf_counter(); eris = mycc.ao2mo(); mycc.kernel(eris=eris); T["ao2mo + CCSD"] = time.perf_counter() - t
t = time.perf_counter(); mycc.ccsd_t(eris=eris); T["(T) energy"] = time.perf_counter() - t
t = time.perf_counter(); F.lambda_kernel(mycc.t1, mycc.t2, eris); T["  C lambda kernel alone"] = time.perf_counter() - t
t = time.perf_counter(); conv, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-8); T["lambda solve (incl. C kernel)"] = time.perf_counter() - t
F._cache["key"] = None
t = time.perf_counter(); F.kernel(mycc.t1, mycc.t2, eris); T["  C density kernel alone (one pass)"] = time.perf_counter() - t
F._cache["key"] = None
t = time.perf_counter(); ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris); T["gradient (incl. C density kernel)"] = time.perf_counter() - t
for k, v in T.items():
    print(f"{k:40s} {v:7.1f} s", flush=True)
tot = T["SCF"] + T["ao2mo + CCSD"] + T["(T) energy"] + T["lambda solve (incl. C kernel)"] + T["gradient (incl. C density kernel)"]
kern = T["  C lambda kernel alone"] + T["  C density kernel alone (one pass)"]
print(f"total {tot:.0f} s; C kernels {kern:.0f} s = {100 * kern / tot:.0f} %", flush=True)
