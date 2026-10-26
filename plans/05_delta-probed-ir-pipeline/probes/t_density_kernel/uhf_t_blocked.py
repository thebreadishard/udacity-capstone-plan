"""The open-shell (UHF) CCSD(T) lambda and density intermediates without whole o³v³ arrays (software ledger row 52, TASKS 98; design note of
23 Oct 2026).

pyscf's `cc/uccsd_t_lambda.py::make_intermediates` and `cc/uccsd_t_rdm.py::_gamma1_intermediates/_gamma2_intermediates` form w, v, d3, rw and
wvd as whole `ijkabc` arrays for four spin cases (aaa, bbb, baa, bba): ≈ 22 GB each for benzene⁺/cc-pVDZ, ≈ 830 GB for acenaphthylene⁺. This
module computes the same quantities over blocks of the three virtual indices, so a step holds o³·B³ numbers (o³·v·B² for γ1's virtual-virtual
terms, which pair two blocks along one index). Every term is one of pyscf's lines: the spin cases' w and v (`_cases`) and the three tables
LAMBDA, GAMMA1 and GAMMA2 carry pyscf's einsum strings, operands and factors; `_acc` cuts each operand on the block's virtual letters. The
permutation operators: r6 and the j↔k swap of r4 act on the occupied axes only, so they stay inside a block; p6 and r4's (j,b)↔(k,c) swap
move the virtual indices too, so w and v are evaluated at the permuted blocks (`_permuted`).

A second route, not a replacement yet: every function here must equal pyscf's element by element (tests/test_uhf_t_blocked.py) before
anything installs it; the C version for speed follows the same blocks.
"""
from __future__ import annotations

import itertools
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from pyscf import lib
from pyscf.cc import uccsd_lambda, uccsd_rdm
from uccsd_gamma2_outcore import V4_SLAB_MB
from uccsd_gamma2_outcore import gamma2_outcore as gamma2_outcore_uccsd

BLOCK = 24                                    # virtual indices per block: o³·BLOCK³ doubles per array in flight
P6 = ((0, 1, 2, 3, 4, 5), (1, 2, 0, 4, 5, 3), (2, 0, 1, 5, 3, 4), (0, 2, 1, 3, 5, 4), (2, 1, 0, 5, 4, 3), (1, 0, 2, 4, 3, 5))
SWAP_JK = (0, 2, 1, 3, 4, 5)
SWAP_JK_BC = (0, 2, 1, 3, 5, 4)
INTEGRALS = ("ovvv", "OVVV", "ovVV", "OVvv", "ovoo", "OVOO", "ovOO", "OVoo", "ovov", "OVOV", "ovOV")
UNPACKED = {"ovvv": "get_ovvv", "OVVV": "get_OVVV", "ovVV": "get_ovVV", "OVvv": "get_OVvv"}   # read through eris' unpacking getters
SIX = ("rw", "rw*", "wvd", "wvd*")            # the block arrays a table term may name

Blocks = tuple[slice, slice, slice]
Fn = Callable[[Blocks], np.ndarray]
Term = tuple[str, str, tuple[str, ...], float]     # (target, pyscf's einsum, operands, factor)


# ------------------------------------------------------------------------------------------------------------------------- block algebra
def _ranges(n: int, size: int) -> list[slice]:
    return [slice(s, min(s + size, n)) for s in range(0, n, size)]


def _cut(letters: str, arr: np.ndarray, where: dict[str, slice]) -> np.ndarray:
    return arr[tuple(where.get(ch, slice(None)) for ch in letters)]


def _term(spec: str, x: np.ndarray, y: np.ndarray, blocks: Blocks) -> np.ndarray:
    """One of pyscf's w/v terms 'X,Y->ijkabc', restricted to the virtual blocks."""
    where = dict(zip(spec.split("->")[1][3:], blocks, strict=True))
    lx, ly = spec.split("->")[0].split(",")
    return np.einsum(spec, _cut(lx, x, where), _cut(ly, y, where), optimize=True)


def _acc(out: np.ndarray, spec: str, operands: tuple, where: dict[str, slice], scale: float) -> None:
    """out += scale · einsum(spec, …): the six-index operands are block arrays already; every other operand and the output are cut on `where`."""
    ins, lz = spec.split("->")
    cut = [x if len(letters) == 6 else _cut(letters, x, where) for letters, x in zip(ins.split(","), operands, strict=True)]
    out[tuple(where.get(ch, slice(None)) for ch in lz)] += scale * np.einsum(spec, *cut, optimize=True)


