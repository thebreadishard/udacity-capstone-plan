"""Module 03 — the jet-cooled ("cold") columns for tetracene (item 61) and coronene (item 62), built 2026-09-13.

Sources (PDFs held locally, text extracts in Papers/_txt, the table pages rendered and read as images on 2026-09-13):
  item 61: Lemmens, Rap, Thunnissen, Mackie, Candian, Tielens, Rijs & Buma, A&A 628, A130 (2019), DOI 10.1051/0004-6361/201935631 (bibliography item 61, Crossref-verified), Table A.2
           "Measured bands of tetracene and pentacene with frequencies in (cm-1) and normalized intensities" (page 10; the header's
           "C10H12" is the paper's typo, tetracene is C18H12). Experimental columns only; the calculated columns are not used.
  item 62: Lemmens, Rijs & Buma, ApJ 923, 238 (2021), Table A1, page 9, block "Coronene" (experimental columns only).
           NOTE: page 10 carries a second block headed "Coronene" (770.1 1.00, 819.2, 1035.4, ...) that sits between the end of the
           hexa(peri)benzocoronene block (page 9 ends at 746.1) and peropyrene; it is read here as the CONTINUATION OF HBC with a
           mis-set species label, NOT as coronene, and is excluded. The user is asked to confirm from the PDF (flagged in PROVENANCE).
Values are transcribed literals, each asserted to occur verbatim in the text extract (a transcription check, not a parse).

u_band for a cold column (Ladder floor form): u_T = 0 (jet-cooled, no temperature term); u_res = the stated laser bandwidth — FELIX
"approximately 1 % of the photon frequency" (2019, lines 161-162; 2021 "0.5 %-1 %", the 1 % end taken), OPO "approximately 0.1 cm-1"
(2021) for the 3 um bands; u_c is NOT derivable (no S/N tabulated) and is left empty, so u_band = u_res is a LOWER BOUND, labelled so.
Families by Module 03's frequency-window rule (build_lab_tables.FAMILY_RULE). Output: out/cold_columns_items61_62.csv and .md."""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_lab_tables import family as window_family  # noqa: E402

REPO = HERE.parents[3]
TXT = {"61": REPO / "Papers/_txt/lemmens2019.txt", "62": REPO / "Papers/_txt/lemmens2021.txt"}
CONSTANTS = {"u_res_rule": {"FELIX": "1 % of the band frequency (stated bandwidth; 2019 ~1 %, 2021 0.5-1 %)", "OPO": "0.1 cm-1 (stated bandwidth, 2021)"},
             "u_c": "not derivable: no S/N tabulated -> empty; u_band = u_res is a lower bound", "u_T": 0.0, "opo_range_cm": [2950, 3150],
             "sources": {"61": "Lemmens et al. 2019, A&A 628, A130, Table A.2 (tetracene, experimental columns)", "62": "Lemmens, Rijs & Buma 2021, ApJ 923, 238, Table A1 page 9 (coronene block)"}}
# (frequency string as printed, relative intensity string or None)
TETRACENE = [("548.0", "0.19"), ("604.0", "0.11"), ("623.0", "0.05"), ("631.3", "0.04"), ("738.7", "1.00"), ("892.9", "0.96"), ("934.4", "0.21"), ("952.4", "0.18"),
             ("975.8", "0.06"), ("996.6", "0.29"), ("1049.4", "0.10"), ("1123.8", "0.35"), ("1081.3", "0.11"), ("1195.4", "0.16"), ("1289.1", "0.62"), ("1328.6", "0.42"),
             ("1381.7", "0.17"), ("1410.0", "0.32"), ("1457.7", "0.18"), ("1498.6", "0.13"), ("1536.9", "0.29"), ("1563.4", "0.08"), ("1574.4", "0.08"), ("1632.1", "0.28"),
             ("1670.6", "0.33"), ("1694.5", "0.48"), ("1767.0", "0.47"), ("1779.6", None), ("1809.5", "0.21"), ("1885.7", None), ("1902.9", "0.20"), ("1917.0", "0.22"),
             ("1947.8", None), ("1968.6", "0.03")]
