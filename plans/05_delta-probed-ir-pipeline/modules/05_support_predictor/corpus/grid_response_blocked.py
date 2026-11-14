"""The XC grid-response nuclear gradient of an RKS calculation, with each atom's grid split into blocks.

pyscf's `grad/rks.py` (2.15.0) evaluates the grid response (`get_vxc_full_response`, `grids_response_becke`) on all of one atom's grid
points at once and ignores max_memory: the GGA AO array (10, ngrid, nao) and the Becke partition derivatives (natm, natm, 3, ngrid) at
an unpruned (150, 974) grid on a 38-atom molecule need > 12 GB, and the cgroup OOM killer stopped TASKS 49's option 3 twice (12 Nov
2026). Every term is a sum over grid points and every partition function is pointwise, so splitting each atom's grid into blocks gives
the same gradient up to summation order. The partition code follows pyscf's `grids_response_becke` (Apache-2.0, The PySCF Developers;
JCP 98, 5612 (1993)) line for line, with the per-block call added.

Use it through `blocked_grid_response()`, which swaps pyscf's `get_vxc_full_response` for the blocked one inside a `with` block:

    with blocked_grid_response():
        g = mf.nuc_grad_method().set(grid_response=True).kernel()

LDA and GGA functionals, closed-shell density matrices and the Becke and Stratmann partitions are supported; anything else raises.
"""
from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterator
from typing import Any

import numpy as np
import pyscf
from pyscf import gto
from pyscf.dft import gen_grid, numint, radi
from pyscf.grad import rks as rks_grad

try:   # the Stratmann branch's helper arrived in pyscf 2.15.0; this module follows that code line for line
    from pyscf.grad.rks import _d1_dot_, _gga_grad_sum_, _grid_response_reciprocal
except ImportError as exc:
    raise ImportError("grid_response_blocked follows pyscf's grid-response code line for line and needs pyscf 2.15.0 or newer; "
                      f"this environment has {pyscf.__version__}") from exc

MEMORY_FRACTION = 0.5          # of max_memory for one block's arrays; the rest is the caller's (density matrix, vmat, the AO screen)
SUPPORTED_XC = ("LDA", "GGA")


