#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decision 20 read-in: arm A at cc-pVTZ, tight [1e-6, 1e-7] versus xtight [1e-7, 1e-8] LNO thresholds, against the same
sealed canonical CCSD(T) truth line (27 benzene points, three modes). Reads the two runs' canonical_comparison*.json
files (written by the M1 chain) and prints one table: per mode, the arm-A smoothness σ and the frequency bias Δω = a2
(cm⁻¹) for the bare LNO energy and for the composite energy, tight and xtight side by side, with the change. Also the
per-point wall time from m1_rows.json. Nothing is recomputed; absolute energies are not read.

Run (Windows or WSL; NumPy/JSON only):  python m1_xtight_readin.py [--tight benzene_cc-pvtz_tight] [--xtight benzene_cc-pvtz_xtight]
Writes results_m1/XTIGHT_READIN.md and xtight_readin.json.
"""
import argparse, json, os
from datetime import datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_m1")
FAM = {6: "CH-oop 865", 12: "CH-ip-bend 1020", 18: "CC-stretch 1357"}


def load(run):
    d = os.path.join(OUT, run)
    comp = {}
    for tag, fn in (("bare", "canonical_comparison.json"), ("composite", "canonical_comparison_composite.json")):
        p = os.path.join(d, fn)
        comp[tag] = json.load(open(p)) if os.path.exists(p) else None
    rows = json.load(open(os.path.join(d, "m1_rows.json")))["rows"] if os.path.exists(os.path.join(d, "m1_rows.json")) else []
    return comp, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tight", default="benzene_cc-pvtz_tight"); ap.add_argument("--xtight", default="benzene_cc-pvtz_xtight")
    a = ap.parse_args()
    T, trows = load(a.tight); X, xrows = load(a.xtight)
    missing = [k for k, v in X.items() if v is None]
    if missing:
        print(f"NOT_READY: xtight comparison files missing: {missing} (the chain writes them after the last point)"); return 1
    lines = [f"# Decision 20 read-in — arm A, cc-pVTZ, tight vs xtight LNO thresholds, against the sealed canonical truth line — {datetime.now():%Y-%m-%d %H:%M}", "",
             f"Runs `{a.tight}` ({len(trows)} arm points) and `{a.xtight}` ({len(xrows)} arm points); same 27 geometries, same DF-RHF reference, frozen core. "
             "Δω = a2 of the even part of E_A − E_canonical (the factor-2 erratum of 2026-09-10 applied: frequency bias = a2, curvature bias = 2·a2). Absolute energies not read.", "",
             "| mode | family | energy | σ tight (µE_h) | σ xtight | Δω tight (cm⁻¹) | Δω xtight | change | a4 tight → xtight (µE_h) |", "|---|---|---|---|---|---|---|---|---|"]
    summary = {}
    for m in (6, 12, 18):
        for tag in ("bare", "composite"):
            kt, kx = T[tag].get(f"mode{m}_A"), X[tag].get(f"mode{m}_A")
            if not kt or not kx:
                lines.append(f"| {m} | {FAM[m]} | {tag} | — | — | — | — | — | — |"); continue
            ch = kx["delta_omega_cm"] - kt["delta_omega_cm"]
            summary[f"mode{m}_{tag}"] = {"sigma_tight_uEh": kt["sigma4_uEh"], "sigma_xtight_uEh": kx["sigma4_uEh"], "dw_tight_cm": kt["delta_omega_cm"], "dw_xtight_cm": kx["delta_omega_cm"], "change_cm": ch, "n_xtight": kx["n"]}
            lines.append(f"| {m} | {FAM[m]} | {tag} | {kt['sigma4_uEh']:.3f} | {kx['sigma4_uEh']:.3f} | {kt['delta_omega_cm']:+.2f} | {kx['delta_omega_cm']:+.2f} | {ch:+.2f} | {kt['a4_uEh']:+.2f} → {kx['a4_uEh']:+.2f} |")
    wt = [r["wall_s"] for r in trows if "wall_s" in r]; wx = [r["wall_s"] for r in xrows if "wall_s" in r]
    if wt and wx:
        lines += ["", f"Wall time per arm-A point: tight median {np.median(wt):.0f} s, xtight median {np.median(wx):.0f} s (×{np.median(wx)/np.median(wt):.1f}); xtight points {len(wx)}."]
        summary["wall_s_median"] = {"tight": float(np.median(wt)), "xtight": float(np.median(wx))}
    comp = [v for k, v in summary.items() if k.endswith("_composite")]
    if comp:
        worst_t = max(abs(v["dw_tight_cm"]) for v in comp); worst_x = max(abs(v["dw_xtight_cm"]) for v in comp)
        lines += ["", f"Composite arm A, largest |Δω| over the three modes: tight {worst_t:.2f} cm⁻¹ → xtight {worst_x:.2f} cm⁻¹. "
                  "Reading for decision 20: if the xtight bias is materially smaller, the residual at tight was LNO truncation; if it is unchanged, the residual sits elsewhere (basis, frozen core, the composite's MP2 term) and tighter thresholds buy nothing at their price. No verdict here; the proposal §3.3 and the M1 note record the numbers."]
        summary["worst_abs_dw_composite_cm"] = {"tight": worst_t, "xtight": worst_x}
    lines += ["", "Printed by probes/m1_xtight_readin.py from the M1 chain's comparison files."]
    txt = "\n".join(lines)
    open(os.path.join(OUT, "XTIGHT_READIN.md"), "w", encoding="utf-8").write(txt); json.dump(summary, open(os.path.join(OUT, "xtight_readin.json"), "w"), indent=1)
    print(txt); return 0


if __name__ == "__main__":
    raise SystemExit(main())
