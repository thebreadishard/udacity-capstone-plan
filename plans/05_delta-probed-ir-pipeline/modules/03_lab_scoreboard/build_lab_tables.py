#!/usr/bin/env python
"""Module 03 - builds the laboratory band dataset and the matrix-gas pairs, exactly as PRE_REGISTRATION.md
(2026-09-11) fixes them. Run:  python build_lab_tables.py

Inputs already in the repository (nothing is downloaded here):
  matrix : ../02_opponent_atlas/out/experimental_3.10/{bands.csv.gz,species.csv}  (PAHdb experimental v3.10, Module 02 parse)
  gas    : NIST WebBook JCAMP records cached by plans 04 and 02 (probes/nist_cache/), gas-phase records only
  R0     : the probe-2a scoreboard rows for benzene (probes/results_m03/benzene/SCOREBOARD_benzene_quantir_0p125.json)
Outputs:
  notebook/bands_lab.csv        one row per laboratory band (matrix bands + gas peaks) - the Module 03 dataset
  notebook/pairs_matrix_gas.csv one row per matched (matrix, gas) pair for the four species with both records
  out/SUMMARY.md                counts, constants, sha256 of every input
Every constant that is a choice is in CONSTANTS and printed; the family rule is Module 02's, copied verbatim.
"""
import hashlib, json, sys
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd
from scipy.signal import find_peaks, peak_prominences

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1]                       # plans/05_delta-probed-ir-pipeline
PLANS = HERE.parents[2]                      # plans/
M02 = HERE.parent / "02_opponent_atlas" / "out" / "experimental_3.10"
sys.path.insert(0, str(PLAN / "probes"))
from m03_band_uncertainty import parse_jcamp, fwhm   # the JCAMP reader of probe 2a (regex tokenizer)

CONSTANTS = {  # PRE_REGISTRATION.md, "Definitions (fixed)"
    "noise_window_cm": [2400.0, 2500.0],
    "noise_rule": "1.4826 * MAD of the linearly detrended noise window",
    "peak_prominence_sigma": 5.0,
    "peak_min_snr": 10.0,
    "position_rule": "parabolic apex through the maximum and its two neighbours",
    "u_c_rule": "u_c = FWHM / (2 * S/N)",
    "match_window_cm": 20.0,
    "match_choice": "largest matrix intensity inside the window; one-to-one, closer gas peak keeps a contested band",
    "msdc_ir_resolution_cm": 8.0,            # SRD 35 description (item 50, snippet grade): all spectra converted to 8.0 cm-1
    "matrix_resolution_cm_hudgins1998": 0.9, # item 8, read: Ar, 10 K, 0.9 cm-1
    "matrix_temperature_K_hudgins1998": 10.0,
    "family_rule_source": "Module 02 build_opponent_atlas.py FAMILY_RULE (copied verbatim)",
}
FAMILY_RULE = [
    (0.0, 650.0, "low / skeletal"), (650.0, 950.0, "CH-oop (10.5-15 um; benzene nu11 at 673 included)"), (950.0, 1100.0, "ring / CH-ip (9-10.5 um)"),
    (1100.0, 1250.0, "CH-ip-bend (8.6 um)"), (1250.0, 1500.0, "CC-stretch/CH-ip (7.7 um)"), (1500.0, 1650.0, "CC-stretch (6.2 um)"),
    (1650.0, 2950.0, "overtone / combination region"), (2950.0, 3200.0, "CH-stretch"), (3200.0, 1e9, "above 3200"),
]


