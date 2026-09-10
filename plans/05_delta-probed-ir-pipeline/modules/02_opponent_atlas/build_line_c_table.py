#!/usr/bin/env python
"""Module 02 — line C (Mai et al. 2025, MLMD anharmonic spectra) read into the opponent atlas.

Source: the Zenodo archive DOI 10.5281/zenodo.14998197 (version 10.5281/zenodo.15771437,
`Supplementary.zip`), fetched 2026-09-10 with the user's permission; data CC BY-NC-SA 4.0, code
Apache-2.0. Inside, `outputs/IR_txt_phdb_1704/IR_txt_{50,300,600}K_qm0.zip` hold one text file per
PAHdb species (`<formula>_<uid>.txt`): a spectrum on a 1 cm⁻¹ grid, 300–3800 cm⁻¹, "Normalized
intensity" (the code's default normalises the total to 1; `qm0` = no quantum correction of the
cross-section). `outputs/IR_txt_EXP/IR_txt_EXP_qm0.zip` holds the 49 experimentally tested species.

What line C therefore is, for the comparison: **positions only** (band maxima of a broadened,
temperature-dependent spectrum) at three temperatures; no absolute intensities, no stick list. The
atlas extracts local maxima above a relative threshold with a parabolic apex on the 1 cm⁻¹ grid and
keeps the spectra's provenance (file name inside the zip, sha256 of the outer archive). The
threshold and the minimum peak separation are printed as pilot-note candidates. Nothing is trained.

Outputs (./out/lineC_mai2025/): species.csv (uid, formula, n_c, which temperatures exist, ladder
rung), peaks.csv.gz (uid, T_K, position_cm, relative_height, family), SUMMARY.md.
"""
import argparse, csv, gzip, hashlib, io, re, zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
CONSTANTS = {"peak_rel_threshold": 0.05, "min_separation_cm": 3.0, "grid_note": "1 cm-1 grid 300-3800; parabolic apex"}
FAMILY_RULE = [(0.0, 650.0, "low / skeletal"), (650.0, 950.0, "CH-oop"), (950.0, 1100.0, "ring / CH-ip"), (1100.0, 1250.0, "CH-ip-bend"),
               (1250.0, 1500.0, "CC-stretch/CH-ip"), (1500.0, 1650.0, "CC-stretch"), (1650.0, 2950.0, "overtone / combination"),
               (2950.0, 3200.0, "CH-stretch"), (3200.0, 1e9, "above 3200")]
LADDER = {"C6H6": "R0", "C10H8": "R1", "C16H10": "R2", "C18H12": "R2", "C24H12": "R3"}

def family(nu):
    for lo, hi, lab in FAMILY_RULE:
        if lo <= nu < hi: return lab
    return "?"

def peaks(x, y, rel, sep):
    ymax = y.max()
    if ymax <= 0: return []
    out = []
    for i in range(1, len(y) - 1):
        if y[i] > y[i - 1] and y[i] >= y[i + 1] and y[i] >= rel * ymax:
            a, b, c = y[i - 1], y[i], y[i + 1]; den = a - 2 * b + c
            sh = 0.5 * (a - c) / den if den else 0.0
            out.append((float(x[i] + sh * (x[1] - x[0])), float(b / ymax)))
    out.sort(key=lambda t: -t[1]); kept = []
    for p, h in out:
        if all(abs(p - q) >= sep for q, _ in kept): kept.append((p, h))
    return sorted(kept)

def read_spectrum(data):
    xs, ys = [], []
    for line in io.StringIO(data.decode("utf-8", "replace")):
        if line.startswith("#") or not line.strip(): continue
        a, b = line.split()[:2]; xs.append(float(a)); ys.append(float(b))
    return np.array(xs), np.array(ys)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", default=str(HERE / "data/Mai2025_zenodo_15771437_Supplementary.zip"))
    a = ap.parse_args()
    arc = Path(a.archive)
    if not arc.exists(): print("NOT_RUN: archive not found"); return
    h = hashlib.sha256(arc.read_bytes()).hexdigest()
    out = HERE / "out" / "lineC_mai2025"; out.mkdir(parents=True, exist_ok=True)
    species, rows, per_T = {}, [], Counter()
    with zipfile.ZipFile(arc) as z:
        inner = [n for n in z.namelist() if re.search(r"outputs/IR_txt_phdb_1704/IR_txt_(\d+)K_qm0\.zip$", n)]
        inner += [n for n in z.namelist() if n.endswith("outputs/IR_txt_EXP/IR_txt_EXP_qm0.zip")]
        for name in inner:
            m = re.search(r"IR_txt_(\d+)K_qm0", name); T = int(m.group(1)) if m else None
            setname = f"{T}K" if T else "EXP"
            with zipfile.ZipFile(io.BytesIO(z.read(name))) as zz:
                for fn in zz.namelist():
                    mm = re.search(r"([A-Za-z0-9]+)_(\d+)(?:_qm0)?\.txt$", fn)
                    if not mm: continue
                    formula, uid = mm.group(1), mm.group(2)
                    x, y = read_spectrum(zz.read(fn))
                    per_T[setname] += 1
                    s = species.setdefault(uid, {"uid": uid, "formula": formula, "n_c": int((re.search(r"C(\d+)", formula) or [0, 0])[1] or 0),
                                                 "sets": set(), "grid": f"{x.min():.0f}-{x.max():.0f}/{len(x)}", "rung": LADDER.get(formula, "")})
                    s["sets"].add(setname)
                    for p, rh in peaks(x, y, CONSTANTS["peak_rel_threshold"], CONSTANTS["min_separation_cm"]):
                        rows.append({"uid": uid, "formula": formula, "set": setname, "position_cm": round(p, 2), "rel_height": round(rh, 4), "family": family(p)})
    with open(out / "species.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["uid", "formula", "n_c", "sets", "grid", "rung"])
        for s in sorted(species.values(), key=lambda s: (s["n_c"], s["uid"])): w.writerow([s["uid"], s["formula"], s["n_c"], "+".join(sorted(s["sets"])), s["grid"], s["rung"]])
    with gzip.open(out / "peaks.csv.gz", "wt", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    ladder_hits = {r: [(s["uid"], s["formula"], "+".join(sorted(s["sets"]))) for s in species.values() if s["rung"] == r] for r in ("R0", "R1", "R2", "R3")}
    big = sorted([(s["n_c"], s["uid"], s["formula"]) for s in species.values()], reverse=True)[:5]
    L = [f"# Opponent atlas — line C, Mai et al. 2025 MLMD spectra — {datetime.now():%Y-%m-%d %H:%M}", "",
         f"Source `{arc.name}` (Zenodo 10.5281/zenodo.15771437), sha256 `{h}`, {arc.stat().st_size:,} bytes; inner sets read: {dict(per_T)}.", "",
         f"**Species: {len(species):,}**; peaks extracted: {len(rows):,} (threshold {CONSTANTS['peak_rel_threshold']} of the spectrum's maximum, minimum separation {CONSTANTS['min_separation_cm']} cm⁻¹, {CONSTANTS['grid_note']}); "
         "intensities are normalised per spectrum (the archive's `Inten_MD (Normalized intensity)`), so line C carries **positions only**.", "",
         f"Largest species: {big}. Ladder: " + "; ".join(f"{r}: {v if v else 'absent'}" for r, v in ladder_hits.items()), "",
         "Peak-extraction constants are pilot-note candidates; nothing is trained here."]
    (out / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))

if __name__ == "__main__":
    main()
