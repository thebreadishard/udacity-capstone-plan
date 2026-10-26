"""The open-shell (UHF) CCSD(T) lambda intermediates without whole o³v³ arrays (software ledger row 52, TASKS 98; design note of 23 Oct 2026).

pyscf's `cc/uccsd_t_lambda.py::make_intermediates` forms w, v, d3, rw and wvd as whole `ijkabc` arrays for four spin cases (aaa, bbb, baa, bba):
≈ 22 GB each for benzene⁺/cc-pVDZ, ≈ 830 GB for acenaphthylene⁺. This module computes the same `l1a_t, l1b_t, l2aa_t, l2ab_t, l2bb_t` over
blocks of the three virtual indices, so a step holds o³·B³ numbers. Every term is pyscf's, written with the same einsum strings; `_term` and
`_acc` slice each operand on the letters of the block's virtual indices. The permutation operators: r6 (and the j↔k swap of r4) act on the
occupied axes only, so they stay inside a block; p6 and r4's (j,b)↔(k,c) swap move the virtual indices too, so w and v are evaluated at the
permuted blocks (`_permuted`). Real orbitals and complex ones are treated as pyscf treats them (the same conj() calls).

A second route, not a replacement yet: `make_intermediates` here must equal pyscf's element by element (tests/test_uhf_t_blocked.py) before
anything installs it; the C version for speed follows the same blocks.
"""
from __future__ import annotations

import itertools
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from pyscf import lib
from pyscf.cc import uccsd_lambda

BLOCK = 24                                    # virtual indices per block: o³·BLOCK³ doubles per array in flight
P6 = ((0, 1, 2, 3, 4, 5), (1, 2, 0, 4, 5, 3), (2, 0, 1, 5, 3, 4), (0, 2, 1, 3, 5, 4), (2, 1, 0, 5, 4, 3), (1, 0, 2, 4, 3, 5))
SWAP_JK = (0, 2, 1, 3, 4, 5)
SWAP_JK_BC = (0, 2, 1, 3, 5, 4)

Blocks = tuple[slice, slice, slice]


def _ranges(n: int, size: int) -> list[slice]:
    return [slice(s, min(s + size, n)) for s in range(0, n, size)]


def _block_letters(spec: str, out: bool) -> str:
    """The three virtual letters of a six-index operand: the output's (a term) or the first input's (a contraction)."""
    six = spec.split("->")[1] if out else spec.split(",")[0]
    if len(six) != 6:
        raise ValueError(f"{spec!r}: the six-index side has {len(six)} letters")
    return six[3:]


def _cut(letters: str, arr: np.ndarray, where: dict[str, slice]) -> np.ndarray:
    return arr[tuple(where.get(ch, slice(None)) for ch in letters)]


def _term(spec: str, x: np.ndarray, y: np.ndarray, blocks: Blocks) -> np.ndarray:
    """One of pyscf's w/v terms 'X,Y->ijkabc', restricted to the virtual blocks."""
    where = dict(zip(_block_letters(spec, out=True), blocks, strict=True))
    lx, ly = spec.split("->")[0].split(",")
    return np.einsum(spec, _cut(lx, x, where), _cut(ly, y, where), optimize=True)


def _acc(out: np.ndarray, spec: str, blk: np.ndarray, y: np.ndarray, blocks: Blocks, scale: float = 1.0) -> None:
    """out += scale · einsum('ijkabc,Y->Z', block, Y) over the block: Y and the output cut on the block's virtual letters."""
    where = dict(zip(_block_letters(spec, out=False), blocks, strict=True))
    ly = spec.split("->")[0].split(",")[1]
    lz = spec.split("->")[1]
    out[tuple(where.get(ch, slice(None)) for ch in lz)] += scale * np.einsum(spec, blk, _cut(ly, y, where), optimize=True)


def _permuted(f: Callable[[Blocks], np.ndarray], blocks: Blocks, axes: tuple[int, ...]) -> np.ndarray:
    """(f's whole array).transpose(axes) on the virtual blocks `blocks`: f evaluated where the transpose reads from."""
    need: list[slice] = [slice(None)] * 3
    for n in range(3, 6):
        need[axes[n] - 3] = blocks[n - 3]
    return f(tuple(need)).transpose(axes)


def _cached(f: Callable[[Blocks], np.ndarray]) -> Callable[[Blocks], np.ndarray]:
    """f memoised on its blocks for one block triple's permutations (≤ 6 distinct evaluations)."""
    memo: dict = {}

    def g(b: Blocks) -> np.ndarray:
        key = tuple((s.start, s.stop) for s in b)
        if key not in memo:
            memo[key] = f(b)
        return memo[key]
    return g