CORONENE = [("121.1", "0.004"), ("381.1", "0.03"), ("549.2", "0.61"), ("770.1", "0.21"), ("854.6", "1.00"), ("1132.1", "0.19"), ("1208.1", "0.08"), ("1306.4", "0.35"),
            ("1607.1", "0.23"), ("1694", "0.09"), ("1774.4", "0.09"), ("1902.8", "0.12"), ("3024.88", "0.14"), ("3030.83", "0.52"), ("3036.62", "0.29"), ("3041.75", "0.29"),
            ("3053.72", "0.28"), ("3062.84", "0.51"), ("3066.84", "1.00"), ("3107.13", "0.11")]


def check_transcription(item, rows):
    t = TXT[item].read_text(encoding="utf-8", errors="replace")
    missing = [f for f, _ in rows if f not in t]
    return missing


def main():
    rows = []
    for item, species, formula, uid, data in (("61", "tetracene", "C18H12", None, TETRACENE), ("62", "coronene", "C24H12", "18", CORONENE)):
        miss = check_transcription(item, data)
        assert not miss, f"item {item}: transcribed values not found in the text extract: {miss}"
        for f, i in data:
            nu = float(f); opo = CONSTANTS["opo_range_cm"][0] <= nu <= CONSTANTS["opo_range_cm"][1]
            u_res = 0.1 if opo else 0.01 * nu
            rows.append({"item": item, "species": species, "formula": formula, "pahdb_uid_matrix": uid, "frequency_cm": nu, "rel_intensity": (float(i) if i else ""),
                         "laser": "OPO" if opo else "FELIX", "u_res_cm": round(u_res, 2), "u_c_cm": "", "u_T_cm": 0.0, "u_band_cm_lower_bound": round(u_res, 2),
                         "family": window_family(nu), "temperature": "jet-cooled (molecular beam)", "source": CONSTANTS["sources"][item]})
    out = HERE / "out"; out.mkdir(exist_ok=True)
    with open(out / "cold_columns_items61_62.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    L = [f"# Cold columns — jet-cooled band lists of tetracene (item 61) and coronene (item 62) ({datetime.now():%Y-%m-%d})", "",
         "Transcribed from the papers' tables (pages rendered and read on 2026-09-13; every value asserted to occur in the text extract). u_T = 0 (jet-cooled); "
         "u_res = stated laser bandwidth (FELIX ≈ 1 % of ν; OPO 0.1 cm⁻¹ at 3 µm); u_c not derivable (no S/N) → **u_band is a lower bound**. Families by the frequency-window rule.", "",
         "**Flag for the user:** the 2021 Table A1 continues on page 10 with a block headed \"Coronene\" (770.1 1.00, 819.2, 1035.4, 1098.9 …) directly after the hexa(peri)benzocoronene "
         "block ends (746.1) and before peropyrene; it is read as HBC's continuation with a mis-set label and excluded here. Confirm from the PDF before R3 scoring.", "",
         "| item | species | ν (cm⁻¹) | rel. int. | laser | u_res (cm⁻¹) | family |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['item']} | {r['species']} | {r['frequency_cm']} | {r['rel_intensity']} | {r['laser']} | {r['u_res_cm']} | {r['family']} |")
    n61 = sum(1 for r in rows if r["item"] == "61"); n62 = sum(1 for r in rows if r["item"] == "62")
    mid62 = [r for r in rows if r["item"] == "62" and 667 <= r["frequency_cm"] <= 1667]
    L += ["", f"Counts: tetracene {n61} bands (Table A.2 experimental column), coronene {n62} bands of which {len(mid62)} in 6–15 µm "
          f"({', '.join(str(r['frequency_cm']) for r in mid62)} — the bibliography's 'six tabulated 6–15 µm bands').", "", "Constants: " + json.dumps(CONSTANTS)]
    (out / "cold_columns_items61_62.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:8] + L[-3:]).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
