import itertools, numpy as np
from pyscf import gto, scf, cc, lib
from pyscf.cc import ccsd_t_lambda, uccsd_t_lambda, uccsd_t_rdm, ccsd_t_rdm, ccsd_rdm, uccsd_rdm
lib.num_threads(8)
mol = gto.M(atom="O 0 0 0.1217; H 0 0.7509 -0.4867; H 0 -0.7509 -0.4867", basis="cc-pvdz", verbose=0)
rmf = scf.RHF(mol).run(conv_tol=1e-12); umf = scf.addons.convert_to_uhf(rmf)
rcc = cc.CCSD(rmf); rcc.conv_tol, rcc.conv_tol_normt = 1e-11, 1e-9; re = rcc.ao2mo(); rcc.kernel(eris=re); rcc.ccsd_t(eris=re)
ucc = cc.UCCSD(umf); ucc.conv_tol, ucc.conv_tol_normt = 1e-11, 1e-9; ue = ucc.ao2mo(); ucc.kernel(eris=ue); ucc.ccsd_t(eris=ue)
_, rl1, rl2 = ccsd_t_lambda.kernel(rcc, re, rcc.t1, rcc.t2, tol=1e-10)
_, ul1, ul2 = uccsd_t_lambda.kernel(ucc, ue, ucc.t1, ucc.t2, tol=1e-10)
r0 = ccsd_rdm._gamma2_intermediates(rcc, rcc.t1, rcc.t2, rl1, rl2)
rT = ccsd_t_rdm._gamma2_intermediates(rcc, rcc.t1, rcc.t2, rl1, rl2, re)
u0 = uccsd_rdm._gamma2_intermediates(ucc, ucc.t1, ucc.t2, ul1, ul2)
uT = uccsd_t_rdm._gamma2_intermediates(ucc, ucc.t1, ucc.t2, ul1, ul2, ue)
names = "ovov vvvv oooo oovv ovvo vvov ovvv ooov".split()
spins = ["aa", "aA", "Aa", "AA"]
for g, n in enumerate(names):
    if r0[g] is None or rT[g] is None:
        print(n, 'RHF block None (r0, rT):', r0[g] is None, rT[g] is None, '; UHF (T) increments:', [None if uT[g][s] is None else float(np.abs(np.asarray(uT[g][s]) - (0 if u0[g][s] is None else np.asarray(u0[g][s]))).max()) for s in range(4)])
        continue
    Y0, YT = np.asarray(r0[g]), np.asarray(rT[g]) - np.asarray(r0[g])
    for s in range(4):
        X0 = u0[g][s]; XT = uT[g][s]
        if X0 is None and XT is None: continue
        X0 = np.asarray(X0); XT = np.asarray(XT) - X0
        perms = [p for p in itertools.permutations(range(4)) if Y0.transpose(p).shape == X0.shape]
        A0 = np.stack([Y0.transpose(p).ravel() for p in perms], 1); AT = np.stack([YT.transpose(p).ravel() for p in perms], 1)
        c, *_ = np.linalg.lstsq(A0, X0.ravel(), rcond=None)
        res0 = np.abs(A0 @ c - X0.ravel()).max(); resT = np.abs(AT @ c - XT.ravel()).max()
        flag = "   <-- (T) increment off" if resT > 1e-8 else ""
        print(f"{n} {spins[s]}: CCSD map residual {res0:.1e}; (T) increment |X| {np.abs(XT).max():.1e} residual {resT:.1e}{flag}")
