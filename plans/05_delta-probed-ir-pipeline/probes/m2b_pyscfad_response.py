#!/usr/bin/env python3
"""M2b - does PySCFAD's shipped LNO-CCSD(T) compute the plan's response R_s? (pre-registered 17 Sep 2026,
GoalGathering/notes/PreRegistration_2026-09-17_M2b_PySCFAD_LNO_as_Engine.md; run only after the user read it).

Arm A is the sealed run results_m1/benzene_cc-pvdz_tight/ (frozen spaces, thresholds [1e-5, 1e-6]).
Arm B is PySCFAD's LNOCCSD_T, ENERGY ONLY (no gradient, no AD tape), at exactly arm A's displaced
geometries: x = coords0 + ((L @ (v / sqrt(omega))) * Minv).reshape(-1, 3), v[m] = q, with L, omega, Minv,
coords0 from results_dryrun/benzene/stageA_hessians.npz - the same file m1_frozen_spaces.py reads.

R_s(m) = 0.5 [E(+1) + E(-1)] - E(0) on LNO-CCSD(T) total energies of each arm. Reading, fixed in the
pre-registration: STAND-IN if |R_s^B - R_s^A| <= 6 uE_h on all three modes at setting (ii) = arm A's
thresholds; PARTIAL if only the C-H modes (12, 6) pass; FAIL otherwise. Setting (i) = PySCFAD defaults,
reported not scored.

WSL, ~/qcad (PySCFAD 0.3.3):
    ~/qcad/bin/python m2b_pyscfad_response.py --smoke           # reference geometry, setting (ii) only
    ~/qcad/bin/python m2b_pyscfad_response.py                   # all 7 geometries x 2 settings, resumable
"""
import argparse
import json
import os
import resource
import time
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DRY = os.path.join(HERE, "results_dryrun", "benzene")
ARM_A = os.path.join(HERE, "results_m1", "benzene_cc-pvdz_tight")
OUT = os.path.join(HERE, "results_m2b")
BASIS = "cc-pvdz"
MODES = [12, 18, 6]
Q = 1.0
SETTINGS = {"i_default": None, "ii_armA": (1e-5, 1e-6)}
BAR_UEH = 6.0


