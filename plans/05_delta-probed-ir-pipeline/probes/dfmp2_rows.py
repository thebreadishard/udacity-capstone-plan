"""Steps 1 and 2 of GoalGathering/notes/PreRegistration_2026-10-19_DFMP2_Composite_Step.md — runs in WSL with psi4 (1.10.2, env vpt2).

  rows   the MP2 Hessian rows of a molecule's symmetry-unique displacements by central differences of psi4's analytic DF-MP2 gradient, at the
         geometry, step, basis, frozen-core count and spherical/Cartesian choice stored in an existing conventional row file (--like), in the
         same file format (cc_composite_full_check.assemble reads it unchanged). Resumable: the file is rewritten after every row, and rows
         already in it are skipped.
             python probes/dfmp2_rows.py rows --like <conventional.npz> --symbols-from <corpus geometry.json> --out <df.npz>
         with --other-basis <basis>, the same plan at another basis (TASKS 184 (b): the QZ rows on a TZ file's plan).
         with --df-basis-scf / --df-basis-mp2, these fitting sets instead of <basis>-jkfit / <basis>-ri: an ANO basis has neither
         set of its own name; cc-pwCVTZ has its own -ri set, which is the one for correlating the core, and lacks only -jkfit.
         with --frozen-core <n>, that many frozen orbitals instead of the plan's (0: all electrons, for a core-valence term).
         with --only-row <k> (repeatable), those of the plan's rows only; the end line is then '=== DF ROWS PARTIAL' unless the
         file is complete, and the exit code is 0 either way — a caller reads the end line.
         with --theory scf, the DF-SCF gradient's rows instead (a basis-set-limit recipe extrapolates the correlation part alone);
         such a file keeps the plan's frozen count as every row file does, though SCF has no use for it.
         A basis psi4 does not ship is a file in a folder named in the environment's PSIPATH, called as psi4 looks for it: the
         name in lower case with + as p and * as s, then .gbs; its fitting sets must then always be named.
         A file that holds rows of another level, plan, state, step or geometry than the call's is refused, and so is an
         unfinished file made with another psi4 version.
         or, for a molecule without a conventional file, planned from the geometry itself as cc_composite_full_check.compute plans it
         (its symmetry-unique displacements, frozen core by the element rule, the anchors' step 0.005 bohr, spherical functions):
             python probes/dfmp2_rows.py rows --geometry <corpus geometry.json> --basis cc-pvtz --out <df.npz>
  water  check W: the analytic DF-MP2 gradient (frozen 1s) against 5-point finite differences of the DF-MP2 energy, cc-pVDZ and cc-pVTZ, at
         a stretched water; line max |Δg| ≤ 1e-6 Eh/bohr on both. Exit 1 when it fails. With --theory scf, the same for the DF-SCF
         gradient.
             python probes/dfmp2_rows.py water --out <result.json>

Both modes take --charge and --multiplicity (default 0 and 1). An open shell (multiplicity > 1) runs UHF DF-MP2 through psi4's DFOCC
module; a row file of an open shell also stores its charge and multiplicity (a closed-shell file keeps the keys it always had).

psi4's own output goes to <out>.psi4.log beside the result. Upstream tests making the same calls: psi4 tests/dfmp2-grad1 (gradient('mp2'),
scf_type df, mp2_type df), tests/dfmp2-grad5 (the analytic gradient against findif with 5 points), and for the open shell
tests/dfmp2-grad2 and dfmp2-grad4 (NO radical, reference uhf, qc_module occ, mp2_type df, the fitting set as df_basis_cc); for the SCF
gradient tests/cbs-xtpl-gradient (gradient('SCF/cc-pVDZ')). tests/psithon2 shows that PSIPATH is honoured for an orbital basis and a
fitting set, in an SCF energy. No upstream test makes a DF-MP2 gradient with a fitting set of another name than the orbital basis's: a
run that does so carries its own check (a row repeated with larger fitting sets).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e8_symmetry as SYM
from cc_composite_full_check import load_geometry
from dfmp2_swap_check import check_same_molecule
from qc_common import CORE_ORBITALS

WATER_LINE = 1e-6                     # Eh/bohr, check W
WATER_BASES = ("cc-pvdz", "cc-pvtz")
WATER = (("O", (0.0, 0.0, -0.13)), ("H", (0.0, 1.52, 1.07)), ("H", (0.0, -1.43, 0.98)))   # bohr; stretched and asymmetric on purpose
CONVERGENCE = 1e-10
ANCHOR_STEP = 0.005                   # bohr: the composite rows' step since 7 Oct (probes/results_m1/composite_rows_2026-10-07)
THEORIES = ("mp2", "scf")


@dataclass(frozen=True)
class Fitting:
    """The auxiliary basis sets of the density fitting, for the SCF and for MP2."""
    scf: str
    mp2: str

    @classmethod
    def named_after(cls, basis: str, scf: str | None = None, mp2: str | None = None) -> Fitting:
        """Return the sets named after the orbital basis, each replaced by the one given."""
        return cls(f"{basis}-jkfit" if scf is None else scf, f"{basis}-ri" if mp2 is None else mp2)

    def __post_init__(self) -> None:
        if not self.scf or not self.mp2:
            raise ValueError(f"a fitting set without a name: {self}")


@dataclass(frozen=True)
class Level:
    """The DF-MP2 level of one row file: the conventional file's basis, frozen count and spherical/Cartesian choice; the machine's share;
    the electronic state; the fitting sets, named after the basis when none are given; the theory whose gradient is taken."""
    basis: str
    frozen: int
    cart: bool
    threads: int = 6
    memory_gb: float = 4.0
    charge: int = 0
    multiplicity: int = 1
    fitting: Fitting | None = None
    theory: str = "mp2"

    def __post_init__(self) -> None:
        if self.frozen < 0 or self.threads < 1 or self.memory_gb <= 0 or self.multiplicity < 1 or self.theory not in THEORIES:
            raise ValueError(f"level out of range: {self}")
        if self.theory == "scf" and self.multiplicity > 1:
            raise ValueError("the SCF rows are built for closed shells only")


def configure(psi4: Any, level: Level, log_path: Path) -> None:
    psi4.set_output_file(str(log_path), True)
    psi4.set_num_threads(level.threads)
    psi4.set_memory(f"{level.memory_gb} GB")
    fitting = level.fitting or Fitting.named_after(level.basis)
    psi4.set_options({"basis": level.basis, "df_basis_scf": fitting.scf, "df_basis_mp2": fitting.mp2, "scf_type": "df",
                      "mp2_type": "df", "num_frozen_docc": level.frozen, "puream": not level.cart, "guess": "sad",
                      "e_convergence": CONVERGENCE, "d_convergence": CONVERGENCE})
    if level.multiplicity > 1:
        # the default DFMP2 module has no UHF gradient; DFOCC takes its correlation fitting set from df_basis_cc, not df_basis_mp2
        psi4.set_options({"reference": "uhf", "qc_module": "occ", "df_basis_cc": fitting.mp2})


def molecule(psi4: Any, symbols: list[str], coords_bohr: np.ndarray, charge: int = 0, multiplicity: int = 1) -> Any:
    """The molecule at exactly these coordinates in this state: bohr, C1, no reorientation, no shift to the centre of mass."""
    atoms = [f"{s} {x:.12f} {y:.12f} {z:.12f}" for s, (x, y, z) in zip(symbols, np.asarray(coords_bohr).reshape(-1, 3), strict=True)]
    return psi4.geometry("\n".join([f"{charge} {multiplicity}", *atoms, "units bohr", "symmetry c1", "no_reorient", "no_com"]))


def gradient(psi4: Any, symbols: list[str], coords_bohr: np.ndarray, dertype: int | None = None, state: tuple[int, int] = (0, 1),
             theory: str = "mp2") -> np.ndarray:
    """Return the DF gradient of `theory` in the (charge, multiplicity) `state`; analytic, or by psi4's finite differences with dertype=0."""
    mol = molecule(psi4, symbols, coords_bohr, *state)
    g = psi4.gradient(theory, molecule=mol) if dertype is None else psi4.gradient(theory, molecule=mol, dertype=dertype)
    psi4.core.clean()
    return np.asarray(g).ravel()


