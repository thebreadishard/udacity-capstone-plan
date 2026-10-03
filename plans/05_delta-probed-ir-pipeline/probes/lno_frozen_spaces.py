"""Frozen LNO spaces for finite differences (the M2 idea of 20 Sep 2026; LNO follow-up cell (b), registered 3 Oct 23:3x).

pyscf's LNO kernel builds, per fragment, the local active space in `mlno.make_las(eris, orbloc, lno_type, lno_param)` and returns
`(orbfrag, frzfrag, uoccact_loc, msg)`: the fragment's full orbital set in the AO basis (nmo columns: frozen occ, active occ LNOs, active vir
LNOs, frozen vir), the indices of its frozen columns, and the fragment LO expressed in the active occ LNOs. `capture()` records these at the
reference geometry; `replay()` returns, at a displaced geometry, the *same* spaces carried over: every stored active orbital is projected onto
the displaced occupied (or virtual) canonical space, the block is Löwdin-orthonormalised and semi-canonicalised in that space, and the frozen
blocks are the orthogonal complements — so the occupied determinant is the displaced Hartree–Fock one and the correlation treatment sees the
reference geometry's domains. The Pipek–Mezey localised orbitals are carried the same way (no re-localisation at the displaced point).

Upstream usage of the pieces this module relies on: `pyscf/lno/lno.py` (`kernel`, `make_las`, `subspace_eigh`) and `pyscf/lno/test/test_lnoccsd.py`
(construction of LNOCCSD with `lo_coeff`, `frag_lolist`, `frozen`); read on 3 Oct 2026 (rule of 29 Sep: a new library call cites the upstream
test that makes the same call).
"""
from __future__ import annotations

import types

import numpy as np

__all__ = ["capture", "replay", "project_lo", "save_store", "load_store"]


def _lowdin_columns(u: np.ndarray) -> np.ndarray:
    """Orthonormalise the columns of u (Euclidean metric; u already lives in an orthonormal MO basis)."""
    m = u.T @ u
    w, v = np.linalg.eigh(m)
    if w.min() < 1e-10:
        raise ValueError(f"projected block lost rank (smallest overlap eigenvalue {w.min():.2e}); the displacement is too large for frozen spaces")
    return u @ (v @ np.diag(w ** -0.5) @ v.T)


def _complement(u: np.ndarray, n: int) -> np.ndarray:
    """Orthonormal basis of R^n orthogonal to the orthonormal columns of u (n×k) — the frozen block."""
    p = np.eye(n) - u @ u.T
    w, v = np.linalg.eigh(p)
    keep = w > 0.5
    assert keep.sum() == n - u.shape[1], (keep.sum(), n, u.shape)
    return v[:, keep]


def _semicanonical(u: np.ndarray, e: np.ndarray) -> np.ndarray:
    """Rotate the block u (in a canonical MO basis with energies e) so that the Fock matrix is diagonal inside it (pyscf's subspace_eigh)."""
    f = u.T @ np.diag(e) @ u
    _, v = np.linalg.eigh(f)
    return u @ v


def project_lo(lo_ref: np.ndarray, c_act: np.ndarray, s: np.ndarray) -> np.ndarray:
    """The reference LOs carried to a new geometry: projected onto the new active-occupied space, orthonormalised, back in the AO basis."""
    u = c_act.T @ s @ lo_ref
    return c_act @ _lowdin_columns(u)


def capture(mcc, store: dict) -> None:
    """Wrap mcc.make_las so that every fragment's (orbfrag, frzfrag, uoccact_loc) lands in store['frags'] in call order."""
    store.setdefault("frags", [])
    original = mcc.make_las

    def make_las(self, eris, orbloc, lno_type, lno_param):
        orbfrag, frzfrag, uloc, msg = original(eris, orbloc, lno_type, lno_param)
        store["frags"].append({"orbfrag": np.array(orbfrag, copy=True), "frzfrag": np.array(frzfrag, copy=True).reshape(-1), "uloc": np.array(uloc, copy=True)})
        return orbfrag, frzfrag, uloc, msg

    mcc.make_las = types.MethodType(make_las, mcc)


def replay(mcc, mf, store: dict) -> None:
    """Wrap mcc.make_las so that fragment i receives the reference's spaces carried to mf's geometry (see the module docstring)."""
    s = mf.get_ovlp()
    occ = mf.mo_occ > 1e-10
    c_o, c_v = mf.mo_coeff[:, occ], mf.mo_coeff[:, ~occ]
    e_o, e_v = mf.mo_energy[occ], mf.mo_energy[~occ]
    nocc, nvir = c_o.shape[1], c_v.shape[1]
    frags = store["frags"]
    counter = {"i": 0}

    def make_las(self, eris, orbloc, lno_type, lno_param):
        rec = frags[counter["i"]]; counter["i"] += 1
        orbfrag, frz = rec["orbfrag"], set(int(j) for j in rec["frzfrag"])
        nmo = orbfrag.shape[1]
        assert nmo == nocc + nvir, (nmo, nocc, nvir)
        act_o = [j for j in range(nocc) if j not in frz]
        act_v = [j for j in range(nocc, nmo) if j not in frz]
        # active blocks: projection of the stored AO orbitals onto the new canonical spaces, orthonormalised, semi-canonical
        u_a = _semicanonical(_lowdin_columns(c_o.T @ s @ orbfrag[:, act_o]), e_o)
        u_b = _semicanonical(_lowdin_columns(c_v.T @ s @ orbfrag[:, act_v]), e_v)
        u_fo = _complement(u_a, nocc)
        u_fv = _complement(u_b, nvir)
        orb_occfrz, orb_occact, orb_viract, orb_virfrz = c_o @ u_fo, c_o @ u_a, c_v @ u_b, c_v @ u_fv
        new = np.hstack((orb_occfrz, orb_occact, orb_viract, orb_virfrz))
        n_fo, n_a, n_b = orb_occfrz.shape[1], orb_occact.shape[1], orb_viract.shape[1]
        frzfrag = np.concatenate((np.arange(0, n_fo), np.arange(n_fo + n_a + n_b, nmo))).astype(int)
        if len(frzfrag) == 0:
            frzfrag = 0
        uloc = orb_occact.T @ s @ orbloc
        msg = f"{n_a}/{nocc} Occ | {n_b}/{nvir} Vir | {n_a + n_b}/{nmo} MOs (frozen spaces of the reference, carried)"
        return new, frzfrag, uloc, msg

    mcc.make_las = types.MethodType(make_las, mcc)


def save_store(path: str, store: dict) -> None:
    arrays = {"lo_coeff": store["lo_coeff"], "n_frags": np.array([len(store["frags"])])}
    for i, f in enumerate(store["frags"]):
        arrays[f"orbfrag_{i}"] = f["orbfrag"]; arrays[f"frzfrag_{i}"] = f["frzfrag"]; arrays[f"uloc_{i}"] = f["uloc"]
    np.savez_compressed(path, **arrays)


def load_store(path: str) -> dict:
    z = np.load(path)
    n = int(z["n_frags"][0])
    return {"lo_coeff": z["lo_coeff"], "frags": [{"orbfrag": z[f"orbfrag_{i}"], "frzfrag": z[f"frzfrag_{i}"], "uloc": z[f"uloc_{i}"]} for i in range(n)]}
