#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Naphthalene geometry at the dry run's level (B3LYP/6-31G*, psi4, same options as
dryrun_dft_delta_recovery.py stage A) — the input the naphthalene single-point timing needs (P13,
2026-09-10). Writes results_dryrun/naphthalene/geometry.json with the same two keys the timing
probe reads (symbols, coords_bohr) plus the level and the wall time. Not the naphthalene dry run
(no Hessians here); stage A of the dry run overwrites nothing and adds stageA.json later.

Runs on Windows in the conda environment `qc` (psi4 1.11):
  C:\\Users\\thebr\\.conda\\envs\\qc\\python.exe naphthalene_geometry.py [--threads 8]
"""
import argparse, json, os, time, platform
from datetime import datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_dryrun", "naphthalene")
BASIS = "6-31g*"
FUNCTIONAL = "b3lyp"

# Idealised D2h start (Å): two fused regular hexagons of side 1.40 Å sharing the C4a–C8a bond on x = 0,
# C–H 1.08 Å radial from each ring centre. psi4 optimises from here.
START = """0 1
C  0.0000  0.7000  0.0000
C  0.0000 -0.7000  0.0000
C  1.2124  1.4000  0.0000
C  1.2124 -1.4000  0.0000
C  2.4249  0.7000  0.0000
C  2.4249 -0.7000  0.0000
C -1.2124  1.4000  0.0000
C -1.2124 -1.4000  0.0000
C -2.4249  0.7000  0.0000
C -2.4249 -0.7000  0.0000
H  1.2124  2.4800  0.0000
H  1.2124 -2.4800  0.0000
H  3.3602  1.2400  0.0000
H  3.3602 -1.2400  0.0000
H -1.2124  2.4800  0.0000
H -1.2124 -2.4800  0.0000
H -3.3602  1.2400  0.0000
H -3.3602 -1.2400  0.0000
no_com
no_reorient
symmetry c1
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    import psi4
    psi4.core.set_output_file(os.path.join(OUT, "geometry_psi4.out"), False)
    psi4.set_memory("8 GB")
    psi4.set_num_threads(args.threads)
    psi4.set_options({"scf_type": "df", "d_convergence": 1e-8, "e_convergence": 1e-10,
                      "dft_spherical_points": 590, "dft_radial_points": 99})
    mol = psi4.geometry(START)
    t0 = time.time()
    e = psi4.optimize(f"{FUNCTIONAL}/{BASIS}", molecule=mol)
    t_opt = time.time() - t0
    symbols = [mol.symbol(i) for i in range(mol.natom())]
    coords = np.array([[mol.x(i), mol.y(i), mol.z(i)] for i in range(mol.natom())])  # bohr
    rec = {"molecule": "naphthalene", "symbols": symbols, "coords_bohr": coords.tolist(),
           "masses_amu": [float(mol.mass(i)) for i in range(mol.natom())], "natom": len(symbols),
           "level": f"{FUNCTIONAL}/{BASIS}", "e_opt_hartree": float(e), "optimize_s": t_opt,
           "psi4": psi4.__version__, "machine": platform.node(), "threads": args.threads,
           "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
    json.dump(rec, open(os.path.join(OUT, "geometry.json"), "w"), indent=1)
    # a few bond lengths as the sanity print (Å)
    B = 0.529177210903
    d = lambda i, j: float(np.linalg.norm(coords[i] - coords[j]) * B)  # noqa: E731
    print(f"naphthalene B3LYP/6-31G*: optimised in {t_opt:.0f} s; E = {e:.6f} E_h; "
          f"C4a-C8a {d(0,1):.4f} Å, C1-C2 {d(2,4):.4f} Å, C-H {d(2,10):.4f} Å; written {OUT}/geometry.json")


if __name__ == "__main__":
    main()
