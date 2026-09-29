"""Fast (T) density intermediates for pyscf's CCSD(T) gradient: a ctypes front to ccsd_t_rdm_kernel.so.

`install()` replaces `_gamma1_intermediates`, `_gamma2_intermediates` and `_gamma2_outcore` in `pyscf.cc.ccsd_t_rdm`
(pyscf.grad.ccsd_t looks them up on the module at call time, so the replacement is seen); `uninstall()` restores them.
The CCSD parts still come from pyscf's `ccsd_rdm`; only the (T) triples work moves to C. The kernel computes all six
(T) contributions in one pass and the result is cached for the (t1, t2, eris) triple so gamma1 and gamma2 pay once.

`check_against_pyscf(mycc, t1, t2, l1, l2, eris)` runs pyscf's Python functions as the second route and returns the largest
element-wise difference over all intermediates (the noise principle applied to our own speed-up; e8_cc_hessian_fd.py runs
it on the reference gradient of every run when --fast-t-density is given). Design note:
GoalGathering/notes/Design_Note_2026-09-29_T_Density_C_Kernel.md; build with build.sh; RHF/real only, any point group.
"""
import ctypes
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SO = os.path.join(HERE, "ccsd_t_rdm_kernel.so")
_lib = None
_cache = {"key": None, "value": None}


def available():
    return os.path.exists(SO)


def _load():
    global _lib
    if _lib is None:
        import pyscf
        from pyscf.cc import _ccsd  # noqa: F401  (loads libcc and, with it, pyscf's BLAS and OpenMP runtime)
        libdir = os.path.join(os.path.dirname(pyscf.__file__), "lib")
        ctypes.CDLL(os.path.join(libdir, "libcc.so"), mode=ctypes.RTLD_GLOBAL)
        _lib = ctypes.CDLL(SO)
        _lib.t_density_intermediates.restype = ctypes.c_int
    return _lib


def _c(a):
    return a.ctypes.data_as(ctypes.c_void_p)


def prepare(t1, t2, eris):
    """The sorted inputs of the kernel from pyscf's eris (active space; same conventions as pyscf.cc.ccsd_t)."""
    nocc, nvir = t1.shape
    nmo = nocc + nvir
    ovvv = np.asarray(eris.get_ovvv())
    ovoo = np.asarray(eris.ovoo)
    ovov = np.asarray(eris.ovov)
    vvop = np.empty((nvir, nvir, nocc, nmo))
    vvop[:, :, :, :nocc] = ovov.transpose(1, 3, 0, 2)
    vvop[:, :, :, nocc:] = ovvv.transpose(1, 3, 0, 2)
    return dict(nocc=nocc, nvir=nvir,
                mo_energy=np.ascontiguousarray(eris.mo_energy, dtype=float),
                t1T=np.ascontiguousarray(t1.T, dtype=float),
                t2T=np.ascontiguousarray(t2.transpose(2, 3, 1, 0), dtype=float),
                vooo=np.ascontiguousarray(ovoo.transpose(1, 0, 2, 3), dtype=float),
                vvop=vvop,
                fvo=np.ascontiguousarray(eris.fock[nocc:, :nocc], dtype=float))


def kernel(t1, t2, eris):
    """All six (T) contributions: goo, gvv, dvo_t, dovov_t, dooov_t, dovvv_t (the increments, not the totals)."""
    if not available():
        raise RuntimeError(f"{SO} not built: run bash {os.path.join(HERE, 'build.sh')}")
    p = prepare(t1, t2, eris)
    nocc, nvir = p["nocc"], p["nvir"]
    out = dict(goo=np.zeros((nocc, nocc)), gvv=np.zeros((nvir, nvir)), dvo=np.zeros((nvir, nocc)),
               dovov=np.zeros((nocc, nvir, nocc, nvir)), dooov=np.zeros((nocc, nocc, nocc, nvir)),
               dovvv=np.zeros((nocc, nvir, nvir, nvir)))
    rc = _load().t_density_intermediates(
        ctypes.c_int(nocc), ctypes.c_int(nvir), _c(p["mo_energy"]), _c(p["t1T"]), _c(p["t2T"]), _c(p["vooo"]),
        _c(p["vvop"]), _c(p["fvo"]), _c(out["goo"]), _c(out["gvv"]), _c(out["dvo"]), _c(out["dovov"]),
        _c(out["dooov"]), _c(out["dovvv"]))
    if rc != 0:
        raise MemoryError("t_density_intermediates: a thread could not allocate its buffers")
    return out


def _cached(t1, t2, eris):
    key = (id(t1), id(t2), id(eris), float(np.sum(t1)), float(np.sum(t2)))
    if _cache["key"] != key:
        _cache["key"], _cache["value"] = key, kernel(t1, t2, eris)
    return _cache["value"]


