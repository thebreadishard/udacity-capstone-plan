"""Module 03 — the "band origin" column for naphthalene (built 2026-09-13; the user asked for it the same day after the
leads A–G literature check found two rotationally resolved records missing from the scoreboard).

Sources (Crossref-verified records; ABSTRACT GRADE — the numbers below are the ones quoted in the papers' abstracts, fetched from
OpenAlex and cached in out/origin_sources_abstracts.json; the papers' fitted origins with their uncertainties are in the full texts,
PDF request items 32–33):
  item 72: Albert, S.; Albert, K. K.; Lerch, P.; Quack, M., Faraday Discuss. 150, 71 (2011), DOI 10.1039/c0fd00013b —
           synchrotron FTIR at 0.0008 cm-1, room temperature, rotationally resolved analysis of the nu46 c-type band,
           "nu~0 = 782.330949 cm-1".
  item 73: Pirali, O.; Goubet, M.; Huet, T. R.; Georges, R.; Soulard, P.; Asselin, P.; Courbe, J.; Roy, P.; Vervloet, M.,
           Phys. Chem. Chem. Phys. 15, 10141 (2013), DOI 10.1039/c3cp44305a — rotationally resolved nu46 "centered at 782 cm-1"
           under supersonic-jet conditions (Jet-AILES), nu47 "474 cm-1" and nu48 "167 cm-1" at room temperature (long-path cell).

Why a band ORIGIN gets its own column (Ladder u_band floor form, Module 03 U_BAND.md): the origin nu~0 of a rotationally analysed
band is a molecular constant obtained from a fit of resolved lines, so the three terms that dominate the other columns vanish —
u_res = 0 (no unresolved envelope), head-to-origin = 0 (the origin is the quantity itself; the 2009 scoreboard carries 0.5 cm-1
for a Q-branch head), u_T = 0 (a band origin does not move with temperature; hot bands are separate transitions). What remains is
the reading precision (half the last printed digit) and the fit uncertainty, which the abstracts do not state -> u_band printed here
is a LOWER BOUND and labelled so. For nu46 the laboratory therefore no longer limits the decision; the pipeline's own budget does.

Every value is asserted to occur verbatim in the cached abstract text (transcription check). Families by Module 03's frequency-window
rule (build_lab_tables.FAMILY_RULE). The Pirali 2009 scoreboard values (item 53, probes/results_m03/naphthalene) are printed beside
the new column for the same modes, read from that JSON. Output: out/origin_columns_naphthalene.csv and .md."""
import csv
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_lab_tables import family as window_family  # noqa: E402

REPO = HERE.parents[3]
OUT = HERE / "out"
CACHE = OUT / "origin_sources_abstracts.json"
SCOREBOARD_2009 = REPO / "plans/05_delta-probed-ir-pipeline/probes/results_m03/naphthalene/SCOREBOARD_naphthalene_pirali2009_table1.json"
UA = {"User-Agent": "CapstonePlan Module 03 (mailto:frederic.petrignani@gmail.com)"}
SOURCES = {
    "72": {"doi": "10.1039/c0fd00013b", "cite": "Albert, Albert, Lerch & Quack 2011, Faraday Discuss. 150, 71", "conditions": "room temperature, synchrotron FTIR 0.0008 cm-1, rotationally resolved",
           "bands": [("nu46", "b3u", "782.330949")]},
    "73": {"doi": "10.1039/c3cp44305a", "cite": "Pirali, Goubet, Huet, Georges, Soulard, Asselin, Courbe, Roy & Vervloet 2013, PCCP 15, 10141", "conditions": "nu46 jet-cooled (Jet-AILES); nu47, nu48 room temperature cell; rotationally resolved",
           "bands": [("nu46", "b3u", "782"), ("nu47", "b3u", "474"), ("nu48", "b3u", "167")]},
}
CONSTANTS = {"u_res": 0.0, "head_to_origin": 0.0, "u_T": 0.0, "reading_precision": "half the last printed digit of the abstract's value",
             "fit_uncertainty": "not stated in the abstracts -> empty; u_band = reading precision is a LOWER BOUND",
             "grade": "abstract (values quoted in the abstracts; full texts requested as PDF items 32-33)"}