def central_row(g_plus: np.ndarray, g_minus: np.ndarray, step: float) -> np.ndarray:
    return (np.asarray(g_plus) - np.asarray(g_minus)) / (2 * step)


@dataclass(frozen=True)
class RowsPlan:
    """What a row file holds besides its rows: where, which displacements, and at which level."""
    source: str
    symbols: tuple[str, ...]
    coords_bohr: np.ndarray
    ks: tuple[int, ...]
    reps: tuple[int, ...]
    step: float
    basis: str
    frozen: int
    cart: bool
    charge: int = 0
    multiplicity: int = 1


def plan_from_like(like_path: str, symbols_from: str, basis: str | None = None) -> RowsPlan:
    """Return the settings of an existing conventional row file, at `basis` when given; the corpus geometry gives the symbols and must be
    the same molecule."""
    like = np.load(like_path)
    x0 = np.asarray(like["coords_bohr"], float)
    geometry = json.loads(Path(symbols_from).read_text(encoding="utf-8"))
    check_same_molecule(x0, np.asarray(geometry["coords_bohr"], float))
    return RowsPlan(like_path, tuple(s.capitalize() for s in geometry["symbols"]), x0, tuple(int(k) for k in like["ks"]),
                    tuple(int(r) for r in like["reps"]), float(like["step"]), str(like["basis"]) if basis is None else basis,
                    int(like["frozen"]), bool(like["cart"]))


