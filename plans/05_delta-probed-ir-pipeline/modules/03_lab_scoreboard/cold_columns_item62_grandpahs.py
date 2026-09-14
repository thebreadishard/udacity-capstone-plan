"""Module 03 — the remaining jet-cooled ("cold") columns of item 62: ovalene, hexa(peri)benzocoronene (HBC) and peropyrene,
transcribed 2026-09-14 from Lemmens, Rijs & Buma, ApJ 923, 238 (2021), Table A1 (pages 9-10; the page renders read on 2026-09-13/14,
`Papers/_txt/pages/Lemmens_2021_p9.png`, `_p10.png`). Experimental columns only (Exp cm-1, Rel. Int.); the calculated columns are not used.
Serves the shape score pre-registered on 2026-09-14 (`notes/PreRegistration_2026-09-14_Shape_Score_Cold_Spectra.md`, §1).

Block boundaries as resolved with the user on 2026-09-13: page 9 carries coronene (transcribed on 13 September in cold_columns_items61_62.py),
ovalene, and the first six HBC bands (276.8-746.1); page 10 opens with a block mis-headed "Coronene" (770.1 1.00, 819.2, ...) that is the
CONTINUATION OF HBC, followed by peropyrene. Peropyrene's frequencies are printed to two decimals and its intensities are normalised so
that 797.00 = 1.00 with 1576.10 printed as 1.16 — kept as printed. As for coronene, the 3 um bands (OPO) and the 5-18 um bands (FELIX) carry
separate normalisations in the source.

u_band for a cold column (Ladder floor form): u_T = 0 (jet-cooled); u_res = the stated laser bandwidth, FELIX "0.5 %-1 %" (the 1 % end taken),
OPO ~0.1 cm-1 for the 3 um bands; u_c not derivable (no S/N tabulated) -> u_band = u_res is a LOWER BOUND, labelled so.
Every value is asserted to occur verbatim in the text extract Papers/_txt/lemmens2021.txt (a transcription check, not a parse).
Output: out/cold_columns_item62_grandpahs.csv and .md."""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_lab_tables import family as window_family  # noqa: E402

REPO = HERE.parents[3]
TXT = REPO / "Papers/_txt/lemmens2021.txt"
CONSTANTS = {"u_res_rule": {"FELIX": "1 % of the band frequency (stated bandwidth 0.5-1 %)", "OPO": "0.1 cm-1 (stated bandwidth)"},
             "u_c": "not derivable: no S/N tabulated -> empty; u_band = u_res is a lower bound", "u_T": 0.0, "opo_range_cm": [2950, 3150],
             "source": "Lemmens, Rijs & Buma 2021, ApJ 923, 238, Table A1 pages 9-10 (experimental columns), DOI 10.3847/1538-4357/ac2f9d",
             "block_boundary": "page-10 block headed 'Coronene' (770.1 1.00 ...) read as the continuation of HBC (user, 2026-09-13)"}
OVALENE = [("276.0", "0.03"), ("340.4", "0.05"), ("389.9", "0.06"), ("421.8", "0.05"), ("546.6", "0.18"), ("577.5", "0.04"), ("638.3", "0.21"), ("765.2", "0.09"),
           ("779.4", "0.07"), ("839.2", "0.69"), ("884.0", "1.00"), ("918.7", "0.25"), ("973.8", "0.14"), ("1073.4", "0.12"), ("1120.5", "0.08"), ("1165.4", "0.71"),
           ("1245.8", "0.53"), ("1277.7", "0.13"), ("1315.3", "0.56"), ("1421.0", "0.49"), ("1533.5", "0.22"), ("1630.5", "0.53"), ("1689.0", "0.18"), ("1723.8", "0.17"),
           ("1765.5", "0.18"), ("1909.9", "0.26"), ("3008.67", "0.08"), ("3029.28", "0.16"), ("3033.62", "0.14"), ("3046.11", "1.00"), ("3053.22", "0.20"), ("3065.77", "0.52")]
