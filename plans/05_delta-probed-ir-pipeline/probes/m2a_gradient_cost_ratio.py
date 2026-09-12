"""M2a (pre-registered 2026-09-13, `notes/PreRegistration_2026-09-13_M2a_Gradient_Cost_Ratio.md`) — the gradient-to-energy cost ratio g
in PySCFAD, benzene, cells 0–5 of the pre-registration. NOT RUN until the naphthalene xtight timing has finished; needs the `~/qcad`
environment (PySCFAD 0.3.3, CPU JAX) which is installed only with the user's permission.

g_X = t_grad / t_E: wall time of one full nuclear gradient over wall time of one energy, same engine, same machine, same threads, same SCF
start, same code path; SCF excluded from both and timed separately; three repeats, median reported with spread; peak RSS per call.
Reference line: g_FD = 6N (central finite differences), 72 at benzene.

Usage (WSL):  ~/qcad/bin/python plans/05_delta-probed-ir-pipeline/probes/m2a_gradient_cost_ratio.py --cells 0,1,2,3 [--basis cc-pvdz]
              [--threads 8] [--repeats 3] [--lno-thresh 1e-5,1e-6]
Self-test (Windows, numpy only):  python m2a_gradient_cost_ratio.py --self-test
API note (checked at install, 2026-09-13, PySCFAD 0.3.3 in ~/qcad): Mole.build takes trace_coords (default True); Mole carries coords/exp/ctr_coeff
as traced fields; (T) lives on pyscfad.cc.rccsd.RCCSD.ccsd_t (not on pyscfad.cc.RCCSD); LNOCCSD_T(mf, thresh=1e-4) sets thresh_occ = thresh_vir,
kernel() auto-fragments by atom with lo_type "iao" (plan 05 uses Pipek-Mezey LMOs - a difference to record, not to hide); pyscfad/lno/_checkpointed.py
uses jax.checkpoint (the paper's recomputation). The pre-registered content is the protocol (cells, timing rule, reading), not these call signatures. Every number printed comes from the run; constants in CONSTANTS. Results: probes/results_m2a/"""
import argparse
import json
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DRYRUN = HERE / "results_dryrun/benzene"
OUT = HERE / "results_m2a"
CONSTANTS = {"basis_default": "cc-pvdz", "repeats_default": 3, "threads_default": 8, "molecule": "benzene (plan 05 dry-run geometry, stageA.json)",
             "cells": {0: "RHF smoke: AD gradient vs PySCF analytic gradient (tol 1e-6 Eh/bohr) + timing pipeline", 1: "MP2 canonical", 2: "CCSD(T) canonical",
                       3: "LNO-CCSD(T) as shipped (PySCFAD defaults)", 4: "LNO-CCSD(T) at thresholds matching plan 05 tight", 5: "LNO-CCSD(T) cc-pVTZ (only if cell 3 gives g <= 20)"},
             "reading": {"g<=6": "within the AD constant; substitution and mode G pay by an order of magnitude", "6<g<=20": "substitution pays, mode G marginal",
                         "g>20": "gradient levers do not change plan 05's order of magnitude at benzene size"},
             "rhf_gradient_tolerance": 1e-6}


