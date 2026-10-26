"""UCCSD's two-particle density intermediates with the v⁴ blocks out of core (software ledger row 52, step 3; TASKS 98).

pyscf 2.14.0's `cc/uccsd_rdm.py::_gamma2_outcore` holds every block in core despite its name (`#TODO: hold d2 intermediates in h5fobj`; master
44313dfb4 unchanged, 26 Oct 2026): gvvvv, gvVvV and gVVVV are whole v⁴ arrays, transposed, symmetrised and compressed — several copies of
nvir⁴ at once (6.4 GB each for acenaphthylene⁺/cc-pVDZ, ≈ 21 GB for the cover's largest cation). `gamma2_outcore` below is that function
(Copyright 2014-2020 The PySCF Developers, Apache License 2.0) with exactly these changes, so it reads against upstream line by line:

1. the three v⁴ intermediates are not formed;
2. their four contractions with t1 (into govvv, goVvV, gOvVv, gOVVV) are reassociated through l2·t1 (o³v), with no v⁴ array;
3. the compressed dvvvv, dvvVV and dVVVV are formed per slab of their first virtual index (`_write_v4`) and written to the HDF5 file, where
   the gradient's `_rdm2_mo2ao` reads them in its own row blocks; the mixed-spin block carries the 1/2 of uccsd_rdm's own compression
   (the one `uccsd_t_rdm` ≤ 2.14.0 omitted, pyscf#3305, fixed by #3387).

The out-of-core path is the gradient's, which asks for the compressed form; compress_vvvv=False is refused. Every other block is pyscf's.
"""
from __future__ import annotations

import numpy
from pyscf import lib

einsum = lib.einsum
V4_SLAB_MB = 2000                              # memory for one slab's two v⁴-sized intermediates (A and Bt of `_write_v4`)


def _slab(nvir_slow: int, nvir_fast: tuple[int, int, int], mb: float) -> int:
    """Virtual indices per slab: A and Bt, each slab·v·v·v doubles, within `mb` megabytes, at least one."""
    a, b, c = nvir_fast
    if a * b * c == 0:
        return 1                                    # a spin block without virtual orbitals: nothing to divide into slabs
    return max(1, int(mb * 1e6 / (2 * 8 * a * b * c)))


