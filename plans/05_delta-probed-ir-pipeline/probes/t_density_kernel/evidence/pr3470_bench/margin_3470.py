"""Margin of test_rccsd_t_lambda.test_rdm_intermediates_real's allclose(rtol=1e-12, atol=1e-15) for the C route (setup copied verbatim)."""
import numpy as np
from pyscf import ao2mo
from pyscf.cc import ccsd_t_rdm, ccsd_t_rdm_slow, rccsd
import pyscf.cc.test.test_rccsd_t_lambda as T

T.setUpModule()
mol, mf = T.mol, T.mf
mycc = rccsd.RCCSD(mf)
np.random.seed(12)
nocc = 5
nmo = 12
nvir = nmo - nocc
eri0 = np.random.random((nmo, nmo, nmo, nmo))
eri0 = ao2mo.restore(1, ao2mo.restore(8, eri0, nmo), nmo)
fock0 = np.random.random((nmo, nmo))
fock0 = fock0 + fock0.T + np.diag(range(nmo)) * 2
t1 = np.random.random((nocc, nvir))
t2 = np.random.random((nocc, nocc, nvir, nvir))
t2 = t2 + t2.transpose(1, 0, 3, 2)
l1 = np.random.random((nocc, nvir))
l2 = np.random.random((nocc, nocc, nvir, nvir))
l2 = l2 + l2.transpose(1, 0, 3, 2)
eris = rccsd._ChemistsERIs(mol)
eris.oooo = eri0[:nocc, :nocc, :nocc, :nocc].copy()
eris.ovoo = eri0[:nocc, nocc:, :nocc, :nocc].copy()
eris.oovv = eri0[:nocc, :nocc, nocc:, nocc:].copy()
eris.ovvo = eri0[:nocc, nocc:, nocc:, :nocc].copy()
eris.ovov = eri0[:nocc, nocc:, :nocc, nocc:].copy()
eris.ovvv = eri0[:nocc, nocc:, nocc:, nocc:].copy()
eris.vvvv = eri0[nocc:, nocc:, nocc:, nocc:].copy()
eris.fock = fock0
eris.mo_energy = fock0.diagonal()
for label, new, ref in (
        ("d1", ccsd_t_rdm._gamma1_intermediates(mycc, t1, t2, l1, l2, eris, for_grad=False),
         ccsd_t_rdm_slow._gamma1_intermediates(mycc, t1, t2, l1, l2, eris, for_grad=False)),
        ("d2", ccsd_t_rdm._gamma2_intermediates(mycc, t1, t2, l1, l2, eris, compress_vvvv=False),
         ccsd_t_rdm_slow._gamma2_intermediates(mycc, t1, t2, l1, l2, eris, compress_vvvv=False))):
    names = ("doo dov dvo dvv" if label == "d1" else "dovov dvvvv doooo doovv dovvo dvvov dovvv dooov").split()
    for n, a, b in zip(names, new, ref):
        a = np.asarray(a).ravel(); b = np.asarray(b).ravel()
        r = np.abs(a - b) / (1e-15 + 1e-12 * np.abs(b))
        i = int(np.argmax(r))
        print(f"{label}.{n:6s} worst ratio {r[i]:9.3g} (fails > 1) at |ref| {abs(b[i]):.2e} |diff| {abs(a[i] - b[i]):.2e}; max|ref| {np.abs(b).max():.1e}")
