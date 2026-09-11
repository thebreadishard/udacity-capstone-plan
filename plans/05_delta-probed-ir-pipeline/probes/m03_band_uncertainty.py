#!/usr/bin/env python
"""Probe 2a — laboratory scoreboard and u_band (Module 03), first version: R0 benzene on the NIST
Quantitative Infrared Database record (Chu, Guenther, Rhoderick & Lafferty 1999, item 56; WebBook
CAS 71-43-2, $NIST SOURCE=QUANT-IR).

What it prints, per scored band (probes README 2a; Ladder §2 decidability rule):
  source class, stated temperature, stated resolution (from the record / the series' documentation,
  never DELTAX), peak position and intensity-weighted centroid, the centroid precision from the
  spectrum's own noise, the position-calibration term (Chu §2.4), the temperature term u_296 per
  family by the Bose rule of the Ladder's dated note of 2026-09-06 (item 52's model, the 0.044 cm⁻¹ K⁻¹
  floor slope for a family without a measured slope), their quadrature sum u_band, the integrated
  band intensity in km/mol with the source's stated uncertainty (3.3 %, k = 2) and the certified /
  non-certified flag (Chu §3.3 windows), and u_band against candidate beat margins (the pilot note
  fixes the margins; here they are candidates and say so).

Rules kept: no number is typed that a file can supply — the DFT mode list (frequencies, families)
comes from results_dryrun/<molecule>/stageA.json, the irreps from stageC_symmetry_prior.json, the
band positions and intensities from the JCAMP record; every constant that is a choice is in
CONSTANTS below and is printed with the table (pilot-note candidates). The sha256 of the source
record and of the printed table are part of the output. No verdict beyond the decidability rule.
"""
import argparse, hashlib, json, math, re, sys
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
K_B = 1.380649e-23; H = 6.62607015e-34; C = 2.99792458e10; N_A = 6.02214076e23  # SI; c in cm/s
HC_OVER_K = H * C / K_B  # K per cm⁻¹ (1.4388)

CONSTANTS = {  # every one a pilot-note candidate; printed with the table
    "irreps_ir_active_D6h": ["A2u", "E1u"],          # the scored set: IR-active fundamentals
    "match_window_rel": [0.90, 1.00],                 # observed/harmonic-DFT ratio window per mode
    "peak_min_snr": 20.0,                             # a maximum counts as a band above this S/N
    "band_edge_k_sigma": 3.0,                         # integration window: contiguous region above 3σ baseline noise
    "band_max_halfwidth_cm": 150.0,                   # guard on that walk
    "noise_window_cm": [2400.0, 2500.0],              # quiet window for the baseline noise (between the CO2 and C–H regions)
    "position_column": "peak",                        # scoreboard position = parabolic peak apex; centroid printed beside it
    "centroid_precision_rule": "u_c = FWHM_obs / (2 · SNR_peak)",
    "calibration_term_cm": 0.0042,                    # Chu 1999 §2.4: RMS on 158 water lines (item 56, read 2026-09-06)
    "intensity_rel_unc_k2": 0.033,                    # Chu 1999 Table 3, benzene, alpha > 1e-4 (item 56)
    "non_certified_windows_cm": [[1325, 1900], [2050, 2225], [2295, 2385], [3550, 3950]],  # Chu §3.3 (item 56)
    "T_ref_K": 296.0, "P_ref_Pa": 101325.0,           # Chu §2.3: coefficients corrected to 296 K, 760 Torr
    "chi_floor_cm_per_K": 0.044,                      # Ladder dated note 2026-09-06 (i): floor slope, item 52 Table 1
    "bath_mode_cutoff_cm": 700.0,                     # item 52 §4.1: the shift is dominated by modes << 700 cm⁻¹
    "u_296_rule": "u_296 = chi_F · (hc nu_m / k_B) · nbar(nu_m, 296 K), nu_m = mean DFT frequency below the cutoff",
    "candidate_margins_cm": [2.0, 5.0, 10.0],         # candidates only; the pilot note fixes the margin per family
    "u_T_decision_29": "R0/R1 room-temperature sources: u_T = the pipeline's computed 0→T shift per band from the DFT X_ik, "
                       "applied as a correction with ±30 % of itself; NOT_RUN until the X_ik exist — the floor below is printed and labelled",
}

