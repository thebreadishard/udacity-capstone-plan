"""Module 03 — is the shape score's family-weight term measuring physics or the free-electron-laser measurement? (2026-09-14, the two-hourly
check's finding step.) The shape score's first column showed line A putting 24-42 percentage points more intensity into the C-H
out-of-plane family than the jet-cooled FELIX lists do. IR-UV ion-dip intensities are not linear in the absorption cross-section, so the
FELIX family weights could be the outlier rather than DFT. Cheapest test with data in hand: a THIRD, independent intensity measurement of
the same molecules — the argon-matrix spectra of PAHdb's experimental library (Module 02 out/experimental_3.10; relative intensities,
Mattioda et al. 2020), which exist for tetracene (uid 282), coronene (18) and HBC (105). Per molecule and family (550-2000 cm-1 window)
the share of the total intensity is printed for FELIX (jet), matrix (10 K argon) and line A (PAHdb theoretical v4.00 as served).
Reading, written before the run: if matrix and line A agree on the C-H out-of-plane share and FELIX stands apart, the FELIX weights carry
a measurement effect and the shape score's family-weight term must be read against the matrix column as well; if matrix agrees with FELIX,
the DFT intensities are wrong by the amount printed. Output: out/shape_family_weights_check.md."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_lab_tables import FAMILY_RULE  # noqa: E402

A02 = HERE.parent / "02_opponent_atlas" / "out"
MOLS = {"tetracene": (282, "out/cold_columns_items61_62.csv"), "coronene": (18, "out/cold_columns_items61_62.csv"), "hexa(peri)benzocoronene": (105, "out/cold_columns_item62_grandpahs.csv")}
WINDOW = (550.0, 2000.0)
FAMS = [lab for lo, hi, lab in FAMILY_RULE if hi > WINDOW[0] and lo < WINDOW[1]]
WIN = {lab: (lo, hi) for lo, hi, lab in FAMILY_RULE}


def shares(f, i):
    m = (f >= WINDOW[0]) & (f < WINDOW[1]); f, i = f[m], i[m]; tot = i.sum()
    return {fam: (float(i[(f >= WIN[fam][0]) & (f < WIN[fam][1])].sum() / tot) if tot else np.nan) for fam in FAMS}


def main():
    th = pd.read_csv(A02 / "theoretical_4.00" / "bands.csv.gz"); ex = pd.read_csv(A02 / "experimental_3.10" / "bands.csv.gz")
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "window_cm": WINDOW, "molecules": {}}
    L = [f"# Family-weight check: jet (FELIX) vs argon matrix vs line A, 550–2000 cm⁻¹ ({out['date']})", "",
         "Share of the total intensity in the window, per family (%). FELIX: relative intensities of the jet-cooled lists (items 61–62); matrix: PAHdb experimental library v3.10 relative intensities (Module 02); line A: PAHdb theoretical v4.00 as served. Reading rule in the script header.", ""]
    for mol, (uid, labfile) in MOLS.items():
        lab = pd.read_csv(HERE / labfile); lab = lab[(lab["species"] == mol) & (lab["laser"] == "FELIX")]
        s_lab = shares(lab["frequency_cm"].to_numpy(float), pd.to_numeric(lab["rel_intensity"], errors="coerce").fillna(0).to_numpy())
        e = ex[(ex["uid"] == uid) & (ex["charge"] == 0)]; s_ex = shares(e["frequency_cm"].to_numpy(float), e["intensity_km_mol"].to_numpy(float))
        t = th[(th["uid"] == uid) & (th["charge"] == 0)]; s_th = shares(t["frequency_cm"].to_numpy(float), t["intensity_km_mol"].to_numpy(float))
        out["molecules"][mol] = {"uid": uid, "n_matrix_bands_window": int(((e["frequency_cm"] >= 550) & (e["frequency_cm"] < 2000)).sum()), "felix": s_lab, "matrix": s_ex, "lineA": s_th}
        L += [f"## {mol} (uid {uid}; matrix bands in window: {out['molecules'][mol]['n_matrix_bands_window']})", "", "| family | FELIX jet % | matrix % | line A % | matrix − FELIX (pp) | line A − matrix (pp) |", "|---|---|---|---|---|---|"]
        for fam in FAMS:
            a, b, c = 100 * s_lab[fam], 100 * s_ex[fam], 100 * s_th[fam]
            L.append(f"| {fam.split(' (')[0]} | {a:.1f} | {b:.1f} | {c:.1f} | {b - a:+.1f} | {c - b:+.1f} |")
        L.append("")
    (HERE / "out" / "shape_family_weights_check.md").write_text("\n".join(L), encoding="utf-8")
    json.dump(out, open(HERE / "out" / "shape_family_weights_check.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
