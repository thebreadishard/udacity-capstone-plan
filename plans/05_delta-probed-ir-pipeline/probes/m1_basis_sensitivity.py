#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decision 26 (P12), input (i): the basis-set sensitivity of the canonical CCSD(T) harmonic curvature
along the three probe-M1 benzene modes, read from the two existing canonical truth lines (cc-pVDZ
and cc-pVTZ, same 27 geometries, same DF-RHF reference, frozen core) and from the full-space DF-MP2
energies stored with the M1 arms at the same points. No new calculation.

For each basis and mode the even part of E(q) is fitted as a0 + a2 q² + a4 q⁴; 2·a2 is the curvature
in that basis (E = ½ ω q² in the dimensionless normal coordinate). Printed: the CHANGE of 2·a2 from
cc-pVDZ to cc-pVTZ per mode, in cm⁻¹, for the total CCSD(T) energy and split into its SCF part, its
CCSD(T) correlation part, the (T) part of that, and — from the arms' files — the full-space MP2
correlation part, so that the share of the correlation basis change that an MP2-level correction
would capture is measured. Absolute curvatures and energies are NOT printed (they would make the
canonical harmonic curvature — and with the DFT Hessian, Δ₂ — readable before the pilot note).

Reading aid: the DZ → TZ step is a measured LOWER bound on the anchor's distance from the basis-set
limit per mode, and its split says which part of a composite anchor (SCF extrapolation, MP2-level
correlation correction) would carry the remaining distance.

Run (Windows or WSL; NumPy only):  python m1_basis_sensitivity.py [--dz benzene_cc-pvdz_tight] [--tz benzene_cc-pvtz_tight]
"""
import argparse, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_m1")
HARTREE_CM = 219474.6313632
FAM = {6: "CH-oop 865", 12: "CH-ip-bend 1020", 18: "CC-stretch 1357"}


def curvature(points, key):
    """2·a2 (in E_h) of the even part of key(point) vs q, plus σ about a degree-4 fit and n."""
    pts = sorted(points, key=lambda p: p["q"])
    q = np.array([p["q"] for p in pts]); e = np.array([key(p) for p in pts])
    qa = np.array(sorted(set(np.round(np.abs(q), 6))))
    ev = np.array([0.5 * (e[np.isclose(q, x)][0] + e[np.isclose(q, -x)][0]) for x in qa])
    A = np.vstack([np.ones_like(qa), qa ** 2, qa ** 4]).T
    c, *_ = np.linalg.lstsq(A, ev, rcond=None)
    res = e - np.polyval(np.polyfit(q, e, 4), q)
    return float(2 * c[1]), float(np.sqrt(np.sum(res ** 2) / max(len(q) - 5, 1))), len(q)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dz", default="benzene_cc-pvdz_tight")
    ap.add_argument("--tz", default="benzene_cc-pvtz_tight")
    a = ap.parse_args()
    truth, arms = {}, {}
    for tag, d in (("dz", a.dz), ("tz", a.tz)):
        truth[tag] = json.load(open(os.path.join(OUT, d, "canonical_truth_sealed.json")))["points"]
        arms[tag] = json.load(open(os.path.join(OUT, d, "m1_sealed_energies.json")))["points"]
    parts = {
        "total CCSD(T)": ("truth", lambda p: p["e_scf"] + p["e_corr_ccsd_t"]),
        "SCF (DF-RHF)": ("truth", lambda p: p["e_scf"]),
        "CCSD(T) correlation": ("truth", lambda p: p["e_corr_ccsd_t"]),
        "of which (T)": ("truth", lambda p: p["e_corr_ccsd_t"] - p["e_corr_ccsd"]),
        "MP2 correlation (full space, from the arms' files)": ("arms", lambda p: p["A"]["e_corr_mp2_full"]),
    }
    lines = ["# Probe M1 — basis-set sensitivity of the canonical curvature, cc-pVDZ → cc-pVTZ (decision 26, input i)",
             "", f"Truth lines `{a.dz}` and `{a.tz}` (same 27 geometries, same DF-RHF reference, frozen core); MP2 from the arms' "
             "files at the same points. Even-part fit a0 + a2 q² + a4 q⁴ per basis; the table gives Δ(2·a2) = TZ − DZ in cm⁻¹. "
             "Absolute curvatures are not printed.",
             "", "| mode | family | " + " | ".join(parts) + " | MP2 share of the correlation change | σ(total) DZ / TZ (µE_h) |",
             "|---|---|" + "---|" * len(parts) + "---|---|"]
    summary = {}
    for m in sorted({p["mode"] for p in truth["tz"]}):
        row, rec = [], {}
        for name, (src, key) in parts.items():
            src_d = truth if src == "truth" else arms
            cd, sd, nd = curvature([p for p in src_d["dz"] if p["mode"] == m], key)
            ct, st, nt = curvature([p for p in src_d["tz"] if p["mode"] == m], key)
            rec[name] = {"delta_cm": (ct - cd) * HARTREE_CM, "n": [nd, nt]}
            if name == "total CCSD(T)":
                rec["sigma_uEh"] = [sd * 1e6, st * 1e6]
            row.append(f"{(ct - cd) * HARTREE_CM:+.1f}")
        share = rec["MP2 correlation (full space, from the arms' files)"]["delta_cm"] / rec["CCSD(T) correlation"]["delta_cm"]
        rec["mp2_share_of_corr_change"] = share
        summary[f"mode{m}"] = rec
        lines.append(f"| {m} | {FAM.get(m, '?')} | " + " | ".join(row) + f" | {share:.2f} | {rec['sigma_uEh'][0]:.3f} / {rec['sigma_uEh'][1]:.3f} |")
    lines += ["", "Reading: the DZ → TZ change is a measured lower bound on the anchor's distance from the basis-set limit per mode "
              "(the first step of a convergent series). The SCF and MP2 columns say how much of it a composite anchor could carry "
              "at negligible cost (SCF extrapolated in a larger basis; an MP2-level correlation correction, as the composite of §3.3 "
              "already does for the LNO truncation). No verdict. Printed by probes/m1_basis_sensitivity.py."]
    txt = "\n".join(lines)
    open(os.path.join(OUT, "BASIS_SENSITIVITY_dz_tz.md"), "w", encoding="utf-8").write(txt)
    json.dump(summary, open(os.path.join(OUT, "basis_sensitivity_dz_tz.json"), "w"), indent=1)
    print(txt)


if __name__ == "__main__":
    main()