def _r6(w: np.ndarray) -> np.ndarray:
    return (w + w.transpose(2, 0, 1, 3, 4, 5) + w.transpose(1, 2, 0, 3, 4, 5)
            - w.transpose(2, 1, 0, 3, 4, 5) - w.transpose(0, 2, 1, 3, 4, 5) - w.transpose(1, 0, 2, 3, 4, 5))


def _same_spin(f: Callable[[Blocks], np.ndarray], blocks: Blocks) -> np.ndarray:
    """r6(p6(f)) on the block."""
    return _r6(sum(_permuted(f, blocks, ax) for ax in P6))


def _mixed_spin(f: Callable[[Blocks], np.ndarray], blocks: Blocks) -> np.ndarray:
    """r4(f) on the block: u = f − f(j↔k), then u + u((j,b)↔(k,c))."""
    def u(b: Blocks) -> np.ndarray:
        x = f(b)
        return x - x.transpose(SWAP_JK)
    return u(blocks) + _permuted(u, blocks, SWAP_JK_BC)


def _d3(e: tuple[np.ndarray, np.ndarray, np.ndarray], blocks: Blocks) -> np.ndarray:
    """lib.direct_sum('ia+jb+kc->ijkabc', e0, e1, e2) on the block."""
    e0, e1, e2 = (x[:, b] for x, b in zip(e, blocks, strict=True))
    return e0[:, None, None, :, None, None] + e1[None, :, None, None, :, None] + e2[None, None, :, None, None, :]


def _sweep(nv: tuple[int, int, int], size: int, w: Callable[[Blocks], np.ndarray], v: Callable[[Blocks], np.ndarray],
           sym: Callable, e: tuple[np.ndarray, np.ndarray, np.ndarray]):
    """Per block triple: (blocks, rw, wvd) = (sym(w)/d3, sym(2w + v)/d3) with w and v memoised for the triple's permutations."""
    for blocks in itertools.product(*(_ranges(n, size) for n in nv)):
        wc, vc = _cached(w), _cached(v)
        d3 = _d3(e, blocks)
        yield blocks, sym(wc, blocks) / d3, sym(lambda b, wc=wc, vc=vc: wc(b) * 2 + vc(b), blocks) / d3


@dataclass
class Spin:
    """The arrays of one UHF calculation the (T) lambda reads: amplitudes, orbital-energy differences, Fock blocks, integrals (g) and their
    conjugates (c)."""
    t1a: np.ndarray
    t1b: np.ndarray
    t2aa: np.ndarray
    t2ab: np.ndarray
    t2bb: np.ndarray
    eia: np.ndarray
    eIA: np.ndarray
    fvo: np.ndarray
    fVO: np.ndarray
    g: dict
    c: dict


@dataclass
class Parts:
    """Accumulators: l1 numerators (divided by e at the end), l2 before symmetrisation (pre), after it (post), and the mixed l2."""
    l1a: np.ndarray
    l1b: np.ndarray
    pre_aa: np.ndarray
    post_aa: np.ndarray
    pre_bb: np.ndarray
    post_bb: np.ndarray
    ab: np.ndarray


def _aaa(s: Spin, p: Parts, block: int) -> None:
    c = s.c

    def w(b):
        return _term("ijae,kceb->ijkabc", s.t2aa, c["ovvv"], b) - _term("mkbc,iajm->ijkabc", s.t2aa, c["ovoo"], b)

    def v(b):
        return _term("jbkc,ia->ijkabc", c["ovov"], s.t1a, b) + _term("jkbc,ai->ijkabc", s.t2aa, s.fvo, b) * .5
    nv = s.t2aa.shape[2]
    for blocks, rw, wvd in _sweep((nv,) * 3, block, w, v, _same_spin, (s.eia, s.eia, s.eia)):
        _acc(p.l1a, "ijkabc,jbkc->ia", rw.conj(), s.g["ovov"], blocks, .25)
        _acc(p.pre_aa, "ijkabc,kceb->ijae", wvd, c["ovvv"], blocks)
        _acc(p.pre_aa, "ijkabc,iajm->mkbc", wvd, c["ovoo"], blocks, -1.0)
        _acc(p.post_aa, "ijkabc,ai->jkbc", rw, s.fvo, blocks)