def plan_from_geometry(geometry_path: str, basis: str, step: float = ANCHOR_STEP) -> RowsPlan:
    """The rows cc_composite_full_check.compute would plan: the geometry's symmetry-unique displacements, frozen core by the element rule."""
    symbols, x0, _ = load_geometry(Path(geometry_path))
    ks, reps = SYM.unique_displacements(SYM.point_group_ops(symbols, x0), len(symbols))
    return RowsPlan(geometry_path, tuple(symbols), x0, tuple(int(k) for k in ks), tuple(int(r) for r in reps), step, basis,
                    sum(CORE_ORBITALS[s] for s in symbols), False)


def save_rows(out: Path, plan: RowsPlan, rows: dict[int, np.ndarray], method: str) -> None:
    """The conventional files' keys with this route's rows, through a temp file moved over the target."""
    tmp = out.with_name(out.name + ".tmp.npz")
    state = {} if (plan.charge, plan.multiplicity) == (0, 1) else {"charge": plan.charge, "multiplicity": plan.multiplicity}
    np.savez(tmp, ks=np.array(plan.ks), reps=np.array(plan.reps), step=plan.step, basis=plan.basis, frozen=plan.frozen, cart=plan.cart,
             coords_bohr=plan.coords_bohr, method=method, **state, **{f"row_{k:02d}": v for k, v in sorted(rows.items())})
    os.replace(tmp, out)


def method_text(version: str, plan: RowsPlan, fitting: Fitting, theory: str) -> str:
    """Return what made the rows, as the file keeps it: '<theory> psi4 <version> (<level>)'."""
    if theory == "scf":
        return f"DF-SCF psi4 {version} ({fitting.scf})"
    shell = "" if plan.multiplicity == 1 else f", UHF via DFOCC, charge {plan.charge}, multiplicity {plan.multiplicity}"
    return f"DF-MP2 psi4 {version} ({fitting.scf} / {fitting.mp2}, frozen {plan.frozen}{shell})"


def method_parts(method: str) -> tuple[str, str, str]:
    """Split a file's method text into theory, psi4 version and level."""
    theory, _, rest = method.partition(" psi4 ")
    version, _, level = rest.partition(" ")
    return theory, version, level