def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

NUM = re.compile(r"[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?")

def parse_jcamp(path):
    """(X++(Y..Y)) AFFN as the WebBook serves it; negative Y values are glued to their neighbour
    ('575.65-309751 220025-333544'), so tokens are cut with a number regex, not whitespace."""
    meta, rows, in_data = {}, [], False
    for line in Path(path).read_text(errors="replace").splitlines():
        line = line.rstrip()
        if line.startswith("##"):
            in_data = line.startswith("##XYDATA")
            if "=" in line:
                k, v = line[2:].split("=", 1); meta[k.strip()] = v.strip()
            continue
        if in_data and line.strip():
            toks = NUM.findall(line)
            if len(toks) >= 2: rows.append([float(t) for t in toks])
    n = int(meta["NPOINTS"]); first, last = float(meta["FIRSTX"]), float(meta["LASTX"])
    step = (last - first) / (n - 1); yf = float(meta.get("YFACTOR", 1)); xf = float(meta.get("XFACTOR", 1))
    xs, ys = [], []
    for row in rows:
        x0, vals = row[0] * xf, row[1:]
        xs.extend(x0 + j * step for j in range(len(vals))); ys.extend(v * yf for v in vals)
    o = np.argsort(xs); x, y = np.array(xs)[o], np.array(ys)[o]
    return meta, x, y, step

def alpha_to_sigma_cm2(alpha, T, P):
    """alpha in (µmol/mol)^-1 m^-1, base 10 → absorption cross-section in cm² per molecule (base e)."""
    n1 = P / (K_B * T) * 1e-6        # absorber number density per µmol/mol, m^-3
    return alpha * math.log(10) / n1 * 1e4

def band_window(x, y, ipk, k_sigma, noise, max_halfwidth):
    """Contiguous region around the peak where the signal stays above k_sigma·σ (baseline noise), at
    most ±max_halfwidth from the peak. Local minima above the threshold do not stop the walk: the P/R
    wings of a perpendicular band are part of the band (a first version stopped at the first local
    minimum and lost half of benzene's ν11; a 5 %-of-peak threshold lost its wings too, the Q branch
    being sixty times higher than the wings). Neighbouring bands inside the region are integrated with
    it: the scoreboard's intensity is that of the band system, and the window is printed."""
    thr = k_sigma * noise
    lo = ipk
    while lo > 0 and y[lo - 1] > thr and x[ipk] - x[lo - 1] <= max_halfwidth: lo -= 1
    hi = ipk
    while hi < len(y) - 1 and y[hi + 1] > thr and x[hi + 1] - x[ipk] <= max_halfwidth: hi += 1
    return lo, hi

def fwhm(x, y, ipk):
    half = 0.5 * y[ipk]; i = ipk
    while i > 0 and y[i] > half: i -= 1
    xl = x[i] + (half - y[i]) / (y[i + 1] - y[i]) * (x[i + 1] - x[i]) if y[i + 1] != y[i] else x[i]
    j = ipk
    while j < len(y) - 1 and y[j] > half: j += 1
    xr = x[j - 1] + (y[j - 1] - half) / (y[j - 1] - y[j]) * (x[j] - x[j - 1]) if y[j - 1] != y[j] else x[j]
    return xr - xl

