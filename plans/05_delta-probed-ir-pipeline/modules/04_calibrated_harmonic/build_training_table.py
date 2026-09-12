#!/usr/bin/env python
"""Module 04 - builds the paired theory<->lab band table (the calibrated-harmonic baseline's dataset)
under RECIPE.md (2026-09-12). Run:  python build_training_table.py

Inputs (Module 02's parses; nothing is downloaded):
  ../02_opponent_atlas/out/theoretical_4.00/{bands.csv.gz,species.csv}   computed bands (PAHdb v4.00, as served)
  ../02_opponent_atlas/out/experimental_3.10/{bands.csv.gz,species.csv}  laboratory (argon-matrix) bands (PAHdb v3.10)
Outputs:
  notebook/training_table.csv   one row per matched (lab band, computed band) pair with the RECIPE features and the target
  out/SUMMARY.md                counts, constants, sha256 of every input
Join rule and constants are RECIPE.md's; every constant is in CONSTANTS and printed.
"""
import hashlib, json
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
M02 = HERE.parent / "02_opponent_atlas" / "out"
CONSTANTS = {
    "match_window_cm": 30.0,                 # |nu_scaled - nu_lab| <= 30
    "min_computed_intensity_km_mol": 1.0,    # IR-active candidates only
    "match_order": "lab bands in descending laboratory intensity; nearest free candidate; one-to-one; no second choice",
    "target": "y = nu_lab - nu_scaled (cm-1), library as served (decision 30)",
    "scale_regions_cm": [[0, 1111], [1111, 2500], [2500, 1e9]],   # Bauschlicher 2018 Table 2 regions as stored
    "intensity_floor_km_mol": 1e-3,
    "ladder_uids": {"330": "R1 naphthalene", "265": "anthracene (locality probe)", "334": "R2 pyrene", "282": "R2 tetracene", "291": "R2 chrysene", "18": "R3 coronene"},
    "family_rule_source": "Module 02 build_opponent_atlas.py FAMILY_RULE (the label stored in the band table)",
}


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def region(nu):
    for i, (lo, hi) in enumerate(CONSTANTS["scale_regions_cm"]):
        if lo <= nu < hi:
            return i
    return -1


