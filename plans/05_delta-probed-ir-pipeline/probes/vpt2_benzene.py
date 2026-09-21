"""pyVPT2 on benzene, B3LYP/6-31G* — the anharmonic step of the shape objective on a real molecule (2026-09-15; the water
self-test of 14 September is `results_vpt2/README.md`). Runs in the `vpt2` environment (pyVPT2 0.1.2, psi4 1.10.2,
qcelemental 0.30.1), Windows, 8 threads; ≈ 3 h estimated (30 modes, 2·30 displaced Hessians at DISP_SIZE 0.05).

Steps: start geometry = the dry run's B3LYP/6-31G* optimum (`results_dryrun/benzene/stageA.json`, psi4 1.11) → re-optimised
here in psi4 1.10.2 (tight) so that the VPT2 reference is a stationary point of this build → harmonic + VPT2 via
`pyvpt2.vpt2_from_schema`. Output: `results_vpt2/benzene_b3lyp_631gs_vpt2.json` (the VPTResult fields) and
`results_vpt2/benzene_b3lyp_631gs_vpt2.md` (per-mode table: harmonic ω, VPT2 ν, harmonic intensity, Fermi flags).

Invocation (PowerShell/Bash, Library\\bin of the vpt2 env on PATH):
  C:/Users/thebr/.conda/envs/vpt2/python.exe -u vpt2_benzene.py --threads 8
"""
import argparse
import json
import os
import time
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_vpt2")
BOHR = 0.529177210903


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--molecule", default="benzene")
    ap.add_argument("--functional", default="b3lyp")
    ap.add_argument("--basis", default="6-31g*")
    ap.add_argument("--no-opt", action="store_true", help="skip the re-optimisation in this psi4 build")
    ap.add_argument("--cache", default=None, help="checkpoint directory (default results_vpt2/cache_<molecule>_<functional>_631gs_psi4-<version>)")
    ap.add_argument("--no-cache", action="store_true", help="run without the checkpoint layer")
    ap.add_argument("--fermi-omega-thresh", type=float, default=200.0, help="pyVPT2 FERMI_OMEGA_THRESH (cm-1); default 200 = pyVPT2 default")
    ap.add_argument("--fermi-k-thresh", type=float, default=1.0, help="pyVPT2 FERMI_K_THRESH (cm-1); 0 = every near-degeneracy within the window goes to a polyad (SPECTRO 2016 recipe, W = 0). Added 21 Sep 2026 after the benzene run of 20 Sep")
    ap.add_argument("--disp-size", type=float, default=0.05, help="pyVPT2 DISP_SIZE in reduced normal coordinates; 0.05 is the pyVPT2 default and, with psi4 FD-of-gradients B3LYP Hessians, too small (21 Sep 2026: route noise up to 1,000 cm-1 in phi_iijj)")
    ap.add_argument("--psi4-points", type=int, default=3, help="psi4 findif points for its internal FD-of-gradients Hessian (3 or 5)")
    ap.add_argument("--tag", default="", help="suffix for the output files (a rerun with other thresholds does not overwrite the first)")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    import psi4
    import qcelemental as qcel
    import pyvpt2
    from pyvpt2 import VPTInput, QCInputSpecification
    psi4.core.set_output_file(os.path.join(OUT, f"{args.molecule}_vpt2_psi4.out"), False)
    psi4.set_num_threads(args.threads)
    psi4.set_memory("8 GB")
    log(f"pyVPT2 {pyvpt2.__version__}, psi4 {psi4.__version__}, qcelemental {qcel.__version__}; {args.molecule} {args.functional}/{args.basis}, {args.threads} threads")

    if args.molecule == "water":   # built-in smoke-test molecule (the 14 September self-test), no stage A needed
        symbols = ["O", "H", "H"]
        x = np.array([[0.0, 0.0, 0.1173], [0.0, 0.7572, -0.4692], [0.0, -0.7572, -0.4692]]) / BOHR
    else:
        a = json.load(open(os.path.join(HERE, "results_dryrun", args.molecule, "stageA.json")))
        symbols, x = a["symbols"], np.array(a["coords_bohr"], float).reshape(-1, 3)
    geom = "\n".join(f"{s} {c[0]*BOHR:.10f} {c[1]*BOHR:.10f} {c[2]*BOHR:.10f}" for s, c in zip(symbols, x))
    mol = psi4.geometry(f"0 1\n{geom}\nunits angstrom\nno_com\nno_reorient\n")
    psi4.set_options({"scf_type": "df", "d_convergence": 1e-10, "e_convergence": 1e-10, "g_convergence": "gau_verytight",
                      "dft_spherical_points": 590, "dft_radial_points": 99})
    cache_dir = None
    if not args.no_cache:
        cache_dir = args.cache or os.path.join(OUT, f"cache_{args.molecule}_{args.functional}_631gs_psi4-{psi4.__version__}")
        os.makedirs(cache_dir, exist_ok=True)
    gcache = os.path.join(cache_dir, "geometry_opt.json") if cache_dir else None
    t0 = time.time()
    if gcache and os.path.exists(gcache):   # a rerun uses exactly the geometry of the first run (bit-identical task keys)
        coords = np.array(json.load(open(gcache))["coords_bohr"])
        log(f"optimised geometry reused from {gcache}")
    else:
        if not args.no_opt:
            log("optimising in this psi4 build (gau_verytight)")
            psi4.optimize(f"{args.functional}/{args.basis}", molecule=mol)
            log(f"optimised in {time.time()-t0:.0f} s")
        coords = np.array([[mol.x(i), mol.y(i), mol.z(i)] for i in range(mol.natom())])   # bohr
        if gcache:
            json.dump({"symbols": symbols, "coords_bohr": coords.tolist(), "level": f"{args.functional}/{args.basis} psi4 {psi4.__version__}",
                       "date": f"{datetime.now():%Y-%m-%d %H:%M}"}, open(gcache, "w"), indent=1)
    shift = float(np.abs(coords - x).max())
    log(f"largest coordinate change against the dry run's geometry: {shift:.2e} bohr")

    qmol = qcel.models.Molecule(symbols=symbols, geometry=coords.reshape(-1).tolist(), molecular_charge=0, molecular_multiplicity=1,
                                fix_com=True, fix_orientation=True)
    spec = QCInputSpecification(model={"method": args.functional, "basis": args.basis},
                                keywords={"scf_type": "df", "d_convergence": 1e-10, "e_convergence": 1e-10,
                                          "dft_spherical_points": 590, "dft_radial_points": 99, "findif__points": args.psi4_points})
    inp = VPTInput(molecule=qmol, input_specification=[spec], keywords={"DISP_SIZE": args.disp_size, "FD": "HESSIAN", "FD_ACC": 2, "FERMI": True, "FERMI_OMEGA_THRESH": args.fermi_omega_thresh, "FERMI_K_THRESH": args.fermi_k_thresh})
    stats = None
    if cache_dir:   # 2026-09-16: checkpoint layer (vpt2_checkpoint.py) — a restart costs one task, not the run
        import sys
        sys.path.insert(0, HERE)
        from vpt2_checkpoint import install
        stats = install(cache_dir)
        log(f"checkpoint cache: {cache_dir} ({len([f for f in os.listdir(cache_dir) if f.endswith('.json')])} tasks stored already)")
    t1 = time.time()
    log("VPT2 started")
    res = pyvpt2.vpt2_from_schema(inp)
    t_vpt2 = time.time() - t1
    log(f"VPT2 done in {t_vpt2:.0f} s" + (f"; cache hits {stats['hits']}, computed {stats['misses']}" if stats else ""))

    def arr(name):
        v = getattr(res, name, None)
        try:
            return np.asarray(v, float).tolist() if v is not None else None
        except Exception:  # noqa: BLE001
            return None

    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "molecule": args.molecule, "functional": args.functional, "basis": args.basis,
           "psi4": psi4.__version__, "pyvpt2": pyvpt2.__version__, "threads": args.threads, "t_opt_s": t1 - t0, "t_vpt2_s": t_vpt2,
           "geometry_shift_bohr": shift, "coords_bohr": coords.tolist(), "symbols": symbols,
           "omega": arr("omega"), "nu": arr("nu"), "harmonic_intensity": arr("harmonic_intensity"),
           "harmonic_zpve": getattr(res, "harmonic_zpve", None), "anharmonic_zpve": getattr(res, "anharmonic_zpve", None),
           "chi": arr("chi"), "phi_ijk": arr("phi_ijk"), "phi_iijj": arr("phi_iijj"), "zeta": arr("zeta"),
           "rotational_constants": arr("rotational_constants")}
    try:
        out["fermi"] = json.loads(json.dumps(getattr(res, "fermi_list", None) or getattr(res, "fermi", None), default=str))
    except Exception:  # noqa: BLE001
        out["fermi"] = None
    def _default(o):   # numpy scalars/arrays inside the VPTResult fields
        return o.tolist() if hasattr(o, "tolist") else str(o)
    json.dump(out, open(os.path.join(OUT, f"{args.molecule}_{args.functional}_631gs_vpt2{args.tag}.json"), "w"), indent=1, default=_default)

    om, nu, it = out["omega"], out["nu"], out["harmonic_intensity"]
    lines = [f"# pyVPT2 — {args.molecule}, {args.functional}/{args.basis}, {out['date']} (psi4 {psi4.__version__}, pyVPT2 {pyvpt2.__version__}, "
             f"{args.threads} threads; optimisation {t1-t0:.0f} s, VPT2 {t_vpt2:.0f} s)", "",
             f"Geometry: the dry run's optimum re-optimised in this build (largest change {shift:.1e} bohr). "
             f"ZPVE harmonic {out['harmonic_zpve']} / anharmonic {out['anharmonic_zpve']} cm⁻¹.", "",
             "| mode | harmonic ω (cm⁻¹) | VPT2 ν (cm⁻¹) | ν − ω | harmonic intensity (km/mol) |", "|---|---|---|---|---|"]
    if om and nu:
        for i, (w, n) in enumerate(zip(om, nu)):
            if abs(w) < 1.0:   # pyVPT2 returns 3N entries; the six translations/rotations are zero
                continue
            ii = f"{it[i]:.1f}" if it and i < len(it) else "—"
            lines.append(f"| {i} | {w:.1f} | {n:.1f} | {n-w:+.1f} | {ii} |")
    lines += ["", f"Fermi resonances: {out.get('fermi')}", "", "Intensities are harmonic only (pyVPT2 has no VPT2 intensities; idea I6)."]
    open(os.path.join(OUT, f"{args.molecule}_{args.functional}_631gs_vpt2{args.tag}.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
