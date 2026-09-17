#!/usr/bin/env python3
"""Dipole derivatives for the shape test (17 September 2026, pre-registered in
GoalGathering/notes/Desk_2026-09-17_Tolerance_and_Label_Count.md, section 1).

The dry run stores Hessians, modes and Delta_2 but no dipole derivatives, so the couplings-vs-shape
test could so far be scored on positions only. This computes ONE Hessian with dipole derivatives at
the low level (B3LYP, the same basis as stage A) on the stage A geometry, and stores the dipole
gradient (3N x 3, E_h-independent units as psi4 gives them) beside the Hessian. Intensities with and
without the off-diagonal block of Delta_2 then follow from the rotated eigenvectors - the plan's own
recipe (reading copy S3.3: anharmonic intensities from the DFT dipole derivatives).

Windows conda env `qc` (psi4 1.11), like the dry run:
    python dipole_derivatives.py --molecule naphthalene --symmetrised --threads 8 --psi4-memory "3 GB"
    python dipole_derivatives.py --check           # water, seconds: confirms the psi4 variable exists
"""
import argparse
import json
import os
import time

import numpy as np
import dryrun_dft_delta_recovery as dr


def dipole_gradient(psi4, mol, functional):
    """Hessian plus dipole gradient at one geometry. psi4 sets CURRENT DIPOLE GRADIENT after an
    analytic Hessian; the (3N, 3) array is the derivative of the dipole with respect to Cartesian
    displacements (psi4's units: e * bohr / bohr = e, i.e. a.u.)."""
    H, wfn = psi4.hessian(f"{functional}/{dr.BASIS}", molecule=mol, return_wfn=True)
    if wfn.has_array_variable("CURRENT DIPOLE GRADIENT"):
        dg = np.asarray(wfn.array_variable("CURRENT DIPOLE GRADIENT"))
    else:
        dg = np.asarray(psi4.core.variable("CURRENT DIPOLE GRADIENT"))
    return np.asarray(H), dg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", default="naphthalene")
    ap.add_argument("--symmetrised", action="store_true")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--psi4-memory", default="3 GB", dest="psi4_memory")
    ap.add_argument("--check", action="store_true", help="water smoke test: does the dipole gradient come out?")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    if args.check:
        out = os.path.join(here, "results_dryrun", "_dipole_check")
        os.makedirs(out, exist_ok=True)
        psi4 = dr.psi4_setup(2, os.path.join(out, "psi4.out"), "1 GB")
        mol = psi4.geometry("0 1\nO 0 0 0.1173\nH 0 0.7572 -0.4692\nH 0 -0.7572 -0.4692\nsymmetry c1\nno_reorient\nno_com")
        t0 = time.time()
        H, dg = dipole_gradient(psi4, mol, dr.FUNCTIONALS["low"])
        print("water: Hessian %s, dipole gradient %s, %.1f s" % (H.shape, dg.shape, time.time() - t0))
        print("dipole gradient (first rows):", np.round(dg[:3], 4).tolist())
        return
    out = os.path.join(here, "results_dryrun", args.molecule + ("_sym" if args.symmetrised else ""))
    a = json.load(open(os.path.join(out, "stageA.json")))
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    psi4 = dr.psi4_setup(args.threads, os.path.join(out, "psi4_dipole.out"), args.psi4_memory)
    mol = dr.make_molecule(psi4, a["symbols"], z["coords"])
    t0 = time.time()
    H, dg = dipole_gradient(psi4, mol, dr.FUNCTIONALS["low"])
    el = time.time() - t0
    dev = float(np.max(np.abs(H - z["H_low"])))
    np.savez(os.path.join(out, "stageA_dipole.npz"), dipole_gradient=dg, H_low_recomputed=H,
             coords=z["coords"], functional=dr.FUNCTIONALS["low"], basis=dr.BASIS)
    dr.log("dipole derivatives: %s at %s/%s, %.0f s; Hessian reproduces stage A's H_low to %.2e E_h/bohr^2; "
           "dipole gradient %s saved to stageA_dipole.npz" % (args.molecule, dr.FUNCTIONALS["low"], dr.BASIS, el, dev, dg.shape))


if __name__ == "__main__":
    main()
