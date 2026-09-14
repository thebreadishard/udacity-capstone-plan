"""Module 03 — the pre-registered SHAPE SCORE (notes/PreRegistration_2026-09-14_Shape_Score_Cold_Spectra.md) against the jet-cooled
band lists, computed for every column that exists. Built 2026-09-14; today only column A exists (PAHdb theoretical v4.00 as served,
Module 02's atlas), so this prints the baseline the reach product must beat. Columns B/D/0/P/N are added by giving --sticks <name>=<csv>
(a stick list with columns frequency_cm, intensity) and are scored identically.

Molecules and their line-A species (neutral, identified from the hydrogen-adjacency counts of Module 02's species table, 2026-09-14):
  tetracene C18H12 uid 282 (D2h: 4 solo H + 8 quartet H; chrysene is uid 291 with 4 duo + 8 quartet), coronene C24H12 uid 18 (12 duo H),
  peropyrene C26H14 uid 2294 (D2h: 8 duo + 6 trio H), ovalene C32H14 uid 4 (D2h: 2 solo + 12 duo H), HBC C42H18 uid 105 (18 trio H).
Laboratory lists: Module 03's cold columns (items 61-62; FELIX bands 550-2000 cm-1 only; the 3 um OPO bands are their own family and
are excluded from the 5-18 um score). Score per family: earth mover's distance between the unit-normalised 10 cm-1 histograms of the family
window (cm-1); family-weight error in percentage points; position term for the family's strongest laboratory band (informational).
Every constant is in CONSTANTS and printed. Output: out/shape_score.md/.json.
Amendment of 2026-09-14 (pre-registration §7, applied at the user's instruction after column B existed): beside the pre-registered EMD on raw
10 cm-1 histograms, an EMD on histograms obtained after convolving BOTH lists with the FELIX bandwidth (Gaussian, FWHM = 1 % of nu, mass
integrated per bin, truncated to the family window, then unit-normalised) is printed for every family and as a second weighted number, so
that a dense stick list is no longer charged for mass in bins a sparse peak table does not list. Both numbers are always printed."""
import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from math import erf, sqrt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_lab_tables import FAMILY_RULE  # noqa: E402

REPO = HERE.parents[3]
ATLAS = HERE.parent / "02_opponent_atlas" / "out" / "theoretical_4.00" / "bands.csv.gz"
CONSTANTS = {"bin_cm": 10.0, "window_cm": [550.0, 2000.0], "families_scored": ["CH-oop (10.5-15 um; benzene nu11 at 673 included)", "ring / CH-ip (9-10.5 um)", "CH-ip-bend (8.6 um)", "CC-stretch/CH-ip (7.7 um)", "CC-stretch (6.2 um)", "overtone / combination region"],
             "position_term_min_fraction": 0.25, "amendment_2026-09-14": {"convolution": "Gaussian, FWHM = 0.01 * nu (FELIX bandwidth), applied to laboratory peaks and predicted sticks alike before binning; mass outside the family window dropped; both EMDs printed", "fwhm_fraction": 0.01, "empty_prediction_rule": "amended term only: a family the laboratory populates but the prediction leaves without broadened mass scores the family width (worst case) and stays in the weighted mean; the pre-registered term keeps its original exclusion"}, "line_A": "PAHdb theoretical v4.00 as served (Module 02 bands.csv.gz, frequency_cm = served scaled frequency)",
             "uids": {"tetracene": 282, "coronene": 18, "peropyrene": 2294, "ovalene": 4, "hexa(peri)benzocoronene": 105},
             "lab_files": {"tetracene": "out/cold_columns_items61_62.csv", "coronene": "out/cold_columns_items61_62.csv", "peropyrene": "out/cold_columns_item62_grandpahs.csv", "ovalene": "out/cold_columns_item62_grandpahs.csv", "hexa(peri)benzocoronene": "out/cold_columns_item62_grandpahs.csv"}}
WIN = {lab: (lo, hi) for lo, hi, lab in FAMILY_RULE}