def family(nu):
    for lo, hi, lab in FAMILY_RULE:
        if lo <= nu < hi:
            return lab
    return "?"


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---- gas-phase records (the WebBook cache; only ##STATE=gas / vapour records) ---------------------------
C04 = PLANS / "04_cc-anchored-ir-pipeline" / "probes" / "nist_cache"
C02 = PLANS / "02_coupled-cluster-anharmonic-ir" / "probes" / "nist_cache"
GAS_RECORDS = [  # (file, species name, formula, PAHdb uid of the neutral matrix entry or None, role, temperature note)
    (C04 / "C91203_0.jdx",  "naphthalene",  "C10H8",  "330", "primary",   "hot lightpipe, not stated"),
    (C02 / "C120127_0.jdx", "anthracene",   "C14H10", "265", "primary",   "hot lightpipe, not stated"),
    (C04 / "C129000_0.jdx", "pyrene",       "C16H10", "334", "primary",   "hot lightpipe, not stated"),
    (C04 / "C218019_0.jdx", "chrysene",     "C18H12", "291", "primary",   "hot lightpipe, not stated"),
    (C04 / "C217594_0.jdx", "triphenylene", "C18H12", None,  "gas only",  "hot lightpipe, not stated"),
    (C04 / "C71432_0.jdx",  "benzene",      "C6H6",   None,  "gas only",  "hot lightpipe, not stated"),
    (C04 / "C91203_1.jdx",  "naphthalene",  "C10H8",  "330", "secondary", "245 C (record)"),
    (C04 / "C71432_1.jdx",  "benzene",      "C6H6",   None,  "gas only",  "not stated (Coblentz cell)"),
]


def gas_peaks(path):
    meta, x, y, step = parse_jcamp(path)
    yunits = meta.get("YUNITS", "").upper()
    if "TRANSMITTANCE" in yunits:
        t = np.clip(y, 1e-4, None)
        t = t / 100.0 if t.max() > 1.5 else t
        y = -np.log10(np.clip(t, 1e-4, 1.0))
    lo, hi = CONSTANTS["noise_window_cm"]
    w = (x >= lo) & (x <= hi)
    if w.sum() < 8:
        w = (x >= x.min()) & (x <= x.min() + 100)
    resid = y[w] - np.polyval(np.polyfit(x[w], y[w], 1), x[w])
    sigma = 1.4826 * np.median(np.abs(resid - np.median(resid)))
    if sigma <= 0:
        sigma = max(float(np.std(resid)), 1e-6)
    idx, _ = find_peaks(y, prominence=CONSTANTS["peak_prominence_sigma"] * sigma)
    prom = peak_prominences(y, idx)[0]
    rows = []
    src = meta.get("$NIST SOURCE", "?")
    res = CONSTANTS["msdc_ir_resolution_cm"] if src == "MSDC-IR" else float(str(meta.get("RESOLUTION", "nan")).split()[0])
    for i, pr in zip(idx, prom):
        snr = y[i] / sigma
        if snr < CONSTANTS["peak_min_snr"] or i == 0 or i == len(y) - 1:
            continue
        y0, y1, y2 = y[i - 1], y[i], y[i + 1]
        den = (y0 - 2 * y1 + y2)
        apex = x[i] + 0.5 * (y0 - y2) / den * step if den != 0 else x[i]
        wd = fwhm(x, y, i)
        rows.append(dict(frequency_cm=round(float(apex), 2), grid_point_cm=float(x[i]), absorbance=float(y1), prominence=float(pr),
                         snr=round(float(snr), 1), fwhm_cm=round(float(wd), 2), u_c_cm=round(float(wd / (2 * snr)), 3), u_res_cm=res))
    return meta, sigma, step, rows


def main():
    out_dir = HERE / "out"
    out_dir.mkdir(exist_ok=True)
    nb = HERE / "notebook"
    nb.mkdir(exist_ok=True)
    inputs = {}
    # ---- matrix side
    mb = pd.read_csv(M02 / "bands.csv.gz", dtype={"uid": str, "charge": str})
    ms = pd.read_csv(M02 / "species.csv", dtype={"uid": str, "charge": str})
    inputs[str(M02 / "bands.csv.gz")] = sha256(M02 / "bands.csv.gz")
    inputs[str(M02 / "species.csv")] = sha256(M02 / "species.csv")
    names = ms.set_index("uid")["route"].str.split("|").str[0].str.strip()
    dois = ms.set_index("uid")["dois"]
    hud = dois.eq("10.1021/jp9834816")
    is_hud = mb.uid.map(hud).fillna(False).astype(bool)
    matrix = pd.DataFrame({
        "phase": "matrix", "source": "PAHdb experimental 3.10 (Ar matrix)", "record": "uid " + mb.uid, "species": mb.uid.map(names),
        "formula": mb.formula, "charge": mb.charge.astype(int), "n_c": mb.n_c, "uid": mb.uid,
        "temperature_K": np.where(is_hud, CONSTANTS["matrix_temperature_K_hudgins1998"], np.nan),
        "resolution_cm": np.where(is_hud, CONSTANTS["matrix_resolution_cm_hudgins1998"], np.nan),
        "frequency_cm": mb.frequency_cm, "intensity": mb.intensity_km_mol, "intensity_unit": "relative (PAHdb experimental)",
        "snr": np.nan, "fwhm_cm": np.nan, "u_c_cm": np.nan,
        "u_res_cm": np.where(is_hud, CONSTANTS["matrix_resolution_cm_hudgins1998"], np.nan),
        "source_ref": mb.uid.map(dois), "role": "matrix",
    })
    matrix["family"] = matrix.frequency_cm.map(family)
    # ---- gas side
    gas_rows, gas_meta = [], []
    for path, name, formula, uid, role, tnote in GAS_RECORDS:
        meta, sigma, step, rows = gas_peaks(path)
        inputs[str(path)] = sha256(path)
        src = meta.get("$NIST SOURCE", "?")
        state = meta.get("STATE", "?")
        gas_meta.append(dict(file=path.name, species=name, source=src, state=state, origin=meta.get("ORIGIN"), resolution=meta.get("RESOLUTION"),
                             deltax=step, n_points=meta.get("NPOINTS"), noise_sigma=sigma, n_peaks=len(rows), role=role))
        for r in rows:
            gas_rows.append(dict(phase="gas", source=f"NIST WebBook {src} ({state[:24]})", record=path.name, species=name, formula=formula, charge=0,
                                 n_c=int(formula[1:].split("H")[0]), uid=uid, temperature_K=(273.15 + 245) if "245" in tnote else np.nan,
                                 resolution_cm=r["u_res_cm"], frequency_cm=r["frequency_cm"], intensity=r["absorbance"],
                                 intensity_unit="absorbance (peak, record units)", snr=r["snr"], fwhm_cm=r["fwhm_cm"], u_c_cm=r["u_c_cm"],
                                 u_res_cm=r["u_res_cm"], source_ref="10.18434/T4D303", role=role, family=family(r["frequency_cm"])))
    gas = pd.DataFrame(gas_rows)
    # ---- R0: probe-2a scoreboard rows for benzene (positions and u_band already printed by probes/m03_band_uncertainty.py)
    sb_path = PLAN / "probes" / "results_m03" / "benzene" / "SCOREBOARD_benzene_quantir_0p125.json"
    sb = json.load(open(sb_path, encoding="utf-8"))
    inputs[str(sb_path)] = sha256(sb_path)
    r0 = []
    for b in sb["scored_bands"]:
        if b.get("status") != "scored":
            continue
        r0.append(dict(phase="gas", source="NIST QUANT-IR cell, 23 C, 0.125 cm-1 (probe 2a table)", record=sb["source_file"], species="benzene",
                       formula="C6H6", charge=0, n_c=6, uid=None, temperature_K=296.15, resolution_cm=0.125, frequency_cm=b["peak_cm"],
                       intensity=b.get("A_km_mol", np.nan), intensity_unit="km/mol (integrated)", snr=b.get("snr_peak"), fwhm_cm=b.get("fwhm_cm"),
                       u_c_cm=b.get("u_c_cm", np.nan), u_res_cm=0.125, source_ref="10.6028/jres.104.004", role="R0 scoreboard", family=family(b["peak_cm"])))
    r0 = pd.DataFrame(r0)
    ds = pd.concat([matrix, gas, r0], ignore_index=True)
    ds.insert(0, "band_id", range(1, len(ds) + 1))
    ds.to_csv(nb / "bands_lab.csv", index=False)
    # ---- the join (PRE_REGISTRATION.md, Definitions 2-4)
    W = CONSTANTS["match_window_cm"]
    pairs = []
    for path, name, formula, uid, role, tnote in GAS_RECORDS:
        if uid is None:
            continue
        g = gas[(gas.record == path.name)].sort_values("intensity", ascending=False)
        m = matrix[matrix.uid == uid]
        taken = {}  # matrix band index -> (gas index, distance)
        for gi, gr in g.iterrows():
            cand = m[(m.frequency_cm - gr.frequency_cm).abs() <= W]
            if cand.empty:
                continue
            mi = cand.intensity.idxmax()
            d = abs(m.loc[mi, "frequency_cm"] - gr.frequency_cm)
            if mi in taken and taken[mi][1] <= d:
                continue          # contested: the closer gas peak keeps it, no second choice
            taken[mi] = (gi, d)
        for mi, (gi, d) in taken.items():
            gr, mr = g.loc[gi], m.loc[mi]
            pairs.append(dict(species=name, uid=uid, gas_record=path.name, gas_role=role, nu_gas_cm=gr.frequency_cm, gas_snr=gr.snr,
                              gas_fwhm_cm=gr.fwhm_cm, u_c_gas_cm=gr.u_c_cm, u_res_gas_cm=gr.u_res_cm, nu_matrix_cm=mr.frequency_cm,
                              matrix_intensity=mr.intensity, delta_cm=round(mr.frequency_cm - gr.frequency_cm, 2), family=family(gr.frequency_cm),
                              n_candidates=int((m.frequency_cm - gr.frequency_cm).abs().le(W).sum())))
    pairs = pd.DataFrame(pairs).sort_values(["gas_role", "species", "nu_gas_cm"]).reset_index(drop=True)
    pairs.to_csv(nb / "pairs_matrix_gas.csv", index=False)
    # ---- summary
    unmatched = {}
    for path, name, formula, uid, role, tnote in GAS_RECORDS:
        if uid is None:
            continue
        ng = int((gas.record == path.name).sum())
        npair = int((pairs.gas_record == path.name).sum())
        nm = int((matrix.uid == uid).sum())
        unmatched[f"{name} / {path.name} ({role})"] = dict(gas_peaks=ng, pairs=npair, gas_unmatched=ng - npair, matrix_bands=nm, matrix_unmatched=nm - npair)
    NL = chr(10)
    L = [f"# Module 03 - laboratory band dataset and matrix-gas pairs - {datetime.now():%Y-%m-%d %H:%M}", "",
         "Built by `build_lab_tables.py` under PRE_REGISTRATION.md (2026-09-11). These are laboratory measurements from the public PAHdb "
         "experimental library and the NIST Chemistry WebBook. Not synthetic, not AI-generated, not the Module 02 dataset.", "",
         f"**Dataset `notebook/bands_lab.csv`: {len(ds):,} rows x {ds.shape[1]} columns** - matrix bands {len(matrix):,} ({matrix.uid.nunique()} species), "
         f"gas peaks {len(gas):,} ({gas.record.nunique()} records, {gas.species.nunique()} species), R0 scoreboard rows {len(r0)}.", "",
         "| gas record | species | source | state | stated resolution | grid | points | noise sigma (absorbance) | peaks | role |", "|---|---|---|---|---|---|---|---|---|---|"]
    for g in gas_meta:
        L.append(f"| {g['file']} | {g['species']} | {g['source']} | {g['state'][:40]} | {g['resolution'] or '- (8.0 by series description)'} | {g['deltax']:.3g} | "
                 f"{g['n_points']} | {g['noise_sigma']:.2e} | {g['n_peaks']} | {g['role']} |")
    L += ["", f"**Pairs `notebook/pairs_matrix_gas.csv`: {len(pairs)}** (primary {int((pairs.gas_role == 'primary').sum())}, secondary {int((pairs.gas_role == 'secondary').sum())}).", "",
          "| species / record | gas peaks | pairs | gas unmatched | matrix bands | matrix unmatched |", "|---|---|---|---|---|---|"]
    for k, v in unmatched.items():
        L.append(f"| {k} | {v['gas_peaks']} | {v['pairs']} | {v['gas_unmatched']} | {v['matrix_bands']} | {v['matrix_unmatched']} |")
    pf = pairs[pairs.gas_role == "primary"].groupby("family").delta_cm.agg(["count", "median", "mean", "std"]).round(2)
    L += ["", "Primary pairs per family (descriptive; the test itself runs in the notebook):", "", "```", pf.to_string(), "```", "", "Constants:", "", "```",
          json.dumps(CONSTANTS, indent=1), "```", "", "Inputs (sha256):", ""]
    L += [f"- `{Path(k).relative_to(PLANS.parent).as_posix()}` - `{v[:16]}...`" for k, v in inputs.items()]
    (out_dir / "SUMMARY.md").write_text(NL.join(L), encoding="utf-8")
    print(NL.join(L))


if __name__ == "__main__":
    main()