def _permuted(f: Fn, blocks: Blocks, axes: tuple[int, ...]) -> np.ndarray:
    """(f's whole array).transpose(axes) on the virtual blocks `blocks`: f evaluated where the transpose reads from."""
    need: list[slice] = [slice(None)] * 3
    for n in range(3, 6):
        need[axes[n] - 3] = blocks[n - 3]
    return f(tuple(need)).transpose(axes)


def _cached(f: Fn) -> Fn:
    """f memoised on its blocks, for one block triple's permutations."""
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


def _p6(f: Fn, blocks: Blocks) -> np.ndarray:
    return sum(_permuted(f, blocks, ax) for ax in P6)


def _r4(f: Fn, blocks: Blocks) -> np.ndarray:
    """r4(f) on the block: u = f − f(j↔k), then u + u((j,b)↔(k,c))."""
    def u(b: Blocks) -> np.ndarray:
        x = f(b)
        return x - x.transpose(SWAP_JK)
    return u(blocks) + _permuted(u, blocks, SWAP_JK_BC)


def _d3(e: tuple[np.ndarray, np.ndarray, np.ndarray], blocks: Blocks) -> np.ndarray:
    """lib.direct_sum('ia+jb+kc->ijkabc', e0, e1, e2) on the block."""
    e0, e1, e2 = (x[:, b] for x, b in zip(e, blocks, strict=True))
    return e0[:, None, None, :, None, None] + e1[None, :, None, None, :, None] + e2[None, None, :, None, None, :]


# ------------------------------------------------------------------------------------------------------------------------- the inputs
@dataclass(frozen=True)
class Inputs:
    """What every (T) quantity reads: amplitudes, orbital-energy differences, Fock blocks, integrals (g) and their conjugates (c)."""
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

    def operand(self, name: str) -> np.ndarray:
        """A table operand: 'c.ovvv' the conjugated integral, 'g.ovov' the integral, 't2aa*' a conjugated amplitude, 'fvo' as named."""
        kind, _, key = name.partition(".")
        if key:
            return {"g": self.g, "c": self.c}[kind][key]
        base = name.removesuffix("*")
        x = {"t1a": self.t1a, "t1b": self.t1b, "t2aa": self.t2aa, "t2ab": self.t2ab, "t2bb": self.t2bb, "fvo": self.fvo, "fVO": self.fVO}[base]
        return x.conj() if name.endswith("*") else x


def inputs(t1, t2, eris) -> Inputs:
    t1a, t1b = t1
    t2aa, t2ab, t2bb = t2
    nocca, noccb = t2ab.shape[:2]
    mo_ea, mo_eb = eris.mo_energy
    g = {k: np.asarray(getattr(eris, UNPACKED[k])() if k in UNPACKED else getattr(eris, k)) for k in INTEGRALS}
    return Inputs(t1a, t1b, t2aa, t2ab, t2bb, mo_ea[:nocca, None] - mo_ea[nocca:], mo_eb[:noccb, None] - mo_eb[noccb:],
                  eris.focka[nocca:, :nocca], eris.fockb[noccb:, :noccb], g, {k: x.conj() for k, x in g.items()})


@dataclass(frozen=True)
class Case:
    """One spin case: the virtual counts and orbital-energy differences of its three positions, pyscf's w and v, same spin or mixed."""
    nv: tuple[int, int, int]
    e: tuple[np.ndarray, np.ndarray, np.ndarray]
    w: Fn
    v: Fn
    mixed: bool