def block_size(natm: int, nao: int, max_memory_mb: float) -> int:
    """Grid points per block: the block's AO array (10 nao) and partition arrays (3 natm² + 5 natm) within MEMORY_FRACTION of max_memory,
    a multiple of pyscf's BLKSIZE and at least one BLKSIZE."""
    bytes_per_point = 8 * (10 * nao + 3 * natm * natm + 5 * natm)
    points = int(max_memory_mb * 1e6 * MEMORY_FRACTION / bytes_per_point)
    return max(gen_grid.BLKSIZE, points // gen_grid.BLKSIZE * gen_grid.BLKSIZE)


def _radii_adjust(grids: Any, mol: gto.Mole) -> tuple[Callable, Callable]:
    """pyscf's radii adjustment of the Becke cell function and its derivative factor."""
    charges = mol.atom_charges()
    if grids.radii_adjust == radi.treutler_atomic_radii_adjust:
        rad = np.sqrt(grids.atomic_radii[charges]) + 1e-200
    elif grids.radii_adjust == radi.becke_atomic_radii_adjust:
        rad = grids.atomic_radii[charges] + 1e-200
    else:
        return (lambda i, j, g: g), (lambda *args: 1)
    rr = rad.reshape(-1, 1) * (1.0 / rad)
    a = 0.25 * (rr.T - rr)
    a[a < -0.5] = -0.5
    a[a > 0.5] = 0.5
    return (lambda i, j, g: g + a[i, j] * (1 - g**2)), (lambda i, j, g: 1 - 2 * a[i, j] * g)


def _smooth_function_derivative(becke_scheme: Callable, mu: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The cell function s(mu) and its derivative factor for the original Becke or the Stratmann scheme."""
    if becke_scheme == gen_grid.original_becke:
        p0 = mu
        p1 = (3 - p0**2) * p0 * 0.5
        p2 = (3 - p1**2) * p1 * 0.5
        p3 = (3 - p2**2) * p2 * 0.5
        return p3, 27.0 / 8.0 * (1 - p2**2) * (1 - p1**2) * (1 - p0**2)
    if becke_scheme == gen_grid.stratmann:
        a = 0.64
        ma = mu / a
        ma2 = ma * ma
        g1 = (1 / 16.0) * (ma * (35 + ma2 * (-35 + ma2 * (21 - 5 * ma2))))
        g1[mu <= -a] = -1
        g1[mu >= a] = 1
        t_uab = (35.0 / 16.0 / a) * (1.0 - ma2 * (3.0 - ma2 * (3.0 - ma2)))
        t_uab[mu <= -a] = 0
        t_uab[mu >= a] = 0
        return g1, t_uab
    raise NotImplementedError(f"grid response for becke_scheme {becke_scheme} is not implemented")


class BeckePartition:
    """The Becke partition weights of one atom's grid points and their nuclear derivatives, as pyscf's `grids_response_becke`."""

    def __init__(self, grids: Any) -> None:
        if grids.becke_scheme not in (gen_grid.original_becke, gen_grid.stratmann):
            raise NotImplementedError(f"becke_scheme {grids.becke_scheme} (only original_becke and stratmann)")
        self.mol = grids.mol
        self.scheme = grids.becke_scheme
        self.atm_coords = np.asarray(self.mol.atom_coords(), order="C")
        self.atm_dist = gto.inter_distance(self.mol, self.atm_coords)
        self.fadjust, self.gadjust = _radii_adjust(grids, self.mol)

    def partition(self, coords: np.ndarray, atom_id: int) -> tuple[np.ndarray, np.ndarray]:
        """pbecke (natm, ngrid) and dpbecke (natm, natm, 3, ngrid) at coords, grid points of atom atom_id."""
        natm, atm_coords, atm_dist = self.mol.natm, self.atm_coords, self.atm_dist
        grid_dist, grid_norm_vec = [], []
        for ia in range(natm):
            v = (atm_coords[ia] - coords).T
            normv = np.linalg.norm(v, axis=0)
            v *= _grid_response_reciprocal(normv)
            grid_dist.append(normv)
            grid_norm_vec.append(v)

        def get_du(ia: int, ib: int) -> np.ndarray:      # JCP 98, 5612 (1993); (B10)
            uab = atm_coords[ia] - atm_coords[ib]
            duab = 1.0 / atm_dist[ia, ib] * grid_norm_vec[ia]
            duab -= uab[:, None] / atm_dist[ia, ib] ** 3 * (grid_dist[ia] - grid_dist[ib])
            return duab

        pbecke = np.ones((natm, coords.shape[0]))
        dpbecke = np.zeros((natm, natm, 3, coords.shape[0]))
        for ia in range(natm):
            for ib in range(ia):
                g = 1 / atm_dist[ia, ib] * (grid_dist[ia] - grid_dist[ib])
                smoothed, t_uab = _smooth_function_derivative(self.scheme, self.fadjust(ia, ib, g))
                t_uab *= 0.5 * self.gadjust(ia, ib, g)
                s_uab = 0.5 * (1 - smoothed)
                s_uba = 0.5 * (1 + smoothed)
                pbecke[ia] *= s_uab
                pbecke[ib] *= s_uba
                pt_uab = -t_uab * _grid_response_reciprocal(s_uab)
                pt_uba = t_uab * _grid_response_reciprocal(s_uba)
                duab = get_du(ia, ib)
                duba = get_du(ib, ia)
                d_a = duba if ia == atom_id else duab
                dpbecke[ia, ia] += pt_uab * d_a
                dpbecke[ia, ib] += pt_uba * d_a
                d_b = duab if ib == atom_id else duba
                dpbecke[ib, ib] -= pt_uba * d_b
                dpbecke[ib, ia] -= pt_uab * d_b
                if atom_id not in (ia, ib):                 # the terms (B8) and (B10) of JCP 98, 5612 miss
                    ua_ub = (grid_norm_vec[ia] - grid_norm_vec[ib]) / atm_dist[ia, ib]
                    dpbecke[atom_id, ia] -= pt_uab * ua_ub
                    dpbecke[atom_id, ib] -= pt_uba * ua_ub
        for ia in range(natm):
            dpbecke[:, ia] *= pbecke[ia]
        return pbecke, dpbecke


def grids_response_blocked(grids: Any, blksize: int) -> Iterator[tuple[int, np.ndarray, np.ndarray, np.ndarray]]:
    """(atom_id, coords, w0, w1) per block of at most blksize points of each atom's grid; w1 is (natm, 3, npoints)."""
    if blksize < 1:
        raise ValueError(f"blksize {blksize} must be positive")
    mol = grids.mol
    becke = BeckePartition(grids)
    atom_grids_tab = grids.gen_atomic_grids(mol, grids.atom_grid, grids.radi_method, grids.level, grids.prune)
    for ia in range(mol.natm):
        coords_all, vol_all = atom_grids_tab[mol.atom_symbol(ia)]
        coords_all = coords_all + becke.atm_coords[ia]
        for p0 in range(0, len(vol_all), blksize):
            coords, vol = coords_all[p0:p0 + blksize], vol_all[p0:p0 + blksize]
            pbecke, dpbecke = becke.partition(coords, ia)
            z = _grid_response_reciprocal(pbecke.sum(axis=0))
            w1 = dpbecke[:, ia] * z
            w1 -= pbecke[ia] * z**2 * dpbecke.sum(axis=1)
            w1 *= vol
            yield ia, coords, vol * pbecke[ia] * z, w1


def get_vxc_full_response_blocked(ni: numint.NumInt, mol: gto.Mole, grids: Any, xc_code: str, dms: np.ndarray, relativity: int = 0,  # noqa: PLR0913  pyscf's signature, called by its get_veff
                                  hermi: int = 1, max_memory: float = 2000, verbose: Any = None) -> tuple[np.ndarray, np.ndarray]:
    """pyscf's `get_vxc_full_response` (excsum (natm, 3), vmat (3, nao, nao)) with each atom's grid in blocks of `block_size` points."""
    xctype = ni._xc_type(xc_code)
    if xctype not in SUPPORTED_XC:
        raise NotImplementedError(f"blocked grid response for xc type {xctype} (only {', '.join(SUPPORTED_XC)})")
    if np.asarray(dms).ndim != 2:
        raise NotImplementedError("blocked grid response for one closed-shell density matrix only")
    make_rho, _nset, nao = ni._gen_rho_evaluator(mol, dms, hermi, False, grids)
    ao_loc = mol.ao_loc_nr()
    excsum = np.zeros((mol.natm, 3))
    vmat = np.zeros((3, nao, nao))
    ao_deriv = 1 if xctype == "LDA" else 2
    for atm_id, coords, weight, weight1 in grids_response_blocked(grids, block_size(mol.natm, nao, max_memory)):
        mask = gen_grid.make_mask(mol, coords)
        ao = ni.eval_ao(mol, coords, deriv=ao_deriv, non0tab=mask, cutoff=grids.cutoff)
        vtmp = np.zeros((3, nao, nao))
        if xctype == "LDA":
            rho = make_rho(0, ao[0], mask, xctype)
            exc, vxc = ni.eval_xc_eff(xc_code, rho, 1, xctype=xctype)[:2]
            aow = numint._scale_ao(ao[0], weight * vxc[0])
            _d1_dot_(vtmp, mol, ao[1:4], aow, mask, ao_loc, True)
            rho0 = rho
        else:
            rho = make_rho(0, ao[:4], mask, xctype)
            exc, vxc = ni.eval_xc_eff(xc_code, rho, 1, xctype=xctype)[:2]
            wv = weight * vxc
            wv[0] *= 0.5
            _gga_grad_sum_(vtmp, mol, ao, wv, mask, ao_loc)
            rho0 = rho[0]
        vmat += vtmp
        excsum += np.einsum("r,r,nxr->nx", exc, rho0, weight1)               # response of the weights
        excsum[atm_id] += np.einsum("xij,ji->x", vtmp, dms) * 2               # response of the grid coordinates
    return excsum, -vmat                                                      # pyscf's sign convention for vmat


@contextlib.contextmanager
def blocked_grid_response() -> Iterator[None]:
    """pyscf's RKS gradients use the blocked grid response inside the block (`get_veff` looks the function up at call time)."""
    original = rks_grad.get_vxc_full_response
    rks_grad.get_vxc_full_response = get_vxc_full_response_blocked
    try:
        yield
    finally:
        rks_grad.get_vxc_full_response = original