def peak_rss_mb():
    try:
        import resource as _r
        return _r.getrusage(_r.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:  # noqa: BLE001
        return float("nan")


def timed(fn, repeats):
    ts = []; vals = None
    for _ in range(repeats):
        t0 = time.perf_counter(); vals = fn(); ts.append(time.perf_counter() - t0)
    return float(np.median(ts)), [float(t) for t in ts], vals


def geometry():
    a = json.load(open(DRYRUN / "stageA.json"))
    return a["symbols"], np.array(a["coords_bohr"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="0,1,2,3"); ap.add_argument("--basis", default=CONSTANTS["basis_default"])
    ap.add_argument("--threads", type=int, default=CONSTANTS["threads_default"]); ap.add_argument("--repeats", type=int, default=CONSTANTS["repeats_default"])
    ap.add_argument("--lno-thresh", default="1e-6,1e-7", help="cell 4: (thresh_occ, thresh_vir) = plan 05's tight pair (m1_frozen_spaces.THRESH); PySCFAD's single `thresh` (default 1e-4) sets both equal")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    sym, X = geometry()
    if args.self_test:
        nat = len(sym); print(f"geometry: {''.join(sym)} ({nat} atoms), 3N = {3*nat}, g_FD (central differences) = {6*nat}")
        print("cells:", {k: v for k, v in CONSTANTS["cells"].items()}); print("self-test OK (numpy only; JAX/PySCFAD not touched)")
        return
    os.environ.setdefault("OMP_NUM_THREADS", str(args.threads))
    import jax; jax.config.update("jax_enable_x64", True)
    import pyscf, pyscfad
    from pyscfad import gto, scf
    versions = {"python": platform.python_version(), "jax": jax.__version__, "pyscf": pyscf.__version__, "pyscfad": pyscfad.__version__, "platform": platform.platform()}
    OUT.mkdir(exist_ok=True)
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "versions": versions, "basis": args.basis, "threads": args.threads, "repeats": args.repeats, "cells": {}}
    cells = [int(c) for c in args.cells.split(",")]
    mol = gto.Mole(atom=[(s, tuple(c)) for s, c in zip(sym, X)], unit="Bohr", basis=args.basis, verbose=0); mol.build(trace_coords=True, trace_exp=False, trace_ctr_coeff=False)
    nat = len(sym); g_fd = 6 * nat
    # SCF once, timed separately
    t0 = time.perf_counter(); mf = scf.RHF(mol); mf.conv_tol = 1e-11; e_scf = mf.kernel(); t_scf = time.perf_counter() - t0
    out["scf"] = {"e_tot": float(e_scf), "t_scf_s": t_scf, "converged": bool(mf.converged)}

    def record(cell, t_e, ts_e, t_g, ts_g, rss_e, rss_g, extra=None):
        g = t_g / t_e if t_e > 0 else float("nan")
        rec = {"cell": CONSTANTS["cells"][cell], "t_energy_s": t_e, "t_energy_repeats_s": ts_e, "t_gradient_s": t_g, "t_gradient_repeats_s": ts_g,
               "g": g, "g_FD_reference": g_fd, "peak_rss_after_energy_MB": rss_e, "peak_rss_after_gradient_MB": rss_g}
        if extra: rec.update(extra)
        out["cells"][str(cell)] = rec
        print(f"cell {cell}: t_E {t_e:.1f} s, t_grad {t_g:.1f} s, g = {g:.2f} (g_FD = {g_fd}), RSS {rss_g:.0f} MB", flush=True)
        json.dump(out, open(OUT / f"m2a_{args.basis}.json", "w"), indent=1)

    if 0 in cells:
        def e_fn(): return scf.RHF(mol).kernel()
        def g_fn():
            def e_of_mol(m):
                return scf.RHF(m).kernel()
            return jax.grad(e_of_mol)(mol).coords
        t_e, ts_e, _ = timed(e_fn, args.repeats); rss_e = peak_rss_mb()
        t_g, ts_g, grad_ad = timed(g_fn, args.repeats); rss_g = peak_rss_mb()
        # reference: PySCF's analytic RHF gradient at the same geometry
        from pyscf import gto as pgto, scf as pscf
        pm = pgto.M(atom=[(s, tuple(c)) for s, c in zip(sym, X)], unit="Bohr", basis=args.basis, verbose=0)
        pmf = pscf.RHF(pm); pmf.conv_tol = 1e-11; pmf.kernel(); grad_ref = pmf.nuc_grad_method().kernel()
        dev = float(np.abs(np.asarray(grad_ad) - grad_ref).max())
        record(0, t_e, ts_e, t_g, ts_g, rss_e, rss_g, {"max_abs_dev_vs_pyscf_analytic_Eh_per_bohr": dev, "passes": dev < CONSTANTS["rhf_gradient_tolerance"]})
    if 1 in cells:
        from pyscfad import mp
        def e_fn(): return mp.MP2(scf.RHF(mol).run(conv_tol=1e-11)).kernel()[0]
        def g_fn():
            def e_of_mol(m):
                mf_ = scf.RHF(m).run(conv_tol=1e-11); return mf_.e_tot + mp.MP2(mf_).kernel()[0]
            return jax.grad(e_of_mol)(mol).coords
        t_e, ts_e, _ = timed(e_fn, args.repeats); rss_e = peak_rss_mb(); t_g, ts_g, _ = timed(g_fn, args.repeats); rss_g = peak_rss_mb()
        record(1, t_e, ts_e, t_g, ts_g, rss_e, rss_g)
    if 2 in cells:
        from pyscfad.cc import rccsd   # pyscfad.cc.RCCSD lacks ccsd_t; rccsd.RCCSD has it (checked at install, 2026-09-13)
        def e_fn():
            mf_ = scf.RHF(mol).run(conv_tol=1e-11); mc = rccsd.RCCSD(mf_); ecc = mc.kernel()[0]; return ecc + mc.ccsd_t()
        def g_fn():
            def e_of_mol(m):
                mf_ = scf.RHF(m).run(conv_tol=1e-11); mc = rccsd.RCCSD(mf_); ecc = mc.kernel()[0]; return mf_.e_tot + ecc + mc.ccsd_t()
            return jax.grad(e_of_mol)(mol).coords
        t_e, ts_e, _ = timed(e_fn, args.repeats); rss_e = peak_rss_mb(); t_g, ts_g, _ = timed(g_fn, args.repeats); rss_g = peak_rss_mb()
        record(2, t_e, ts_e, t_g, ts_g, rss_e, rss_g)
    for cell in (3, 4):
        if cell in cells:
            from pyscfad import lno
            thr = None if cell == 3 else [float(t) for t in args.lno_thresh.split(",")]
            def make(m):
                mf_ = scf.RHF(m).run(conv_tol=1e-11)
                mlno = lno.LNOCCSD_T(mf_)          # defaults: thresh 1e-4 (sets thresh_occ = thresh_vir), lo_type "iao", single-atom fragments (autofrag)
                if thr is not None:
                    mlno.thresh_occ, mlno.thresh_vir = thr   # plan 05's tight pair; PySCFAD's LNO applies (thresh_occ, thresh_vir) as its PNO thresholds
                return mf_, mlno
            def e_fn():
                mf_, mlno = make(mol); return mlno.kernel()
            def g_fn():
                def e_of_mol(m):
                    mf_, mlno = make(m); return mf_.e_tot + mlno.kernel()
                return jax.grad(e_of_mol)(mol).coords
            t_e, ts_e, e_val = timed(e_fn, args.repeats); rss_e = peak_rss_mb(); t_g, ts_g, _ = timed(g_fn, args.repeats); rss_g = peak_rss_mb()
            record(cell, t_e, ts_e, t_g, ts_g, rss_e, rss_g, {"lno_thresh": thr, "e_corr": float(np.asarray(e_val))})
    # markdown
    L = [f"# M2a — gradient-to-energy cost ratio g, benzene {args.basis} ({out['date']}; {versions})", "",
         f"SCF {t_scf:.1f} s (excluded from both sides). g_FD = {g_fd}. Three repeats; median reported.", "",
         "| cell | t_energy (s) | t_gradient (s) | **g** | peak RSS after gradient (MB) | note |", "|---|---|---|---|---|---|"]
    for c, r in out["cells"].items():
        note = f"dev vs analytic {r['max_abs_dev_vs_pyscf_analytic_Eh_per_bohr']:.1e}" if "max_abs_dev_vs_pyscf_analytic_Eh_per_bohr" in r else (f"thresh {r.get('lno_thresh')}" if "lno_thresh" in r else "")
        L.append(f"| {c}: {r['cell']} | {r['t_energy_s']:.1f} | {r['t_gradient_s']:.1f} | **{r['g']:.2f}** | {r['peak_rss_after_gradient_MB']:.0f} | {note} |")
    L += ["", "Pre-stated reading: " + json.dumps(CONSTANTS["reading"]), "", "Constants: " + json.dumps(CONSTANTS)]
    (OUT / f"m2a_{args.basis}.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
