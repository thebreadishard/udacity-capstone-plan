"""Decision 45, option B — the noise floor σ of the tight cc-pVTZ labels read from the anchor's own points (27 September 2026, after the
densification of mode 12 to nine points q = 0, ±0.25, ±0.5, ±0.75, ±1).

Two witnesses, both differences of sealed energies (no absolute energy is printed):
  even part  even(q) = ½[E(+q) + E(−q)] − E(0) fitted as ½ k q² + ¼ c₄ q⁴ (the deck's model of a response); with four amplitudes the fit leaves
             two degrees of freedom and the residual RMS is σ_even; a q⁶ term is fitted beside it to show how much of the residual is truncation;
  odd part   odd(q) = ½[E(+q) − E(−q)] fitted as g q + h q³ (a force term plus its cubic); its residual is σ_odd, independent of the even fit.
Per energy: σ_E ≈ σ_part × √2 (each part is half a sum or difference of two independent energies; E(0) is common to all even values and cancels
in the fit's residual only partly, so σ_even is quoted as is and the √2 conversion is marked approximate).
Modes with two amplitudes (22, 31) determine (k, c₄) and (g, h) exactly and leave no residual: they give no σ, as decision 45 foresaw for the
in-plane families ("at the coarser spacing, and the error budget says so"); their odd-to-even ratios are printed as a plausibility line.

Usage:  python m1_noise_option_b.py results_m1/naphthalene_cc-pvtz_tight_m3 [out.md]"""
import os
import sys
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from m3_even_odd_parts import KEYS, read  # noqa: E402


def fit(A, y):
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ coef
    dof = len(y) - A.shape[1]
    sigma = float(np.sqrt((res ** 2).sum() / dof)) if dof > 0 else None
    return coef, res, dof, sigma


def main() -> int:
    d = sys.argv[1]
    ref, pts, fam = read(d)
    L = [f"# Decision 45, option B — noise floor of the tight cc-pVTZ labels from the anchor's points ({d}), µE_h; printed {datetime.now():%Y-%m-%d %H:%M} "
         f"by probes/m1_noise_option_b.py", ""]
    summary = {}
    for m in sorted(pts):
        P = pts[m]
        e0 = P.get(0.0, ref)
        qs = np.array(sorted({abs(q) for q in P if q != 0 and -q in P}))
        f, nu = fam.get(m, ("?", float("nan")))
        L += [f"## mode {m} ({f}, {nu:.1f} cm⁻¹): amplitudes {qs.tolist()} ({2 * len(qs) + 1} points)", ""]
        if len(qs) < 3:
            L += ["Two amplitudes: (k, c₄) and (g, h) are determined exactly, no residual, no σ (decision 45: the in-plane families keep the coarser spacing).", ""]
            L += ["| quantity | k | c₄ | g | h | max |odd| / even(1) |", "|---|---|---|---|---|---|"]
            for key, name in KEYS:
                ev = np.array([0.5 * (P[q][key] + P[-q][key]) - e0[key] for q in qs]) * 1e6
                od = np.array([0.5 * (P[q][key] - P[-q][key]) for q in qs]) * 1e6
                (k, c4), *_ = fit(np.array([[0.5 * q ** 2, 0.25 * q ** 4] for q in qs]), ev)
                (g, h), *_ = fit(np.array([[q, q ** 3] for q in qs]), od)
                L.append(f"| {name} | {k:+.1f} | {c4:+.1f} | {g:+.3f} | {h:+.3f} | {np.abs(od).max() / abs(ev[-1]):.1e} |")
            L.append("")
            continue
        L += ["| quantity | k | c₄ | even residuals (µE_h) | σ_even (dof) | with q⁶: σ (dof) | g | h | odd residuals (µE_h) | σ_odd (dof) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for key, name in KEYS:
            ev = np.array([0.5 * (P[q][key] + P[-q][key]) - e0[key] for q in qs]) * 1e6
            od = np.array([0.5 * (P[q][key] - P[-q][key]) for q in qs]) * 1e6
            (k, c4), res_e, dof_e, s_e = fit(np.array([[0.5 * q ** 2, 0.25 * q ** 4] for q in qs]), ev)
            _c6, _r6, dof_6, s_6 = fit(np.array([[0.5 * q ** 2, 0.25 * q ** 4, q ** 6] for q in qs]), ev)
            (g, h), res_o, dof_o, s_o = fit(np.array([[q, q ** 3] for q in qs]), od)
            L.append(f"| {name} | {k:+.1f} | {c4:+.1f} | {', '.join(f'{r:+.2f}' for r in res_e)} | {s_e:.2f} ({dof_e}) | "
                     f"{(f'{s_6:.2f} ({dof_6})') if s_6 is not None else '—'} | {g:+.3f} | {h:+.3f} | {', '.join(f'{r:+.3f}' for r in res_o)} | {s_o:.3f} ({dof_o}) |")
            if key == "e_tot_composite":
                summary[m] = dict(sigma_even=s_e, sigma_odd=s_o, k=k, c4=c4, even_1=float(ev[-1]))
        L.append("")
    for m, s in summary.items():
        L += [f"**Reading, mode {m}, composite:** σ_even {s['sigma_even']:.2f} µE_h (2 dof), σ_odd {s['sigma_odd']:.3f} µE_h (2 dof) → per energy ≈ "
              f"{s['sigma_even'] * np.sqrt(2):.2f} / {s['sigma_odd'] * np.sqrt(2):.2f} µE_h (× √2, approximate); against the response even(1) = {s['even_1']:+.0f} µE_h "
              f"that is {s['sigma_even'] * np.sqrt(2) / abs(s['even_1']):.1e} / {s['sigma_odd'] * np.sqrt(2) / abs(s['even_1']):.1e} relative. "
              f"The even-part residual still contains the q⁶ truncation of the two-term model (see the q⁶ column); the odd-part σ is the cleaner noise witness.", ""]
    text = "\n".join(L)
    print(text)
    if len(sys.argv) > 2:
        open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
