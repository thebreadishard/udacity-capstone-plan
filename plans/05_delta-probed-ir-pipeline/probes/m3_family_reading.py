"""M3 (probe B1) per-family reading of the anchor's sealed energies, DZ against TZ (23 September 2026; the 20 September reading of mode 12
was assembled by hand from m3_even_odd_parts.py — this makes every family's table reproducible).

For one mode present in both the cc-pVDZ and the cc-pVTZ M3 directories: even-part curvature fit even(q) = ½ k q² + ¼ c₄ q⁴ on |q| = 0.5, 1.0
for SCF, LNO-CCSD(T) correlation, LNO-MP2 correlation, full-MP2 correlation and the composite of arm A; Δk and Δω = ½ Δk × 219474.63/10⁶
cm⁻¹ per µE_h/q²; the pre-registered beyond-MP2 increment in both definitions (k(LNO-CC) − k(LNO-MP2) as the composite carries it; the
mixed form k(LNO-CC) − k(full MP2)); ω′ = ω_B3LYP √(k/k_B3LYP) per method and basis. Prints markdown.

Usage: python m3_family_reading.py <mode> <delta_b cm-1> [--dz results_m1/naphthalene_cc-pvdz_tight_m3] [--tz results_m1/naphthalene_cc-pvtz_tight_m3]
"""
import argparse
import json
from pathlib import Path

import numpy as np

CM_PER_UEH = 219474.6313705 / 1e6      # cm⁻¹ per µE_h (k in µE_h/q² -> Δω = ½ Δk × this)
COMPS = [("e_scf", "SCF"), ("e_corr_lno_ccsd_t", "LNO-CCSD(T) corr"), ("e_corr_lno_mp2", "LNO-MP2 corr"), ("e_corr_mp2_full", "full MP2 corr"),
         ("e_tot_composite", "composite")]