def hist(freqs, ints, lo, hi, w):
    edges = np.arange(lo, hi + w, w); h, _ = np.histogram(freqs, bins=edges, weights=ints)
    return h


def hist_conv(freqs, ints, lo, hi, w, frac):
    """Histogram of Gaussian-broadened sticks (FWHM = frac * nu): each stick's mass is integrated per bin via the error function."""
    edges = np.arange(lo, hi + w, w); h = np.zeros(len(edges) - 1)
    for nu, I in zip(freqs, ints):
        if I <= 0:
            continue
        sig = frac * nu / (2 * sqrt(2 * np.log(2)))
        cdf = np.array([0.5 * (1 + erf((e - nu) / (sig * sqrt(2)))) for e in edges])
        h += I * np.diff(cdf)
    return h


def emd_cm(a, b, w):
    if a.sum() <= 0 or b.sum() <= 0:
        return None
    a = a / a.sum(); b = b / b.sum()
    return float(np.abs(np.cumsum(a) - np.cumsum(b)).sum() * w)


def score(lab_f, lab_i, st_f, st_i):
    lo, hi = CONSTANTS["window_cm"]; w = CONSTANTS["bin_cm"]
    m_lab = (lab_f >= lo) & (lab_f < hi); m_st = (st_f >= lo) & (st_f < hi)
    lab_f, lab_i, st_f, st_i = lab_f[m_lab], lab_i[m_lab], st_f[m_st], st_i[m_st]
    tot_lab = lab_i.sum(); tot_st = st_i.sum(); rows = []; wsum = 0.0; wemd = 0.0; wemd_c = 0.0; wsum_c = 0.0; frac = CONSTANTS["amendment_2026-09-14"]["fwhm_fraction"]
    for fam in CONSTANTS["families_scored"]:
        flo, fhi = WIN[fam]; flo, fhi = max(flo, lo), min(fhi, hi)
        ml = (lab_f >= flo) & (lab_f < fhi); ms = (st_f >= flo) & (st_f < fhi)
        share_lab = float(lab_i[ml].sum() / tot_lab) if tot_lab else 0.0; share_st = float(st_i[ms].sum() / tot_st) if tot_st else 0.0
        e = emd_cm(hist(lab_f[ml], lab_i[ml], flo, fhi, w), hist(st_f[ms], st_i[ms], flo, fhi, w), w)
        # amended term (2026-09-14): sticks of the whole window contribute broadened mass to this family's bins
        hl_c = hist_conv(lab_f, lab_i, flo, fhi, w, frac); hs_c = hist_conv(st_f, st_i, flo, fhi, w, frac)
        # a prediction with no broadened mass in a family the laboratory populates scores the worst case (the family width), not an exclusion
        e_c = (emd_cm(hl_c, hs_c, w) if hs_c.sum() > 0 else float(fhi - flo)) if hl_c.sum() > 0 else None
        pos = None
        if ml.any():
            k = int(np.argmax(lab_i[ml])); nu0 = float(lab_f[ml][k])
            cand = st_f[ms][st_i[ms] >= CONSTANTS["position_term_min_fraction"] * (st_i[ms].max() if ms.any() else 0)] if ms.any() else np.array([])
            pos = float(np.min(np.abs(cand - nu0))) if cand.size else None
        rows.append({"family": fam, "n_lab": int(ml.sum()), "n_sticks": int(ms.sum()), "share_lab_pct": 100 * share_lab, "share_pred_pct": 100 * share_st,
                     "family_weight_error_pp": 100 * abs(share_lab - share_st), "emd_cm": e, "emd_conv_cm": e_c, "strongest_lab_band_cm": (float(lab_f[ml][int(np.argmax(lab_i[ml]))]) if ml.any() else None), "position_term_cm": pos})
        if e is not None:
            wsum += share_lab; wemd += share_lab * e
        if e_c is not None:
            wsum_c += share_lab; wemd_c += share_lab * e_c
    return rows, (wemd / wsum if wsum else None), (wemd_c / wsum_c if wsum_c else None)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sticks", action="append", default=[], help="extra column: name=path.csv (frequency_cm,intensity[,molecule])"); args = ap.parse_args()
    bands = pd.read_csv(ATLAS); out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "molecules": {}}
    L = [f"# Shape score against jet-cooled band lists — {out['date']}", "", f"Pre-registration: `GoalGathering/notes/PreRegistration_2026-09-14_Shape_Score_Cold_Spectra.md`. Window {CONSTANTS['window_cm']} cm⁻¹, bins {CONSTANTS['bin_cm']} cm⁻¹; per family the earth mover's distance (cm⁻¹) between unit-normalised histograms, the family-weight error (percentage points) and the position term for the strongest laboratory band; **EMD conv.** is the amended term of 2026-09-14 (both lists convolved with the FELIX bandwidth, 1 % of ν, before binning) — pre-registered and amended numbers are always printed side by side. Column A = {CONSTANTS['line_A']}.", ""]
    for mol, uid in CONSTANTS["uids"].items():
        lab = pd.read_csv(HERE / CONSTANTS["lab_files"][mol]); lab = lab[(lab["species"] == mol) & (lab["laser"] == "FELIX") & (lab["rel_intensity"] != "")]
        lab_f = lab["frequency_cm"].astype(float).to_numpy(); lab_i = pd.to_numeric(lab["rel_intensity"], errors="coerce").fillna(0).to_numpy()
        st = bands[(bands["uid"] == uid) & (bands["charge"] == 0)]
        cols = {"A": (st["frequency_cm"].to_numpy(float), st["intensity_km_mol"].to_numpy(float))}
        for s in args.sticks:
            name, path = s.split("=", 1); df = pd.read_csv(path)
            if "molecule" in df.columns: df = df[df["molecule"] == mol]
            if len(df): cols[name] = (df["frequency_cm"].to_numpy(float), df["intensity"].to_numpy(float))
        res = {}
        L += [f"## {mol} — laboratory bands in window: {int(((lab_f >= 550) & (lab_f < 2000)).sum())}; line A uid {uid}, sticks in window: {int(((cols['A'][0] >= 550) & (cols['A'][0] < 2000)).sum())}", "", "| column | family | n_lab | n_sticks | lab share % | pred share % | weight error (pp) | EMD (cm⁻¹) | EMD conv. (cm⁻¹) | strongest lab band | position term (cm⁻¹) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, (sf, si) in cols.items():
            rows, wm, wmc = score(lab_f, lab_i, sf, si); res[name] = {"rows": rows, "weighted_emd_cm": wm, "weighted_emd_conv_cm": wmc}
            for r in rows:
                L.append(f"| {name} | {r['family'].split(' (')[0]} | {r['n_lab']} | {r['n_sticks']} | {r['share_lab_pct']:.1f} | {r['share_pred_pct']:.1f} | {r['family_weight_error_pp']:.1f} | {('%.1f' % r['emd_cm']) if r['emd_cm'] is not None else '—'} | {('%.1f' % r['emd_conv_cm']) if r['emd_conv_cm'] is not None else '—'} | {r['strongest_lab_band_cm'] or '—'} | {('%.1f' % r['position_term_cm']) if r['position_term_cm'] is not None else '—'} |")
            L.append(f"| **{name}** | **intensity-weighted EMD over families (pre-registered / amended)** | | | | | | **{wm:.1f}** | **{wmc:.1f}** | | |" if wm is not None else f"| {name} | (no overlap) | | | | | | | | | |")
        L.append(""); out["molecules"][mol] = {"uid": uid, "n_lab_window": int(((lab_f >= 550) & (lab_f < 2000)).sum()), "columns": res}
    L += ["Reading: these are the baselines (column A) the reach product must beat under the pre-registered losing/winning conditions; no verdict is possible until columns 0, P or N exist. Constants: " + json.dumps(CONSTANTS)]
    (HERE / "out" / "shape_score.md").write_text("\n".join(L), encoding="utf-8"); json.dump(out, open(HERE / "out" / "shape_score.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
