import numpy as np
from pyscf import gto, scf, cc
from pyscf.cc import ccsd_t_lambda
from pyscf.grad import ccsd_t as G
mol = gto.M(atom=[[8, (0., 0., 0.)], [1, (0., -0.757, 0.587)], [1, (0., 0.757, 0.587)]], basis="631g", verbose=0)
mf = scf.RHF(mol).run(conv_tol=1e-12)
mycc = cc.CCSD(mf); mycc.conv_tol, mycc.conv_tol_normt = 1e-10, 1e-8
eris = mycc.ao2mo(); mycc.kernel(eris=eris); et = mycc.ccsd_t(eris=eris)
_, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2)
g_ref = G.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris=eris)
e_s, g_s = G.Gradients(mycc).as_scanner()(mol)
print(f"scanner energy - E_CCSD(T) = {e_s - (mycc.e_tot + et):.2e}   (E_(T) = {et:.2e})")
print(f"scanner gradient max|g - g_CCSD(T)| = {np.abs(g_s - g_ref).max():.2e}")
