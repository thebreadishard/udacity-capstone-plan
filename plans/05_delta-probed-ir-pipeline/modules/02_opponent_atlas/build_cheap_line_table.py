#!/usr/bin/env python
"""Module 02 — the cheap line (Bos et al. 2025, ML-corrected DFT scaling) read into the opponent atlas.

Source: the Supporting Information of Bos et al., ACS Omega 10, 62282 (2025), DOI
10.1021/acsomega.5c10225, CC BY-NC-ND 4.0 — the Europe PMC public copy (PMC12750190) placed in
./data/ on the user's instruction 2026-09-10. `ao5c10225_si_001.xlsx`, sheet `PAHdb-SVR`: per band the
computed B3LYP/4-31G harmonic frequency (the authors' own Gaussian runs, `<uid>_GaussReadable`), the
conventionally scaled value, the computed intensity and features, and the SVR-predicted frequency.
`ao5c10225_si_002.xlsx`, sheet `training`: the 465 band instances (no species identifier).

Outputs (./out/cheapline_bos2025/): bands.csv (uid, formula and charge from the atlas' theoretical
species table, computed, scaled, predicted frequency, intensity, family), species.csv, SUMMARY.md.
Nothing is trained; the pickled models are not run here.
"""
import csv, hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
FAMILY_RULE = [(0.0, 650.0, "low / skeletal"), (650.0, 950.0, "CH-oop"), (950.0, 1100.0, "ring / CH-ip"), (1100.0, 1250.0, "CH-ip-bend"),
               (1250.0, 1500.0, "CC-stretch/CH-ip"), (1500.0, 1650.0, "CC-stretch"), (1650.0, 2950.0, "overtone / combination"),
               (2950.0, 3200.0, "CH-stretch"), (3200.0, 1e9, "above 3200")]
LADDER = {"C6H6": "R0", "C10H8": "R1", "C16H10": "R2", "C18H12": "R2", "C24H12": "R3"}
def family(nu):
    for lo, hi, lab in FAMILY_RULE:
        if lo <= nu < hi: return lab
    return "?"

def main():
    f1 = HERE / "data/bos2025_si/ao5c10225_si_001.xlsx"; f2 = HERE / "data/bos2025_si/ao5c10225_si_002.xlsx"
    if not f1.exists(): print("NOT_RUN: SI not found"); return
    h1 = hashlib.sha256(f1.read_bytes()).hexdigest(); h2 = hashlib.sha256(f2.read_bytes()).hexdigest()
    d = pd.read_excel(f1); tr = pd.read_excel(f2)
    d["uid"] = d["UID"].astype(str).str.split("_").str[0]
    sp = pd.read_csv(HERE / "out/theoretical_4.00/species.csv", dtype=str).set_index("uid")
    d["formula"] = d["uid"].map(sp["formula"]); d["charge"] = d["uid"].map(sp["charge"]); d["n_c"] = d["uid"].map(sp["n_c"])
    d["pahdb_n_modes"] = d["uid"].map(sp["n_modes"])
    ratio = (d["Scaled Computational Frequency (cm^-1)"] / d["Computational Frequency (cm^-1)"]).round(4)
    out = HERE / "out" / "cheapline_bos2025"; out.mkdir(parents=True, exist_ok=True)
    b = pd.DataFrame({"uid": d["uid"], "formula": d["formula"], "charge": d["charge"], "n_c": d["n_c"],
                      "computed_cm": d["Computational Frequency (cm^-1)"], "scaled_cm": d["Scaled Computational Frequency (cm^-1)"],
                      "predicted_svr_cm": d["Predicted Frequency (cm^-1)"], "intensity_km_mol": d["Computational Intensity"]})
    b["family"] = b["predicted_svr_cm"].map(family)
    b.to_csv(out / "bands.csv", index=False)
    s = b.groupby("uid").agg(formula=("formula", "first"), charge=("charge", "first"), n_c=("n_c", "first"), rows=("computed_cm", "size")).reset_index()
    s["pahdb_n_modes"] = s["uid"].map(sp["n_modes"]); s["rung"] = s["formula"].map(LADDER).fillna("")
    s.to_csv(out / "species.csv", index=False)
    lad = {r: s[s.rung == r][["uid", "formula", "charge"]].values.tolist() for r in ("R0", "R1", "R2", "R3")}
    shift = (b["predicted_svr_cm"] - b["scaled_cm"])
    L = [f"# Opponent atlas — cheap line, Bos et al. 2025 (ML-corrected scaling) — {datetime.now():%Y-%m-%d %H:%M}", "",
         f"Sources `{f1.name}` sha256 `{h1[:16]}…`, `{f2.name}` sha256 `{h2[:16]}…` (Europe PMC copy of the ACS Supporting Information, CC BY-NC-ND 4.0).", "",
         f"**Species with ML-scaled spectra in the SI: {s.shape[0]}** (all PAHdb theoretical uids; n_C {int(s.n_c.astype(int).min())}–{int(s.n_c.astype(int).max())}); "
         f"**bands: {len(b):,}**; conventional scale factor in the file: {ratio.value_counts().head(3).to_dict()} (uniform, on the authors' own B3LYP/4-31G frequencies, not PAHdb's stored values); "
         f"rows per species equal PAHdb's mode count for {(s.rows.astype(int) == s.pahdb_n_modes.astype(int)).sum()} of {len(s)} species (the SI lists the authors' own harmonic sets, which differ in count from PAHdb's for most species).", "",
         f"SVR − conventional shift: mean {shift.mean():+.2f} cm⁻¹, MAD {shift.abs().mean():.2f}, range {shift.min():+.1f} … {shift.max():+.1f}.", "",
         f"Training instances (sheet `training`): {len(tr)} rows, columns {list(tr.columns)}; no species identifier, so the molecule-level leakage question cannot be checked from the SI.", "",
         "Ladder: " + "; ".join(f"{r}: {v if v else 'absent'}" for r, v in lad.items()), "",
         "Family labels by the SVR-predicted position with the atlas' frequency-range rule (pilot-note candidate). Nothing is trained; the pickled models are not run."]
    (out / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))

if __name__ == "__main__":
    main()