def stored_rows(out: Path, plan: RowsPlan, method: str) -> dict[int, np.ndarray]:
    """Return the rows already in `out`; a file of another level, plan, state, step or geometry than this call's is refused, and so
    is an unfinished file of another psi4 version (a finished one is left as it is: nothing is added to it)."""
    if not out.exists():
        return {}
    with np.load(out) as z:
        if "method" not in z.files:
            raise SystemExit(f"{out} is not a row file of this script (it names no method); give another --out")
        theory_was, version_was, level_was = method_parts(str(z["method"]))
        was = (theory_was, level_was, str(z["basis"]), int(z["frozen"]), float(z["step"]), bool(z["cart"]),
               tuple(int(k) for k in z["ks"]), tuple(int(r) for r in z["reps"]),
               int(z["charge"]) if "charge" in z.files else 0, int(z["multiplicity"]) if "multiplicity" in z.files else 1)
        same_place = z["coords_bohr"].shape == plan.coords_bohr.shape and np.array_equal(z["coords_bohr"], plan.coords_bohr)
        rows = {int(k[4:]): z[k] for k in z.files if k.startswith("row_")}
    theory_now, version_now, level_now = method_parts(method)
    now = (theory_now, level_now, plan.basis, plan.frozen, plan.step, plan.cart, plan.ks, plan.reps, plan.charge, plan.multiplicity)
    if was != now or not same_place:
        where = "" if same_place else ", at another geometry"
        raise SystemExit(f"{out} holds rows of {was}{where}; this call is {now}. Give another --out, or the options the file was made with.")
    if version_was != version_now and set(plan.ks) - set(rows):
        raise SystemExit(f"{out} is unfinished and was made with psi4 {version_was}; this is psi4 {version_now}. Finish it with that "
                         "version, or give another --out.")
    return rows


def rows_to_run(ks: tuple[int, ...], only: list[int] | None) -> tuple[int, ...]:
    """Return the plan's displacements, or those of them named by --only-row; one the plan does not have is refused."""
    if not only:
        return ks
    unknown = sorted(set(only) - set(ks))
    if unknown:
        raise SystemExit(f"--only-row {unknown}: not among the plan's displacements {list(ks)}")
    return tuple(k for k in ks if k in only)


def run_rows(a: argparse.Namespace) -> int:
    import psi4
    plan = plan_from_like(a.like, a.symbols_from, a.other_basis) if a.like else plan_from_geometry(a.geometry, a.basis)
    plan = replace(plan, charge=a.charge, multiplicity=a.multiplicity, frozen=plan.frozen if a.frozen_core is None else a.frozen_core)
    todo = rows_to_run(plan.ks, a.only_row)
    fitting = Fitting.named_after(plan.basis, a.df_basis_scf, a.df_basis_mp2)
    method = method_text(psi4.__version__, plan, fitting, a.theory)
    out = Path(a.out)
    rows = stored_rows(out, plan, method)
    level = Level(plan.basis, plan.frozen, plan.cart, a.threads, a.memory_gb, plan.charge, plan.multiplicity, fitting, a.theory)
    configure(psi4, level, out.with_suffix(".psi4.log"))
    print(f"[{time.strftime('%H:%M:%S')}] {len(todo)} rows of {plan.source} at {plan.basis}, {len(rows)} already done", flush=True)
    for k in todo:
        if k in rows:
            continue
        t0 = time.time()
        g = []
        for sign in (+1, -1):
            x = plan.coords_bohr.ravel().copy()
            x[k] += sign * plan.step
            g.append(gradient(psi4, list(plan.symbols), x, state=(plan.charge, plan.multiplicity), theory=a.theory))
        rows[k] = central_row(g[0], g[1], plan.step)
        save_rows(out, plan, rows, method)
        print(f"[{time.strftime('%H:%M:%S')}] df-{a.theory} {plan.basis} k={k}: H_kk {rows[k][k]:+.6f} ({time.time() - t0:.0f} s)", flush=True)
    if set(plan.ks) - set(rows):
        print(f"=== DF ROWS PARTIAL {out} ({len(rows)} of {len(plan.ks)} rows; --only-row)", flush=True)
    else:
        print(f"=== DF ROWS DONE {out} ({len(rows)} rows)", flush=True)
    return 0


