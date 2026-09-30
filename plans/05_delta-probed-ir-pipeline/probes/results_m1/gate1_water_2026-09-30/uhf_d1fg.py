import numpy as np
from pyscf import gto, scf, cc, lib
from pyscf.cc import ccsd_t_lambda, uccsd_t_lambda, uccsd_t_rdm, ccsd_t_rdm, ccsd_rdm, uccsd_rdm
from pyscf.grad import ccsd_t as GRT, uccsd_t as GUT
lib.num_threads(8)
mol = gto.M(atom="O 0 0 0.1217; H 0 0.7509 -0.4867; H 0 -0.7509 -0.4867", basis="cc-pvdz", verbose=0)
rmf = scf.RHF(mol).run(conv_tol=1e-12); umf = scf.addons.convert_to_uhf(rmf)
rcc = cc.CCSD(rmf); rcc.conv_tol, rcc.conv_tol_normt = 1e-11, 1e-9; re = rcc.ao2mo(); rcc.kernel(eris=re); rcc.ccsd_t(eris=re)
ucc = cc.UCCSD(umf); ucc.conv_tol, ucc.conv_tol_normt = 1e-11, 1e-9; ue = ucc.ao2mo(); ucc.kernel(eris=ue); ucc.ccsd_t(eris=ue)
_, rl1, rl2 = ccsd_t_lambda.kernel(rcc, re, rcc.t1, rcc.t2, tol=1e-10)
_, ul1, ul2 = uccsd_t_lambda.kernel(ucc, ue, ucc.t1, ucc.t2, tol=1e-10)
names = ["oo", "ov", "vo", "vv"]
r0 = ccsd_rdm._gamma1_intermediates(rcc, rcc.t1, rcc.t2, rl1, rl2)
u0 = uccsd_rdm._gamma1_intermediates(ucc, ucc.t1, ucc.t2, ul1, ul2)
rf = ccsd_t_rdm._gamma1_intermediates(rcc, rcc.t1, rcc.t2, rl1, rl2, re, for_grad=True)
uf = uccsd_t_rdm._gamma1_intermediates(ucc, ucc.t1, ucc.t2, ul1, ul2, ue, for_grad=True)
for i, n in enumerate(names):
    dr = rf[i] - r0[i]; du = uf[i][0] - u0[i][0]
    c = (du * dr).sum() / max((dr * dr).sum(), 1e-300)
    off = ~np.eye(*dr.shape, dtype=bool) if dr.shape[0] == dr.shape[1] else np.ones(dr.shape, bool)
    print(f"(T) increment {n}: |dR| {np.abs(dr).max():.1e} |dU_alpha| {np.abs(du).max():.1e}  best scale U/R {c:.4f}  residual {np.abs(du - c*dr).max():.1e}  diag-only? U-offdiag {np.abs(du[off]).max() if off.any() else 0:.1e} R-offdiag {np.abs(dr[off]).max():.1e}")
# gradient experiments on the UHF side: halve the (T) oo/vv increments, keep vo
gr = GRT.Gradients(rcc).kernel(rcc.t1, rcc.t2, rl1, rl2, re)
orig = uccsd_t_rdm._gamma1_intermediates
def scaled(s_oovv, s_vo):
    def f(mycc, t1, t2, l1, l2, eris=None, for_grad=False):
        base = uccsd_rdm._gamma1_intermediates(mycc, t1, t2, l1, l2)
        full = orig(mycc, t1, t2, l1, l2, eris, for_grad)
        out = []
        for i, (b, d) in enumerate(zip(base, full)):
            s = s_vo if i == 2 else (s_oovv if i in (0, 3) else 1.0)
            out.append(tuple(bb + s * (dd - bb) for bb, dd in zip(b, d)))
        return out
    return f
for s_oovv, s_vo in [(1, 1), (.5, 1), (1, .5), (.5, .5), (0, 1), (1, 0), (2, 1), (1, 2)]:
    uccsd_t_rdm._gamma1_intermediates = scaled(s_oovv, s_vo)
    gu = GUT.Gradients(ucc).kernel(ucc.t1, ucc.t2, ul1, ul2, ue)
    print(f"scale oo/vv {s_oovv} vo {s_vo}: |g_U - g_R| {np.abs(gu - gr).max():.1e}")
uccsd_t_rdm._gamma1_intermediates = orig
