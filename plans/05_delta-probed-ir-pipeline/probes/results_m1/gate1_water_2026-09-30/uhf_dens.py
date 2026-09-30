import numpy as np
from pyscf import gto, scf, cc, lib, ao2mo
from pyscf.cc import ccsd_t_lambda, uccsd_t_lambda, uccsd_t_rdm, ccsd_t_rdm
lib.num_threads(8)
mol = gto.M(atom="O 0 0 0.1217; H 0 0.7509 -0.4867; H 0 -0.7509 -0.4867", basis="cc-pvdz", verbose=0)
rmf = scf.RHF(mol).run(conv_tol=1e-12); umf = scf.addons.convert_to_uhf(rmf)
rcc = cc.CCSD(rmf); rcc.conv_tol, rcc.conv_tol_normt = 1e-11, 1e-9; re = rcc.ao2mo(); rcc.kernel(eris=re); ert = rcc.ccsd_t(eris=re)
ucc = cc.UCCSD(umf); ucc.conv_tol, ucc.conv_tol_normt = 1e-11, 1e-9; ue = ucc.ao2mo(); ucc.kernel(eris=ue); eut = ucc.ccsd_t(eris=ue)
_, rl1, rl2 = ccsd_t_lambda.kernel(rcc, re, rcc.t1, rcc.t2, tol=1e-10)
_, ul1, ul2 = uccsd_t_lambda.kernel(ucc, ue, ucc.t1, ucc.t2, tol=1e-10)
nmo, nocc = rcc.nmo, rcc.nocc
C = rmf.mo_coeff; h1 = C.T @ rmf.get_hcore() @ C; eri = ao2mo.restore(1, ao2mo.kernel(mol, C), nmo)
R1 = ccsd_t_rdm.make_rdm1(rcc, rcc.t1, rcc.t2, rl1, rl2, re); R2 = ccsd_t_rdm.make_rdm2(rcc, rcc.t1, rcc.t2, rl1, rl2, re)
U1 = uccsd_t_rdm.make_rdm1(ucc, ucc.t1, ucc.t2, ul1, ul2, ue); U2 = uccsd_t_rdm.make_rdm2(ucc, ucc.t1, ucc.t2, ul1, ul2, ue)
Er = np.einsum('pq,pq', h1, R1) + .5 * np.einsum('pqrs,pqrs', eri, R2) + mol.energy_nuc()
u1 = U1[0] + U1[1]; u2 = U2[0] + U2[1] + U2[1].transpose(2, 3, 0, 1) + U2[2]
Eu = np.einsum('pq,pq', h1, u1) + .5 * np.einsum('pqrs,pqrs', eri, u2) + mol.energy_nuc()
E = rcc.e_tot + ert
print(f"Tr(HD) RHF - E_CCSD(T) {Er - E:.1e};  UHF {Eu - E:.1e}")
o, v = slice(0, nocc), slice(nocc, nmo)
print("rdm1 UHF(sum) - RHF: " + ", ".join(f"{n} {np.abs((u1 - R1)[a, b]).max():.1e}" for n, a, b in [("oo", o, o), ("ov", o, v), ("vo", v, o), ("vv", v, v)]))
blocks = {}
for n in "oooo ooov oovv ovov ovvo ovvv vvvv ovoo vooo".split():
    s = tuple(o if c == "o" else v for c in n); blocks[n] = np.abs((u2 - R2)[s]).max()
print("rdm2 UHF(sum) - RHF: " + ", ".join(f"{k} {x:.1e}" for k, x in blocks.items()))