def _cases(s: Inputs) -> dict[str, Case]:
    c, t1a, t1b, t2aa, t2ab, t2bb, fvo, fVO = s.c, s.t1a, s.t1b, s.t2aa, s.t2ab, s.t2bb, s.fvo, s.fVO
    _, _, nva, nvb = t2ab.shape

    def w_aaa(b):
        return _term("ijae,kceb->ijkabc", t2aa, c["ovvv"], b) - _term("mkbc,iajm->ijkabc", t2aa, c["ovoo"], b)

    def v_aaa(b):
        return _term("jbkc,ia->ijkabc", c["ovov"], t1a, b) + _term("jkbc,ai->ijkabc", t2aa, fvo, b) * .5

    def w_bbb(b):
        return _term("ijae,kceb->ijkabc", t2bb, c["OVVV"], b) - _term("imab,kcjm->ijkabc", t2bb, c["OVOO"], b)

    def v_bbb(b):
        return _term("jbkc,ia->ijkabc", c["OVOV"], t1b, b) + _term("jkbc,ai->ijkabc", t2bb, fVO, b) * .5

    def w_baa(b):                       # I, A beta; j, k, b, c alpha
        return (_term("jIeA,kceb->IjkAbc", t2ab, c["ovvv"], b) * 2 + _term("jIbE,kcEA->IjkAbc", t2ab, c["ovVV"], b) * 2
                + _term("jkbe,IAec->IjkAbc", t2aa, c["OVvv"], b) - _term("mIbA,kcjm->IjkAbc", t2ab, c["ovoo"], b) * 2
                - _term("jMbA,kcIM->IjkAbc", t2ab, c["ovOO"], b) * 2 - _term("jmbc,IAkm->IjkAbc", t2aa, c["OVoo"], b))

    def v_baa(b):
        return (_term("jbkc,IA->IjkAbc", c["ovov"], t1b, b) + _term("kcIA,jb->IjkAbc", c["ovOV"], t1a, b) * 2
                + _term("jkbc,AI->IjkAbc", t2aa, fVO, b) * .5 + _term("kIcA,bj->IjkAbc", t2ab, fvo, b) * 2)

    def w_bba(b):                       # i, a alpha; j, k, b, c beta
        return (_term("ijae,kceb->ijkabc", t2ab, c["OVVV"], b) * 2 + _term("ijeb,kcea->ijkabc", t2ab, c["OVvv"], b) * 2
                + _term("jkbe,iaec->ijkabc", t2bb, c["ovVV"], b) - _term("imab,kcjm->ijkabc", t2ab, c["OVOO"], b) * 2
                - _term("mjab,kcim->ijkabc", t2ab, c["OVoo"], b) * 2 - _term("jmbc,iakm->ijkabc", t2bb, c["ovOO"], b))

    def v_bba(b):
        return (_term("jbkc,ia->ijkabc", c["OVOV"], t1a, b) + _term("iakc,jb->ijkabc", c["ovOV"], t1b, b) * 2
                + _term("JKBC,ai->iJKaBC", t2bb, fvo, b) * .5 + _term("iKaC,BJ->iJKaBC", t2ab, fVO, b) * 2)

    a, b_ = s.eia, s.eIA
    return {"aaa": Case((nva,) * 3, (a, a, a), w_aaa, v_aaa, False), "bbb": Case((nvb,) * 3, (b_, b_, b_), w_bbb, v_bbb, False),
            "baa": Case((nvb, nva, nva), (b_, a, a), w_baa, v_baa, True), "bba": Case((nva, nvb, nvb), (a, b_, b_), w_bba, v_bba, True)}


# ------------------------------------------------------------------------------------------------------------------------- rw and wvd per block
def _lambda_pair(case: Case, blocks: Blocks) -> tuple[np.ndarray, np.ndarray]:
    """(rw, wvd) of the lambda and of γ2: r6(p6(w))/d3 and r6(p6(2w + v))/d3, or r4(·)/d3 for a mixed case."""
    w, v = _cached(case.w), _cached(case.v)
    d3 = _d3(case.e, blocks)
    if case.mixed:
        return _r4(w, blocks) / d3, _r4(lambda b: w(b) * 2 + v(b), blocks) / d3
    return _r6(_p6(w, blocks)) / d3, _r6(_p6(lambda b: w(b) * 2 + v(b), blocks)) / d3


def _gamma1_pair(case: Case, blocks: Blocks) -> tuple[np.ndarray, np.ndarray]:
    """(rw, wvd) of γ1: p6(r6(w))/d3 and p6(w + v)/d3, or r4(w)/d3 and (w + v)/d3 for a mixed case."""
    w, v = _cached(case.w), _cached(case.v)
    d3 = _d3(case.e, blocks)
    if case.mixed:
        return _r4(w, blocks) / d3, (w(blocks) + v(blocks)) / d3
    return _p6(lambda b: _r6(w(b)), blocks) / d3, _p6(lambda b: w(b) + v(b), blocks) / d3


