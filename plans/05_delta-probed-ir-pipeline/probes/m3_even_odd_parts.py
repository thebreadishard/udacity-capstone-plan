"""Even and odd parts of the sealed M1/M3 energies per mode, in µE_h — differences only, no absolute energy is printed.

For each mode m and amplitude |q| present on both sides:
    even(q) = ½[E(+q) + E(−q)] − E(0)      the quadratic response the deck uses
    odd(q)  = ½[E(+q) − E(−q)]             the force term Δ₁·p; zero for an irrep-pure non-totally-symmetric pattern
                                           at a symmetric equilibrium (ledger I14 / decision 37 prerequisite)
printed for the SCF energy, the LNO-CCSD(T) correlation energy, the full-MP2 correlation energy and the composite
(SCF + LNO-CCSD(T) − LNO-MP2 + full MP2) of arm A, plus the even-part curvature fit  even(q) ≈ ½ k q² + ¼ c₄ q⁴.

Usage:  python m3_even_odd_parts.py results_m1/naphthalene_cc-pvdz_tight_m3 [more dirs...]
Written 2026-09-15 (the 02:52 reading of mode 12 was done by hand; this makes it reproducible for every mode).
"""
import json
import os
import sys

import numpy as np

KEYS = [("e_scf", "SCF"), ("e_corr_lno_ccsd_t", "LNO-CCSD(T) corr"), ("e_corr_mp2_full", "MP2 corr"),
        ("e_tot_composite", "composite")]


def read(d):
    s = json.load(open(os.path.join(d, "m1_sealed_energies.json")))
    rows = json.load(open(os.path.join(d, "m1_rows.json")))["rows"] if os.path.exists(os.path.join(d, "m1_rows.json")) else []
    fam = {r["mode"]: (r["family"], r["freq_cm"]) for r in rows}
    pts = {}
    for p in s["points"]:
        pts.setdefault(p["mode"], {})[round(p["q"], 6)] = p["A"]
    return s["reference"]["A"], pts, fam


def main():
    for d in sys.argv[1:]:
        ref, pts, fam = read(d)
        print(f"# {d}\n")
        for m in sorted(pts):
            P = pts[m]
            e0 = P.get(0.0, ref)   # q = 0 of the run if visited, else the reference arm A
            qs = sorted({abs(q) for q in P if q != 0 and -q in P})
            f, nu = fam.get(m, ("?", float("nan")))
            print(f"## mode {m} ({f}, {nu:.1f} cm⁻¹): |q| with both signs = {qs}; "
                  f"q = 0 {'visited' if 0.0 in P else 'from the reference arm A'}\n")
            if not qs:   # 2026-09-19: a mode still running (no ± pair yet) is reported, not a crash
                print(f"(no ± pair yet: {len(P)} point(s) sealed at q = {sorted(P)})\n")
                continue
            print("| quantity | " + " | ".join(f"even({q:g})" for q in qs) + " | " + " | ".join(f"odd({q:g})" for q in qs)
                  + " | k (µE_h/q²) | c₄ (µE_h/q⁴) |")
            print("|---|" + "---|" * (2 * len(qs) + 2))
            for key, name in KEYS:
                ev = [0.5 * (P[q][key] + P[-q][key]) - e0[key] for q in qs]
                od = [0.5 * (P[q][key] - P[-q][key]) for q in qs]
                ev_u, od_u = [x * 1e6 for x in ev], [x * 1e6 for x in od]
                if len(qs) >= 2:
                    A = np.array([[0.5 * q ** 2, 0.25 * q ** 4] for q in qs])
                    k, c4 = np.linalg.lstsq(A, np.array(ev_u), rcond=None)[0]
                    fit = f"{k:+.1f} | {c4:+.1f}"
                else:
                    fit = f"{2 * ev_u[0] / qs[0] ** 2:+.1f} | —"
                print(f"| {name} | " + " | ".join(f"{x:+.2f}" for x in ev_u) + " | " + " | ".join(f"{x:+.3f}" for x in od_u)
                      + f" | {fit} |")
            print()
        missing = [m for m in pts if not any(q != 0 and -q in pts[m] for q in pts[m])]
        if missing:
            print(f"(modes without a ± pair yet: {missing})\n")


if __name__ == "__main__":
    main()
