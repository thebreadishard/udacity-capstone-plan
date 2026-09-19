"""X19a — does an IP-tuned range-separated hybrid shrink the coupled-cluster correction? (pre-registered 16 Sep 2026;
script 19 Sep 2026; runs on the Hetzner machine, never beside the anchor run)

Truth: the sealed canonical CCSD(T)/cc-pVTZ scan of benzene along the three M1 probe modes (6 CH-oop 865, 12 CH-ip-bend
1020, 18 CC-stretch 1357; q = −1 … +1 in steps of 0.25; `canonical_truth_sealed.json`), fitted per mode as an even
degree-4 polynomial in q: E = E0 + a2 q² + a4 q⁴. With the M1 convention (x = x0 + (L v/√ω) M^{-1/2}, v = q e_m) the
first-order frequency shift of a functional against the truth is Δω = (a2_CC − a2_func) × 219474.63 cm⁻¹ — the same
quantity M1's CANONICAL_COMPARISON tables print for the arms (“frequency bias Δω = a2”).

Baselines, same 27 geometries, cc-pVTZ, DF, grid (99, 590), psi4 1.11: (i) B3LYP; (ii) LRC-ωPBEh at psi4's default
ω = 0.2 bohr⁻¹; (iii) LRC-ωPBEh at ω* tuned on benzene by the ionisation-potential condition
J(ω) = ε_HOMO(N; ω) + [E(N−1; ω) − E(N; ω)] = 0 (neutral RKS singlet, cation UKS doublet, same geometry, same basis):
ω scanned 0.10 … 0.50 in steps of 0.05, then 0.01 inside the bracketing interval; ω* = the 0.01 grid point with the
smallest |J|.

Reading (fixed 16 Sep): WIN if RMS over the three modes of Δω(tuned) ≤ 0.5 × RMS Δω(B3LYP) with no sign flip on any
mode; LOSE if ≥ 0.8 × or a sign flip; between: inconclusive (X19b runs anyway).

Resumable: every energy is cached in <out>_cache.json keyed by (functional, ω, state, mode, q).
Usage: python x19_tuned_functional.py --stagea stageA_hessians.npz --stagea-json stageA.json
                                      --truth canonical_truth_sealed.json --out x19_tuned_functional [--threads 16]
                                      [--memory-gb 24] [--smoke]
"""
import argparse
import json
import os
import time
from datetime import datetime

import numpy as np

HARTREE2CM = 219474.6313705
MODES = [6, 12, 18]
QS = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
OMEGA_COARSE = [round(0.10 + 0.05 * i, 2) for i in range(9)]      # 0.10 … 0.50


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def fit_a2(qs, es):
    """Even degree-4 fit E = E0 + a2 q² + a4 q⁴ (odd terms included so the even part is unbiased); returns a2, a4, σ."""
    qs = np.asarray(qs, float); es = np.asarray(es, float) - np.mean(es)
    A = np.stack([np.ones_like(qs), qs, qs ** 2, qs ** 3, qs ** 4], 1)
    c, *_ = np.linalg.lstsq(A, es, rcond=None)
    resid = es - A @ c
    return float(c[2]), float(c[4]), float(np.std(resid))


