"""L2b, measurement 1 — accuracy of cheaper correlation tiers on benzene (pre-registered 25 September 2026,
PreRegistration_2026-09-25_L2b_Cheaper_Label_Tier.md). Along the anchor's three probed modes (B3LYP/6-31G* modes 6, 12, 18: C–H out-of-plane,
C–H in-plane bend, C–C stretch), energies at q = ±0.5, ±1 (the anchor's displacement x = x0 + L q/√ω · M^-1/2) and the reference, for:
  T0 LNO-CCSD(T) tight [1e-6,1e-7]   T2 LNO-CCSD tight (same run, e_corr_ccsd)   T1 LNO-CCSD(T) normal [1e-5,1e-6]   T3 LNO-CCSD normal (same run)
  T4' SCF + DF-MP2 only (what the MP2-anchored deck has before its transferred increment)
each as the composite E_SCF + E_corr(tier) − E_LNO-MP2 + E_MP2(full) (for T4': E_SCF + E_MP2). Curvature k from the even part (½ k q² + ¼ c4 q⁴ on
|q| = 0.5, 1), reference k_ref = Lᵀ H_mw L / ω from the canonical CCSD(T)/cc-pVDZ Hessian of E8 at the same geometry; ω′ = ω_B3LYP √(k / ω_B3LYP,au).
Read-out per tier: max |ω′(tier) − ω′(canonical)| over the three modes; wall seconds per energy per tier. Licensed if ≤ 2.5 cm⁻¹ (and the price part passes).

Usage: python l2b_tiers_benzene.py <stageA dir> <e8 hessian npz> <out dir> [--threads 16] [--max-memory 16000] [--basis cc-pvdz] [--smoke]
"""
import argparse
import json
import os
import time
from datetime import datetime

import numpy as np

THRESH = {"tight": [1e-6, 1e-7], "normal": [1e-5, 1e-6]}
HARTREE2CM = 219474.6313705
MODES = [6, 12, 18]


def log(msg, out):
    line = f"[{datetime.now():%H:%M:%S}] {msg}"; print(line, flush=True); open(os.path.join(out, "l2b_benzene.log"), "a", encoding="utf-8").write(line + "\n")


def make_mol(symbols, coords, basis, max_memory):
    from pyscf import gto
    return gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, coords)], unit="Bohr", basis=basis, verbose=0, max_memory=max_memory, symmetry=False)


def scf_pm_mp2(mol, frozen):
    from pyscf import scf, lo, mp
    mf = scf.RHF(mol).density_fit(); mf.conv_tol = 1e-11; mf.kernel(); assert mf.converged
    nocc = int(np.count_nonzero(mf.mo_occ)); mlo = lo.PipekMezey(mol, mf.mo_coeff[:, frozen:nocc]); lo_c = mlo.kernel()
    for _ in range(100):
        lo1, stable = mlo.stability_jacobi(return_status=True)
        if stable: break
        mlo = lo.PipekMezey(mol, lo1); mlo.init_guess = None; lo_c = mlo.kernel()
    m = mp.dfmp2.DFMP2(mf, frozen=frozen) if hasattr(mp, "dfmp2") else mp.MP2(mf, frozen=frozen); m.verbose = 0; m.kernel()
    return mf, lo_c, float(m.e_corr)


def lno_run(mf, lo_c, frozen, thresh):
    from pyscf.lno import LNOCCSD_T
    t = time.time(); mcc = LNOCCSD_T(mf, lo_c, [[i] for i in range(lo_c.shape[1])], frozen=frozen); mcc.lno_thresh = THRESH[thresh]; mcc.verbose = 2; mcc.kernel()
    return dict(e_ccsd_t=float(mcc.e_corr_ccsd_t), e_ccsd=float(mcc.e_corr_ccsd), e_pt2=float(mcc.e_corr_pt2), seconds=round(time.time() - t, 1))


def energies(symbols, coords, basis, frozen, max_memory):
    """Composite energies of all tiers at one geometry, with wall seconds per tier."""
    t = time.time(); mol = make_mol(symbols, coords, basis, max_memory); mf, lo_c, emp2 = scf_pm_mp2(mol, frozen); t_base = round(time.time() - t, 1)
    tight = lno_run(mf, lo_c, frozen, "tight"); normal = lno_run(mf, lo_c, frozen, "normal"); e0 = float(mf.e_tot)
    return {"T0 LNO-CCSD(T) tight": e0 + tight["e_ccsd_t"] - tight["e_pt2"] + emp2, "T2 LNO-CCSD tight": e0 + tight["e_ccsd"] - tight["e_pt2"] + emp2,
            "T1 LNO-CCSD(T) normal": e0 + normal["e_ccsd_t"] - normal["e_pt2"] + emp2, "T3 LNO-CCSD normal": e0 + normal["e_ccsd"] - normal["e_pt2"] + emp2,
            "T4' SCF + MP2": e0 + emp2}, {"scf_pm_mp2": t_base, "lno_tight": tight["seconds"], "lno_normal": normal["seconds"]}


