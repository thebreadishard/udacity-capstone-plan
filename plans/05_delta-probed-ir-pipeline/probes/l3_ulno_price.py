"""L3 — the unrestricted LNO-CCSD(T)/cc-pVDZ price of a radical cation (obstacle 9; 24 September 2026). Same shape as l2_lno_price.py:
DF-UHF (conv 1e-11), Pipek–Mezey per spin with Jacobi sweeps (the forge test recipe), ULNOCCSD_T with one fragment per localised orbital of
either spin, tight thresholds, frozen 1s cores, UMP2 for the composite; three points: reference and q = ±1 along the UKS-B3LYP mode nearest
--mode-near cm⁻¹ (default 990, the ring-breathing region). Geometry directory = a cation row (geometry.json + hessian_b3lyp.npz from cation_rows.py).

Usage: python l3_ulno_price.py <row dir> <out dir> [--threads 16] [--max-memory 24000] [--thresh tight] [--basis cc-pvdz] [--mode-near 990]
       python l3_ulno_price.py --smoke <out dir> [--threads 4]      (water cation, one point)
"""
import argparse
import json
import os
import resource
import time
from datetime import datetime

import numpy as np
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reduced_coords import harmonic_check, omega_from_eigenvalue, reduced_displacement   # noqa: E402  (25 Sep 2026: one displacement convention, checked)

THRESH = {"normal": [1e-5, 1e-6], "tight": [1e-6, 1e-7], "xtight": [1e-7, 1e-8]}
AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705


def log(msg, out):
    line = f"[{datetime.now():%H:%M:%S}] {msg}"; print(line, flush=True)
    open(os.path.join(out, "l3.log"), "a", encoding="utf-8").write(line + "\n")


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6


def make_mol(symbols, coords_bohr, basis, max_memory):
    from pyscf import gto
    return gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, coords_bohr)], unit="Bohr", basis=basis, charge=1, spin=1, verbose=0, max_memory=max_memory, symmetry=False)


def run_uhf(mol, dm0=None):
    from pyscf import scf
    mf = scf.UHF(mol).density_fit(); mf.conv_tol = 1e-11; mf.max_cycle = 200
    mf.kernel(dm0) if dm0 is not None else mf.kernel()
    if not mf.converged:   # 25 Sep 2026: benzene+ at the displaced geometry did not converge from the atom guess — second-order SCF from the best density, then a level shift
        dm = mf.make_rdm1(); mf = scf.UHF(mol).density_fit().newton(); mf.conv_tol = 1e-11; mf.max_cycle = 100; mf.kernel(dm)
    if not mf.converged:
        dm = mf.make_rdm1(); mf = scf.UHF(mol).density_fit(); mf.conv_tol = 1e-11; mf.max_cycle = 400; mf.level_shift = 0.5; mf.damp = 0.3; mf.kernel(dm)
    if not mf.converged: raise RuntimeError("UHF did not converge (atom guess, newton, level shift)")
    return mf


def pm_localise(mol, orbocc):
    from pyscf import lo
    mlo = lo.PipekMezey(mol, orbocc); lo_coeff = mlo.kernel()
    for _ in range(100):
        lo1, stable = mlo.stability_jacobi(return_status=True)   # pyscf 2.14 API (the forge test's older order tripped the smoke, 24 Sep 22:4x)
        if stable: break
        mlo = lo.PipekMezey(mol, lo1); mlo.init_guess = None; lo_coeff = mlo.kernel()
    return lo_coeff


def full_ump2(mf, frozen):
    from pyscf import mp
    m = mp.UMP2(mf, frozen=frozen); m.verbose = 0; m.kernel(with_t2=False); return float(m.e_corr)


