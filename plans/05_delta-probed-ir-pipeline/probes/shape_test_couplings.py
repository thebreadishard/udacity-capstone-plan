#!/usr/bin/env python3
"""The shape test: do the couplings change the convolved spectrum, or only the stick positions?
Pre-registered 17 September 2026 (GoalGathering/notes/Desk_2026-09-17_Tolerance_and_Label_Count.md, section 1).

Stage C's diagonal-only column is a statement about positions. Couplings also move INTENSITY: the
off-diagonal block of Delta_2 rotates the normal modes, and intensity follows the eigenvectors. The
deliverable in the goal sentence is spectral shape, so the question is scored on the convolved
spectrum, at the resolutions the ladder's references actually have.

Inputs (naphthalene_sym): stageA_hessians.npz (omega, L, Minv, D2_direct, H_low) and stageA_dipole.npz
(the low-level Cartesian dipole gradient, dipole_derivatives.py). No new energies.

Two spectra from the same DFT dipole derivatives:
  FULL      omega^2 + Delta^Q            (diagonal and couplings)
  DIAGONAL  omega^2 + diag(Delta^Q)      (what the diagonal-only route delivers)
each as sticks (positions from the eigenvalues, intensities from the rotated dipole derivatives), then
convolved with Gaussians of FWHM 1, 5 and 13 cm-1 - PAHdb-anharmonic's own 1 cm-1, and the 5-17 cm-1
of the free-electron-laser references that cover every molecule above naphthalene.

Pre-registered reading: if at 5 and 13 cm-1 the two convolved spectra differ by less than the
reference could distinguish (max |difference| below 5 % of the peak in every window), the diagonal-only
route is a licensed rung for the large molecules; if not, the couplings are needed for shape and the
tolerance note settles nothing about them.
"""
import argparse
import json
import os

import numpy as np

HARTREE_TO_CM = 219474.63
FWHMS = [1.0, 5.0, 13.0]
WINDOWS = {"3 um C-H stretch": (2950, 3150), "6-9 um": (1100, 1650), "11-14 um C-H oop": (700, 950)}


def sticks(omega, D_Q, dmu_dQ):
    """Positions (cm-1) and intensities (a.u., |dmu/dQ'|^2) of the corrected surface."""
    W2 = np.diag(omega ** 2) + D_Q
    lam, U = np.linalg.eigh(W2)
    nu = np.sqrt(np.abs(lam)) * HARTREE_TO_CM
    d = dmu_dQ @ U                      # (3, M): dipole derivatives along the rotated modes
    inten = np.sum(d ** 2, axis=0)
    return nu, inten


def convolve(nu, inten, grid, fwhm):
    s = fwhm / (2 * np.sqrt(2 * np.log(2)))
    return np.sum(inten[:, None] * np.exp(-0.5 * ((grid[None, :] - nu[:, None]) / s) ** 2), axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = args.dir or os.path.join(here, "results_dryrun", "naphthalene_sym")
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    dz = np.load(os.path.join(out, "stageA_dipole.npz"))
    omega, L, Minv = z["omega_au"], z["L"], z["Minv"]
    D2q = z["D2_direct"]
    s = np.sqrt(omega)
    D_Q = D2q * np.outer(s, s)          # dimensionless-q -> mass-weighted-Q units, as family_rms_freq_error does
    dg = dz["dipole_gradient"]           # (3N, 3) Cartesian
    # Cartesian -> normal coordinates: dmu/dQ_i = sum_a (dmu/dx_a) M^-1/2_a L_ai
    dmu_dQ = (dg.T * Minv[None, :]) @ L  # (3, M)

    grid = np.arange(400.0, 3400.0, 0.25)
    res = {"fwhm": {}, "sticks": {}}
    nu_f, I_f = sticks(omega, D_Q, dmu_dQ)
    nu_d, I_d = sticks(omega, np.diag(np.diag(D_Q)), dmu_dQ)
    res["sticks"] = {"full": {"nu": nu_f.tolist(), "I": I_f.tolist()}, "diagonal": {"nu": nu_d.tolist(), "I": I_d.tolist()}}
    order = np.argsort(nu_f)
    print("sticks: %d modes; strongest full-spectrum bands (cm-1, intensity):" % len(nu_f))
    for k in np.argsort(-I_f)[:6]:
        print("  %8.1f  %8.4f   (diagonal-only: %8.1f  %8.4f)" % (nu_f[k], I_f[k], nu_d[k], I_d[k]))
    print("\nconvolved shapes, max |full - diagonal| as a fraction of the full spectrum's peak in the window:")
    print("%-22s %8s %8s %8s" % ("window", "1 cm-1", "5 cm-1", "13 cm-1"))
    verdict_ok = True
    for name, (lo, hi) in WINDOWS.items():
        m = (grid >= lo) & (grid <= hi)
        row = []
        for f in FWHMS:
            Sf, Sd = convolve(nu_f, I_f, grid[m], f), convolve(nu_d, I_d, grid[m], f)
            peak = float(Sf.max()) if Sf.max() > 0 else 1.0
            frac = float(np.max(np.abs(Sf - Sd)) / peak)
            row.append(frac)
            res["fwhm"].setdefault(str(f), {})[name] = frac
            if f >= 5.0 and frac > 0.05:
                verdict_ok = False
        print("%-22s %7.1f%% %7.1f%% %7.1f%%" % (name, 100 * row[0], 100 * row[1], 100 * row[2]))
    print("\nPre-registered reading (5 %% of peak at 5 and 13 cm-1): %s"
          % ("PASS - the couplings do not change the shape the references can see; diagonal-only is a licensed rung for the large molecules"
             if verdict_ok else
             "FAIL - the couplings change the convolved shape at reference resolution; they are needed for shape"))
    res["verdict"] = "PASS" if verdict_ok else "FAIL"
    res["note"] = ("DFT stand-in Delta_2 (BHHLYP-B3LYP, 6-31G*), harmonic intensities from the B3LYP dipole gradient; "
                   "the plan's anharmonic intensity step is not applied here")
    json.dump(res, open(os.path.join(out, "shape_test_couplings.json"), "w"), indent=1)
    print("written: shape_test_couplings.json")


if __name__ == "__main__":
    main()
