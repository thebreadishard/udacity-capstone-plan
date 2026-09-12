#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Q10 — the calibration (coverage) check of the error budget (Ladder §4 item 15, decision 31, P23, 2026-09-10).

Written 2026-09-12 evening, BEFORE any pipeline-vs-laboratory band position exists, so that the arithmetic and the
table layout are fixed in advance. Two modes:

  1. Readiness (runs now, from Module 03's laboratory table): per rung × family, how many laboratory bands exist,
     from which records, with which u_band (the Ladder's measured band-centre uncertainty, Module 03 columns of
     2026-09-12), and which opponent lines hold the species (Module 02 outputs). This is the laboratory half of
     Q10 and the list of families the check can ever be run on.
  2. Coverage (runs only when a pipeline bands CSV is given): for every scored band, the indicator
     |ω_pipeline − ω_lab| ≤ k·u_total, u_total = sqrt(u_band² + u_pipeline²), for k = 1 and 2; coverage fraction
     per rung, per family and overall against the nominal 68 % / 95 %. The pass thresholds are CANDIDATES here;
     the pilot note fixes them (proposal §6) — the script refuses to print a verdict until CONSTANTS says
     "fixed_by": "pilot note <date>". A budget below threshold is reported as incomplete with its deficit; the
     script has no code path that widens u_pipeline.

Usage:  python q10_coverage.py                      # readiness table -> results_m03/Q10_READINESS.md
        python q10_coverage.py --pipeline bands.csv # + coverage table -> results_m03/Q10_COVERAGE.md
The pipeline CSV needs columns: rung, species, family, omega_pipeline_cm, u_pipeline_cm, lab_record, omega_lab_cm, u_band_cm.
"""
import argparse, json, os
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent
M03 = PLAN / "modules" / "03_lab_scoreboard" / "notebook" / "bands_lab.csv"
M02 = PLAN / "modules" / "02_opponent_atlas" / "out"
OUT = HERE / "results_m03"

CONSTANTS = {
    "k_values": [1, 2],
    "nominal_coverage": {"1": 0.68, "2": 0.95},
    "pass_thresholds": {"overall_k2_min": None, "per_rung_k2_floor": None, "fixed_by": "NOT FIXED — candidates go into the pilot note; no verdict is printed until then"},
    "u_total_rule": "u_total = sqrt(u_band^2 + u_pipeline^2); u_band from Module 03 (Ladder rule), u_pipeline from the pipeline's per-band budget",
    "no_widening_rule": "a budget whose coverage falls below the thresholds is declared incomplete and the deficit reported; u_pipeline is never enlarged by this script",
    # ladder species by PAHdb uid (Ladder §2 rows; triphenylene uid 211 = the neutral C18H12 with twelve quartet hydrogens in the theoretical library)
    "ladder": {"R0": {"benzene": None}, "R1": {"naphthalene": "330"}, "R2": {"pyrene": "334", "chrysene": "291", "triphenylene": "211", "tetracene": "282"}, "R3": {"coronene": "18"}},
    "opponent_lines": {"A theoretical 4.00": "theoretical_4.00", "B anharmonic 1.00": "anharmonic_1.00", "cheap Bos 2025": "cheapline_bos2025", "C Mai 2025": "lineC_mai2025", "matrix experimental 3.10": "experimental_3.10"},
}


def readiness():
    ds = pd.read_csv(M03, dtype={"uid": str})
    gas = ds[ds.phase == "gas"].copy()
    rows = []
    present = {}
    for line, d in CONSTANTS["opponent_lines"].items():
        f = M02 / d / "species.csv"
        if f.exists():
            s = pd.read_csv(f, dtype=str)
            col = "uid" if "uid" in s.columns else s.columns[0]
            present[line] = set(s[col].astype(str))
    for rung, species in CONSTANTS["ladder"].items():
        for name, uid in species.items():
            g = gas[gas.species == name]
            opp = {line: (uid in ids) if uid else (name == "benzene" and line == "B anharmonic 1.00") for line, ids in present.items()}
            if g.empty:
                rows.append(dict(rung=rung, species=name, family="(no gas-phase record in Module 03)", records="", n_bands=0, u_band_min=np.nan, u_band_median=np.nan,
                                 T_source=", ".join(sorted(set())), opponents=", ".join(k for k, v in opp.items() if v)))
                continue
            for fam, gf in g.groupby("family", sort=False):
                rows.append(dict(rung=rung, species=name, family=fam, records="; ".join(sorted(set(gf.record.astype(str)))), n_bands=int(len(gf)),
                                 u_band_min=float(gf.u_band_cm.min()), u_band_median=float(gf.u_band_cm.median()),
                                 T_source="; ".join(sorted(set(gf.temperature_source.astype(str)))), opponents=", ".join(k for k, v in opp.items() if v)))
    R = pd.DataFrame(rows)
    OUT.mkdir(exist_ok=True)
    R.to_csv(OUT / "q10_readiness.csv", index=False)
    L = [f"# Q10 readiness — the laboratory half of the calibration check, per rung and family ({datetime.now():%Y-%m-%d %H:%M})", "",
         "Decision 31 (Ladder §4 item 15): for every scored band, |ω_pipeline − ω_lab| ≤ k·u_total is printed for k = 1, 2 and the coverage "
         "reported per rung, family and overall against 68 % / 95 %. No pipeline band exists yet, so this file lists what the check can be run on: "
         "the laboratory bands of Module 03 with their u_band (Ladder rule; hot-source floor form), and the opponent lines that hold the species. "
         "The pass thresholds are not fixed here (pilot note). Printed by probes/q10_coverage.py.", "",
         "| rung | species | family | records | n bands | u_band min | u_band median | temperature source | opponent lines holding the species |",
         "|---|---|---|---|---|---|---|---|---|"]
    for _, r in R.iterrows():
        L.append(f"| {r.rung} | {r.species} | {r.family} | {r.records} | {r.n_bands} | {'' if pd.isna(r.u_band_min) else f'{r.u_band_min:.2f}'} | "
                 f"{'' if pd.isna(r.u_band_median) else f'{r.u_band_median:.2f}'} | {r.T_source[:80]} | {r.opponents} |")
    L += ["", "Reading: a family can enter Q10 only where a laboratory band exists (n ≥ 1) and its u_band is finite; the u_total of the check adds the pipeline's "
          "own budget to the u_band shown. Species without a gas-phase record (tetracene, coronene) enter through matrix data under the matrix gate and the "
          "labelled cold columns (Ladder dated notes 2026-09-05/06) — those columns are not in Module 03's table yet and are listed as owed there.", "",
          "Constants: " + json.dumps(CONSTANTS["pass_thresholds"]) + " | ladder uids: " + json.dumps(CONSTANTS["ladder"])]
    (OUT / "Q10_READINESS.md").write_text("\n".join(L), encoding="utf-8")
    return R


def coverage(pipeline_csv):
    P = pd.read_csv(pipeline_csv)
    need = ["rung", "species", "family", "omega_pipeline_cm", "u_pipeline_cm", "lab_record", "omega_lab_cm", "u_band_cm"]
    missing = [c for c in need if c not in P.columns]
    if missing:
        raise SystemExit(f"pipeline CSV lacks columns {missing}")
    P["u_total_cm"] = np.sqrt(P.u_band_cm ** 2 + P.u_pipeline_cm ** 2)
    P["abs_dev_cm"] = (P.omega_pipeline_cm - P.omega_lab_cm).abs()
    for k in CONSTANTS["k_values"]:
        P[f"inside_k{k}"] = P.abs_dev_cm <= k * P.u_total_cm
    def cov(df):
        return {f"k{k}": float(df[f"inside_k{k}"].mean()) for k in CONSTANTS["k_values"]} | {"n": int(len(df))}
    table = {"overall": cov(P), "per_rung": {r: cov(d) for r, d in P.groupby("rung")}, "per_family": {f: cov(d) for f, d in P.groupby("family")},
             "per_rung_family": {f"{r} / {f}": cov(d) for (r, f), d in P.groupby(["rung", "family"])}}
    th = CONSTANTS["pass_thresholds"]
    verdict = "no verdict: pass thresholds not fixed (pilot note)" if th["overall_k2_min"] is None else None
    if verdict is None:
        ok_overall = table["overall"]["k2"] >= th["overall_k2_min"]
        ok_rungs = all(v["k2"] >= th["per_rung_k2_floor"] for v in table["per_rung"].values())
        verdict = "budget complete" if (ok_overall and ok_rungs) else "budget INCOMPLETE — deficit: " + json.dumps(
            {"overall_k2": round(th["overall_k2_min"] - table["overall"]["k2"], 3), "rungs_below_floor": [r for r, v in table["per_rung"].items() if v["k2"] < th["per_rung_k2_floor"]]})
    OUT.mkdir(exist_ok=True)
    json.dump({"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "coverage": table, "verdict": verdict}, open(OUT / "q10_coverage.json", "w"), indent=1)
    P.to_csv(OUT / "q10_coverage_bands.csv", index=False)
    L = [f"# Q10 coverage — |ω_pipeline − ω_lab| ≤ k·u_total ({datetime.now():%Y-%m-%d %H:%M})", "", f"Bands: {len(P)}. Nominal: k = 1 → 68 %, k = 2 → 95 %. **{verdict}**", "",
         "| scope | n | coverage k = 1 | coverage k = 2 |", "|---|---|---|---|", f"| overall | {table['overall']['n']} | {table['overall']['k1']:.3f} | {table['overall']['k2']:.3f} |"]
    for scope in ("per_rung", "per_family", "per_rung_family"):
        for key, v in table[scope].items():
            L.append(f"| {key} | {v['n']} | {v['k1']:.3f} | {v['k2']:.3f} |")
    (OUT / "Q10_COVERAGE.md").write_text("\n".join(L), encoding="utf-8")
    return table, verdict


def _selftest():
    """Arithmetic check on a hand-made three-row table (not data, not a result): deviations 0.5, 1.5, 3.0 with u_total 1 → k1 coverage 1/3, k2 coverage 2/3."""
    df = pd.DataFrame(dict(rung=["R0"] * 3, species="x", family=["f"] * 3, omega_pipeline_cm=[100.5, 101.5, 103.0], u_pipeline_cm=[0.0] * 3, lab_record="t", omega_lab_cm=[100.0] * 3, u_band_cm=[1.0] * 3))
    df["u_total_cm"] = np.sqrt(df.u_band_cm ** 2 + df.u_pipeline_cm ** 2); df["abs_dev_cm"] = (df.omega_pipeline_cm - df.omega_lab_cm).abs()
    assert abs((df.abs_dev_cm <= 1 * df.u_total_cm).mean() - 1 / 3) < 1e-12 and abs((df.abs_dev_cm <= 2 * df.u_total_cm).mean() - 2 / 3) < 1e-12
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", default=None, help="CSV of pipeline bands matched to laboratory bands (see docstring); absent → readiness only")
    args = ap.parse_args()
    assert _selftest()
    R = readiness()
    print(f"readiness: {len(R)} rung x species x family rows -> {OUT / 'Q10_READINESS.md'}")
    if args.pipeline:
        table, verdict = coverage(args.pipeline)
        print("coverage overall:", table["overall"], "|", verdict)