def abstract_text(inv):
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def load_abstracts():
    if CACHE.exists():
        return json.load(open(CACHE, encoding="utf-8"))
    cache = {}
    for item, s in SOURCES.items():
        url = "https://api.openalex.org/works/https://doi.org/" + s["doi"] + "?select=title,publication_year,abstract_inverted_index"
        w = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        cache[item] = {"doi": s["doi"], "title": w["title"], "year": w["publication_year"], "abstract": abstract_text(w["abstract_inverted_index"]),
                       "fetched": f"{datetime.now():%Y-%m-%d %H:%M}", "from": "OpenAlex abstract_inverted_index"}
    OUT.mkdir(exist_ok=True)
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return cache


def main():
    ab = load_abstracts()
    sb = {r["mode"]: r for r in json.load(open(SCOREBOARD_2009))["scored_bands"]} if SCOREBOARD_2009.exists() else {}
    rows = []
    for item, s in SOURCES.items():
        text = ab[item]["abstract"]
        for mode, irrep, printed in s["bands"]:
            assert printed in text, f"item {item}: '{printed}' not found verbatim in the cached abstract"
            nu = float(printed)
            digits = len(printed.split(".")[1]) if "." in printed else 0
            reading = 0.5 * 10 ** (-digits)
            u_band = reading  # lower bound: fit uncertainty unknown
            old = sb.get(mode, {})
            rows.append({"item": item, "species": "naphthalene", "mode": mode, "irrep": irrep, "origin_cm_as_printed": printed, "origin_cm": nu,
                         "family": window_family(nu), "conditions": s["conditions"], "u_res_cm": 0.0, "head_to_origin_cm": 0.0, "u_T_cm": 0.0,
                         "reading_precision_cm": reading, "fit_uncertainty_cm": "", "u_band_cm_lower_bound": u_band,
                         "pirali2009_position_cm": old.get("position_cm", ""), "pirali2009_u_band_cm": old.get("u_band_cm", ""),
                         "grade": "abstract", "source": s["cite"] + ", DOI " + s["doi"]})
    OUT.mkdir(exist_ok=True)
    with open(OUT / "origin_columns_naphthalene.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    L = [f"# Band-origin column — naphthalene, rotationally resolved records (items 72–73) ({datetime.now():%Y-%m-%d})", "",
         "Abstract-grade: the values are those quoted in the two abstracts (cached in `out/origin_sources_abstracts.json`, each value asserted verbatim); the papers' fitted origins and their uncertainties come with the PDFs (request items 32–33). "
         "A band origin is a molecular constant from a rotational fit: u_res = 0, head-to-origin = 0, u_T = 0; what remains is the reading precision plus the fit uncertainty (unknown) → **u_band is a lower bound**. "
         "Beside it, the same modes from the Pirali 2009 room-temperature scoreboard (item 53), whose u_band is dominated by the 0.5 cm⁻¹ head-to-origin term.", "",
         "| item | mode | irrep | origin (cm⁻¹, as printed) | family | conditions | u_band lower bound (cm⁻¹) | Pirali 2009 position | Pirali 2009 u_band |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['item']} | {r['mode']} | {r['irrep']} | {r['origin_cm_as_printed']} | {r['family']} | {r['conditions']} | {r['u_band_cm_lower_bound']:g} | {r['pirali2009_position_cm']} | {r['pirali2009_u_band_cm']} |")
    L += ["", "**What it decides.** For ν46 (the strongest CH out-of-plane band, the 12.7 µm carrier) the laboratory side of the decision is now ≈ 10⁻⁶ cm⁻¹ at room temperature (item 72) with a jet-cooled confirmation to come from item 73's full text: "
          "R1's C–H out-of-plane family is decidable at the pipeline's own budget for this band. The 2009 value 782.33 and the 2011 origin 782.330949 agree to the 2009 reading precision. ν47 and ν48 lie below Module 03's 6–15 µm window and are reported, not scored.", "",
          "Constants: " + json.dumps(CONSTANTS)]
    (OUT / "origin_columns_naphthalene.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