Pair = Callable[[Case, Blocks], tuple[np.ndarray, np.ndarray]]


def _resolve(name: str, rw: np.ndarray, wvd: np.ndarray, s: Inputs) -> np.ndarray:
    if name in SIX:
        x = rw if name.startswith("rw") else wvd
        return x.conj() if name.endswith("*") else x
    return s.operand(name)


def _six_letters(term: Term) -> list[str]:
    _, spec, names, _ = term
    return [letters for letters, n in zip(spec.split("->")[0].split(","), names, strict=True) if n in SIX]


# ------------------------------------------------------------------------------------------------------------------------- the sweeps
def _local_sweep(case: Case, pair: Pair, terms: list[Term], s: Inputs, out: dict, size: int) -> None:
    """Every term whose six-index operands share their virtual letters: one pass over the block triples."""
    if not terms:
        return
    for blocks in itertools.product(*(_ranges(n, size) for n in case.nv)):
        rw, wvd = pair(case, blocks)
        for term in terms:
            target, spec, names, scale = term
            where = dict(zip(_six_letters(term)[0][3:], blocks, strict=True))
            _acc(out[target], spec, tuple(_resolve(n, rw, wvd, s) for n in names), where, scale)


def _paired_sweep(case: Case, pair: Pair, term: Term, s: Inputs, out: dict, size: int) -> None:
    """A term 'X,Y->ab' whose two six-index operands differ in one virtual position p: for each pair of blocks at the other two positions the
    blocks along p are held (o³·v·B² per operand) and every block pair along p is contracted."""
    target, spec, names, scale = term
    lx, ly = _six_letters(term)
    p = next(k for k in range(3, 6) if lx[k] != ly[k])
    others = [k for k in range(3, 6) if k != p]
    along = _ranges(case.nv[p - 3], size)
    for fixed in itertools.product(*(_ranges(case.nv[k - 3], size) for k in others)):
        held = []
        for blk in along:
            b: list[slice] = [slice(None)] * 3
            b[p - 3] = blk
            for k, sl in zip(others, fixed, strict=True):
                b[k - 3] = sl
            held.append(pair(case, (b[0], b[1], b[2])))
        shared = {lx[k]: sl for k, sl in zip(others, fixed, strict=True)}
        for (bx, (rwx, wvx)), (by, (rwy, wvy)) in itertools.product(zip(along, held, strict=True), repeat=2):
            x, y = _resolve(names[0], rwx, wvx, s), _resolve(names[1], rwy, wvy, s)
            _acc(out[target], spec, (x, y), {lx[p]: bx, ly[p]: by} | shared, scale)


def _run(table: dict[str, list[Term]], pair: Pair, s: Inputs, out: dict, size: int) -> None:
    if size < 1:
        raise ValueError(f"block {size}: at least one virtual index per block")
    for name, case in _cases(s).items():
        six = {term: _six_letters(term) for term in table[name]}
        paired = [t for t, ls in six.items() if len(ls) == 2 and ls[0][3:] != ls[1][3:]]
        _local_sweep(case, pair, [t for t in table[name] if t not in paired], s, out, size)
        for term in paired:
            _paired_sweep(case, pair, term, s, out, size)