def curvatures(d, mode):
    s = json.load(open(Path(d) / "m1_sealed_energies.json"))
    rows = json.load(open(Path(d) / "m1_rows.json"))["rows"]
    ref = s["reference"]["A"]
    pts = {(p["q"]): p["A"] for p in s["points"] if p["mode"] == mode}
    freq = next(r["freq_cm"] for r in rows if r["mode"] == mode); fam = next(r["family"] for r in rows if r["mode"] == mode)
    out = {}
    for key, _ in COMPS:
        ev = {}
        for q in (0.5, 1.0):
            if q in pts and -q in pts:
                ev[q] = 0.5 * (pts[q][key] + pts[-q][key]) * 1e6 - ref[key] * 1e6
        assert len(ev) == 2, (d, mode, key, sorted(pts))
        # even(q) = ½ k q² + ¼ c₄ q⁴  ->  two equations
        A = np.array([[0.5 * q * q, 0.25 * q ** 4] for q in (0.5, 1.0)]); b = np.array([ev[0.5], ev[1.0]])
        k, c4 = np.linalg.solve(A, b); out[key] = (float(k), float(c4))
    return freq, fam, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", type=int); ap.add_argument("delta_b", type=float, help="benzene's registered beyond-MP2 increment for this family, cm-1")
    ap.add_argument("--dz", default="results_m1/naphthalene_cc-pvdz_tight_m3"); ap.add_argument("--tz", default="results_m1/naphthalene_cc-pvtz_tight_m3")
    a = ap.parse_args()
    freq, fam, dz = curvatures(a.dz, a.mode); _, _, tz = curvatures(a.tz, a.mode)
    k_b3lyp = freq / CM_PER_UEH          # ω = ½ k_B3LYP × CM_PER_UEH × 2 ... k in the same units as the fit: ω[cm⁻¹] = k[µE_h/q²] × CM_PER_UEH
    print(f"# Probe M3 (B1), family read — mode {a.mode}, {fam}, {freq:.1f} cm⁻¹ (B3LYP/6-31G* mode vector; k_B3LYP = {k_b3lyp:.1f} µE_h/q²)\n")
    print("| component | k at cc-pVDZ | c₄ at DZ | k at cc-pVTZ | c₄ at TZ | Δk TZ − DZ | Δω TZ − DZ (cm⁻¹) |\n|---|---|---|---|---|---|---|")
    for key, name in COMPS:
        dk = tz[key][0] - dz[key][0]
        print(f"| {name} | {dz[key][0]:+.1f} | {dz[key][1]:+.1f} | {tz[key][0]:+.1f} | {tz[key][1]:+.1f} | {dk:+.1f} | **{0.5 * dk * CM_PER_UEH:+.1f}** |")
    b1 = {b: (c["e_tot_composite"][0] - c["e_scf"][0] - c["e_corr_mp2_full"][0]) for b, c in (("dz", dz), ("tz", tz))}     # k(LNO-CC) − k(LNO-MP2)
    b1c = {b: (c["e_corr_lno_ccsd_t"][0] - c["e_corr_lno_mp2"][0]) for b, c in (("dz", dz), ("tz", tz))}                      # the same, direct
    b2 = {b: (c["e_corr_lno_ccsd_t"][0] - c["e_corr_mp2_full"][0]) for b, c in (("dz", dz), ("tz", tz))}
    print(f"\n(check: composite − SCF − full MP2 = LNO-CC − LNO-MP2 to {max(abs(b1[b] - b1c[b]) for b in b1):.2f} µE_h/q²)\n")
    print(f"## The pre-registered quantity: beyond-MP2 increment of the curvature, DZ → TZ (benzene Δ_b = {a.delta_b:+.1f} cm⁻¹ for this family)\n")
    print("| definition | DZ | TZ | Δ_n = TZ − DZ | Δ_n − Δ_b | rule (win ≤ 2.5, lose > 5 or sign flip) |\n|---|---|---|---|---|---|")
    for label, bb in (("what the composite carries: k(LNO-CC) − k(LNO-MP2)", b1), ("mixed form of 15 Sep: k(LNO-CC) − k(full MP2)", b2)):
        dn = 0.5 * (bb["tz"] - bb["dz"]) * CM_PER_UEH; diff = dn - a.delta_b
        flip = (dn * a.delta_b) < 0
        verdict = "**WIN**" if (abs(diff) <= 2.5 and not flip) else ("**LOSE**" if (abs(diff) > 5 or flip) else "between (neither win nor lose)")
        print(f"| {label} | {bb['dz']:+.1f} | {bb['tz']:+.1f} | {bb['tz'] - bb['dz']:+.1f} µE_h/q² = **{dn:+.1f} cm⁻¹** | **{abs(diff):.1f} cm⁻¹**{', sign flipped' if flip else ''} | {verdict} |")
    print("\n## The frequency each method would give along this mode, ω′ = ω_B3LYP √(k / k_B3LYP) (cm⁻¹)\n\n| method | cc-pVDZ | cc-pVTZ |\n|---|---|---|")
    for name, f in (("SCF", lambda c: c["e_scf"][0]), ("SCF + full MP2", lambda c: c["e_scf"][0] + c["e_corr_mp2_full"][0]),
                    ("SCF + LNO-CCSD(T)", lambda c: c["e_scf"][0] + c["e_corr_lno_ccsd_t"][0]), ("composite", lambda c: c["e_tot_composite"][0])):
        print(f"| {name} | {freq * np.sqrt(f(dz) / k_b3lyp):.0f} | {freq * np.sqrt(f(tz) / k_b3lyp):.0f} |")
    print(f"\nc₄/k of the LNO-CCSD(T) correlation part: DZ {100 * dz['e_corr_lno_ccsd_t'][1] / abs(dz['e_corr_lno_ccsd_t'][0]):.1f} %, TZ {100 * tz['e_corr_lno_ccsd_t'][1] / abs(tz['e_corr_lno_ccsd_t'][0]):.1f} %.")


if __name__ == "__main__":
    main()