def table_mode(a):
    """Scoreboard from a transcribed band table (Pirali 2009 Table 1 for naphthalene): class 'resolved
    fundamental' (decision 21) — u_T = 0, a head-to-origin term (from the table's metadata), the paper's
    resolution as the resolution term, and half the last printed digit as the reading precision. No
    intensities. Families: the Ladder's frequency-range rule plus the paper's symmetry (b3u = out-of-plane);
    matching to the pipeline's DFT modes waits for the naphthalene dry-run mode table (owed)."""
    T = json.load(open(a.table, encoding="utf-8"))
    out_dir = HERE / "results_m03" / a.molecule; out_dir.mkdir(parents=True, exist_ok=True)
    res = float(T["resolution_cm"]); h2o = float(T["head_to_origin_cm"]); cal = 0.0
    FAM = [(0, 650, "low / skeletal"), (650, 950, "CH-oop"), (950, 1100, "ring / CH-ip"), (1100, 1250, "CH-ip-bend"),
           (1250, 1500, "CC-stretch/CH-ip"), (1500, 1650, "CC-stretch"), (1650, 2950, "overtone / combination"), (2950, 3200, "CH-stretch")]
    rows = []
    for b in T["bands"]:
        txt = str(b["experiment_cm"]); nu = float(txt)
        dec = len(txt.split(".")[1]) if "." in txt else 0
        u_read = 0.5 * 10 ** (-dec)
        fam = next((lab for lo, hi, lab in FAM if lo <= nu < hi), "?")
        if b["symmetry"] == "b3u" and nu < 1000: fam = "CH-oop / out-of-plane (b3u)"
        u_band = math.sqrt(res ** 2 + u_read ** 2 + h2o ** 2)
        rows.append({"mode": b["mode"], "symmetry": b["symmetry"], "position_cm": nu, "printed_as": txt, "family": fam,
                     "band_type": {"b1u": "a/b-type, in-plane", "b2u": "a/b-type, in-plane", "b3u": "c-type, out-of-plane"}[b["symmetry"]],
                     "resolution_term_cm": res, "reading_precision_cm": u_read, "head_to_origin_cm": h2o, "u_T_cm": 0.0,
                     "u_band_cm": round(u_band, 3), "calc_cane_cm": b.get("calc_cm"), "flag": b.get("flag", ""),
                     "decidable_at_candidate_margins": {str(t): bool(u_band < t) for t in CONSTANTS["candidate_margins_cm"]}})
    tag = Path(a.table).stem
    result = {"molecule": a.molecule, "source": T["source"], "source_file": Path(a.table).name, "source_sha256": sha256(a.table),
              "source_class": T["source_class"], "temperature_K": T["temperature_K"], "notes": T["notes"],
              "constants_used": {"resolution_cm": res, "head_to_origin_cm": h2o, "u_T": "0 (decision 21)", "reading_precision": "half the last printed digit"},
              "scored_bands": rows, "printed_by": "probes/m03_band_uncertainty.py --table", "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
    (out_dir / f"SCOREBOARD_{a.molecule}_{tag}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    L = [f"# Scoreboard — {a.molecule} — {T['source'].split(' — ')[0]} ({tag}) — probe 2a, {result['date']}", "",
         f"Source class: **{T['source_class']}**, {T['temperature_K']} K; transcription `{Path(a.table).name}`, sha256 `{result['source_sha256'][:16]}…`. "
         f"u_band = √(res² + reading² + head-to-origin²) with res = {res} cm⁻¹ (the paper's resolution), reading = half the last printed digit, "
         f"head-to-origin = {h2o} cm⁻¹ (decision 21's labelled upper bound), u_T = 0 (the fundamental is resolved from its hot bands). No intensities in this source.", "",
         "| mode | irrep | band type | position (cm⁻¹, as printed) | family | reading | **u_band** | Cané calc. | decidable at 2 / 5 / 10 | flag |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        d = r["decidable_at_candidate_margins"]
        L.append(f"| {r['mode']} | {r['symmetry']} | {r['band_type']} | **{r['printed_as']}** | {r['family']} | {r['reading_precision_cm']} | **{r['u_band_cm']}** | {r['calc_cane_cm']} | {' / '.join('yes' if d[str(t)] else 'no' for t in CONSTANTS['candidate_margins_cm'])} | {r['flag']} |")
    L += ["", "Notes from the transcription: " + " ".join(T["notes"]), "",
          "Matching to the pipeline's DFT modes (irrep, family by mode vector) waits for the naphthalene dry-run mode table; the family column is the frequency-range rule plus the paper's symmetry. Printed by `probes/m03_band_uncertainty.py --table`."]
    (out_dir / f"SCOREBOARD_{a.molecule}_{tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", default="benzene")
    ap.add_argument("--jdx", default=str(HERE / "scoreboards/benzene/C71432_quantir_res1.93_boxcar.jdx"))
    ap.add_argument("--tag", default="quantir_1p93")
    ap.add_argument("--table", default=None, help="a transcribed band table (JSON) instead of a JCAMP record: source class 'resolved fundamental' (decision 21)")
    ap.add_argument("--resolution-cm", type=float, default=None, help="override the record's RESOLUTION (document why)")
    a = ap.parse_args()
    if a.table:
        return table_mode(a)
    C_ = CONSTANTS
    out_dir = HERE / "results_m03" / a.molecule; out_dir.mkdir(parents=True, exist_ok=True)
    stageA = json.load(open(HERE / "results_dryrun" / a.molecule / "stageA.json"))
    sym = json.load(open(HERE / "results_dryrun" / a.molecule / "stageC_symmetry_prior.json"))
    freqs = np.array(stageA["freq_low_cm"], float); fams = stageA["families"]; labels = sym["labels"]
    meta, x, y, step = parse_jcamp(a.jdx)
    if len(y) != int(meta["NPOINTS"]): print(f"NOT_RUN: parsed {len(y)} of {meta['NPOINTS']} points"); sys.exit(1)
    T_rec = meta.get("TEMPERATURE", "?"); res_rec = float(meta["RESOLUTION"]) if "RESOLUTION" in meta else None
    res = a.resolution_cm if a.resolution_cm is not None else res_rec
    # noise from the quiet window (MAD of the linearly detrended signal)
    w0, w1 = C_["noise_window_cm"]; m = (x >= w0) & (x <= w1)
    p = np.polyfit(x[m], y[m], 1); r = y[m] - np.polyval(p, x[m]); noise = 1.4826 * np.median(np.abs(r - np.median(r)))
    # peaks above the S/N threshold
    peaks = []
    for i in range(1, len(y) - 1):
        if y[i] > y[i - 1] and y[i] >= y[i + 1] and y[i] > C_["peak_min_snr"] * noise:
            a_, b_, c_ = y[i - 1], y[i], y[i + 1]; den = a_ - 2 * b_ + c_
            sh = 0.5 * (a_ - c_) / den if den else 0.0
            peaks.append((i, float(x[i] + sh * step), float(b_ - 0.25 * (a_ - c_) * sh)))
    # temperature term per family (Bose rule; floor slope; nu_m from the DFT modes below the cutoff)
    bath = freqs[freqs < C_["bath_mode_cutoff_cm"]]; nu_m = float(bath.mean())
    theta = HC_OVER_K * nu_m; nbar = 1.0 / math.expm1(theta / C_["T_ref_K"])
    u296 = C_["chi_floor_cm_per_K"] * theta * nbar; u296_linear = C_["chi_floor_cm_per_K"] * C_["T_ref_K"]
    # scored set: IR-active DFT modes, one row per degenerate block
    rows, used = [], set()
    for k in range(len(freqs)):
        if not any(l in C_["irreps_ir_active_D6h"] for l in labels[k]): continue
        blk = tuple(j for j in range(len(freqs)) if abs(freqs[j] - freqs[k]) < 1.0 and labels[j] == labels[k])
        if blk in used: continue
        used.add(blk)
        lo_w, hi_w = C_["match_window_rel"][0] * freqs[k], C_["match_window_rel"][1] * freqs[k]
        cand = [pk for pk in peaks if lo_w <= pk[1] <= hi_w]
        row = {"dft_mode_index": list(blk), "irrep": "+".join(labels[k]), "family": fams[k], "omega_dft_cm": round(float(freqs[k]), 1),
               "match_window_cm": [round(lo_w, 1), round(hi_w, 1)]}
        if not cand:
            row.update(status="no band above threshold in window"); rows.append(row); continue
        ipk, xpk, ypk = max(cand, key=lambda t: t[2])
        lo, hi = band_window(x, y, ipk, C_["band_edge_k_sigma"], noise, C_["band_max_halfwidth_cm"])
        xs, ys = x[lo:hi + 1], y[lo:hi + 1]
        area_alpha = float(np.trapezoid(ys, xs))                        # (µmol/mol)^-1 m^-1 cm^-1
        sig = alpha_to_sigma_cm2(ys, C_["T_ref_K"], C_["P_ref_Pa"])
        A_km = float(np.trapezoid(sig, xs)) * N_A / 1e5                # cm/molecule → km/mol
        centroid = float(np.trapezoid(xs * ys, xs) / area_alpha)
        width = float(fwhm(x, y, ipk)); snr = float(ypk / noise)
        u_c = width / (2 * snr)
        u_band = math.sqrt(res ** 2 + u_c ** 2 + C_["calibration_term_cm"] ** 2 + u296 ** 2)
        u_band_noT = math.sqrt(res ** 2 + u_c ** 2 + C_["calibration_term_cm"] ** 2)
        cert = not any(w[0] <= xpk <= w[1] for w in C_["non_certified_windows_cm"])
        u_A_source = 0.5 * C_["intensity_rel_unc_k2"] * A_km
        u_A_base = float(noise * (xs[-1] - xs[0])) / area_alpha * A_km if area_alpha else float("nan")
        row.update(status="scored", peak_cm=round(xpk, 2), centroid_cm=round(centroid, 2), peak_minus_centroid_cm=round(xpk - centroid, 2),
                   window_cm=[round(float(xs[0]), 1), round(float(xs[-1]), 1)], fwhm_cm=round(width, 2), snr_peak=round(snr, 0),
                   resolution_term_cm=res, centroid_precision_cm=round(u_c, 4), calibration_term_cm=C_["calibration_term_cm"],
                   u_296_cm=round(u296, 2), u_band_cm=round(u_band, 2), u_band_without_T_cm=round(u_band_noT, 3),
                   ratio_obs_dft=round(xpk / freqs[k], 4),
                   intensity_km_per_mol=round(A_km, 2), u_intensity_source_km_per_mol=round(u_A_source, 2),
                   u_intensity_baseline_km_per_mol=round(u_A_base, 2), intensity_certified=cert,
                   integrated_alpha=area_alpha,
                   decidable_at_candidate_margins={str(t): bool(u_band < t) for t in C_["candidate_margins_cm"]})
        rows.append(row)
    scored_pos = {r["peak_cm"] for r in rows if r.get("status") == "scored"}
    windows = [r["window_cm"] for r in rows if r.get("status") == "scored"]
    extras = [{"peak_cm": round(pk[1], 2), "rel_height": round(pk[2] / max(p[2] for p in peaks), 3)} for pk in peaks
              if not any(w[0] <= pk[1] <= w[1] for w in windows) and pk[2] > 0.02 * max(p[2] for p in peaks)]
    result = {"molecule": a.molecule, "source_file": str(Path(a.jdx).name), "source_sha256": sha256(a.jdx),
              "record": {k: meta.get(k) for k in ("TITLE", "ORIGIN", "$NIST SOURCE", "STATE", "TEMPERATURE", "PRESSURE", "RESOLUTION",
                                                   "DATA PROCESSING", "YUNITS", "DELTAX", "NPOINTS", "FIRSTX", "LASTX")},
              "source_class": "cell (quantitative, flow, N2-broadened; item 56)", "stated_temperature": T_rec,
              "resolution_used_cm": res, "noise_alpha_units": noise, "noise_window_cm": C_["noise_window_cm"],
              "temperature_term": {"nu_m_cm": round(nu_m, 1), "bath_modes_cm": [round(float(v), 1) for v in bath], "theta_K": round(theta, 1),
                                   "nbar_296": round(nbar, 4), "u_296_bose_cm": round(u296, 2), "u_296_linear_bound_cm": round(u296_linear, 2)},
              "constants": C_, "scored_bands": rows, "unassigned_maxima_above_2pct": extras,
              "printed_by": "probes/m03_band_uncertainty.py", "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
    js = out_dir / f"SCOREBOARD_{a.molecule}_{a.tag}.json"; js.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    table_sha = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    L = [f"# Scoreboard — {a.molecule} — NIST Quantitative IR record ({a.tag}) — probe 2a, {result['date']}", "",
         f"Source `{result['source_file']}`, sha256 `{result['source_sha256'][:16]}…`; record: {meta.get('$NIST SOURCE')}, {meta.get('ORIGIN')}, "
         f"state {meta.get('STATE')}, temperature {T_rec} (record header; Chu 1999 §2.3: coefficients corrected to 296 K and 760 Torr), "
         f"resolution {res_rec} cm⁻¹ (record header; DELTAX {meta.get('DELTAX')} not used), {meta.get('DATA PROCESSING')}, y in {meta.get('YUNITS')}, "
         f"{meta.get('NPOINTS')} points {meta.get('FIRSTX')}–{meta.get('LASTX')} cm⁻¹.", "",
         f"Baseline noise (MAD, linear detrend) in {w0:.0f}–{w1:.0f} cm⁻¹: {noise:.3e} (record units). "
         f"Temperature term (Ladder dated note 2026-09-06; item 52 model): bath modes below {C_['bath_mode_cutoff_cm']:.0f} cm⁻¹ = "
         f"{', '.join(f'{v:.0f}' for v in bath)} → ν_m = {nu_m:.0f} cm⁻¹ (θ = {theta:.0f} K, n̄(296) = {nbar:.3f}); "
         f"χ_F = floor {C_['chi_floor_cm_per_K']} cm⁻¹ K⁻¹ (no measured benzene slope) → **u_296 = {u296:.2f} cm⁻¹** (linear bound {u296_linear:.1f}). "
         f"**Decision 29 (2026-09-10):** on this room-temperature source u_T is the pipeline's computed 0→296 K shift per band ±30 % "
         f"once the DFT anharmonic constants exist (NOT_RUN); the floor is printed until then and the u_band column carries it.", "",
         "| DFT mode(s) | irrep | family | ω_DFT | match window | peak (cm⁻¹) | centroid | integration window | FWHM | S/N | res | u_c | u_296 | **u_band** | u_band w/o T | obs/DFT | A (km/mol) | u_A src | u_A base | certified | decidable at 2 / 5 / 10 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("status") != "scored":
            L.append(f"| {r['dft_mode_index']} | {r['irrep']} | {r['family']} | {r['omega_dft_cm']} | {r['match_window_cm']} | — {r['status']} |" + " |" * 15); continue
        d = r["decidable_at_candidate_margins"]
        L.append(f"| {r['dft_mode_index']} | {r['irrep']} | {r['family']} | {r['omega_dft_cm']} | {r['match_window_cm'][0]}–{r['match_window_cm'][1]} | **{r['peak_cm']}** | {r['centroid_cm']} | {r['window_cm'][0]}–{r['window_cm'][1]} | {r['fwhm_cm']} | {r['snr_peak']:.0f} | {r['resolution_term_cm']} | {r['centroid_precision_cm']} | {r['u_296_cm']} | **{r['u_band_cm']}** | {r['u_band_without_T_cm']} | {r['ratio_obs_dft']} | {r['intensity_km_per_mol']} | {r['u_intensity_source_km_per_mol']} | {r['u_intensity_baseline_km_per_mol']} | {'yes' if r['intensity_certified'] else '**no (Chu §3.3 window)**'} | {' / '.join('yes' if d[str(t)] else 'no' for t in C_['candidate_margins_cm'])} |")
    L += ["", f"Unassigned maxima above 2 % of the strongest band (combination / overtone bands; not scored): " +
          (", ".join(f"{e['peak_cm']} ({e['rel_height']:.2f})" for e in extras) if extras else "none"), "",
          "Columns: peak = parabolic apex of the strongest maximum in the window; centroid = intensity-weighted over the integration window "
          f"(the contiguous region above {C_['band_edge_k_sigma']:.0f}σ baseline noise, at most ±{C_['band_max_halfwidth_cm']:.0f} cm⁻¹); u_c = FWHM/(2·S/N); res = the record's stated "
          f"resolution; calibration term {C_['calibration_term_cm']} cm⁻¹ (Chu §2.4) inside u_band; u_band = √(res² + u_c² + cal² + u_296²); "
          f"A = ∫σ dν̃ with σ = α·ln10/n₁ at {C_['T_ref_K']:.0f} K, {C_['P_ref_Pa']:.0f} Pa; u_A src = {C_['intensity_rel_unc_k2']*50:.2f} % (Chu Table 3, k = 2 → k = 1); "
          "u_A base = noise × window width; 'decidable' compares u_band with **candidate** margins — the pilot note fixes the margin per family.", "",
          "Constants (all pilot-note candidates): " + json.dumps(C_, ensure_ascii=False), "",
          f"Table sha256 `{table_sha[:16]}…`. Printed by `probes/m03_band_uncertainty.py`; the JSON beside this file has the full precision."]
    md = out_dir / f"SCOREBOARD_{a.molecule}_{a.tag}.md"; md.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))

if __name__ == "__main__":
    main()