def _write_v4(h5fobj, name: str, tau, lam, scale: float, slab_mb: float = V4_SLAB_MB):
    """pyscf's d-block `D = g.T(0,2,1,3)[−g.T(0,3,1,2)]; D += D.T(1,0,3,2).conj(); D = (D + D.T(1,0,2,3))/2` compressed on both pairs, from
    g[a,b,c,d] = scale·Σ_ij tau[ijab]·lam[ijcd] with lam already antisymmetrised where pyscf subtracts, per slab of the first index p:
    D1[p,q,r,s] = A, D1[q,p,r,s] = Bt (both from contractions sliced on p), F = (A + Bt + (A + Bt)ᵀ⁽⁰¹³²⁾*)/2, rows (p ≥ q), columns (r ≥ s)."""
    _, _, nv1, nv2 = tau.shape
    rows_tril, cols_tril = numpy.tril_indices(nv1), numpy.tril_indices(nv2)
    cols = cols_tril[0] * nv2 + cols_tril[1]
    ds = h5fobj.create_dataset(name, (len(rows_tril[0]), len(cols)), tau.dtype)
    size = _slab(nv1, (nv1, nv2, nv2), slab_mb)
    for p0 in range(0, nv1, size):
        p1 = min(p0 + size, nv1)
        a = einsum("ijpr,ijqs->pqrs", tau[:, :, p0:p1], lam) * scale
        bt = einsum("ijqr,ijps->pqrs", tau, lam[:, :, p0:p1]) * scale
        f = a + bt
        f = (f + f.transpose(0, 1, 3, 2).conj()) * .5
        rows = numpy.concatenate([(p - p0) * nv1 + numpy.arange(p + 1) for p in range(p0, p1)])
        ds[p0 * (p0 + 1) // 2:p1 * (p1 + 1) // 2] = lib.take_2d(f.reshape((p1 - p0) * nv1, nv2 * nv2), rows, cols)
    return ds


def gamma2_outcore(cc, t1, t2, l1, l2, h5fobj, compress_vvvv=True, slab_mb: float = V4_SLAB_MB):  # noqa: PLR0913, PLR0915  pyscf's function as it is, so it reads against upstream
    if not compress_vvvv:
        raise ValueError("gamma2_outcore writes the compressed v⁴ blocks the gradient reads; compress_vvvv=False is the in-core path")
    t1a, t1b = t1
    t2aa, t2ab, t2bb = t2
    l1a, l1b = l1
    l2aa, l2ab, l2bb = l2

    tauaa = t2aa + numpy.einsum('ia,jb->ijab', 2*t1a, t1a)
    tauab = t2ab + numpy.einsum('ia,jb->ijab',   t1a, t1b)
    taubb = t2bb + numpy.einsum('ia,jb->ijab', 2*t1b, t1b)
    miajb = einsum('ikac,kjcb->iajb', l2aa, t2aa)
    miajb+= einsum('ikac,jkbc->iajb', l2ab, t2ab)
    miaJB = einsum('ikac,kjcb->iajb', l2aa, t2ab)
    miaJB+= einsum('ikac,kjcb->iajb', l2ab, t2bb)
    mIAjb = einsum('kica,jkbc->iajb', l2bb, t2ab)
    mIAjb+= einsum('kica,kjcb->iajb', l2ab, t2aa)
    mIAJB = einsum('ikac,kjcb->iajb', l2bb, t2bb)
    mIAJB+= einsum('kica,kjcb->iajb', l2ab, t2ab)
    miAjB = einsum('ikca,jkcb->iajb', l2ab, t2ab)
    mIaJb = einsum('kiac,kjbc->iajb', l2ab, t2ab)

    goovv = (l2aa.conj() + tauaa) * .25
    goOvV = (l2ab.conj() + tauab) * .5
    gOOVV = (l2bb.conj() + taubb) * .25

    tmpa  = einsum('kc,kica->ia', l1a, t2aa)
    tmpa += einsum('kc,ikac->ia', l1b, t2ab)
    tmpb  = einsum('kc,kica->ia', l1b, t2bb)
    tmpb += einsum('kc,kica->ia', l1a, t2ab)
    goovv += einsum('ia,jb->ijab', tmpa, t1a)
    goOvV += einsum('ia,jb->ijab', tmpa, t1b) * .5
    goOvV += einsum('ia,jb->jiba', tmpb, t1a) * .5
    gOOVV += einsum('ia,jb->ijab', tmpb, t1b)

    tmpa = einsum('kc,kb->cb', l1a, t1a)
    tmpb = einsum('kc,kb->cb', l1b, t1b)
    goovv += einsum('cb,ijca->ijab', tmpa, t2aa) * .5
    goOvV -= einsum('cb,ijac->ijab', tmpb, t2ab) * .5
    goOvV -= einsum('cb,jica->jiba', tmpa, t2ab) * .5
    gOOVV += einsum('cb,ijca->ijab', tmpb, t2bb) * .5
    tmpa = einsum('kc,jc->kj', l1a, t1a)
    tmpb = einsum('kc,jc->kj', l1b, t1b)
    goovv += einsum('kiab,kj->ijab', tauaa, tmpa) * .5
    goOvV -= einsum('ikab,kj->ijab', tauab , tmpb) * .5
    goOvV -= einsum('kiba,kj->jiba', tauab , tmpa) * .5
    gOOVV += einsum('kiab,kj->ijab', taubb, tmpb) * .5

    tmpa  = numpy.einsum('ldjd->lj', miajb)
    tmpa += numpy.einsum('ldjd->lj', miAjB)
    tmpb  = numpy.einsum('ldjd->lj', mIAJB)
    tmpb += numpy.einsum('ldjd->lj', mIaJb)
    goovv -= einsum('lj,liba->ijab', tmpa, tauaa) * .25
    goOvV -= einsum('lj,ilab->ijab', tmpb, tauab) * .25
    goOvV -= einsum('lj,liba->jiba', tmpa, tauab) * .25
    gOOVV -= einsum('lj,liba->ijab', tmpb, taubb) * .25
    tmpa  = numpy.einsum('ldlb->db', miajb)
    tmpa += numpy.einsum('ldlb->db', mIaJb)
    tmpb  = numpy.einsum('ldlb->db', mIAJB)
    tmpb += numpy.einsum('ldlb->db', miAjB)
    goovv -= einsum('db,jida->ijab', tmpa, tauaa) * .25
    goOvV -= einsum('db,ijad->ijab', tmpb, tauab) * .25
    goOvV -= einsum('db,jida->jiba', tmpa, tauab) * .25
    gOOVV -= einsum('db,jida->ijab', tmpb, taubb) * .25

    goovv -= einsum('ldia,ljbd->ijab', miajb, tauaa) * .5
    goovv += einsum('LDia,jLbD->ijab', mIAjb, t2ab ) * .5
    gOOVV -= einsum('ldia,ljbd->ijab', mIAJB, taubb) * .5
    gOOVV += einsum('ldia,ljdb->ijab', miaJB, t2ab ) * .5
    goOvV -= einsum('LDia,LJBD->iJaB', mIAjb, taubb) * .25
    goOvV += einsum('ldia,lJdB->iJaB', miajb, t2ab ) * .25
    goOvV -= einsum('ldIA,ljbd->jIbA', miaJB, tauaa) * .25
    goOvV += einsum('LDIA,jLbD->jIbA', mIAJB, t2ab ) * .25
    goOvV += einsum('lDiA,lJbD->iJbA', miAjB, tauab) * .5
    goOvV += einsum('LdIa,jd,LB->jIaB', mIaJb, t1a, t1b) * .5

    tmpaa = einsum('klcd,ijcd->ijkl', l2aa, tauaa) * .25**2
    tmpbb = einsum('klcd,ijcd->ijkl', l2bb, taubb) * .25**2
    tmpabab = einsum('kLcD,iJcD->iJkL', l2ab, tauab) * .5
    goovv += einsum('ijkl,klab->ijab', tmpaa, tauaa)
    goOvV += einsum('ijkl,klab->ijab', tmpabab, tauab)
    gOOVV += einsum('ijkl,klab->ijab', tmpbb, taubb)
    goovv = goovv.conj()
    goOvV = goOvV.conj()
    gOOVV = gOOVV.conj()

    # change 1: gvvvv, gvVvV, gVVVV (scale·einsum('ijab,ijcd->abcd', tau, l2)) are not formed

    goooo = einsum('ijab,klab->ijkl', l2aa, tauaa) * .125
    goOoO = einsum('ijab,klab->ijkl', l2ab, tauab) * .25
    gOOOO = einsum('ijab,klab->ijkl', l2bb, taubb) * .125

    gooov = einsum('jkba,ib->jkia', tauaa, -0.25 * l1a)
    goOoV = einsum('jkba,ib->jkia', tauab, -0.5  * l1a)
    gOoOv = einsum('kjab,ib->jkia', tauab, -0.5  * l1b)
    gOOOV = einsum('jkba,ib->jkia', taubb, -0.25 * l1b)

    gooov += einsum('iljk,la->jkia', goooo, t1a)
    goOoV += einsum('iljk,la->jkia', goOoO, t1b) * 2
    gOoOv += einsum('likj,la->jkia', goOoO, t1a) * 2
    gOOOV += einsum('iljk,la->jkia', gOOOO, t1b)

    tmpa  = numpy.einsum('icjc->ij', miajb) * .25
    tmpa += numpy.einsum('icjc->ij', miAjB) * .25
    tmpb  = numpy.einsum('icjc->ij', mIAJB) * .25
    tmpb += numpy.einsum('icjc->ij', mIaJb) * .25
    gooov -= einsum('ij,ka->jkia', tmpa, t1a)
    goOoV -= einsum('ij,ka->jkia', tmpa, t1b)
    gOoOv -= einsum('ij,ka->jkia', tmpb, t1a)
    gOOOV -= einsum('ij,ka->jkia', tmpb, t1b)

    gooov += einsum('icja,kc->jkia', miajb, .5 * t1a)
    goOoV += einsum('icja,kc->jkia', miAjB, .5 * t1b)
    goOoV -= einsum('icJA,kc->kJiA', miaJB, .5 * t1a)
    gOoOv += einsum('icja,kc->jkia', mIaJb, .5 * t1a)
    gOoOv -= einsum('ICja,KC->KjIa', mIAjb, .5 * t1b)
    gOOOV += einsum('icja,kc->jkia', mIAJB, .5 * t1b)

    gooov = gooov.conj()
    goOoV = goOoV.conj()
    gOoOv = gOoOv.conj()
    gOOOV = gOOOV.conj()
    gooov += einsum('jkab,ib->jkia', l2aa, .25*t1a)
    goOoV -= einsum('jkba,ib->jkia', l2ab, .5 *t1a)
    gOoOv -= einsum('kjab,ib->jkia', l2ab, .5 *t1b)
    gOOOV += einsum('jkab,ib->jkia', l2bb, .25*t1b)

    govvv = einsum('ja,ijcb->iacb', .25 * l1a, tauaa)
    goVvV = einsum('ja,ijcb->iacb', .5  * l1b, tauab)
    gOvVv = einsum('ja,jibc->iacb', .5  * l1a, tauab)
    gOVVV = einsum('ja,ijcb->iacb', .25 * l1b, taubb)

    # change 2: einsum('bcad,id->iabc', gvvvv, t1a) and its three partners, reassociated through l2·t1 (no v⁴ array)
    govvv += einsum('jkbc,jkai->iabc', tauaa, einsum('jkad,id->jkai', l2aa, t1a)) * .125
    goVvV -= einsum('jKbc,jKai->iabc', tauab, einsum('jKda,id->jKai', l2ab, t1a)) * .5
    gOvVv -= einsum('jKcb,jKai->iabc', tauab, einsum('jKad,id->jKai', l2ab, t1b)) * .5
    gOVVV += einsum('jkbc,jkai->iabc', taubb, einsum('jkad,id->jkai', l2bb, t1b)) * .125

    tmpa  = numpy.einsum('kakb->ab', miajb) * .25
    tmpa += numpy.einsum('kakb->ab', mIaJb) * .25
    tmpb  = numpy.einsum('kakb->ab', mIAJB) * .25
    tmpb += numpy.einsum('kakb->ab', miAjB) * .25
    govvv += einsum('ab,ic->iacb', tmpa, t1a)
    goVvV += einsum('ab,ic->iacb', tmpb, t1a)
    gOvVv += einsum('ab,ic->iacb', tmpa, t1b)
    gOVVV += einsum('ab,ic->iacb', tmpb, t1b)

    govvv += einsum('kaib,kc->iabc', miajb, .5 * t1a)
    goVvV += einsum('KAib,KC->iAbC', mIAjb, .5 * t1b)
    goVvV -= einsum('kAiB,kc->iAcB', miAjB, .5 * t1a)
    gOvVv += einsum('kaIB,kc->IaBc', miaJB, .5 * t1a)
    gOvVv -= einsum('KaIb,KC->IaCb', mIaJb, .5 * t1b)
    gOVVV += einsum('kaib,kc->iabc', mIAJB, .5 * t1b)
    govvv = govvv.conj()
    goVvV = goVvV.conj()
    gOvVv = gOvVv.conj()
    gOVVV = gOVVV.conj()
    govvv += einsum('ijbc,ja->iabc', l2aa, .25*t1a)
    goVvV += einsum('iJbC,JA->iAbC', l2ab, .5 *t1b)
    gOvVv += einsum('jIcB,ja->IaBc', l2ab, .5 *t1a)
    gOVVV += einsum('ijbc,ja->iabc', l2bb, .25*t1b)

    govvo = einsum('ia,jb->ibaj', l1a, t1a)
    goVvO = einsum('ia,jb->ibaj', l1a, t1b)
    gOvVo = einsum('ia,jb->ibaj', l1b, t1a)
    gOVVO = einsum('ia,jb->ibaj', l1b, t1b)

    govvo += numpy.einsum('iajb->ibaj', miajb)
    goVvO += numpy.einsum('iajb->ibaj', miaJB)
    gOvVo += numpy.einsum('iajb->ibaj', mIAjb)
    gOVVO += numpy.einsum('iajb->ibaj', mIAJB)
    goVoV = numpy.einsum('iajb->ibja', miAjB)
    gOvOv = numpy.einsum('iajb->ibja', mIaJb)

    govvo -= einsum('ikac,jc,kb->ibaj', l2aa, t1a, t1a)
    goVvO -= einsum('iKaC,JC,KB->iBaJ', l2ab, t1b, t1b)
    gOvVo -= einsum('kIcA,jc,kb->IbAj', l2ab, t1a, t1a)
    gOVVO -= einsum('ikac,jc,kb->ibaj', l2bb, t1b, t1b)
    goVoV += einsum('iKcA,jc,KB->iBjA', l2ab, t1a, t1b)
    gOvOv += einsum('kIaC,JC,kb->IbJa', l2ab, t1b, t1a)

    dovov = goovv.transpose(0,2,1,3) - goovv.transpose(0,3,1,2)
    doooo = goooo.transpose(0,2,1,3) - goooo.transpose(0,3,1,2)
    dovvv = govvv.transpose(0,2,1,3) - govvv.transpose(0,3,1,2)
    dooov = gooov.transpose(0,2,1,3) - gooov.transpose(1,2,0,3)
    dovvo = govvo.transpose(0,2,1,3)
    dovov =(dovov + dovov.transpose(2,3,0,1)) * .5
    doooo = doooo + doooo.transpose(1,0,3,2).conj()
    dovvo =(dovvo + dovvo.transpose(3,2,1,0).conj()) * .5
    doovv =-dovvo.transpose(0,3,2,1)
    dvvov = None

    dOVOV = gOOVV.transpose(0,2,1,3) - gOOVV.transpose(0,3,1,2)
    dOOOO = gOOOO.transpose(0,2,1,3) - gOOOO.transpose(0,3,1,2)
    dOVVV = gOVVV.transpose(0,2,1,3) - gOVVV.transpose(0,3,1,2)
    dOOOV = gOOOV.transpose(0,2,1,3) - gOOOV.transpose(1,2,0,3)
    dOVVO = gOVVO.transpose(0,2,1,3)
    dOVOV =(dOVOV + dOVOV.transpose(2,3,0,1)) * .5
    dOOOO = dOOOO + dOOOO.transpose(1,0,3,2).conj()
    dOVVO =(dOVVO + dOVVO.transpose(3,2,1,0).conj()) * .5
    dOOVV =-dOVVO.transpose(0,3,2,1)
    dVVOV = None

    dovOV = goOvV.transpose(0,2,1,3)
    dooOO = goOoO.transpose(0,2,1,3) * 2
    dovVV = goVvV.transpose(0,2,1,3)
    dooOV = goOoV.transpose(0,2,1,3)
    dovVO = goVvO.transpose(0,2,1,3)

    dOVvv = gOvVv.transpose(0,2,1,3)
    dOOov = gOoOv.transpose(0,2,1,3)
    dOVvo = gOvVo.transpose(0,2,1,3)
    dooVV = goVoV.transpose(0,2,1,3)
    dOOvv = gOvOv.transpose(0,2,1,3)

    dooOO = dooOO + dooOO.transpose(1,0,3,2).conj()
    dovVO = (dovVO + dOVvo.transpose(3,2,1,0).conj()) * .5
    dooVV =-(dooVV + dooVV.transpose(1,0,3,2).conj()) * .5
    dvvOV = None

    dOVov = None
    dVVvv = None
    dOOoo = None
    dOVvo =  dovVO.transpose(3,2,1,0).conj()
    dOOvv =-(dOOvv + dOOvv.transpose(1,0,3,2).conj()) * .5
    dVVov = None

    # change 3: the compressed v⁴ blocks, per slab, into the HDF5 file
    dvvvv = _write_v4(h5fobj, "gamma2_dvvvv", tauaa, l2aa - l2aa.transpose(0, 1, 3, 2), .125, slab_mb)
    dvvVV = _write_v4(h5fobj, "gamma2_dvvVV", tauab, l2ab, .5, slab_mb)
    dVVVV = _write_v4(h5fobj, "gamma2_dVVVV", taubb, l2bb - l2bb.transpose(0, 1, 3, 2), .125, slab_mb)

    return ((dovov, dovOV, dOVov, dOVOV),
            (dvvvv, dvvVV, dVVvv, dVVVV),
            (doooo, dooOO, dOOoo, dOOOO),
            (doovv, dooVV, dOOvv, dOOVV),
            (dovvo, dovVO, dOVvo, dOVVO),
            (dvvov, dvvOV, dVVov, dVVOV),
            (dovvv, dovVV, dOVvv, dOVVV),
            (dooov, dooOV, dOOov, dOOOV))