def even_k(E, E0):
    """k, c4 from even(q) = ½ k q² + ¼ c4 q⁴ at |q| = 0.5, 1 (µE_h units not needed: keep hartree/q²)."""
    ev = {q: 0.5 * (E[q] + E[-q]) - E0 for q in (0.5, 1.0)}
    A = np.array([[0.5 * q * q, 0.25 * q ** 4] for q in (0.5, 1.0)]); k, c4 = np.linalg.solve(A, np.array([ev[0.5], ev[1.0]])); return float(k), float(c4)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("stagea"); ap.add_argument("e8npz"); ap.add_argument("out"); ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--max-memory", type=int, default=16000); ap.add_argument("--basis", default="cc-pvdz"); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    from pyscf import lib
    lib.num_threads(a.threads); os.makedirs(a.out, exist_ok=True)
    if a.smoke:
        sym = ["O", "H", "H"]; x = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])
        E, sec = energies(sym, x, a.basis, 1, a.max_memory); log(f"smoke water: {json.dumps({k: round(v, 6) for k, v in E.items()})} | seconds {sec}", a.out); log("smoke done", a.out); return
    A = json.load(open(os.path.join(a.stagea, "stageA.json"))); z = np.load(os.path.join(a.stagea, "stageA_hessians.npz")); h8 = np.load(a.e8npz)
    sym, x0, L, w, Minv = A["symbols"], np.asarray(z["coords"]), z["L"], z["omega_au"], z["Minv"]
    assert np.max(np.abs(np.asarray(h8["coords_bohr"]) - x0)) < 1e-6, "E8 Hessian is not at the stage-A geometry"
    frozen = sum(1 for s in sym if s.upper() != "H"); Hmw = np.asarray(h8["H_projected"]) * np.outer(Minv, Minv)
    log(f"L2b benzene: {a.basis}, frozen core {frozen}, modes {MODES} ({[round(A['freq_low_cm'][k]) for k in MODES]} cm⁻¹), {a.threads} threads", a.out)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "basis": a.basis, "threads": a.threads, "modes": {}, "seconds": {}}
    E_ref, sec = energies(sym, x0, a.basis, frozen, a.max_memory); res["reference"] = E_ref; res["seconds"]["reference"] = sec
    log(f"reference: {json.dumps({k: round(v, 8) for k, v in E_ref.items()})} | seconds {sec}", a.out)
    for k in MODES:
        omega_cm = float(A["freq_low_cm"][k]); k_can = float(L[:, k] @ Hmw @ L[:, k] / w[k]); k_b3 = float(w[k])
        pts = {}
        for q in (-1.0, -0.5, 0.5, 1.0):
            x = x0 + ((L[:, k] * q / np.sqrt(w[k])) * Minv).reshape(-1, 3)
            E, sec = energies(sym, x, a.basis, frozen, a.max_memory); pts[q] = E; res["seconds"][f"mode{k}_q{q:+.1f}"] = sec
            log(f"mode {k} q={q:+.1f}: T0 {E['T0 LNO-CCSD(T) tight']:.8f} | seconds {sec}", a.out)
        row = {"omega_b3lyp_cm": omega_cm, "family": A["families"][k], "k_b3lyp_au": k_b3, "k_canonical_ccsd_t": k_can, "omega_prime_canonical": omega_cm * np.sqrt(abs(k_can / k_b3)), "tiers": {}}
        for tier in E_ref:
            kt, c4 = even_k({q: pts[q][tier] for q in pts}, E_ref[tier]); op = omega_cm * np.sqrt(abs(kt / k_b3))
            row["tiers"][tier] = {"k": kt, "c4": c4, "omega_prime": op, "d_omega_prime_vs_canonical": op - row["omega_prime_canonical"]}
        res["modes"][str(k)] = row
        log(f"mode {k} ({row['family']}, {omega_cm:.0f}): canonical ω′ {row['omega_prime_canonical']:.1f} | " + " | ".join(f"{t.split()[0]} {v['omega_prime']:.1f} ({v['d_omega_prime_vs_canonical']:+.1f})" for t, v in row["tiers"].items()), a.out)
        json.dump(res, open(os.path.join(a.out, "l2b_benzene.json"), "w"), indent=1)
    res["max_abs_d_omega_prime"] = {tier: max(abs(res["modes"][str(k)]["tiers"][tier]["d_omega_prime_vs_canonical"]) for k in MODES) for tier in E_ref}
    res["licensed_accuracy"] = {tier: bool(v <= 2.5) for tier, v in res["max_abs_d_omega_prime"].items()}
    json.dump(res, open(os.path.join(a.out, "l2b_benzene.json"), "w"), indent=1)
    log("ACCURACY: " + " | ".join(f"{t}: max |Δω′| {v:.1f} cm⁻¹ {'≤ 2.5 ✓' if v <= 2.5 else '> 2.5'}" for t, v in res["max_abs_d_omega_prime"].items()), a.out)
    log("L2b benzene finished", a.out)


if __name__ == "__main__":
    main()
