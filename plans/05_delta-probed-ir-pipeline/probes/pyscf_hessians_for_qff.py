"""Analytic DFT Hessians with pyscf at a set of displaced geometries, written as qcschema-like json so that
`qff_from_hessians.py` can assemble the quartic force field from them (21 September 2026).

Why: psi4 has no analytic B3LYP Hessian, so its Hessians are finite differences of gradients; a quartic force field by a second
finite difference on top of that is noisy (benzene, 20–21 September: two-route disagreement of the semi-diagonal quartic constants
median 22, max 1,265 cm⁻¹). pyscf has analytic RKS Hessians. This script takes the geometries of an existing cache directory (the
psi4/pyVPT2 displacements, so that the two force fields are compared point by point), computes the analytic Hessian at each, and
writes `<out_dir>/<same file name>` with the fields qff_from_hessians.py reads: driver, molecule{symbols, geometry (bohr)}, return_result.

Usage: python pyscf_hessians_for_qff.py <cache_dir> <out_dir> [--xc b3lyp] [--basis 6-31g*] [--grid 99,590] [--threads 4]
Note on the functional: pyscf's 'b3lyp' is the Gaussian definition (VWN3-type correlation); psi4's 'b3lyp' is the same family. The
noise diagnostic does not depend on this; absolute frequencies do at the cm⁻¹ level, and the report says which was used.
pyscf's own log (every SCF cycle and the Hessian's step timers, `library_log.py`) is appended to `<out_dir>/pyscf.log`, so a Hessian that
runs for an hour shows whether it is computing (19 Oct 2026). A stalled DIIS falls back to the second-order solver (`scf_converge.py`;
acenaphthylene's T reference Hessian, 19 Oct).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import time
from typing import Any, TextIO

import numpy as np
from library_log import PYSCF_LOG_NAME, pyscf_mole
from scf_converge import converged_scf


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("cache_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--xc", default="b3lyp")
    ap.add_argument("--basis", default="6-31g*")
    ap.add_argument("--grid", default="99,590")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--conv", type=float, default=1e-11)
    ap.add_argument("--max-first-seconds", type=float, default=None, help="13 Oct 2026 (S1's stop rule): stop after the first Hessian computed "
                    "in this call when it took longer than this — time first, then the rest")
    ap.add_argument("--guess-from-previous", action="store_true", help="19 Oct 2026: start each SCF from the previous Hessian's converged "
                    "density (displaced geometries are close; DIIS from pyscf's default guess stalls for acenaphthylene at def2-TZVP)")
    return ap.parse_args()


def rks_setup(mol: Any, xc: str, grid: str, conv: float) -> Any:
    """The RKS of every Hessian here: functional, unpruned (radial, angular) grid, energy and gradient thresholds."""
    from pyscf import dft
    rad, ang = (int(x) for x in grid.split(","))
    mf = dft.RKS(mol)
    mf.xc = xc
    mf.grids.atom_grid = (rad, ang)
    mf.grids.prune = None
    mf.conv_tol = conv
    mf.conv_tol_grad = 1e-8
    return mf


def displaced_geometry(path: str) -> dict[str, Any] | None:
    """The record of a cache file that asks for a Hessian, None for any other file."""
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    if not isinstance(d, dict) or d.get("driver") != "hessian" or "molecule" not in d:
        return None
    return d


def hessian_record(d: dict[str, Any], a: argparse.Namespace, lib_log: TextIO, dm0: Any = None) -> tuple[dict[str, Any], float, Any]:
    """The analytic Hessian at one displaced geometry as the record qff_from_hessians.py reads, with its energy and the converged density
    (the next geometry's start with --guess-from-previous). The SCF starts from dm0 when given and falls back to the second-order solver
    when DIIS stalls (scf_converge.py); raises SCFNotConverged (a RuntimeError) when that fails too."""
    from pyscf.hessian import rks as rks_hess
    rad, ang = (int(x) for x in a.grid.split(","))
    sym = d["molecule"]["symbols"]
    geom = np.array(d["molecule"]["geometry"], float).reshape(-1, 3)
    mol = pyscf_mole(lib_log, atom=[(s, tuple(x)) for s, x in zip(sym, geom, strict=True)], unit="Bohr", basis=a.basis, symmetry=False)
    mf = rks_setup(mol, a.xc, a.grid, a.conv)
    t0 = time.time()
    mf, e = converged_scf(mf, 200, log=lambda m: print(m, flush=True), dm0=dm0)
    H = rks_hess.Hessian(mf).kernel()                      # (natm, natm, 3, 3) in E_h/bohr²
    n = mol.natm
    Hc = H.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
    rec = {"driver": "hessian", "model": {"method": f"pyscf {a.xc}", "basis": a.basis},
           "keywords": {"grid": [rad, ang], "conv_tol": a.conv, "scf_type": "exact integrals", "hessian": "analytic (pyscf.hessian.rks)"},
           "molecule": {"symbols": sym, "geometry": geom.reshape(-1).tolist()},
           "return_result": Hc.reshape(-1).tolist(), "properties": {"return_energy": float(e)},
           "provenance": {"creator": "pyscf", "routine": "pyscf_hessians_for_qff.py", "wall_s": round(time.time() - t0, 1)}}
    return rec, float(e), mf.make_rdm1()


def main() -> None:
    a = parse_args()
    from pyscf import lib
    lib.num_threads(a.threads)
    os.makedirs(a.out_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(a.cache_dir, "*.json")))
    max_first = a.max_first_seconds                            # the stop rule reads the first Hessian computed in this call only
    done, t_all, dm = 0, time.time(), None
    with open(os.path.join(a.out_dir, PYSCF_LOG_NAME), "a", encoding="utf-8") as lib_log:
        for f in files:
            d = displaced_geometry(f)
            if d is None:
                continue
            out = os.path.join(a.out_dir, os.path.basename(f))
            if os.path.exists(out):
                done += 1
                continue
            print(f"[{time.strftime('%H:%M:%S')}] start {done + 1}/{len(files)} {os.path.basename(f)}", flush=True)
            t0 = time.time()
            try:
                rec, e, dm_new = hessian_record(d, a, lib_log, dm if a.guess_from_previous else None)
            except RuntimeError as exc:
                raise SystemExit(f"{exc} at {f}") from exc
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(rec, fh)
            dm = dm_new
            done += 1
            print(f"[{time.strftime('%H:%M:%S')}] {done}/{len(files)} {os.path.basename(f)} E = {e:.8f} in {time.time()-t0:.0f} s", flush=True)
            if max_first is not None and time.time() - t0 > max_first:
                raise SystemExit(f"STOP: the first Hessian took {time.time() - t0:.0f} s > {max_first:.0f} s — re-price before the rest")
            max_first = None
    print(f"done: {done} Hessians in {(time.time()-t_all)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
