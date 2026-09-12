#!/usr/bin/env python
"""One molecule of the Module 05 corpus, inside the conda env `qc` (psi4 1.11). Called by run_corpus.py:
    python psi4_worker.py <job.json>
job.json: {"id", "layer", "xyz_angstrom": [[sym, x, y, z], ...], "deck": {...}, "out_dir", "optimise": bool,
           "grid_check": bool}
Writes into out_dir: geometry.json, hessian_b3lyp.npz, hessian_wb97x.npz, result.json (timings, energies, frequencies,
peak memory). Hessians are stored raw (hartree/bohr^2, Cartesian) AND translation/rotation-projected; frequencies from the
projected, mass-weighted Hessian. Exit code 0 on success; the error text goes to result.json on failure."""
import json, os, sys, time, traceback
import numpy as np


def project_tr(H, masses, coords):
    """Project translations and rotations out of a Cartesian Hessian (hartree/bohr^2; coords in bohr)."""
    n = len(masses); M = np.repeat(masses, 3); Hw = H / np.sqrt(np.outer(M, M))
    com = (coords * masses[:, None]).sum(0) / masses.sum(); x = coords - com
    vecs = []
    for k in range(3):
        v = np.zeros((n, 3)); v[:, k] = np.sqrt(masses); vecs.append(v.ravel())
    for k in range(3):
        v = np.zeros((n, 3)); e = np.zeros(3); e[k] = 1
        v[:] = np.cross(e, x) * np.sqrt(masses)[:, None]; vecs.append(v.ravel())
    Q, _ = np.linalg.qr(np.array(vecs).T)
    P = np.eye(3 * n) - Q @ Q.T
    Hp = P @ Hw @ P
    return Hp * np.sqrt(np.outer(M, M))   # back to Cartesian (unweighted) with TR removed


def frequencies_cm(H, masses):
    M = np.repeat(masses, 3); Hw = H / np.sqrt(np.outer(M, M))
    w2 = np.linalg.eigvalsh(Hw)
    AMU = 1.66053906660e-27; HART_B2 = 4.3597447222071e-18 / (0.529177210903e-10) ** 2; C = 2.99792458e10
    w = np.sign(w2) * np.sqrt(np.abs(w2) * HART_B2 / AMU) / (2 * np.pi * C)
    return w


def main(job_path):
    job = json.load(open(job_path)); out = job["out_dir"]; os.makedirs(out, exist_ok=True)
    res = {"id": job["id"], "layer": job["layer"], "deck": job["deck"], "status": "failed", "timings_s": {}}
    t0 = time.time()
    try:
        import psi4, resource_probe  # noqa: F401  (resource_probe optional)
    except Exception:
        import psi4
    try:
        d = job["deck"]
        psi4.set_memory(f"{d['memory_gb']} GB"); psi4.set_num_threads(d["threads"]); psi4.core.set_output_file(os.path.join(out, "psi4.out"), False)
        geom = "\n".join(f"{s} {x:.8f} {y:.8f} {z:.8f}" for s, x, y, z in job["xyz_angstrom"])
        mol = psi4.geometry(f"{d['charge']} {d['multiplicity']}\n{geom}\nunits angstrom\nsymmetry c1\nno_reorient\nno_com\n")
        psi4.set_options({"basis": d["basis"], "scf_type": d["scf_type"], "e_convergence": d["e_convergence"], "d_convergence": d["d_convergence"],
                          "dft_radial_points": d["dft_radial_points"], "dft_spherical_points": d["dft_spherical_points"], "reference": d["reference"]})
        if job.get("optimise", True):
            t = time.time(); e_opt = psi4.optimize(d["low_functional"], molecule=mol); res["timings_s"]["optimise"] = round(time.time() - t, 1); res["e_opt"] = e_opt
        coords = np.array(mol.geometry()); masses = np.array([mol.mass(i) for i in range(mol.natom())]); syms = [mol.symbol(i) for i in range(mol.natom())]
        json.dump({"symbols": syms, "coords_bohr": coords.tolist(), "masses_amu": masses.tolist(), "optimised_at": d["low_functional"] if job.get("optimise", True) else "input geometry"}, open(os.path.join(out, "geometry.json"), "w"), indent=1)
        for tag, func in (("b3lyp", d["low_functional"]), ("wb97x", d["high_functional"])):
            t = time.time(); e, wfn = psi4.hessian(func, molecule=mol, return_wfn=True)
            H = np.array(wfn.hessian()); Hp = project_tr(H, masses, coords); fr = frequencies_cm(Hp, masses)
            np.savez_compressed(os.path.join(out, f"hessian_{tag}.npz"), H_raw=H, H_projected=Hp, freq_cm=fr, energy=float(e))
            res["timings_s"][f"hessian_{tag}"] = round(time.time() - t, 1); res[f"e_{tag}"] = float(e); res[f"freq_{tag}_cm"] = [round(float(x), 2) for x in np.sort(fr)]
            res[f"n_imaginary_{tag}"] = int((fr < -10).sum())
        if job.get("grid_check"):
            g = d["grid_check_for_timing_test"]; psi4.set_options({"dft_radial_points": g["radial"], "dft_spherical_points": g["spherical"]})
            t = time.time(); e, wfn = psi4.hessian(d["low_functional"], molecule=mol, return_wfn=True); H2 = project_tr(np.array(wfn.hessian()), masses, coords)
            H1 = np.load(os.path.join(out, "hessian_b3lyp.npz"))["H_projected"]
            res["grid_check"] = {"radial": g["radial"], "spherical": g["spherical"], "seconds": round(time.time() - t, 1), "max_abs_dH_hartree_bohr2": float(np.abs(H2 - H1).max()),
                                 "max_abs_dfreq_cm": float(np.abs(np.sort(frequencies_cm(H2, masses)) - np.sort(frequencies_cm(H1, masses))).max())}
        res["status"] = "done"
    except Exception:
        res["error"] = traceback.format_exc()[-3000:]
    try:
        import psutil; res["peak_rss_gb"] = round(psutil.Process().memory_info().peak_wset / 1e9, 2)
    except Exception:
        pass
    res["timings_s"]["total"] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(out, "result.json"), "w"), indent=1)
    sys.exit(0 if res["status"] == "done" else 1)


if __name__ == "__main__":
    main(sys.argv[1])
