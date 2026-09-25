"""L2 — the LNO-CCSD(T)/cc-pVDZ price of one substituted molecule (pre-registered 24 September 2026,
PreRegistration_2026-09-24_L2_LNO_Label_Price_Substituted.md). The anchor's deck (m1_frozen_spaces.py) at cc-pVDZ, fresh localisation at
every point (arm C), three points: the reference and q = ±1 along the B3LYP mode with the largest amplitude on the neighbourhood atoms.

Usage: python l2_lno_price.py <molecule dir with geometry.json + hessian_b3lyp.npz> <out dir> [--near 0,1,2] [--threads 8] [--max-memory 16000]
                              [--thresh tight] [--basis cc-pvdz] [--smoke]   (--smoke: water, one point, seconds)
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
    open(os.path.join(out, "l2.log"), "a", encoding="utf-8").write(line + "\n")


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6


def make_mol(symbols, coords_bohr, basis, max_memory):
    from pyscf import gto
    return gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, coords_bohr)], unit="Bohr", basis=basis, verbose=0, max_memory=max_memory, symmetry=False)


def run_scf(mol):
    from pyscf import scf
    mf = scf.RHF(mol).density_fit(); mf.conv_tol = 1e-11; mf.kernel()
    if not mf.converged: raise RuntimeError("SCF did not converge")
    return mf


def pm_localise(mol, orbocc):
    from pyscf import lo
    mlo = lo.PipekMezey(mol, orbocc); lo_coeff = mlo.kernel()
    for _ in range(100):
        lo1, stable = mlo.stability_jacobi(return_status=True)
        if stable: break
        mlo = lo.PipekMezey(mol, lo1); mlo.init_guess = None; lo_coeff = mlo.kernel()
    return lo_coeff


def full_mp2(mf, frozen):
    from pyscf import mp
    m = mp.dfmp2.DFMP2(mf, frozen=frozen) if hasattr(mp, "dfmp2") else mp.MP2(mf, frozen=frozen)
    m.verbose = 0; m.kernel(); return float(m.e_corr)


TIER = "t0"


def point(symbols, coords, basis, thresh, frozen, max_memory, out, tag):
    from pyscf.lno import LNOCCSD, LNOCCSD_T
    thresh = {"t0": "tight", "t1": "normal", "t2": "tight", "t3": "normal"}[TIER]; triples = TIER in ("t0", "t1")
    rec = {"tag": tag, "stages_s": {}, "rss_gb": {}}
    t = time.time(); mol = make_mol(symbols, coords, basis, max_memory); mf = run_scf(mol); rec["stages_s"]["scf"] = round(time.time() - t, 1); rec["rss_gb"]["scf"] = round(rss_gb(), 2)
    nocc = int(np.count_nonzero(mf.mo_occ)); C_act = mf.mo_coeff[:, frozen:nocc]
    t = time.time(); lo_c = pm_localise(mol, C_act); rec["stages_s"]["pm"] = round(time.time() - t, 1)
    frag_lolist = [[i] for i in range(lo_c.shape[1])]
    t = time.time(); mcc = (LNOCCSD_T if triples else LNOCCSD)(mf, lo_c, frag_lolist, frozen=frozen); mcc.lno_thresh = THRESH[thresh]; mcc.verbose = 3; mcc.kernel()
    rec["stages_s"]["lno_ccsd_t"] = round(time.time() - t, 1); rec["rss_gb"]["lno_ccsd_t"] = round(rss_gb(), 2)
    t = time.time(); emp2 = full_mp2(mf, frozen); rec["stages_s"]["mp2"] = round(time.time() - t, 1)
    ecc, ept2 = float(mcc.e_corr_ccsd_t if triples else mcc.e_corr_ccsd), float(mcc.e_corr_pt2)
    rec.update(tier=TIER, thresh=thresh, triples=triples, n_fragments=len(frag_lolist), e_scf=float(mf.e_tot), e_corr_lno_ccsd_t=ecc, e_corr_lno_mp2=ept2, e_corr_mp2_full=emp2,
               e_tot_composite=float(mf.e_tot) + ecc - ept2 + emp2, wall_s=round(sum(rec["stages_s"].values()), 1))
    log(f"{tag}: SCF {rec['stages_s']['scf']} s, PM {rec['stages_s']['pm']} s, LNO-CCSD(T) {rec['stages_s']['lno_ccsd_t']} s ({len(frag_lolist)} fragments), MP2 {rec['stages_s']['mp2']} s; "
        f"peak RSS {rec['rss_gb']['lno_ccsd_t']} GB; E_composite {rec['e_tot_composite']:.8f}", out)
    return rec


def neighbourhood_mode(H, masses_amu, near):
    """B3LYP normal modes (mass-weighted, projected Hessian): index of the vibrational mode with the largest amplitude on `near`, plus L, omega, Minv."""
    m = np.repeat(np.asarray(masses_amu) * AMU2AU, 3); Minv = 1 / np.sqrt(m)
    w, L = np.linalg.eigh(H * np.outer(Minv, Minv)); keep = np.argsort(np.abs(w))[6:]; keep = keep[np.argsort(w[keep])]
    idx = np.concatenate([np.arange(3 * a, 3 * a + 3) for a in near])
    amp = [float(np.sum(L[idx, k] ** 2)) for k in keep]
    k = keep[int(np.argmax(amp))]
    return k, L, w, Minv, max(amp)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("moldir"); ap.add_argument("out"); ap.add_argument("--near", default="")
    ap.add_argument("--threads", type=int, default=8); ap.add_argument("--max-memory", type=int, default=16000); ap.add_argument("--thresh", default="tight")
    ap.add_argument("--basis", default="cc-pvdz"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--tier", default="t0", choices=["t0", "t1", "t2", "t3"], help="L2b (25 Sep 2026): t0 LNO-CCSD(T) tight (the anchor), t1 LNO-CCSD(T) normal, t2 LNO-CCSD tight, t3 LNO-CCSD normal")
    a = ap.parse_args()
    global TIER; TIER = a.tier
    from pyscf import lib
    lib.num_threads(a.threads); os.makedirs(a.out, exist_ok=True)
    if a.smoke:
        symbols = ["O", "H", "H"]; coords = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])
        log(f"smoke: water {a.basis} {a.thresh}, {a.threads} threads", a.out)
        rec = point(symbols, coords, a.basis, a.thresh, 1, a.max_memory, a.out, "water")
        json.dump(rec, open(os.path.join(a.out, "smoke_water.json"), "w"), indent=1); log("smoke done", a.out); return
    g = json.load(open(os.path.join(a.moldir, "geometry.json"))); symbols = g["symbols"]; coords0 = np.asarray(g["coords_bohr"], float)
    H = np.load(os.path.join(a.moldir, "hessian_b3lyp.npz"))["H_projected"]
    near = [int(t) for t in a.near.split(",") if t]
    frozen = sum(1 for s in symbols if s.upper() != "H")
    k, L, w, Minv, amp = neighbourhood_mode(H, g["masses_amu"], near)
    omega_cm = np.sqrt(abs(w[k])) * HARTREE2CM; k_b3lyp = float(w[k])   # curvature in mass-weighted, dimensionless-q units: E = ½ ω q² (au) → k = ω² … ω in au
    log(f"L2: {os.path.basename(a.moldir.rstrip('/'))} {a.basis} {a.thresh}, {len(symbols)} atoms, frozen core {frozen}, {a.threads} threads, max_memory {a.max_memory} MB; "
        f"neighbourhood atoms {near}; mode {k} ({omega_cm:.0f} cm⁻¹, neighbourhood amplitude {amp:.2f})", a.out)
    recs = []; res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "molecule": os.path.basename(a.moldir.rstrip("/")), "basis": a.basis, "thresh": a.thresh,
                      "threads": a.threads, "max_memory_mb": a.max_memory, "frozen": frozen, "near": near, "mode": int(k), "omega_b3lyp_cm": float(omega_cm), "points": recs}
    for q in (0.0, 1.0, -1.0):
        omega_au = omega_from_eigenvalue(w[k]); x = reduced_displacement(coords0, L[:, k], omega_au, Minv, q)   # 25 Sep 2026: ÷sqrt(ω), not ÷ω; checked
        if q != 0.0: harmonic_check(H, coords0, x, omega_au, q)
        recs.append(dict(point(symbols, x, a.basis, a.thresh, frozen, a.max_memory, a.out, f"q{q:+.1f}"), q=q))
        json.dump(res, open(os.path.join(a.out, "l2_price.json"), "w"), indent=1)
    E = {r["q"]: r["e_tot_composite"] for r in recs}
    # even part at q = ±1: E(q) − E(0) ≈ ½ k_cc q² in the anchor's units where B3LYP gives ½ ω q² with ω in au → ratio k_cc/k_b3lyp = (E(1)+E(−1)−2E(0)) / ω
    kcc = (E[1.0] + E[-1.0] - 2 * E[0.0]); ratio = kcc / np.sqrt(abs(w[k]))
    res["curvature_ratio_cc_over_b3lyp"] = float(ratio); res["omega_prime_cm"] = float(omega_cm * np.sqrt(abs(ratio)))
    res["price_lno_ccsd_t_s_mean"] = float(np.mean([r["stages_s"]["lno_ccsd_t"] for r in recs])); res["price_point_s_mean"] = float(np.mean([r["wall_s"] for r in recs]))
    P = res["price_point_s_mean"] / 60
    res["verdict"] = "PASS" if P <= 30 else ("FAIL" if P > 120 else "BETWEEN")
    json.dump(res, open(os.path.join(a.out, "l2_price.json"), "w"), indent=1)
    log(f"sanity: ω′ along mode {k} = {res['omega_prime_cm']:.0f} cm⁻¹ vs B3LYP {omega_cm:.0f} (curvature ratio {ratio:.3f})", a.out)
    log(f"PRICE: {P:.1f} min per point ({res['price_lno_ccsd_t_s_mean']/60:.1f} min of it LNO-CCSD(T)) at {a.threads} threads → {res['verdict']}", a.out)
    log("L2 finished", a.out)


if __name__ == "__main__":
    main()
