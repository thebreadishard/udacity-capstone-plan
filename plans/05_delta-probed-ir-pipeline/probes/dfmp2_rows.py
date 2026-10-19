"""Steps 1 and 2 of GoalGathering/notes/PreRegistration_2026-10-19_DFMP2_Composite_Step.md — runs in WSL with psi4 (1.10.2, env vpt2).

  rows   the MP2 Hessian rows of a molecule's symmetry-unique displacements by central differences of psi4's analytic DF-MP2 gradient, at the
         geometry, step, basis, frozen-core count and spherical/Cartesian choice stored in an existing conventional row file (--like), in the
         same file format (cc_composite_full_check.assemble reads it unchanged). Resumable: the file is rewritten after every row, and rows
         already in it are skipped.
             python probes/dfmp2_rows.py rows --like <conventional.npz> --symbols-from <corpus geometry.json> --out <df.npz>
  water  check W: the analytic DF-MP2 gradient (frozen 1s) against 5-point finite differences of the DF-MP2 energy, cc-pVDZ and cc-pVTZ, at
         a stretched water; line max |Δg| ≤ 1e-6 Eh/bohr on both. Exit 1 when it fails.
             python probes/dfmp2_rows.py water --out <result.json>

psi4's own output goes to <out>.psi4.log beside the result. Upstream tests making the same calls: psi4 tests/dfmp2-grad1 (gradient('mp2'),
scf_type df, mp2_type df) and tests/dfmp2-grad5 (the analytic gradient against findif with 5 points).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dfmp2_swap_check import check_same_molecule

WATER_LINE = 1e-6                     # Eh/bohr, check W
WATER_BASES = ("cc-pvdz", "cc-pvtz")
WATER = (("O", (0.0, 0.0, -0.13)), ("H", (0.0, 1.52, 1.07)), ("H", (0.0, -1.43, 0.98)))   # bohr; stretched and asymmetric on purpose
CONVERGENCE = 1e-10


@dataclass(frozen=True)
class Level:
    """The DF-MP2 level of one row file: the conventional file's basis, frozen count and spherical/Cartesian choice; the machine's share."""
    basis: str
    frozen: int
    cart: bool
    threads: int = 6
    memory_gb: float = 4.0

    def __post_init__(self) -> None:
        if self.frozen < 0 or self.threads < 1 or self.memory_gb <= 0:
            raise ValueError(f"level out of range: {self}")


def configure(psi4: Any, level: Level, log_path: Path) -> None:
    psi4.set_output_file(str(log_path), True)
    psi4.set_num_threads(level.threads)
    psi4.set_memory(f"{level.memory_gb} GB")
    psi4.set_options({"basis": level.basis, "df_basis_scf": f"{level.basis}-jkfit", "df_basis_mp2": f"{level.basis}-ri", "scf_type": "df",
                      "mp2_type": "df", "num_frozen_docc": level.frozen, "puream": not level.cart, "guess": "sad",
                      "e_convergence": CONVERGENCE, "d_convergence": CONVERGENCE})


def molecule(psi4: Any, symbols: list[str], coords_bohr: np.ndarray) -> Any:
    """A neutral singlet at exactly these coordinates: bohr, C1, no reorientation, no shift to the centre of mass."""
    atoms = [f"{s} {x:.12f} {y:.12f} {z:.12f}" for s, (x, y, z) in zip(symbols, np.asarray(coords_bohr).reshape(-1, 3), strict=True)]
    return psi4.geometry("\n".join(["0 1", *atoms, "units bohr", "symmetry c1", "no_reorient", "no_com"]))


def gradient(psi4: Any, symbols: list[str], coords_bohr: np.ndarray, dertype: int | None = None) -> np.ndarray:
    mol = molecule(psi4, symbols, coords_bohr)
    g = psi4.gradient("mp2", molecule=mol) if dertype is None else psi4.gradient("mp2", molecule=mol, dertype=dertype)
    psi4.core.clean()
    return np.asarray(g).ravel()


def central_row(g_plus: np.ndarray, g_minus: np.ndarray, step: float) -> np.ndarray:
    return (np.asarray(g_plus) - np.asarray(g_minus)) / (2 * step)


def like_settings(like: dict[str, np.ndarray]) -> tuple[list[int], np.ndarray, float, str, int, bool]:
    return ([int(k) for k in like["ks"]], np.asarray(like["coords_bohr"], float), float(like["step"]), str(like["basis"]), int(like["frozen"]),
            bool(like["cart"]))


def save_rows(out: Path, like: dict[str, np.ndarray], rows: dict[int, np.ndarray], method: str) -> None:
    """The conventional file's keys with this route's rows, through a temp file moved over the target."""
    tmp = out.with_name(out.name + ".tmp.npz")
    np.savez(tmp, ks=like["ks"], reps=like["reps"], step=like["step"], basis=like["basis"], frozen=like["frozen"], cart=like["cart"],
             coords_bohr=like["coords_bohr"], method=method, **{f"row_{k:02d}": v for k, v in sorted(rows.items())})
    os.replace(tmp, out)


def run_rows(a: argparse.Namespace) -> int:
    import psi4
    like = dict(np.load(a.like))
    ks, x0, step, basis, frozen, cart = like_settings(like)
    geometry = json.loads(Path(a.symbols_from).read_text(encoding="utf-8"))
    check_same_molecule(x0, np.asarray(geometry["coords_bohr"], float))
    symbols = [s.capitalize() for s in geometry["symbols"]]
    out = Path(a.out)
    rows = {int(k[4:]): v for k, v in np.load(out).items() if k.startswith("row_")} if out.exists() else {}
    configure(psi4, Level(basis, frozen, cart, a.threads, a.memory_gb), out.with_suffix(".psi4.log"))
    method = f"DF-MP2 psi4 {psi4.__version__} ({basis}-jkfit / {basis}-ri, frozen {frozen})"
    print(f"[{time.strftime('%H:%M:%S')}] {len(ks)} rows of {a.like} at {basis}, {len(rows)} already done", flush=True)
    for k in ks:
        if k in rows:
            continue
        t0 = time.time()
        g = []
        for sign in (+1, -1):
            x = x0.ravel().copy()
            x[k] += sign * step
            g.append(gradient(psi4, symbols, x))
        rows[k] = central_row(g[0], g[1], step)
        save_rows(out, like, rows, method)
        print(f"[{time.strftime('%H:%M:%S')}] df-mp2 {basis} k={k}: H_kk {rows[k][k]:+.6f} ({time.time() - t0:.0f} s)", flush=True)
    print(f"=== DF ROWS DONE {out} ({len(rows)} rows)", flush=True)
    return 0


def run_water(a: argparse.Namespace) -> int:
    import psi4
    out = Path(a.out)
    symbols = [s for s, _ in WATER]
    x = np.array([c for _, c in WATER], float)
    res = {}
    for basis in WATER_BASES:
        configure(psi4, Level(basis, 1, False, a.threads, a.memory_gb), out.with_suffix(".psi4.log"))
        analytic = gradient(psi4, symbols, x)
        psi4.set_options({"points": 5})
        findif = gradient(psi4, symbols, x, dertype=0)
        res[basis] = {"max_abs_diff": float(np.abs(analytic - findif).max()), "analytic": analytic.tolist(), "findif": findif.tolist()}
        print(f"[{time.strftime('%H:%M:%S')}] water {basis}: max |analytic - findif| {res[basis]['max_abs_diff']:.2e} Eh/bohr", flush=True)
    passed = all(v["max_abs_diff"] <= WATER_LINE for v in res.values())
    out.write_text(json.dumps({"line": WATER_LINE, "passed": passed, "psi4": psi4.__version__, "bases": res}, indent=1), encoding="utf-8")
    print(f"=== WATER CHECK {'PASS' if passed else 'FAIL'} (line {WATER_LINE:g} Eh/bohr)", flush=True)
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    rows = sub.add_parser("rows")
    rows.add_argument("--like", required=True)
    rows.add_argument("--symbols-from", required=True)
    rows.add_argument("--out", required=True)
    water = sub.add_parser("water")
    water.add_argument("--out", required=True)
    for p in (rows, water):
        p.add_argument("--threads", type=int, default=6)
        p.add_argument("--memory-gb", type=float, default=4.0)
    a = ap.parse_args(argv)
    return run_rows(a) if a.mode == "rows" else run_water(a)


if __name__ == "__main__":
    sys.exit(main())
