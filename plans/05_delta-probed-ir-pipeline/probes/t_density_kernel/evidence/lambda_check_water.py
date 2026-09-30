import sys, time, numpy as np
sys.path.insert(0, "/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/t_density_kernel")
import t_density_fast as F
from pyscf import gto, scf, cc, lib
lib.num_threads(8)
for symmetry, frozen, basis in ((False, 1, "cc-pvdz"), (True, 1, "cc-pvdz"), (False, 0, "6-31g")):
    mol = gto.M(atom="O 0 0 0.1173; H 0 0.7572 -0.4692; H 0 -0.7572 -0.4692", basis=basis, symmetry=symmetry, verbose=0)
    mf = scf.RHF(mol).run(conv_tol=1e-12)
    mycc = cc.CCSD(mf, frozen=frozen); mycc.conv_tol, mycc.conv_tol_normt = 1e-11, 1e-9
    eris = mycc.ao2mo(); mycc.kernel(eris=eris)
    t0 = time.time(); d = F.check_lambda_against_pyscf(mycc, mycc.t1, mycc.t2, eris)
    ref_mag = np.abs(F.lambda_kernel(mycc.t1, mycc.t2, eris)[1]).max()
    print(f"symmetry {symmetry} frozen {frozen} {basis}: max |C - pyscf| l1_t {d['l1_t']:.1e}, l2_t {d['l2_t']:.1e} (|l2_t| {ref_mag:.1e}; {time.time()-t0:.1f} s)")