class Engine:
    def __init__(self, symbols, coords0, basis, threads, memory_gb, outfile, smoke=False):
        import psi4
        self.psi4 = psi4
        psi4.set_memory(f"{memory_gb} GB"); psi4.set_num_threads(threads)
        psi4.core.set_output_file(outfile, False)
        self.symbols, self.coords0, self.basis, self.smoke = symbols, np.asarray(coords0), basis, smoke
        self.base_opts = {"basis": basis, "scf_type": "df", "e_convergence": 1e-10, "d_convergence": 1e-10,
                          "dft_radial_points": 75 if smoke else 99, "dft_spherical_points": 302 if smoke else 590,
                          "maxiter": 200}

    def mol(self, coords, charge=0, mult=1):
        geom = "\n".join(f"{s} {x:.10f} {y:.10f} {z:.10f}" for s, (x, y, z) in zip(self.symbols, coords))
        return self.psi4.geometry(f"{charge} {mult}\n{geom}\nunits bohr\nsymmetry c1\nno_reorient\nno_com\n")

    def energy(self, func, omega, coords, charge=0, mult=1, want_homo=False):
        p = self.psi4
        p.core.clean(); p.core.clean_options()
        opts = dict(self.base_opts); opts["reference"] = "uks" if mult != 1 else "rks"
        if omega is not None:
            opts["dft_omega"] = float(omega)
        p.set_options(opts)
        m = self.mol(coords, charge, mult)
        e, wfn = p.energy(func, molecule=m, return_wfn=True)
        homo = None
        if want_homo:
            eps = np.asarray(wfn.epsilon_a()); nocc = wfn.nalpha()
            homo = float(np.sort(eps)[nocc - 1])
        return float(e), homo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stagea", required=True); ap.add_argument("--stagea-json", required=True)
    ap.add_argument("--truth", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=16); ap.add_argument("--memory-gb", type=int, default=24)
    ap.add_argument("--basis", default="cc-pvtz"); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()

    z = np.load(a.stagea); sj = json.load(open(a.stagea_json))
    L, omega_au, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    symbols = sj["symbols"]
    modes, qs = (MODES, QS) if not a.smoke else ([MODES[0]], [-0.5, 0.0, 0.5])
    basis = a.basis if not a.smoke else "6-31g"
    omegas = OMEGA_COARSE if not a.smoke else [0.3, 0.4]

    def geometry(m, q):
        v = np.zeros(len(omega_au)); v[m] = q
        return coords0 + ((L @ (v / np.sqrt(omega_au))) * Minv).reshape(-1, 3)

    # truth: a2 per mode from the sealed canonical scan (total energy = e_scf + e_corr_ccsd_t)
    truth = json.load(open(a.truth))["points"]
    a2_cc = {}
    for m in modes:
        pts = sorted([p for p in truth if p["mode"] == m], key=lambda p: p["q"])
        if len(pts) >= 5:
            a2, a4, sig = fit_a2([p["q"] for p in pts], [p["e_scf"] + p["e_corr_ccsd_t"] for p in pts])
            a2_cc[m] = {"a2": a2, "a4": a4, "sigma": sig, "n": len(pts)}
        else:
            a2_cc[m] = {"a2": 0.0, "a4": 0.0, "sigma": 0.0, "n": len(pts), "note": "no canonical points (smoke)"}
    log("truth a2 (E_h): " + ", ".join(f"mode {m} {a2_cc[m]['a2']:.6e} (σ {a2_cc[m]['sigma']*1e6:.3f} µE_h, n {a2_cc[m]['n']})" for m in modes))

    cache_path = a.out + "_cache.json"
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}

    def save():
        tmp = cache_path + ".tmp"; json.dump(cache, open(tmp, "w"), indent=0); os.replace(tmp, cache_path)

    eng = Engine(symbols, coords0, basis, a.threads, a.memory_gb, a.out + "_psi4.out", smoke=a.smoke)

    def cached_energy(func, omega, state, m, q, charge=0, mult=1, want_homo=False):
        key = f"{func}|{omega}|{state}|{m}|{q}"
        if key in cache and (not want_homo or cache[key].get("homo") is not None):
            return cache[key]["e"], cache[key].get("homo")
        t = time.time()
        e, homo = eng.energy(func, omega, geometry(m, q), charge, mult, want_homo)
        cache[key] = {"e": e, "homo": homo, "wall_s": round(time.time() - t, 1)}; save()
        log(f"{func} ω={omega} {state} mode {m} q={q:+.2f}: E={e:.10f}" + (f" ε_HOMO={homo:.6f}" if homo is not None else "") + f" ({cache[key]['wall_s']} s)")
        return e, homo

    # ---- stage 1: ω tuning at the reference geometry (mode 0, q 0 is the same geometry for every mode)
    def J(omega):
        eN, homo = cached_energy("lrc-wpbeh", omega, "N", modes[0], 0.0, 0, 1, want_homo=True)
        eC, _ = cached_energy("lrc-wpbeh", omega, "cation", modes[0], 0.0, 1, 2)
        return homo + (eC - eN), eN, eC, homo

    scan = {}
    for w in omegas:
        scan[w] = J(w)[0]; log(f"J(ω={w}) = {scan[w]:+.6f} E_h")
    ws = sorted(scan)
    bracket = None
    for w1, w2 in zip(ws, ws[1:]):
        if np.sign(scan[w1]) != np.sign(scan[w2]):
            bracket = (w1, w2); break
    fine = {}
    if bracket and not a.smoke:
        for w in np.round(np.arange(bracket[0], bracket[1] + 1e-9, 0.01), 2):
            fine[float(w)] = J(float(w))[0]
    allJ = {**scan, **fine}
    omega_star = min(allJ, key=lambda w: abs(allJ[w]))
    log(f"ω* = {omega_star} (|J| = {abs(allJ[omega_star]):.6f} E_h; bracket {bracket})")

    # ---- stage 2: the three functionals along the three modes
    funcs = [("b3lyp", None, "B3LYP"), ("lrc-wpbeh", 0.2, "LRC-ωPBEh ω=0.2 (default)"), ("lrc-wpbeh", omega_star, f"LRC-ωPBEh ω*={omega_star}")]
    table = {}
    for func, w, label in funcs:
        table[label] = {}
        for m in modes:
            es = [cached_energy(func, w, "scan", m, q)[0] for q in qs]
            a2, a4, sig = fit_a2(qs, es)
            dw = (a2_cc[m]["a2"] - a2) * HARTREE2CM
            table[label][m] = {"a2": a2, "a4": a4, "sigma_uEh": sig * 1e6, "delta_omega_cm": dw}
            log(f"{label:28s} mode {m}: a2 {a2:.6e}  Δω = {dw:+.2f} cm⁻¹  (fit σ {sig*1e6:.3f} µE_h)")

    def rms(label):
        return float(np.sqrt(np.mean([table[label][m]["delta_omega_cm"] ** 2 for m in modes])))

    r_b3, r_def, r_tun = rms(funcs[0][2]), rms(funcs[1][2]), rms(funcs[2][2])
    flips = [m for m in modes if np.sign(table[funcs[2][2]][m]["delta_omega_cm"]) != np.sign(table[funcs[0][2]][m]["delta_omega_cm"])
             and abs(table[funcs[0][2]][m]["delta_omega_cm"]) > 0.5]
    ratio = r_tun / r_b3 if r_b3 > 0 else float("nan")
    verdict = "WIN" if (ratio <= 0.5 and not flips) else ("LOSE" if (ratio >= 0.8 or flips) else "INCONCLUSIVE")
    if a.smoke:
        verdict = "SMOKE (no truth; code path only)"
    log(f"RMS Δω: B3LYP {r_b3:.2f}, LRC-ωPBEh default {r_def:.2f}, tuned {r_tun:.2f} cm⁻¹; ratio tuned/B3LYP {ratio:.2f}; sign flips {flips} → {verdict}")

    out = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "basis": basis, "modes": modes, "qs": qs, "truth_a2": a2_cc,
           "omega_scan_J": {str(k): v for k, v in allJ.items()}, "omega_star": omega_star, "bracket": bracket,
           "table": {lab: {str(m): v for m, v in d.items()} for lab, d in table.items()},
           "rms_delta_omega_cm": {"B3LYP": r_b3, "LRC-wPBEh_default": r_def, "LRC-wPBEh_tuned": r_tun},
           "ratio_tuned_over_b3lyp": ratio, "sign_flips": flips, "verdict": verdict, "smoke": a.smoke,
           "threads": a.threads, "grid": [eng.base_opts["dft_radial_points"], eng.base_opts["dft_spherical_points"]]}
    json.dump(out, open(a.out + ".json", "w"), indent=1)
    md = [f"# X19a — IP-tuned LRC-ωPBEh against B3LYP on benzene's three probe modes, truth canonical CCSD(T)/{basis} ({out['date']})", "",
          f"ω* = {omega_star} bohr⁻¹ (J bracket {bracket}); grid {out['grid']}; {a.threads} threads.", "",
          "| functional | " + " | ".join(f"mode {m} Δω (cm⁻¹)" for m in modes) + " | RMS |", "|---|" + "---|" * (len(modes) + 1)]
    for func, w, label in funcs:
        md.append(f"| {label} | " + " | ".join(f"{table[label][m]['delta_omega_cm']:+.2f}" for m in modes) + f" | {rms(label):.2f} |")
    md += ["", f"Ratio tuned/B3LYP = {ratio:.2f}; sign flips: {flips or 'none'}; **{verdict}** (pre-registered: WIN ≤ 0.5 without flip, LOSE ≥ 0.8 or flip)."]
    open(a.out + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    log("wrote " + a.out + ".json/.md")


if __name__ == "__main__":
    main()
