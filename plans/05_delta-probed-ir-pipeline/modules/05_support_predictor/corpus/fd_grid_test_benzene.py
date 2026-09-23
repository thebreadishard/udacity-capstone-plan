"""Pin the mechanism of benzene's wrong corpus wB97X Hessian (23 Sep 2026): psi4 finite-difference Hessians at the corpus geometry with
(a) the corpus deck exactly (grid 75/302, DF, C1, 3-point 0.005 bohr) — reproducibility; (b) the same with a (99,590) grid — grid noise;
(c) B3LYP with the corpus deck for the same comparison. Prints the sorted frequencies against the analytic pyscf ones and the degenerate-pair splits.
Usage: python benzene_fd_tests.py <molecule dir> [--threads 16]"""
import argparse, json, sys, time
import numpy as np, psi4
ap = argparse.ArgumentParser(); ap.add_argument("d"); ap.add_argument("--threads", type=int, default=16); a = ap.parse_args()
d = a.d; g = json.load(open(d + "/geometry.json")); deck = json.load(open(d + "/result.json"))["deck"]
chk = json.load(open(d + "/analytic_check.json"))
psi4.set_num_threads(a.threads); psi4.set_memory("20 GB"); psi4.core.set_output_file("/root/m05run/benzene_fd_tests.out", False)
geom = "\n".join(f"{s} {x[0]*0.529177210903:.10f} {x[1]*0.529177210903:.10f} {x[2]*0.529177210903:.10f}" for s, x in zip(g["symbols"], g["coords_bohr"]))
def run(xc, radial, spherical, label):
    mol = psi4.geometry(f"0 1\n{geom}\nunits angstrom\nsymmetry c1\nno_reorient\nno_com\n")
    psi4.set_options({"basis": deck["basis"], "scf_type": deck["scf_type"], "e_convergence": deck["e_convergence"], "d_convergence": deck["d_convergence"],
                      "dft_radial_points": radial, "dft_spherical_points": spherical, "reference": "rhf"})
    t0 = time.time(); e, wfn = psi4.frequencies(xc, molecule=mol, return_wfn=True, dertype=1)
    fr = np.sort(np.array(wfn.frequencies().to_array())); fa = np.array(chk["wb97x" if "97" in xc.lower() else "b3lyp"]["freq_analytic"])
    n = len(fa); fr = fr[-n:]
    print(f"{label}: {time.time()-t0:.0f} s | max |Δ vs analytic| {np.abs(fr-fa).max():.0f} cm-1 | pairs: {fr[2]:.0f}/{fr[3]:.0f}, {fr[16]:.0f}/{fr[17]:.0f}, {fr[22]:.0f}/{fr[23]:.0f}", flush=True)
    print("   ", np.round(fr, 0).astype(int).tolist(), flush=True)
    psi4.core.clean()
run(deck["high_functional"], deck["dft_radial_points"], deck["dft_spherical_points"], "(a) wB97X, corpus deck (grid 75/302)")
run(deck["high_functional"], 99, 590, "(b) wB97X, grid 99/590")
run(deck["low_functional"], deck["dft_radial_points"], deck["dft_spherical_points"], "(c) B3LYP, corpus deck")
