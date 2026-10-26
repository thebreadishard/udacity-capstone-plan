"""TASKS 133: E8's reference CCSD(T) gradient (probes/e8_cc_hessian_fd.py, its arguments passed unchanged, --only-reference) with the
relative residual of every CPHF solve recorded. pyscf 2.14.0's lib.krylov ignores lindep and its cphf.solve_nos1 does not pass one; master's
#3333 changed both, so the Z-vector of a CC gradient can stop early on the release. With --upstream-cphf <pyscf checkout> the CPHF solve is
that checkout's cphf.solve with its lib.krylov (both loaded from their files, in place only during the solve), everything else — pyscf,
the C kernels, BLAS and OpenMP — unchanged: the run isolates #3333. Writes krylov_residuals.json beside E8's reference.npz.

    python probes/krylov_cost_check.py [--upstream-cphf ~/pyscf-wt-base] <E8 arguments …> --only-reference
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import e8_cc_hessian_fd as E8
import numpy as np
import pyscf
from pyscf import lib
from pyscf.scf import cphf

Solve = Callable[..., tuple]


def relative_residual(fvind: Callable, mo_energy: np.ndarray, mo_occ: np.ndarray, h1: np.ndarray, mo1: np.ndarray) -> float:
    """|x + e_ai·fvind(x) − b| / |b| with b = −e_ai·h1: the equation solve_nos1 hands lib.krylov (no level shift), x its solution."""
    e_ai = 1 / (mo_energy[mo_occ == 0][:, None] - mo_energy[mo_occ > 0])
    x = mo1.reshape(-1, *e_ai.shape)
    b = -e_ai * h1.reshape(-1, *e_ai.shape)
    r = x + e_ai * np.asarray(fvind(x)).reshape(x.shape) - b
    return float(np.linalg.norm(r) / np.linalg.norm(b))


def recording(original: Solve, records: list[dict]) -> Solve:
    """cphf.solve that also appends {'residual': …} per call; a call with s1 or a level shift is recorded as not measured."""
    def solve(fvind, mo_energy, mo_occ, h1, s1=None, **kw):
        mo1, e1 = original(fvind, mo_energy, mo_occ, h1, s1, **kw)
        if s1 is not None or kw.get("level_shift", 0):
            records.append({"residual": None, "why": "s1 or a level shift: not solve_nos1's equation"})
        else:
            records.append({"residual": relative_residual(fvind, mo_energy, mo_occ, h1, mo1), "max_cycle": kw.get("max_cycle")})
        return mo1, e1
    return solve


def _module_from_file(name: str, path: Path) -> ModuleType:
    if not path.exists():
        raise SystemExit(f"{path} does not exist")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def upstream_solve(checkout: Path) -> tuple[Solve, ModuleType]:
    """The checkout's cphf.solve, run with the checkout's lib.krylov in place of the release's for the duration of each call."""
    helper = _module_from_file("upstream_linalg_helper", checkout / "pyscf" / "lib" / "linalg_helper.py")
    upstream = _module_from_file("upstream_cphf", checkout / "pyscf" / "scf" / "cphf.py")
    if upstream.lib is not lib:
        raise SystemExit("the checkout's cphf did not bind the running pyscf.lib: the krylov swap would not reach it")

    def solve(*args, **kw):
        released = lib.krylov
        lib.krylov = helper.krylov
        try:
            return upstream.solve(*args, **kw)
        finally:
            lib.krylov = released
    return solve, upstream


def passes_lindep(module: ModuleType) -> bool:
    return "lindep" in inspect.getsource(module.solve_nos1)


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--upstream-cphf", type=Path)
    own, args = ap.parse_known_args(argv)
    if "--only-reference" not in args:
        raise SystemExit("krylov_cost_check: pass --only-reference (TASKS 133 needs the reference gradient only)")
    out = Path(E8.build_parser().parse_args(args).out)
    if (out / "reference.npz").exists():
        raise SystemExit(f"{out / 'reference.npz'} exists: E8 would read it back and no CPHF solve would be recorded")
    solver, module = upstream_solve(own.upstream_cphf.expanduser()) if own.upstream_cphf else (cphf.solve, cphf)
    records: list[dict] = []
    released = cphf.solve
    cphf.solve = recording(solver, records)
    try:
        sys.argv = [E8.__file__, *args]
        E8.main()
    finally:
        cphf.solve = released
    if not records:
        raise SystemExit("krylov_cost_check: no CPHF solve was recorded — the gradient did not go through cphf.solve")
    E8.write_json(str(out / "krylov_residuals.json"), {
        "pyscf_version": pyscf.__version__, "pyscf_path": pyscf.__file__, "cphf": str(own.upstream_cphf or "released"),
        "solve_nos1_passes_lindep": passes_lindep(module), "solves": records})
    print(f"=== (KC) done: cphf {own.upstream_cphf or 'released'}, lindep {passes_lindep(module)}, residuals "
          f"{[r['residual'] for r in records]}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
