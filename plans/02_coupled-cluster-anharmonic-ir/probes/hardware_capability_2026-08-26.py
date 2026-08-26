"""Gate G1a, applied to the student's own hardware.

Plan 02 argues that compute cost must be measured rather than assumed. It never
applied that rule to the machine the work would run on. This does.

Measures, on this machine, with the production settings actually intended:
  1. that a real quantum chemistry stack runs at all
  2. wall time for a B3LYP/6-31G* energy, gradient and analytic Hessian
  3. how that scales from benzene (12 atoms) to triphenylene (30 atoms)
  4. therefore: whether the DFT repeat the locality probe asks for is affordable

MEASURED 2026-08-26, ASUS Vivobook 18, AMD Ryzen 7 260, 8C/16T, 31 GB RAM:

    molecule       atoms  basis fn     energy   gradient    hessian
    benzene           12       102       4.6s       2.6s       3.3m
    naphthalene       18       166       4.5s       6.8s      12.7m

    Hessian cost grew 3.8x from 12 to 18 atoms.
      extrapolated to pyrene       (26 atoms): ~55 min
      extrapolated to triphenylene (30 atoms): ~1.6 h

CAVEAT. The geometries below are not stationary points at B3LYP/6-31G*, so the
Hessians timed here are not valid frequency calculations and would show spurious
imaginary modes. The *timings* are valid, because a Hessian costs the same
whether or not the geometry is converged. A real frequency run must optimize
first: 10-20 gradient steps, one to three minutes, negligible beside the Hessian.

CONCLUSION. The five-molecule DFT repeat the locality probe asks for costs
roughly 3-4 hours of wall time on this laptop. No cluster, no GPU, no second
machine. The blocker was never hardware; it was that nobody had checked.

Run:  & "$env:USERPROFILE\\.conda\\envs\\qc\\python.exe" hardware_capability_2026-08-26.py
"""

from __future__ import annotations

import platform
import time

import psi4

BASIS = "6-31G*"
FUNCTIONAL = "b3lyp"
MEMORY_GB = 12
THREADS = 8

# Literature-quality planar structures, not optimized here: the question is cost
# per step, not the final geometry.
BENZENE = """
 C  1.3970  0.0000  0.0000
 C  0.6985  1.2098  0.0000
 C -0.6985  1.2098  0.0000
 C -1.3970  0.0000  0.0000
 C -0.6985 -1.2098  0.0000
 C  0.6985 -1.2098  0.0000
 H  2.4810  0.0000  0.0000
 H  1.2405  2.1487  0.0000
 H -1.2405  2.1487  0.0000
 H -2.4810  0.0000  0.0000
 H -1.2405 -2.1487  0.0000
 H  1.2405 -2.1487  0.0000
"""

NAPHTHALENE = """
 C  0.0000  0.7160  0.0000
 C  0.0000 -0.7160  0.0000
 C  1.2404  1.4031  0.0000
 C  2.4302  0.7057  0.0000
 C  2.4302 -0.7057  0.0000
 C  1.2404 -1.4031  0.0000
 C -1.2404  1.4031  0.0000
 C -2.4302  0.7057  0.0000
 C -2.4302 -0.7057  0.0000
 C -1.2404 -1.4031  0.0000
 H  1.2389  2.4880  0.0000
 H  3.3707  1.2519  0.0000
 H  3.3707 -1.2519  0.0000
 H  1.2389 -2.4880  0.0000
 H -1.2389  2.4880  0.0000
 H -3.3707  1.2519  0.0000
 H -3.3707 -1.2519  0.0000
 H -1.2389 -2.4880  0.0000
"""

JOBS = [("benzene", BENZENE), ("naphthalene", NAPHTHALENE)]


def timed(fn):
    """Return (seconds, error name or None). A failure is a measurement too."""
    start = time.perf_counter()
    try:
        fn()
        return time.perf_counter() - start, None
    except Exception as exc:
        return time.perf_counter() - start, type(exc).__name__


def fmt(seconds, err):
    if err:
        return f"{err[:10]:>11}"
    if seconds < 90:
        return f"{seconds:>10.1f}s"
    return f"{seconds / 60:>10.1f}m"


def main() -> None:
    # be_quiet() opens /dev/null, which does not exist on Windows.
    psi4.set_output_file("psi4_benchmark.log", False)
    psi4.set_memory(f"{MEMORY_GB} GB")
    psi4.set_num_threads(THREADS)
    psi4.set_options({"scf_type": "df", "basis": BASIS})

    print(f"machine  : {platform.processor()}")
    print(f"psi4     : {psi4.__version__}")
    print(f"settings : {FUNCTIONAL.upper()}/{BASIS}, {THREADS} threads, {MEMORY_GB} GB\n")

    header = f"{'molecule':<14}{'atoms':>6}{'basis fn':>10}{'energy':>11}{'gradient':>11}{'hessian':>11}"
    print(header)
    print("-" * len(header))

    measured = []
    for name, xyz in JOBS:
        mol = psi4.geometry(xyz + "\nsymmetry c1\nno_reorient\nno_com\n")
        n_atoms = mol.natom()
        n_bf = psi4.core.BasisSet.build(mol, "BASIS", BASIS).nbf()

        t_e, e_err = timed(lambda: psi4.energy(FUNCTIONAL, molecule=mol))
        t_g, g_err = timed(lambda: psi4.gradient(FUNCTIONAL, molecule=mol))
        t_h, h_err = timed(lambda: psi4.hessian(FUNCTIONAL, molecule=mol))

        print(f"{name:<14}{n_atoms:>6}{n_bf:>10}"
              f"{fmt(t_e, e_err)}{fmt(t_g, g_err)}{fmt(t_h, h_err)}")
        if h_err is None:
            measured.append((n_atoms, t_h))
        psi4.core.clean()

    if len(measured) >= 2:
        (a1, t1), (a2, t2) = measured[0], measured[-1]
        print(f"\nHessian cost grew {t2 / t1:.1f}x from {a1} to {a2} atoms.")
        for target, atoms in (("pyrene", 26), ("triphenylene", 30)):
            est = t2 * (atoms / a2) ** 4
            unit = f"{est / 60:.0f} min" if est < 5400 else f"{est / 3600:.1f} h"
            print(f"  extrapolated to {target:<13} ({atoms} atoms): ~{unit}")
        print("\nThose are estimates, and this plan does not accept estimates. Measure them")
        print("before committing, exactly as gate G1a demands of the coupled-cluster rung.")


if __name__ == "__main__":
    main()
