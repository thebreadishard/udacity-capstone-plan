"""The relaxed methyl torsion scan of 4-methylimidazole for TASKS 177
(`GoalGathering/notes/PreRegistration_2026-11-04_Methyl_Rotor_Variational.md`, part A; the user, 4 Nov 2026: 'Ja, doe optie 4 met optie 2
ernaast').

Point k sets the dihedral H6–C0–C1–C2 to τ₀ + 10° k and optimises everything else (geomeTRIC through pyscf, `$set dihedral 7 1 2 3 <τ>`;
upstream: geomeTRIC `tests/test_prepare.py` for the constraint syntax, pyscf `geomopt/geometric_solver.py` `optimize(..., constraints=)`),
from the reference with its top turned rigidly by 10° k. The energy at the optimised geometry is then taken with the Hessian runs' RKS. A
point whose dihedral moved more than 0.05° stops the run. One json per point; a point already written is skipped.

    python probes/methyl_torsion_scan.py <out_dir> --lane 0 --lanes 4 [--threads 3] [--smoke]
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
from methyl_rotor_grid import METHYL_C, RING_C, RING_NEXT, TOP, energy_function, reference, tau_of, turn_top, write_json

STEP_DEG = 10.0
N_POINTS = 13            # k = 0 … 12: 0–120°, k = 12 the periodicity check
DIHEDRAL_TOL_DEG = 0.05
CONVERGENCE = "GAU_TIGHT"  # geomeTRIC's set: gradient rms 1e-5 Eh/bohr, so the energy error is far below the 0.5 cm⁻¹ check


def constrained_minimum(symbols: list[str], x: np.ndarray, target_deg: float, threads: int, work: Path, lib_log) -> np.ndarray:
    """The geometry (bohr) that minimises the energy with the torsion held at target_deg."""
    from library_log import pyscf_mole
    from methyl_rotor_grid import BASIS, CONV, GRID, XC
    from pyscf import lib
    from pyscf.geomopt.geometric_solver import optimize
    from pyscf_hessians_for_qff import rks_setup
    lib.num_threads(threads)
    con = work / "constraints.txt"
    i, j, k, m = (TOP[0] + 1, METHYL_C + 1, RING_C + 1, RING_NEXT + 1)
    con.write_text(f"$set\ndihedral {i} {j} {k} {m} {target_deg:.6f}\n$end\n", encoding="utf-8")
    mol = pyscf_mole(lib_log, atom=[(s, tuple(r)) for s, r in zip(symbols, x, strict=True)], unit="Bohr", basis=BASIS, symmetry=False)
    mol_eq = optimize(rks_setup(mol, XC, GRID, CONV), constraints=str(con), maxsteps=200, convergence_set=CONVERGENCE)
    return np.asarray(mol_eq.atom_coords(unit="Bohr"))


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Command line; --smoke is points 0 and 6 only."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_dir")
    ap.add_argument("--lane", type=int, default=0)
    ap.add_argument("--lanes", type=int, default=1)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(argv)
    if not 0 <= a.lane < a.lanes:
        raise SystemExit(f"--lane {a.lane} outside 0..{a.lanes - 1}")
    return a


def main(argv: list[str] | None = None) -> int:
    """This lane's scan points."""
    from library_log import PYSCF_LOG_NAME
    a = parse_args(argv)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ref = reference()
    x0 = ref.geom.reshape(-1, 3)
    tau0 = tau_of(x0)
    ks = [0, 6] if a.smoke else list(range(N_POINTS))
    mine = [k for k in ks if k % a.lanes == a.lane]
    with open(out / f"scan_lane{a.lane:02d}_{PYSCF_LOG_NAME}", "a", encoding="utf-8") as lib_log:
        energy = energy_function(lib_log, a.threads)
        for k in mine:
            rec_path = out / f"scan_k{k:02d}.json"
            if rec_path.exists():
                continue
            t0 = time.time()
            target = (tau0 + STEP_DEG * k + 180.0) % 360.0 - 180.0
            work = out / f"work_k{k:02d}"
            work.mkdir(exist_ok=True)
            x = constrained_minimum(ref.symbols, turn_top(x0, STEP_DEG * k), target, a.threads, work, lib_log)
            got = (tau_of(x) - target + 180.0) % 360.0 - 180.0
            if abs(got) > DIHEDRAL_TOL_DEG:
                raise SystemExit(f"k {k}: the torsion moved {got:+.3f}° from its set value {target:.3f}°")
            e = energy(ref.symbols, x)
            write_json(rec_path, {"k": k, "tau0_deg": tau0, "target_deg": target, "achieved_deg": tau_of(x), "energy": e,
                                  "symbols": ref.symbols, "geometry_bohr": x.tolist(), "convergence": CONVERGENCE})
            print(f"[{time.strftime('%H:%M:%S')}] scan lane {a.lane} k {k} τ {target:.2f}° E = {e:.12f} ({time.time() - t0:.0f} s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