HBC = [("276.8", "0.05"), ("530.5", "0.02"), ("548.0", "0.05"), ("594.4", "0.12"), ("680.7", "0.18"), ("746.1", "0.11"),
       ("770.1", "1.00"), ("819.2", "0.03"), ("1035.4", "0.08"), ("1098.9", "0.67"), ("1232.1", "0.26"), ("1312.0", "0.16"), ("1384.0", "0.75"), ("1414.9", "0.17"),
       ("1501.7", "0.26"), ("1582.4", "0.61"), ("1628.2", "0.06"), ("1647.6", "0.10"), ("1686.3", "0.06"), ("1709.0", "0.07"), ("1726.0", "0.05"), ("1772.4", "0.18"),
       ("1847.3", "0.09"), ("1923.5", "0.12"), ("3007.2", "0.04"), ("3028.6", "0.64"), ("3046.1", "0.06"), ("3055.3", "0.27"), ("3061.4", "0.37"), ("3071.5", "0.36"),
       ("3087.5", "0.40"), ("3100.2", "1.00"), ("3109.2", "0.50")]
PEROPYRENE = [("182.40", "0.04"), ("186.00", "0.05"), ("221.80", "0.08"), ("492.90", "0.03"), ("506.10", "0.05"), ("548.50", "0.07"), ("666.70", "0.19"), ("749.80", "0.16"),
              ("772.00", "0.06"), ("797.00", "1.00"), ("837.20", "0.94"), ("869.20", "0.16"), ("965.40", "0.22"), ("1018.50", "0.02"), ("1050.50", "0.45"), ("1112.00", "0.25"),
              ("1155.00", "0.11"), ("1179.10", "0.81"), ("1231.90", "0.28"), ("1267.50", "0.07"), ("1293.60", "0.50"), ("1326.90", "0.95"), ("1384.60", "0.29"), ("1420.40", "0.93"),
              ("1482.80", "0.76"), ("1542.60", "0.12"), ("1576.10", "1.16"), ("1598.50", "0.13")]
SPECIES = [("ovalene", "C32H14", OVALENE, "page 9"), ("hexa(peri)benzocoronene", "C42H18", HBC, "pages 9-10 (continuation block mis-headed 'Coronene')"), ("peropyrene", "C26H14", PEROPYRENE, "page 10")]


def main():
    t = TXT.read_text(encoding="utf-8", errors="replace")
    rows = []
    for species, formula, data, pages in SPECIES:
        missing = [f for f, _ in data if f not in t]
        assert not missing, f"{species}: transcribed values not found verbatim in the text extract: {missing}"
        for f, i in data:
            nu = float(f); opo = CONSTANTS["opo_range_cm"][0] <= nu <= CONSTANTS["opo_range_cm"][1]; u_res = 0.1 if opo else 0.01 * nu
            rows.append({"item": "62", "species": species, "formula": formula, "frequency_cm": nu, "rel_intensity": float(i), "laser": "OPO" if opo else "FELIX",
                         "u_res_cm": round(u_res, 2), "u_c_cm": "", "u_T_cm": 0.0, "u_band_cm_lower_bound": round(u_res, 2), "family": window_family(nu),
                         "temperature": "jet-cooled (molecular beam)", "table_pages": pages, "source": CONSTANTS["source"]})
    out = HERE / "out"; out.mkdir(exist_ok=True)
    with open(out / "cold_columns_item62_grandpahs.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    L = [f"# Cold columns — item 62, the remaining GrandPAHs: ovalene, HBC, peropyrene ({datetime.now():%Y-%m-%d})", "",
         "Transcribed from Table A1 of Lemmens, Rijs & Buma 2021 (pages 9–10 rendered and read; every value asserted to occur verbatim in the text extract). u_T = 0 (jet-cooled); u_res = the stated bandwidth (FELIX ≈ 1 % of ν; OPO 0.1 cm⁻¹ at 3 µm); u_c not derivable → **u_band is a lower bound**. "
         "Families by the frequency-window rule. The page-10 block headed \"Coronene\" is HBC's continuation (resolved with the user 2026-09-13). Peropyrene's intensities are printed relative to 797.00 = 1.00, with 1576.10 = 1.16 as printed.", "",
         "| species | ν (cm⁻¹) | rel. int. | laser | u_res (cm⁻¹) | family |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['species']} | {r['frequency_cm']} | {r['rel_intensity']} | {r['laser']} | {r['u_res_cm']} | {r['family']} |")
    counts = {s: sum(1 for r in rows if r["species"] == s) for s, *_ in SPECIES}
    mid = {s: sum(1 for r in rows if r["species"] == s and 550 <= r["frequency_cm"] <= 2000) for s, *_ in SPECIES}
    L += ["", f"Counts: {counts}; of which in 550–2000 cm⁻¹ (the shape-score window): {mid}.", "", "Constants: " + json.dumps(CONSTANTS)]
    (out / "cold_columns_item62_grandpahs.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:6] + L[-3:]).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