def _bbb(s: Spin, p: Parts, block: int) -> None:
    c = s.c

    def w(b):
        return _term("ijae,kceb->ijkabc", s.t2bb, c["OVVV"], b) - _term("imab,kcjm->ijkabc", s.t2bb, c["OVOO"], b)

    def v(b):
        return _term("jbkc,ia->ijkabc", c["OVOV"], s.t1b, b) + _term("jkbc,ai->ijkabc", s.t2bb, s.fVO, b) * .5
    nv = s.t2bb.shape[2]
    for blocks, rw, wvd in _sweep((nv,) * 3, block, w, v, _same_spin, (s.eIA, s.eIA, s.eIA)):
        _acc(p.l1b, "ijkabc,jbkc->ia", rw.conj(), s.g["OVOV"], blocks, .25)
        _acc(p.pre_bb, "ijkabc,kceb->ijae", wvd, c["OVVV"], blocks)
        _acc(p.pre_bb, "ijkabc,iajm->mkbc", wvd, c["OVOO"], blocks, -1.0)
        _acc(p.post_bb, "ijkabc,ai->jkbc", rw, s.fVO, blocks)


def _baa(s: Spin, p: Parts, block: int) -> None:
    """I and A beta; j, k, b, c alpha."""
    c, t2ab, t2aa = s.c, s.t2ab, s.t2aa

    def w(b):
        return (_term("jIeA,kceb->IjkAbc", t2ab, c["ovvv"], b) * 2 + _term("jIbE,kcEA->IjkAbc", t2ab, c["ovVV"], b) * 2
                + _term("jkbe,IAec->IjkAbc", t2aa, c["OVvv"], b) - _term("mIbA,kcjm->IjkAbc", t2ab, c["ovoo"], b) * 2
                - _term("jMbA,kcIM->IjkAbc", t2ab, c["ovOO"], b) * 2 - _term("jmbc,IAkm->IjkAbc", t2aa, c["OVoo"], b))

    def v(b):
        return (_term("jbkc,IA->IjkAbc", c["ovov"], s.t1b, b) + _term("kcIA,jb->IjkAbc", c["ovOV"], s.t1a, b) * 2
                + _term("jkbc,AI->IjkAbc", t2aa, s.fVO, b) * .5 + _term("kIcA,bj->IjkAbc", t2ab, s.fvo, b) * 2)
    _, _, nvira, nvirb = t2ab.shape
    for blocks, rw, wvd in _sweep((nvirb, nvira, nvira), block, w, v, _mixed_spin, (s.eIA, s.eia, s.eia)):
        _acc(p.l1a, "ijkabc,kcia->jb", rw.conj(), s.g["ovOV"], blocks, .5)
        _acc(p.l1b, "ijkabc,jbkc->ia", rw.conj(), s.g["ovov"], blocks, .25)
        _acc(p.pre_aa, "ijkabc,iaec->jkbe", wvd, c["OVvv"], blocks)
        _acc(p.pre_aa, "ijkabc,iakm->jmbc", wvd, c["OVoo"], blocks, -1.0)
        _acc(p.post_aa, "ijkabc,ai->jkbc", rw, s.fVO, blocks)
        _acc(p.ab, "ijkabc,kceb->jiea", wvd, c["ovvv"], blocks)
        _acc(p.ab, "ijkabc,kcea->jibe", wvd, c["ovVV"], blocks)
        _acc(p.ab, "ijkabc,kcjm->miba", wvd, c["ovoo"], blocks, -1.0)
        _acc(p.ab, "ijkabc,kcim->jmba", wvd, c["ovOO"], blocks, -1.0)
        _acc(p.ab, "ijkabc,bj->kica", rw, s.fvo, blocks)


