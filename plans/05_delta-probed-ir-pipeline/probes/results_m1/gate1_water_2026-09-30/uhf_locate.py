"""Where is the UCCSD(T) gradient error? (1) UHF on closed-shell water vs the (correct) RHF route; (2) UCCSD(T) lambda vs RHF (T) lambda
mapped to spin blocks; (3) energy from the (T) densities vs E_CCSD(T)."""
import numpy as np
from pyscf import gto, scf, cc, lib
from pyscf.cc import ccsd_t_lambda, uccsd_t_lambda, uccsd_t_rdm, ccsd_t_rdm
from pyscf.grad import ccsd_t as GRT, uccsd_t as GUT
lib.num_threads(8)
mol = gto.M(atom="O 0 0 0.1217; H 0 0.7509 -0.4867; H 0 -0.7509 -0.4867", basis="cc-pvdz", verbose=0)
rmf = scf.RHF(mol).run(conv_tol=1e-12); umf = scf.addons.convert_to_uhf(rmf)
rcc = cc.CCSD(rmf); rcc.conv_tol, rcc.conv_tol_normt = 1e-11, 1e-9; reris = rcc.ao2mo(); rcc.kernel(eris=reris); ert = rcc.ccsd_t(eris=reris)
ucc = cc.UCCSD(umf); ucc.conv_tol, ucc.conv_tol_normt = 1e-11, 1e-9; ueris = ucc.ao2mo(); ucc.kernel(eris=ueris); eut = ucc.ccsd_t(eris=ueris)
print(f"E(T) RHF {ert:.10f} UHF {eut:.10f} diff {abs(ert-eut):.1e}")
_, rl1, rl2 = ccsd_t_lambda.kernel(rcc, reris, rcc.t1, rcc.t2, tol=1e-10)
_, ul1, ul2 = uccsd_t_lambda.kernel(ucc, ueris, ucc.t1, ucc.t2, tol=1e-10)
# spin blocks of a closed shell: l1a = l1b = rl1; l2ab = rl2; l2aa = rl2 - rl2.transpose(1,0,2,3)
print("lambda l1a vs RHF:", np.abs(ul1[0]-rl1).max(), " l2ab:", np.abs(ul2[1]-rl2).max(), " l2aa:", np.abs(ul2[0]-(rl2-rl2.transpose(1,0,2,3))).max())
_, cl1, cl2 = ccsd_t_lambda.kernel(rcc, reris, rcc.t1, rcc.t2, tol=1e-10) if False else (None, None, None)
# CCSD lambda for reference: how far is the (T) lambda from it (scale of the effect)
rl1c, rl2c = rcc.solve_lambda(eris=reris)
print("scale: |(T) lambda - CCSD lambda| RHF l1", np.abs(rl1-rl1c).max(), "l2", np.abs(rl2-rl2c).max())
gr = GRT.Gradients(rcc).kernel(rcc.t1, rcc.t2, rl1, rl2, reris)
gu = GUT.Gradients(ucc).kernel(ucc.t1, ucc.t2, ul1, ul2, ueris)
print("gradient UHF-route vs RHF-route (closed shell):", np.abs(gu-gr).max())
# UHF gradient with the RHF lambda mapped to spin blocks: isolates density/grad code from the lambda solver
ml1 = (rl1, rl1); ml2 = (rl2-rl2.transpose(1,0,2,3), rl2, rl2-rl2.transpose(1,0,2,3))
gm = GUT.Gradients(ucc).kernel(ucc.t1, ucc.t2, ml1, ml2, ueris)
print("UHF grad code with RHF (T) lambda vs RHF route:", np.abs(gm-gr).max())
