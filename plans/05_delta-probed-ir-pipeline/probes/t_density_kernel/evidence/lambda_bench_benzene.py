"""C (T)-lambda kernel vs pyscf make_intermediates on benzene/cc-pVDZ, frozen 6, the E8 reference geometry; 30 Sep 2026."""
import json, sys, time, numpy as np
sys.path.insert(0, "/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/t_density_kernel")
import t_density_fast as F
from pyscf import gto, scf, cc, lib
from pyscf.cc import ccsd_t_lambda
lib.num_threads(int(sys.argv[2]) if len(sys.argv) > 2 else 16)
g = json.load(open(sys.argv[1]))
mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"])], unit="Bohr", basis="cc-pvdz", verbose=0, max_memory=12000)
mf = scf.RHF(mol).run(conv_tol=1e-11)
mycc = cc.CCSD(mf, frozen=6); mycc.conv_tol, mycc.conv_tol_normt = 1e-9, 1e-7
t0 = time.time(); eris = mycc.ao2mo(); mycc.kernel(eris=eris); print(f"CCSD {time.time()-t0:.0f} s, nocc {mycc.nocc} nvir {mycc.nmo-mycc.nocc}, threads {lib.num_threads()}", flush=True)
t0 = time.time(); l1c, l2c = F.lambda_kernel(mycc.t1, mycc.t2, eris); tc = time.time() - t0
print(f"C kernel: {tc:.1f} s", flush=True)
t0 = time.time(); ref = ccsd_t_lambda.make_intermediates(mycc, mycc.t1, mycc.t2, eris); tp = time.time() - t0
print(f"pyscf make_intermediates: {tp:.1f} s (includes the CCSD intermediates)", flush=True)
print(f"max |C - pyscf|: l1_t {np.abs(ref.l1_t - l1c).max():.1e} (|l1_t| {np.abs(l1c).max():.1e}), l2_t {np.abs(ref.l2_t - l2c).max():.1e} (|l2_t| {np.abs(l2c).max():.1e})", flush=True)