def point(symbols, coords, basis, thresh, frozen, max_memory, out, tag, dm0=None):
    from pyscf.lno import ULNOCCSD_T
    rec = {"tag": tag, "stages_s": {}, "rss_gb": {}}
    t = time.time(); mol = make_mol(symbols, coords, basis, max_memory); mf = run_uhf(mol, dm0); rec["stages_s"]["scf"] = round(time.time() - t, 1); point.last_dm = mf.make_rdm1()
    rec["s2"] = float(mf.spin_square()[0])
    t = time.time(); lo_coeff = []
    for s in range(2):
        nocc = int(np.count_nonzero(mf.mo_occ[s])); lo_coeff.append(pm_localise(mol, mf.mo_coeff[s][:, frozen:nocc]))
    rec["stages_s"]["pm"] = round(time.time() - t, 1)
    frag_lolist = [[[i], []] for i in range(lo_coeff[0].shape[1])] + [[[], [i]] for i in range(lo_coeff[1].shape[1])]
    t = time.time(); mcc = ULNOCCSD_T(mf, lo_coeff, frag_lolist, frozen=frozen); mcc.lno_thresh = THRESH[thresh]; mcc.verbose = 3; mcc.kernel()
    rec["stages_s"]["ulno_ccsd_t"] = round(time.time() - t, 1); rec["rss_gb"]["ulno_ccsd_t"] = round(rss_gb(), 2)
    t = time.time(); emp2 = full_ump2(mf, frozen); rec["stages_s"]["ump2"] = round(time.time() - t, 1)
    ecc, ept2 = float(mcc.e_corr_ccsd_t), float(mcc.e_corr_pt2)
    rec.update(n_fragments=len(frag_lolist), e_scf=float(mf.e_tot), e_corr_ulno_ccsd_t=ecc, e_corr_ulno_mp2=ept2, e_corr_ump2_full=emp2,
               e_tot_composite=float(mf.e_tot) + ecc - ept2 + emp2, wall_s=round(sum(rec["stages_s"].values()), 1))
    log(f"{tag}: UHF {rec['stages_s']['scf']} s (<S²> {rec['s2']:.3f}), PM {rec['stages_s']['pm']} s, ULNO-CCSD(T) {rec['stages_s']['ulno_ccsd_t']} s ({len(frag_lolist)} fragments), "
        f"UMP2 {rec['stages_s']['ump2']} s; peak RSS {rec['rss_gb']['ulno_ccsd_t']} GB; E_composite {rec['e_tot_composite']:.8f}", out)
    return rec


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("rowdir", nargs="?"); ap.add_argument("out"); ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--max-memory", type=int, default=24000); ap.add_argument("--thresh", default="tight"); ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--mode-near", type=float, default=990.0); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    from pyscf import lib
    lib.num_threads(a.threads); os.makedirs(a.out, exist_ok=True)
    if a.smoke:
        symbols = ["O", "H", "H"]; coords = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])
        log(f"smoke: water cation {a.basis} {a.thresh}, {a.threads} threads", a.out)
        rec = point(symbols, coords, a.basis, a.thresh, 1, a.max_memory, a.out, "water+")
        json.dump(rec, open(os.path.join(a.out, "smoke_water_cation.json"), "w"), indent=1); log("smoke done", a.out); return
    g = json.load(open(os.path.join(a.rowdir, "geometry.json"))); symbols = g["symbols"]; coords0 = np.asarray(g["coords_bohr"], float)
    H = np.load(os.path.join(a.rowdir, "hessian_b3lyp.npz"))["H_projected"]; frozen = sum(1 for s in symbols if s.upper() != "H")
    m = np.repeat(np.asarray(g["masses_amu"]) * AMU2AU, 3); Minv = 1 / np.sqrt(m)
    w, L = np.linalg.eigh(H * np.outer(Minv, Minv)); keep = np.argsort(np.abs(w))[6:]
    cm = np.sqrt(np.abs(w[keep])) * HARTREE2CM; k = keep[int(np.argmin(np.abs(cm - a.mode_near)))]; omega_cm = float(np.sqrt(abs(w[k])) * HARTREE2CM)
    omega_au = omega_from_eigenvalue(w[k])   # 25 Sep 2026: w is ω²; the displacement divides by sqrt(ω), not by ω (the bug that cost benzene+ a 56-min point at +0.27 E_h)
    log(f"L3: {os.path.basename(a.rowdir.rstrip('/'))} {a.basis} {a.thresh}, {len(symbols)} atoms, frozen core {frozen}, {a.threads} threads, max_memory {a.max_memory} MB; mode {k} ({omega_cm:.0f} cm⁻¹)", a.out)
    recs = []; res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "row": os.path.basename(a.rowdir.rstrip("/")), "basis": a.basis, "thresh": a.thresh, "threads": a.threads,
                      "max_memory_mb": a.max_memory, "frozen": frozen, "mode": int(k), "omega_b3lyp_cm": omega_cm, "points": recs}
    pj = os.path.join(a.out, "l3_price.json"); prev = {}
    if os.path.exists(pj):   # 25 Sep 2026: resume — finished points are reused (benzene+ reference: 59 min)
        try: prev = {r["tag"]: r for r in json.load(open(pj))["points"] if "e_tot_composite" in r}
        except Exception: prev = {}
    if prev: log(f"resume: reusing finished points {sorted(prev)}", a.out)
    ref_dm = None
    for q in (0.0, 1.0, -1.0):
        x = reduced_displacement(coords0, L[:, k], omega_au, Minv, q); tag = f"q{q:+.1f}"
        if q != 0.0: log(f"{tag}: harmonic check ½dᵀHd / ½ωq² = {harmonic_check(H, coords0, x, omega_au, q):.4f}; max atom displacement {np.linalg.norm(x - coords0, axis=1).max():.3f} bohr", a.out)
        if tag in prev:
            recs.append(prev[tag])
            if q == 0.0: ref_dm = run_uhf(make_mol(symbols, x, a.basis, a.max_memory)).make_rdm1()   # the reference density is the guess for the displaced points
            continue
        recs.append(dict(point(symbols, x, a.basis, a.thresh, frozen, a.max_memory, a.out, tag, dm0=ref_dm), q=q))
        if q == 0.0: ref_dm = point.last_dm
        json.dump(res, open(pj, "w"), indent=1)
    E = {r["q"]: r["e_tot_composite"] for r in recs}; ratio = (E[1.0] + E[-1.0] - 2 * E[0.0]) / np.sqrt(abs(w[k]))
    res["curvature_ratio_cc_over_b3lyp"] = float(ratio); res["omega_prime_cm"] = float(omega_cm * np.sqrt(abs(ratio)))
    res["price_point_s_mean"] = float(np.mean([r["wall_s"] for r in recs])); res["price_ulno_ccsd_t_s_mean"] = float(np.mean([r["stages_s"]["ulno_ccsd_t"] for r in recs]))
    json.dump(res, open(os.path.join(a.out, "l3_price.json"), "w"), indent=1)
    log(f"sanity: ω′ along mode {k} = {res['omega_prime_cm']:.0f} cm⁻¹ vs UKS-B3LYP {omega_cm:.0f} (curvature ratio {ratio:.3f})", a.out)
    log(f"PRICE: {res['price_point_s_mean']/60:.1f} min per point ({res['price_ulno_ccsd_t_s_mean']/60:.1f} min of it ULNO-CCSD(T)) at {a.threads} threads", a.out)
    log("L3 finished", a.out)


if __name__ == "__main__":
    main()