def run_water(a: argparse.Namespace) -> int:
    import psi4
    out = Path(a.out)
    symbols = [s for s, _ in WATER]
    x = np.array([c for _, c in WATER], float)
    res = {}
    for basis in WATER_BASES:
        configure(psi4, Level(basis, 1, False, a.threads, a.memory_gb, a.charge, a.multiplicity, theory=a.theory), out.with_suffix(".psi4.log"))
        analytic = gradient(psi4, symbols, x, state=(a.charge, a.multiplicity), theory=a.theory)
        psi4.set_options({"points": 5})
        findif = gradient(psi4, symbols, x, dertype=0, state=(a.charge, a.multiplicity), theory=a.theory)
        res[basis] = {"max_abs_diff": float(np.abs(analytic - findif).max()), "analytic": analytic.tolist(), "findif": findif.tolist()}
        print(f"[{time.strftime('%H:%M:%S')}] water {a.theory} {basis}: max |analytic - findif| {res[basis]['max_abs_diff']:.2e} Eh/bohr", flush=True)
    passed = all(v["max_abs_diff"] <= WATER_LINE for v in res.values())
    out.write_text(json.dumps({"line": WATER_LINE, "passed": passed, "psi4": psi4.__version__, "theory": a.theory, "charge": a.charge,
                               "multiplicity": a.multiplicity,
                               "bases": res}, indent=1), encoding="utf-8")
    print(f"=== WATER CHECK {'PASS' if passed else 'FAIL'} (line {WATER_LINE:g} Eh/bohr)", flush=True)
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    rows = sub.add_parser("rows")
    source = rows.add_mutually_exclusive_group(required=True)
    source.add_argument("--like", help="a conventional row file whose settings are copied (needs --symbols-from)")
    source.add_argument("--geometry", help="a corpus geometry.json whose own symmetry plans the rows (needs --basis)")
    rows.add_argument("--symbols-from")
    rows.add_argument("--basis")
    rows.add_argument("--other-basis", help="with --like: the file's plan at this basis instead of its own")
    rows.add_argument("--out", required=True)
    rows.add_argument("--df-basis-scf", help="the SCF fitting set instead of <basis>-jkfit")
    rows.add_argument("--df-basis-mp2", help="the MP2 fitting set instead of <basis>-ri")
    rows.add_argument("--frozen-core", type=int, help="frozen orbitals instead of the plan's count; 0 correlates all electrons")
    rows.add_argument("--only-row", type=int, action="append", help="compute this displacement of the plan only; repeatable")
    water = sub.add_parser("water")
    water.add_argument("--out", required=True)
    for p in (rows, water):
        p.add_argument("--threads", type=int, default=6)
        p.add_argument("--memory-gb", type=float, default=4.0)
        p.add_argument("--charge", type=int, default=0)
        p.add_argument("--multiplicity", type=int, default=1, help="2S+1; above 1 runs UHF DF-MP2 through psi4's DFOCC")
        p.add_argument("--theory", choices=THEORIES, default="mp2", help="whose DF gradient: mp2, or scf (closed shells)")
    a = ap.parse_args(argv)
    if a.mode == "rows" and a.like and (a.basis or not a.symbols_from):
        ap.error("--like takes its basis from the file and needs --symbols-from")
    if a.mode == "rows" and a.other_basis and not a.like:
        ap.error("--other-basis changes the basis of a --like plan; --geometry takes --basis")
    if a.mode == "rows" and a.geometry and (a.symbols_from or not a.basis):
        ap.error("--geometry needs --basis and takes its symbols from the geometry")
    if a.mode == "rows" and a.frozen_core is not None and a.frozen_core < 0:
        ap.error("--frozen-core is a number of orbitals, at least 0")
    if a.mode == "rows" and "" in (a.df_basis_scf, a.df_basis_mp2):
        ap.error("a fitting set needs a name; leave the option out for the set named after the basis")
    if a.mode == "rows" and a.theory == "scf" and (a.frozen_core is not None or a.df_basis_mp2 is not None):
        ap.error("--theory scf has no correlation part: --frozen-core and --df-basis-mp2 do not apply")
    if a.theory == "scf" and a.multiplicity > 1:
        ap.error("--theory scf is built for closed shells only")
    if a.multiplicity < 1:
        ap.error("--multiplicity is 2S+1, at least 1")
    return run_rows(a) if a.mode == "rows" else run_water(a)


if __name__ == "__main__":
    sys.exit(main())
