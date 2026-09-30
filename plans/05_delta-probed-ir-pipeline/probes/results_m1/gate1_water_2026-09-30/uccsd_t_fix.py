import numpy as np
from pyscf import lib


def install_uccsd_t_dvvvv_fix():
    from pyscf.cc import uccsd_t_rdm
    if getattr(uccsd_t_rdm._gamma2_intermediates, "_dpir_fixed", False):
        return
    orig = uccsd_t_rdm._gamma2_intermediates

    def fixed(mycc, t1, t2, l1, l2, eris=None, compress_vvvv=False):
        d2 = orig(mycc, t1, t2, l1, l2, eris, False)
        if not compress_vvvv:
            return d2
        nvira, nvirb = t2[1].shape[2:]
        ia = np.tril_indices(nvira); ia = ia[0] * nvira + ia[1]
        ib = np.tril_indices(nvirb); ib = ib[0] * nvirb + ib[1]

        def comp(x, na, nb, i1, i2):
            x = x + x.transpose(1, 0, 2, 3)
            return lib.take_2d(x.reshape(na**2, nb**2), i1, i2) * .5
        dvvvv, dvvVV, dVVvv, dVVVV = d2[1]
        vv = (comp(dvvvv, nvira, nvira, ia, ia), comp(dvvVV, nvira, nvirb, ia, ib), dVVvv, comp(dVVVV, nvirb, nvirb, ib, ib))
        return (d2[0], vv) + tuple(d2[2:])
    fixed._dpir_fixed = True
    uccsd_t_rdm._gamma2_intermediates = fixed