def _check_real(*arrays):
    if any(np.iscomplexobj(a) for a in arrays):
        raise ValueError("t_density_fast supports real-valued RHF-CCSD(T) only")


def _gamma1_intermediates(mycc, t1, t2, l1, l2, eris=None, for_grad=False):
    from pyscf.cc import ccsd_rdm
    _check_real(t1, t2, l1, l2)
    doo, dov, dvo, dvv = ccsd_rdm._gamma1_intermediates(mycc, t1, t2, l1, l2)
    if eris is None:
        eris = mycc.ao2mo()
    t = _cached(t1, t2, eris)
    nocc, nvir = t1.shape
    dvo = dvo + t["dvo"]
    if not for_grad:
        doo[np.diag_indices(nocc)] -= t["goo"].diagonal() * .5
        dvv[np.diag_indices(nvir)] += t["gvv"].diagonal() * .5
    else:
        doo = doo - t["goo"] * .5
        dvv = dvv + t["gvv"] * .5
    return doo, dov, dvo, dvv


def _gamma2_intermediates(mycc, t1, t2, l1, l2, eris=None, compress_vvvv=False):
    from pyscf import lib
    from pyscf.cc import ccsd_rdm
    _check_real(t1, t2, l1, l2)
    dovov, dvvvv, doooo, doovv, dovvo, dvvov, dovvv, dooov = ccsd_rdm._gamma2_intermediates(mycc, t1, t2, l1, l2)
    if eris is None:
        eris = mycc.ao2mo()
    t = _cached(t1, t2, eris)
    dovov = dovov + t["dovov"]
    dooov = dooov + t["dooov"]
    dovvv = dovvv + t["dovvv"]
    dvvov = dovvv.transpose(2, 3, 0, 1)
    if compress_vvvv:
        nvir = mycc.nmo - mycc.nocc
        idx = np.tril_indices(nvir)
        vidx = idx[0] * nvir + idx[1]
        dvvvv = dvvvv + dvvvv.transpose(1, 0, 2, 3)
        dvvvv = dvvvv + dvvvv.transpose(0, 1, 3, 2)
        dvvvv = lib.take_2d(dvvvv.reshape(nvir**2, nvir**2), vidx, vidx)
        dvvvv *= .25
    return dovov, dvvvv, doooo, doovv, dovvo, dvvov, dovvv, dooov


def _gamma2_outcore(mycc, t1, t2, l1, l2, eris, h5fobj, compress_vvvv=False):
    return _gamma2_intermediates(mycc, t1, t2, l1, l2, eris, compress_vvvv)


_ORIGINALS = {}


def install():
    from pyscf.cc import ccsd_t_rdm as M
    if not _ORIGINALS:
        for name in ("_gamma1_intermediates", "_gamma2_intermediates", "_gamma2_outcore"):
            _ORIGINALS[name] = getattr(M, name)
    M._gamma1_intermediates = _gamma1_intermediates
    M._gamma2_intermediates = _gamma2_intermediates
    M._gamma2_outcore = _gamma2_outcore


def uninstall():
    from pyscf.cc import ccsd_t_rdm as M
    for name, fn in _ORIGINALS.items():
        setattr(M, name, fn)


def check_against_pyscf(mycc, t1, t2, l1, l2, eris):
    """Second route: pyscf's Python intermediates versus ours; returns {name: max |difference|} over both gammas."""
    from pyscf.cc import ccsd_t_rdm
    g1_ref = _ORIGINALS.get("_gamma1_intermediates", ccsd_t_rdm._gamma1_intermediates)
    g2_ref = _ORIGINALS.get("_gamma2_intermediates", ccsd_t_rdm._gamma2_intermediates)
    if g1_ref is _gamma1_intermediates or g2_ref is _gamma2_intermediates:
        raise RuntimeError("check_against_pyscf: the reference functions are not available (installed before import?)")
    diffs = {}
    for for_grad in (False, True):
        ref = g1_ref(mycc, t1, t2, l1, l2, eris, for_grad=for_grad)
        new = _gamma1_intermediates(mycc, t1, t2, l1, l2, eris, for_grad=for_grad)
        for name, r, n in zip(("doo", "dov", "dvo", "dvv"), ref, new):
            diffs[f"{name}[for_grad={for_grad}]"] = float(np.max(np.abs(np.asarray(r) - np.asarray(n))))
    ref = g2_ref(mycc, t1, t2, l1, l2, eris)
    new = _gamma2_intermediates(mycc, t1, t2, l1, l2, eris)
    for name, r, n in zip(("dovov", "dvvvv", "doooo", "doovv", "dovvo", "dvvov", "dovvv", "dooov"), ref, new):
        diffs[name] = float(np.max(np.abs(np.asarray(r) - np.asarray(n))))
    return diffs