# ------------------------------------------------------------------------------------------------------------------------- pyscf's lines
# 'rw*' = rw.conj(), 'c.x' = the conjugated integral, 'g.x' = the integral, 't2aa*' = the conjugated amplitude.
LAMBDA: dict[str, list[Term]] = {
    "aaa": [("l1a", "ijkabc,jbkc->ia", ("rw*", "g.ovov"), .25), ("pre_aa", "ijkabc,kceb->ijae", ("wvd", "c.ovvv"), 1.),
            ("pre_aa", "ijkabc,iajm->mkbc", ("wvd", "c.ovoo"), -1.), ("post_aa", "ijkabc,ai->jkbc", ("rw", "fvo"), 1.)],
    "bbb": [("l1b", "ijkabc,jbkc->ia", ("rw*", "g.OVOV"), .25), ("pre_bb", "ijkabc,kceb->ijae", ("wvd", "c.OVVV"), 1.),
            ("pre_bb", "ijkabc,iajm->mkbc", ("wvd", "c.OVOO"), -1.), ("post_bb", "ijkabc,ai->jkbc", ("rw", "fVO"), 1.)],
    "baa": [("l1a", "ijkabc,kcia->jb", ("rw*", "g.ovOV"), .5), ("l1b", "ijkabc,jbkc->ia", ("rw*", "g.ovov"), .25),
            ("pre_aa", "ijkabc,iaec->jkbe", ("wvd", "c.OVvv"), 1.), ("pre_aa", "ijkabc,iakm->jmbc", ("wvd", "c.OVoo"), -1.),
            ("post_aa", "ijkabc,ai->jkbc", ("rw", "fVO"), 1.), ("ab", "ijkabc,kceb->jiea", ("wvd", "c.ovvv"), 1.),
            ("ab", "ijkabc,kcea->jibe", ("wvd", "c.ovVV"), 1.), ("ab", "ijkabc,kcjm->miba", ("wvd", "c.ovoo"), -1.),
            ("ab", "ijkabc,kcim->jmba", ("wvd", "c.ovOO"), -1.), ("ab", "ijkabc,bj->kica", ("rw", "fvo"), 1.)],
    "bba": [("l1a", "ijkabc,jbkc->ia", ("rw*", "g.OVOV"), .25), ("l1b", "ijkabc,iakc->jb", ("rw*", "g.ovOV"), .5),
            ("pre_bb", "ijkabc,iaec->jkbe", ("wvd", "c.ovVV"), 1.), ("pre_bb", "ijkabc,iakm->jmbc", ("wvd", "c.ovOO"), -1.),
            ("post_bb", "ijkabc,ai->jkbc", ("rw", "fvo"), 1.), ("ab", "ijkabc,kceb->ijae", ("wvd", "c.OVVV"), 1.),
            ("ab", "ijkabc,kcea->ijeb", ("wvd", "c.OVvv"), 1.), ("ab", "ijkabc,kcjm->imab", ("wvd", "c.OVOO"), -1.),
            ("ab", "ijkabc,kcim->mjab", ("wvd", "c.OVoo"), -1.), ("ab", "ijkabc,bj->ikac", ("rw", "fVO"), 1.)],
}
GAMMA1: dict[str, list[Term]] = {
    "aaa": [("goo", "iklabc,jklabc->ij", ("wvd*", "rw"), .125), ("gvv", "ijkacd,ijkbcd->ab", ("wvd", "rw*"), .125),
            ("gvo", "jkbc,ijkabc->ai", ("t2aa*", "rw"), .125)],
    "bbb": [("gOO", "iklabc,jklabc->ij", ("wvd*", "rw"), .125), ("gVV", "ijkacd,ijkbcd->ab", ("wvd", "rw*"), .125),
            ("gVO", "jkbc,ijkabc->ai", ("t2bb*", "rw"), .125)],
    "baa": [("goo", "kilabc,kjlabc->ij", ("wvd*", "rw"), .25), ("goo", "kliabc,kljabc->ij", ("wvd*", "rw"), .25),
            ("gOO", "iklabc,jklabc->ij", ("wvd*", "rw"), .25), ("gvv", "ijkcad,ijkcbd->ab", ("wvd", "rw*"), .25),
            ("gvv", "ijkcda,ijkcdb->ab", ("wvd", "rw*"), .25), ("gVV", "ijkacd,ijkbcd->ab", ("wvd", "rw*"), .25),
            ("gvo", "kica,ijkabc->bj", ("t2ab*", "rw"), .5), ("gVO", "jkbc,ijkabc->ai", ("t2aa*", "rw"), .125)],
    "bba": [("goo", "iklabc,jklabc->ij", ("wvd*", "rw"), .25), ("gOO", "kilabc,kjlabc->ij", ("wvd*", "rw"), .25),
            ("gOO", "kliabc,kljabc->ij", ("wvd*", "rw"), .25), ("gvv", "ijkacd,ijkbcd->ab", ("wvd", "rw*"), .25),
            ("gVV", "ijkcad,ijkcbd->ab", ("wvd", "rw*"), .25), ("gVV", "ijkcda,ijkcdb->ab", ("wvd", "rw*"), .25),
            ("gVO", "ikac,ijkabc->bj", ("t2ab*", "rw"), .5), ("gvo", "jkbc,ijkabc->ai", ("t2bb*", "rw"), .125)],
}
GAMMA2: dict[str, list[Term]] = {
    "aaa": [("dovov", "ia,ijkabc->jbkc", ("t1a", "rw*"), .25), ("dooov", "mkbc,ijkabc->jmia", ("t2aa", "wvd*"), -.125),
            ("dovvv", "kjcf,ijkabc->iafb", ("t2aa", "wvd*"), .125)],
    "bbb": [("dOVOV", "ia,ijkabc->jbkc", ("t1b", "rw*"), .25), ("dOOOV", "mkbc,ijkabc->jmia", ("t2bb", "wvd*"), -.125),
            ("dOVVV", "kjcf,ijkabc->iafb", ("t2bb", "wvd*"), .125)],
    "baa": [("dovvv", "jiea,ijkabc->kceb", ("t2ab", "wvd*"), .25), ("dovVV", "jibe,ijkabc->kcea", ("t2ab", "wvd*"), .25),
            ("dOVvv", "jkbe,ijkabc->iaec", ("t2aa", "wvd*"), .125), ("dooov", "miba,ijkabc->jmkc", ("t2ab", "wvd*"), -.25),
            ("dOOov", "jmba,ijkabc->imkc", ("t2ab", "wvd*"), -.25), ("dooOV", "jmbc,ijkabc->kmia", ("t2aa", "wvd*"), -.125),
            ("dovov", "ia,ijkabc->jbkc", ("t1b", "rw*"), .25), ("dovOV", "jb,ijkabc->kcia", ("t1a", "rw*"), .25)],
    "bba": [("dOVVV", "ijae,ijkabc->kceb", ("t2ab", "wvd*"), .25), ("dOVvv", "ijeb,ijkabc->kcea", ("t2ab", "wvd*"), .25),
            ("dovVV", "jkbe,ijkabc->iaec", ("t2bb", "wvd*"), .125), ("dOOOV", "imab,ijkabc->jmkc", ("t2ab", "wvd*"), -.25),
            ("dooOV", "mjab,ijkabc->imkc", ("t2ab", "wvd*"), -.25), ("dOOov", "jmbc,ijkabc->kmia", ("t2bb", "wvd*"), -.125),
            ("dOVOV", "ia,ijkabc->jbkc", ("t1a", "rw*"), .25), ("dovOV", "jb,ijkabc->iakc", ("t1b", "rw*"), .25)],
}