def log(msg):
    print("[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg), flush=True)


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def geometries():
    a = json.load(open(os.path.join(DRY, "stageA.json")))
    z = np.load(os.path.join(DRY, "stageA_hessians.npz"))
    L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    zA = np.load(os.path.join(ARM_A, "frozen_spaces_reference.npz"))
    dev = float(np.max(np.abs(zA["coords0"] - coords0)))
    assert dev < 1e-10, "arm A's reference geometry differs from the dry run's: %.2e bohr" % dev
    geoms = {"ref": coords0}
    for m in MODES:
        for q in (+Q, -Q):
            v = np.zeros(len(omega)); v[m] = q
            geoms["m%d_q%+.1f" % (m, q)] = coords0 + ((L @ (v / np.sqrt(omega))) * Minv).reshape(-1, 3)
    return a["symbols"], geoms


def lno_energy(symbols, coords_bohr, thresh, threads):
    from pyscfad import gto, scf, lno
    from pyscfad.df.df_jk import density_fit
    from pyscf import lib
    lib.num_threads(threads)
    mol = gto.Mole()
    mol.atom = [(s, tuple(map(float, c))) for s, c in zip(symbols, coords_bohr)]
    mol.unit = "Bohr"; mol.basis = BASIS; mol.verbose = 0; mol.max_memory = 10000
    try:
        mol.build(trace_coords=False)          # energy only: no AD tape (M2a API note, 13 Sep)
    except TypeError:
        mol.build()
    mf = density_fit(scf.RHF(mol)).run(conv_tol=1e-11)
    mf.max_memory = 10000
    mlno = lno.LNOCCSD_T(mf)
    mlno.max_memory = 10000
    if thresh is not None:
        mlno.thresh_occ, mlno.thresh_vir = thresh
    mlno.kernel()                              # returns None; energies land on the object
    # 17 Sep 22:2x, read from pyscfad/lno/ccsd.py: e_corr_ccsd_t is the (T) INCREMENT alone (efrag_cc_t);
    # the LNO-CCSD(T) correlation is e_corr = e_corr_ccsd + e_corr_ccsd_t. The smoke run (ref, setting ii)
    # stored e_scf + e_corr_ccsd_t = -230.7578 against arm A's -231.5810 and exposed it. All three pieces
    # are kept so the record cannot be misread again.
    return dict(e_scf=float(mf.e_tot), e_corr_ccsd=float(mlno.e_corr_ccsd), e_corr_t_increment=float(mlno.e_corr_ccsd_t),
                e_corr_pt2=float(mlno.e_corr_pt2), e_corr=float(mlno.e_corr),
                e_tot=float(mf.e_tot + mlno.e_corr))


def arm_a_rs():
    s = json.load(open(os.path.join(ARM_A, "m1_sealed_energies.json")))
    pts = {(p["mode"], p["q"]): p["A"] for p in s["points"]}
    e = lambda m, q: pts[(m, q)]["e_scf"] + pts[(m, q)]["e_corr_lno_ccsd_t"]
    return {m: 0.5 * (e(m, 1.0) + e(m, -1.0)) - e(m, 0.0) for m in MODES}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--threads", type=int, default=4)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cache_path = os.path.join(OUT, "m2b_energies.json")
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    symbols, geoms = geometries()
    todo = [("ref", "ii_armA")] if args.smoke else [(g, s) for s in SETTINGS for g in geoms]
    for gname, sname in todo:
        key = "%s|%s" % (gname, sname)
        if key in cache:
            continue
        t0 = time.time()
        rec = lno_energy(symbols, geoms[gname], SETTINGS[sname], args.threads)
        rec["wall_s"] = time.time() - t0; rec["peak_rss_mb"] = rss_mb()
        cache[key] = rec
        json.dump(cache, open(cache_path, "w"), indent=1)
        log("%-16s %-10s E_tot %.8f  (%.0f s, peak %.0f MB)" % (gname, sname, rec["e_tot"], rec["wall_s"], rec["peak_rss_mb"]))
    if args.smoke:
        return
    rsA = arm_a_rs()
    out = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "basis": BASIS, "modes": MODES, "q": Q,
           "bar_uEh": BAR_UEH, "arm_A": ARM_A, "R_s": {}}
    print("\nR_s = 0.5[E(+1)+E(-1)] - E(0), LNO-CCSD(T) total energies, uE_h")
    print("%-6s %12s %14s %14s %12s %12s" % ("mode", "arm A", "B (ii) armA thr", "|B-A| (ii)", "B (i) def", "|B-A| (i)"))
    verdicts = {}
    for m in MODES:
        row = {}
        for sname in SETTINGS:
            e = lambda g: cache["%s|%s" % (g, sname)]["e_tot"]
            row[sname] = 0.5 * (e("m%d_q+1.0" % m) + e("m%d_q-1.0" % m)) - e("ref")
        dA = rsA[m] * 1e6; dii = row["ii_armA"] * 1e6; di = row["i_default"] * 1e6
        verdicts[m] = abs(dii - dA) <= BAR_UEH
        out["R_s"][m] = {"A": dA, "B_ii": dii, "B_i": di, "diff_ii": dii - dA, "diff_i": di - dA, "pass_ii": verdicts[m]}
        print("%-6d %12.3f %14.3f %14.3f %12.3f %12.3f" % (m, dA, dii, abs(dii - dA), di, abs(di - dA)))
    if all(verdicts.values()):
        verdict = "STAND-IN: PySCFAD's LNO computes the plan's response within 3x the frozen-space noise on all three modes"
    elif verdicts[12] and verdicts[6] and not verdicts[18]:
        verdict = "PARTIAL: C-H modes pass, the C-C stretch does not - a mixed deck, priced before adoption"
    else:
        verdict = "FAIL: the shipped engine does not compute the plan's quantity; M2 (in-house gradients) goes on the schedule"
    out["verdict"] = verdict
    print("\nPre-registered bar %.0f uE_h at setting (ii). %s" % (BAR_UEH, verdict))
    json.dump(out, open(os.path.join(OUT, "m2b_result.json"), "w"), indent=1)
    print("written: results_m2b/m2b_result.json")


if __name__ == "__main__":
    main()
