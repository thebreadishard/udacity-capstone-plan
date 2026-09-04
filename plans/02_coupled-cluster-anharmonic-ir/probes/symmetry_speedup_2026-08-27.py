"""Measure what molecular symmetry is worth, because so far it has been worth nothing.

Every frequency job in this repository ran in C1. The geometry block written by
psi4_geometry() ended in "symmetry c1 / no_reorient / no_com" - three lines put there
so that Psi4's atom indices would keep matching RDKit's, which they do, at the price
of computing benzene as if it were a shapeless collection of twelve atoms.

The cause is not the keyword alone. MMFF coordinates are never exactly symmetric, so
even with the keyword removed Psi4's detector finds C1 for all eight molecules. What
recovers the symmetry is snapping the geometry onto its nearest point group first:

    auto-detect on the raw MMFF geometry : c1 for all eight
    after symmetrize(1e-2)               : d2h, d2h, d2h, c2v, c2v, c2h, d2h, d2h

Psi4 only supports abelian groups, so benzene's D6h is used as D2h and triphenylene's
D3h as C2v. That is still a factor of four to eight in group order over C1.

WHAT THIS SCRIPT MEASURES

  The same molecule, same functional, same basis, same convergence, computed twice:
  once as it has always been computed, once with symmetry. Two numbers come out.

    speed    - wall time of the Hessian, which is where the hours go
    identity - the frequency lists must agree. Symmetry is a bookkeeping device; if
               it changes an answer, something is wrong and the speed is worthless.

  The C1 side is not recomputed. It is read from the stored result of the original
  run, which is what the comparison is actually about.

Run:  python symmetry_speedup_2026-08-27.py [molecule]
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import psi4

HERE = Path(__file__).parent
STORED = HERE / "results_dft_locality"
AGREE_CM = 0.1          # two runs of the same physics may not differ by more than this


def probe_module():
    spec = importlib.util.spec_from_file_location(
        "dft", HERE / "dft_locality_2026-08-26.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "benzene"
    dft = probe_module()

    baseline_path = STORED / f"{name}.json"
    if not baseline_path.exists():
        raise SystemExit(f"no stored C1 run for {name}; nothing to compare against")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    entry = next(m for m in dft.MOLECULES if m[0] == name)

    psi4.set_output_file(str(HERE / f"symmetry_{name}.log"), False)
    psi4.set_memory(f"{dft.MEMORY_GB} GB")
    psi4.set_num_threads(dft.THREADS)
    psi4.set_options({"scf_type": "df", "basis": dft.BASIS,
                      "g_convergence": "gau", "geom_maxiter": 200})

    print(f"{name}: recomputing with symmetry, comparing against the stored C1 run\n")
    t0 = time.perf_counter()
    data, _ = dft.run_molecule(entry[0], entry[1], entry[2], entry[3], symmetry="auto")
    wall = time.perf_counter() - t0

    old_h = baseline["seconds_hessian"]
    new_h = data["seconds_hessian"]
    old_o = baseline["seconds_optimize"]
    new_o = data["seconds_optimize"]

    print(f"{'':<14}{'C1':>12}{'symmetry':>12}{'speedup':>10}")
    print("-" * 48)
    print(f"{'optimize':<14}{old_o:>11.1f}s{new_o:>11.1f}s{old_o/max(new_o,1e-9):>9.2f}x")
    print(f"{'hessian':<14}{old_h:>11.1f}s{new_h:>11.1f}s{old_h/max(new_h,1e-9):>9.2f}x")
    print(f"{'total':<14}{old_o+old_h:>11.1f}s{wall:>11.1f}s"
          f"{(old_o+old_h)/max(wall,1e-9):>9.2f}x")

    old_nu = np.array(baseline["frequencies_cm"])
    new_nu = np.array(data["frequencies_cm"])
    (HERE / f"symmetry_{name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\n{'':<14}modes {len(old_nu)} vs {len(new_nu)}")
    if len(old_nu) != len(new_nu):
        raise SystemExit("different number of modes - the runs are not comparable")

    old_s, new_s = np.sort(old_nu), np.sort(new_nu)
    delta = np.abs(new_s - old_s)
    print(f"{'':<14}largest frequency difference: {delta.max():.4f} cm^-1")
    print(f"\n{'mode':>6}{'C1':>12}{'symmetry':>12}{'diff':>10}")
    print("-" * 40)
    for i in np.argsort(delta)[::-1][:10]:
        print(f"{i:>6}{old_s[i]:>12.2f}{new_s[i]:>12.2f}{new_s[i]-old_s[i]:>+10.2f}")
    print(f"\n{'':<14}above 100 cm^-1 only: "
          f"{np.abs(new_s - old_s)[old_s > 100].max():.4f} cm^-1")
    for key in ("n_imaginary", "n_near_zero"):
        print(f"{'':<14}{key}: {baseline[key]} -> {data[key]}")

    print()
    if delta.max() <= AGREE_CM:
        print(f"IDENTICAL to {AGREE_CM} cm^-1. Symmetry is safe to switch on, and the")
        print("speedup above is free.")
    else:
        print(f"NOT identical: {delta.max():.3f} cm^-1 apart. Symmetry changed an answer")
        print("it cannot legitimately change. Do not switch it on; find out why first.")


if __name__ == "__main__":
    main()