# ------------------------------------------------------------------------------------------------------------------------- the entry points
def _eab(e1: np.ndarray, e2: np.ndarray) -> np.ndarray:
    return lib.direct_sum("ia+jb->ijab", e1, e2)


def make_intermediates(mycc, t1, t2, eris, block: int = BLOCK):
    """pyscf's `uccsd_t_lambda.make_intermediates`, blocked: the UCCSD lambda intermediates plus l1a_t, l1b_t, l2aa_t, l2ab_t, l2bb_t."""
    s = inputs(t1, t2, eris)
    out = {"l1a": np.zeros_like(s.t1a), "l1b": np.zeros_like(s.t1b), "pre_aa": np.zeros_like(s.t2aa), "post_aa": np.zeros_like(s.t2aa),
           "pre_bb": np.zeros_like(s.t2bb), "post_bb": np.zeros_like(s.t2bb), "ab": np.zeros_like(s.t2ab)}
    _run(LAMBDA, _lambda_pair, s, out, block)
    imds = uccsd_lambda.make_intermediates(mycc, t1, t2, eris)
    imds.l1a_t, imds.l1b_t = out["l1a"] / s.eia, out["l1b"] / s.eIA
    imds.l2aa_t = (out["pre_aa"] + out["pre_aa"].transpose(1, 0, 3, 2) + out["post_aa"]).conj() / _eab(s.eia, s.eia) * .5
    imds.l2bb_t = (out["pre_bb"] + out["pre_bb"].transpose(1, 0, 3, 2) + out["post_bb"]).conj() / _eab(s.eIA, s.eIA) * .5
    imds.l2ab_t = out["ab"].conj() / _eab(s.eia, s.eIA) * .5
    return imds