def main():
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "notebook").mkdir(exist_ok=True)
    files = {k: M02 / k for k in ["theoretical_4.00/bands.csv.gz", "theoretical_4.00/species.csv", "experimental_3.10/bands.csv.gz", "experimental_3.10/species.csv"]}
    inputs = {k: sha256(v) for k, v in files.items()}
    th = pd.read_csv(files["theoretical_4.00/bands.csv.gz"], dtype={"uid": str, "charge": str})
    ths = pd.read_csv(files["theoretical_4.00/species.csv"], dtype={"uid": str, "charge": str}).set_index("uid")
    ex = pd.read_csv(files["experimental_3.10/bands.csv.gz"], dtype={"uid": str, "charge": str})
    exs = pd.read_csv(files["experimental_3.10/species.csv"], dtype={"uid": str, "charge": str}).set_index("uid")
    uids = [u for u in exs.index if u in ths.index]
    dropped = [u for u in exs.index if u not in ths.index]
    W, IMIN = CONSTANTS["match_window_cm"], CONSTANTS["min_computed_intensity_km_mol"]
    rows, unmatched = [], {}
    for uid in uids:
        lab = ex[ex.uid == uid].copy()
        comp = th[(th.uid == uid) & (th.intensity_km_mol >= IMIN)].copy()
        lab["rel_int_lab"] = lab.intensity_km_mol / lab.intensity_km_mol.max()
        comp["rel_int_comp"] = comp.intensity_km_mol / th[th.uid == uid].intensity_km_mol.max()
        taken = set()
        n_un = 0
        for _, lb in lab.sort_values("intensity_km_mol", ascending=False).iterrows():
            cand = comp[(~comp.index.isin(taken)) & ((comp.frequency_cm - lb.frequency_cm).abs() <= W)]
            if cand.empty:
                n_un += 1
                continue
            ci = (cand.frequency_cm - lb.frequency_cm).abs().idxmin()
            c = comp.loc[ci]
            taken.add(ci)
            s = ths.loc[uid]
            rows.append(dict(
                uid=uid, formula=s.formula, charge=int(s.charge), n_c=int(s.n_c), n_h=int(s.n_h), has_n=int(int(s.n_n) > 0),
                n_solo=s.n_solo, n_duo=s.n_duo, n_trio=s.n_trio, n_quartet=s.n_quartet, point_group=s.symmetry,
                ladder=CONSTANTS["ladder_uids"].get(uid, ""), lab_doi=exs.loc[uid, "dois"], species_name=str(exs.loc[uid, "route"]).split("|")[0].strip(),
                nu_lab_cm=lb.frequency_cm, rel_int_lab=round(float(lb.rel_int_lab), 4),
                nu_scaled_cm=c.frequency_cm, nu_unscaled_cm=c.frequency_unscaled_cm, scale=c.scale, scale_region=region(c.frequency_unscaled_cm),
                intensity_km_mol=c.intensity_km_mol, log10_intensity=float(np.log10(max(c.intensity_km_mol, CONSTANTS["intensity_floor_km_mol"]))),
                rel_int_comp=round(float(c.rel_int_comp), 4), irrep=c.symmetry, family=c.family,
                n_candidates=int(((comp.frequency_cm - lb.frequency_cm).abs() <= W).sum()),
                y_cm=round(float(lb.frequency_cm - c.frequency_cm), 3),
            ))
        unmatched[uid] = dict(lab_bands=len(lab), matched=len(lab) - n_un, unmatched=n_un, computed_active=len(comp))
    df = pd.DataFrame(rows)
    df.insert(0, "pair_id", range(1, len(df) + 1))
    df.to_csv(HERE / "notebook" / "training_table.csv", index=False)
    um = pd.DataFrame(unmatched).T
    NL = chr(10)
    fam = df.groupby("family").y_cm.agg(["count", "mean", "median", "std"]).round(2)
    L = [f"# Module 04 - paired theory<->lab band table - {datetime.now():%Y-%m-%d %H:%M}", "",
         "Built by `build_training_table.py` under RECIPE.md (2026-09-12). The training table is a derived dataset matching public computed "
         "bands (PAHdb theoretical v4.00, as served) to public laboratory bands (PAHdb experimental v3.10, argon matrix); it is not "
         "AI-generated. Pre-release: the Zenodo release of reading 1 is still the student's action.", "",
         f"**Species joined: {len(uids)}** (experimental entries without a theoretical record, dropped: {dropped}). "
         f"**Pairs: {len(df):,}** of {int(um.lab_bands.sum()):,} laboratory bands ({int(um.unmatched.sum()):,} unmatched, {int(um.unmatched.sum()) / int(um.lab_bands.sum()):.1%}); "
         f"columns: {df.shape[1]}.", "",
         f"Target y = nu_lab - nu_scaled: mean {df.y_cm.mean():+.2f}, median {df.y_cm.median():+.2f}, SD {df.y_cm.std():.2f}, MAE of the zero model {df.y_cm.abs().mean():.2f} cm-1; "
         f"pairs with more than one candidate: {int((df.n_candidates > 1).sum())}.", "",
         "Per family (target):", "", "```", fam.to_string(), "```", "",
         "Ladder molecules:", "", "```", df[df.ladder != ""].groupby(["uid", "species_name"]).y_cm.agg(["count", "mean", "median"]).round(2).to_string(), "```", "",
         "Constants:", "", "```", json.dumps(CONSTANTS, indent=1), "```", "", "Inputs (sha256):", ""]
    L += [f"- `{k}` - `{v[:16]}...`" for k, v in inputs.items()]
    (HERE / "out" / "SUMMARY.md").write_text(NL.join(L), encoding="utf-8")
    print(NL.join(L))


if __name__ == "__main__":
    main()