def _bba(s: Spin, p: Parts, block: int) -> None:
    """i and a alpha; j, k, b, c beta."""
    c, t2ab, t2bb = s.c, s.t2ab, s.t2bb

    def w(b):
        return (_term("ijae,kceb->ijkabc", t2ab, c["OVVV"], b) * 2 + _term("ijeb,kcea->ijkabc", t2ab, c["OVvv"], b) * 2
                + _term("jkbe,iaec->ijkabc", t2bb, c["ovVV"], b) - _term("imab,kcjm->ijkabc", t2ab, c["OVOO"], b) * 2
                - _term("mjab,kcim->ijkabc", t2ab, c["OVoo"], b) * 2 - _term("jmbc,iakm->ijkabc", t2bb, c["ovOO"], b))

    def v(b):
        return (_term("jbkc,ia->ijkabc", c["OVOV"], s.t1a, b) + _term("iakc,jb->ijkabc", c["ovOV"], s.t1b, b) * 2
                + _term("JKBC,ai->iJKaBC", t2bb, s.fvo, b) * .5 + _term("iKaC,BJ->iJKaBC", t2ab, s.fVO, b) * 2)
    _, _, nvira, nvirb = t2ab.shape
    for blocks, rw, wvd in _sweep((nvira, nvirb, nvirb), block, w, v, _mixed_spin, (s.eia, s.eIA, s.eIA)):
        _acc(p.l1a, "ijkabc,jbkc->ia", rw.conj(), s.g["OVOV"], blocks, .25)
        _acc(p.l1b, "ijkabc,iakc->jb", rw.conj(), s.g["ovOV"], blocks, .5)
        _acc(p.pre_bb, "ijkabc,iaec->jkbe", wvd, c["ovVV"], blocks)
        _acc(p.pre_bb, "ijkabc,iakm->jmbc", wvd, c["ovOO"], blocks, -1.0)
        _acc(p.post_bb, "ijkabc,ai->jkbc", rw, s.fvo, blocks)
        _acc(p.ab, "ijkabc,kceb->ijae", wvd, c["OVVV"], blocks)
        _acc(p.ab, "ijkabc,kcea->ijeb", wvd, c["OVvv"], blocks)
        _acc(p.ab, "ijkabc,kcjm->imab", wvd, c["OVOO"], blocks, -1.0)
        _acc(p.ab, "ijkabc,kcim->mjab", wvd, c["OVoo"], blocks, -1.0)
        _acc(p.ab, "ijkabc,bj->ikac", rw, s.fVO, blocks)


INTEGRALS = ("ovvv", "OVVV", "ovVV", "OVvv", "ovoo", "OVOO", "ovOO", "OVoo", "ovov", "OVOV", "ovOV")
STORED = {"ovvv": "get_ovvv", "OVVV": "get_OVVV", "ovVV": "get_ovVV", "OVvv": "get_OVvv"}   # read through eris' unpacking getters


def _spin(t1, t2, eris) -> Spin:
    t1a, t1b = t1
    t2aa, t2ab, t2bb = t2
    nocca, noccb = t2ab.shape[:2]
    mo_ea, mo_eb = eris.mo_energy
    g = {k: np.asarray(getattr(eris, STORED[k])() if k in STORED else getattr(eris, k)) for k in INTEGRALS}
    return Spin(t1a, t1b, t2aa, t2ab, t2bb, mo_ea[:nocca, None] - mo_ea[nocca:], mo_eb[:noccb, None] - mo_eb[noccb:],
                eris.focka[nocca:, :nocca], eris.fockb[noccb:, :noccb], g, {k: x.conj() for k, x in g.items()})


def make_intermediates(mycc, t1, t2, eris, block: int = BLOCK):
    """pyscf's `uccsd_t_lambda.make_intermediates`, blocked over the virtual indices: the UCCSD lambda intermediates plus l1a_t, l1b_t,
    l2aa_t, l2ab_t, l2bb_t, equal to pyscf's to rounding."""
    if block < 1:
        raise ValueError(f"block {block}: at least one virtual index per block")
    imds = uccsd_lambda.make_intermediates(mycc, t1, t2, eris)
    s = _spin(t1, t2, eris)
    p = Parts(np.zeros_like(s.t1a), np.zeros_like(s.t1b), np.zeros_like(s.t2aa), np.zeros_like(s.t2aa), np.zeros_like(s.t2bb),
              np.zeros_like(s.t2bb), np.zeros_like(s.t2ab))
    for case in (_aaa, _bbb, _baa, _bba):
        case(s, p, block)
    imds.l1a_t, imds.l1b_t = p.l1a / s.eia, p.l1b / s.eIA
    imds.l2aa_t = (p.pre_aa + p.pre_aa.transpose(1, 0, 3, 2) + p.post_aa).conj() / lib.direct_sum("ia+jb->ijab", s.eia, s.eia) * .5
    imds.l2bb_t = (p.pre_bb + p.pre_bb.transpose(1, 0, 3, 2) + p.post_bb).conj() / lib.direct_sum("ia+jb->ijab", s.eIA, s.eIA) * .5
    imds.l2ab_t = p.ab.conj() / lib.direct_sum("ia+jb->ijab", s.eia, s.eIA) * .5
    return imds