def gamma1_intermediates(mycc, t1, t2, l1, l2, eris=None, for_grad=False, block: int = BLOCK):  # noqa: PLR0913  (pyscf's signature + block)
    """pyscf's `uccsd_t_rdm._gamma1_intermediates`, blocked."""
    d1 = uccsd_rdm._gamma1_intermediates(mycc, t1, t2, l1, l2)
    s = inputs(t1, t2, mycc.ao2mo() if eris is None else eris)
    nocca, noccb, nvira, nvirb = s.t2ab.shape
    dt = s.t2ab.dtype
    out = {"goo": np.zeros((nocca, nocca), dt), "gOO": np.zeros((noccb, noccb), dt), "gvv": np.zeros((nvira, nvira), dt),
           "gVV": np.zeros((nvirb, nvirb), dt), "gvo": np.zeros((nvira, nocca), dt), "gVO": np.zeros((nvirb, noccb), dt)}
    _run(GAMMA1, _gamma1_pair, s, out, block)
    (doo, dOO), _, (dvo, dVO), (dvv, dVV) = d1
    if for_grad:
        doo -= out["goo"]
        dOO -= out["gOO"]
        dvv += out["gvv"]
        dVV += out["gVV"]
    else:
        doo[np.diag_indices(nocca)] -= out["goo"].diagonal()
        dOO[np.diag_indices(noccb)] -= out["gOO"].diagonal()
        dvv[np.diag_indices(nvira)] += out["gvv"].diagonal()
        dVV[np.diag_indices(nvirb)] += out["gVV"].diagonal()
    dvo += out["gvo"]
    dVO += out["gVO"]
    return d1


def _compress(x: np.ndarray, na: int, nb: int) -> np.ndarray:
    """A v⁴ block in pyscf's compressed pair form, with the 1/2 that pyscf ≤ 2.14.0 omitted on the mixed-spin block (pyscf#3305, #3387)."""
    ia, ib = np.tril_indices(na), np.tril_indices(nb)
    x = x + x.transpose(1, 0, 2, 3)
    return lib.take_2d(x.reshape(na**2, nb**2), ia[0] * na + ia[1], ib[0] * nb + ib[1]) * .5


def gamma2_intermediates(mycc, t1, t2, l1, l2, eris=None, compress_vvvv=False, block: int = BLOCK):  # noqa: PLR0913  (pyscf's signature + block)
    """pyscf's `uccsd_t_rdm._gamma2_intermediates`, blocked (the (T) terms; the UCCSD part and its v⁴ blocks are pyscf's, in core)."""
    d2 = uccsd_rdm._gamma2_intermediates(mycc, t1, t2, l1, l2)
    s = inputs(t1, t2, mycc.ao2mo() if eris is None else eris)
    _add_t_gamma2(d2, s, block)
    if not compress_vvvv:
        return d2
    nvira, nvirb = s.t2ab.shape[2:]
    dvvvv, dvvVV, dVVvv, dVVVV = d2[1]
    return (d2[0], (_compress(dvvvv, nvira, nvira), _compress(dvvVV, nvira, nvirb), dVVvv, _compress(dVVVV, nvirb, nvirb)), *d2[2:])


def gamma2_outcore(mycc, t1, t2, l1, l2, eris, h5fobj, compress_vvvv=True, block: int = BLOCK,  # noqa: PLR0913  (pyscf's signature + sizes)
                   slab_mb: float = V4_SLAB_MB):
    """pyscf's `uccsd_t_rdm._gamma2_outcore` as its name says: the UCCSD part from `uccsd_gamma2_outcore` (v⁴ blocks compressed into
    `h5fobj`), the (T) terms blocked. The gradient's call; compress_vvvv=False is refused there."""
    d2 = gamma2_outcore_uccsd(mycc, t1, t2, l1, l2, h5fobj, compress_vvvv, slab_mb)
    _add_t_gamma2(d2, inputs(t1, t2, eris), block)
    return d2


def _add_t_gamma2(d2: tuple, s: Inputs, block: int) -> None:
    """The (T) terms of GAMMA2 added in place to pyscf's UCCSD d2 blocks (none of them a v⁴ block)."""
    (dovov, dovOV, _, dOVOV), _, _, _, _, _, (dovvv, dovVV, dOVvv, dOVVV), (dooov, dooOV, dOOov, dOOOV) = d2
    out = {"dovov": dovov, "dovOV": dovOV, "dOVOV": dOVOV, "dovvv": dovvv, "dovVV": dovVV, "dOVvv": dOVvv, "dOVVV": dOVVV,
           "dooov": dooov, "dooOV": dooOV, "dOOov": dOOov, "dOOOV": dOOOV}
    _run(GAMMA2, _lambda_pair, s, out, block)
