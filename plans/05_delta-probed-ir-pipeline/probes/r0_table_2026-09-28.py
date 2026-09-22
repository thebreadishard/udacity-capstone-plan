"""The R0 table for the 28 September conversation (decision 48, the user's second yes of 22 Sep): all twenty Wilson modes, four
columns — curvature at the B3LYP geometry (ω′), the geometry term (from the deck's own a1g gradient and the T3 cubics), their sum,
the literature CCSD(T) harmonic — plus B3LYP and the flags. Every number is read from files: R0_DIAGONAL_READING_2026-09-22.json,
r0_geometry_term_cc.json, benzene_r0_harmonic_refs_m1_index.json.

Usage: python r0_table_2026-09-28.py [--out results_m1/R0_TABLE_2026-09-28.md]
"""
import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results_m1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(R, "R0_TABLE_2026-09-28.md"))
    a = ap.parse_args()
    rd = json.load(open(os.path.join(R, "R0_DIAGONAL_READING_2026-09-22.json")))
    gt = json.load(open(os.path.join(R, "r0_geometry_term_cc.json")))
    harm = json.load(open(os.path.join(R, "benzene_r0_harmonic_refs_m1_index.json")))
    term = {int(r[0]): r[3] for r in gt["rows"]}
    OPEN = {5: "open: −36 not explained by thresholds or geometry", 10: "open: −45 not explained by thresholds or geometry"}
    lines = ["# Benzene R0 — corrected harmonic frequencies for the 28 September table (cm⁻¹)", "",
             "ω′ = curvature of the composite (SCF + LNO-CCSD(T) − LNO-MP2 + full MP2, cc-pVTZ, transported frozen spaces) along the B3LYP/6-31G* mode at the "
             "B3LYP geometry (R0 diagonal deck, 22 Sep 2026). Geometry term = first-order shift towards the high-level minimum, ½ Σ_k φ_iik ΔQ_k, with ΔQ from the "
             f"deck's own a1g gradient (q_breathing {gt['dQ_cc']['11']:+.3f}, q_CH {gt['dQ_cc']['29']:+.3f}, i.e. r_CH shorter by 0.0046 Å) and φ the B3LYP cubic constants of the "
             "two-route QFF (T3). Literature CCSD(T): Miani et al. 2000 Table II (their ref. 26). Decision 48: curvature + geometry term is the corrected harmonic.", "",
             "| Wilson | sym | family | ω B3LYP | ω′ curvature | geometry term | ω′ + term | ω CCSD(T) | Δ before | Δ after | note |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for m in sorted(rd, key=int):
        mi = int(m); h = harm[m]; wcc = h.get("ccsdt_omega"); t = term.get(mi, float("nan"))
        wp = rd[m]["omega_cc"]; w = rd[m]["omega_b3lyp"]
        note = OPEN.get(mi, "")
        if wcc is None:
            note = (note + "; " if note else "") + "no CCSD(T) value in the source"
        rows.append((mi, h["wilson"], h["sym"], rd[m]["family"], w, wp, t, wp + t, wcc))
        lines.append(f"| ν{h['wilson']} | {h['sym']} | {rd[m]['family']} | {w:.1f} | {wp:.1f} | {t:+.1f} | {wp + t:.1f} | {wcc if wcc else '—'} | "
                     f"{(wp - wcc) if wcc else float('nan'):+.1f} | {(wp + t - wcc) if wcc else float('nan'):+.1f} | {note} |".replace("+nan", "—").replace("nan", "—"))
    def fam(r):
        return "C–H stretch" if r[4] > 3000 else ("out-of-plane" if "oop" in r[3] else "in-plane")
    lines += ["", "| group | modes | MAE ω_B3LYP − ω_CC | MAE ω′ − ω_CC | MAE (ω′ + term) − ω_CC |", "|---|---|---|---|---|"]
    for F in ("in-plane", "out-of-plane", "C–H stretch", "all"):
        sel = [r for r in rows if r[8] is not None and (F == "all" or fam(r) == F)]
        lines.append(f"| {F} | {len(sel)} | {np.mean([abs(r[4] - r[8]) for r in sel]):.1f} | {np.mean([abs(r[5] - r[8]) for r in sel]):.1f} | {np.mean([abs(r[7] - r[8]) for r in sel]):.1f} |")
    lines += ["", "Open rows are shown, not dropped (the user, 22 Sep). The b2g pair ν4/ν5 and a ≈ −10 cm⁻¹ offset of the in-plane modes against this literature column "
              "remain unexplained; next suspects: the diagonal-only reading (b2g mixing) and the composite's basis / frozen-core level against the unknown basis of ref. 26. "
              "Fundamentals are not compared here: the anharmonic shifts come from the two-route QFF (median 4.3 cm⁻¹ against Miani's own force field)."]
    txt = "\n".join(lines) + "\n"
    open(a.out, "w", encoding="utf-8").write(txt); print(txt)


if __name__ == "__main__":
    main()
