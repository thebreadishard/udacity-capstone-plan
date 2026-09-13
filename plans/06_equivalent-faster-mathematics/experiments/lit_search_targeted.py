"""Targeted literature check (2026-09-13) for the reflection's leads A–G, second pass after lit_search_openalex.py's generic
relevance search returned mostly off-topic hits. Three phases, exactly as run interactively on 13 September and re-run by this script:
  1. OpenAlex title-restricted searches (title.search, sorted by citation count) -> lit_search_titles_<date>.json
  2. Crossref bibliographic queries for named candidate records (author-title strings), top-2 -> lit_check_crossref_<date>.json
  3. OpenAlex title+abstract searches with quoted phrases, relevance order -> lit_search_pointed_<date>.json
Records only (title, venue, DOI, citation count, abstract truncated). Every record cited in the reading note
(GoalGathering/Reading_Note_2026-09-13_Literature_Check_Leads_A-G.md) was verified by DOI against Crossref before citing;
author lists in the note come from those Crossref records, never from memory. Free APIs, polite mailto in the user agent."""
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "CapstonePlan literature check (mailto:frederic.petrignani@gmail.com)"}
TITLE_QUERIES = {
 "A: optimally tuned range-separated hybrid (title)": "optimally tuned range-separated hybrid",
 "A: tuned range-separated vibrational (title)": "range-separated hybrid vibrational frequencies",
 "A: functional parameters fitted harmonic frequencies (title)": "functional harmonic frequencies fitted",
 "A: delocalization error vibrational frequencies (title)": "delocalization error vibrational",
 "A: Kekule mode B2u benzene DFT (title)": "Kekule mode benzene",
 "A: learned functional coupled cluster accuracy (title)": "density functional machine learning coupled cluster accuracy",
 "A: DM21 pushing frontiers density functionals (title)": "pushing the frontiers of density functionals",
 "D: scaled quantum mechanical force field (title)": "scaled quantum mechanical force field",
 "D: transferable scale factors internal coordinates (title)": "scale factors force field transferable",
 "E: DMRG embedding density functional (title)": "density matrix renormalization group embedding",
 "E: DMRG frequencies vibrational (title)": "density matrix renormalization group vibrational",
 "C: infrared intensities coupled cluster benchmark (title)": "infrared intensities coupled cluster",
 "B: Bayesian optimization force field parameters (title)": "Bayesian force field parameterization",
 "B: active learning Hessian / vibrational (title)": "active learning vibrational spectra",
 "G: jet-cooled infrared PAH (title)": "jet-cooled infrared polycyclic aromatic",
 "F: graphene phonon dispersion beyond DFT / GW (title)": "phonon dispersion graphene beyond density functional",
 "F: coupled cluster graphene (title)": "coupled cluster graphene",
}
CROSSREF_QUERIES = [
 ("A", "Baer Livshits Salzner tuned range-separated hybrids in density functional theory Annual Review of Physical Chemistry 2010"),
 ("A", "Korzdorfer Sears Sutton Bredas long-range corrected hybrid functionals for pi-conjugated systems dependence of the range-separation parameter on conjugation length"),
 ("A", "Karolewski Kronik Kummel using optimally tuned range separated hybrid functionals in ground-state calculations consequences and caveats"),
 ("A", "Kesharwani Brauer Martin frequency and zero-point vibrational energy scale factors for double-hybrid density functionals"),
 ("A", "Moran Simmonett Leach Allen Schleyer Schaefer popular theoretical methods predict benzene and arenes to be nonplanar"),
 ("A", "Shaik Shurki Danovich Hiberty a different story of pi-delocalization the distortivity of pi-electrons and its chemical manifestations Chemical Reviews"),
 ("A", "Martin Taylor Lee harmonic frequencies of benzene a case for atomic natural orbital basis sets"),
 ("A", "Kaser Boittier Upadhyay Meuwly transfer learning to CCSD(T) accurate anharmonic frequencies from machine learning models"),
 ("A", "Ramakrishnan Dral Rupp von Lilienfeld big data meets quantum chemistry approximations the delta-machine learning approach"),
 ("A", "Mardirossian Head-Gordon thirty years of density functional theory in computational chemistry an overview and extensive assessment of 200 density functionals"),
 ("D", "Bauschlicher Langhoff the calculation of accurate harmonic frequencies of large molecules the polycyclic aromatic hydrocarbons as a case study Spectrochimica Acta"),
 ("D", "Langhoff theoretical infrared spectra for polycyclic aromatic hydrocarbon neutrals cations and anions Journal of Physical Chemistry 1996"),
 ("E", "Hachmann Dorando Aviles Chan the radical character of the acenes a density matrix renormalization group study"),
 ("E", "Hu Chan excited-state geometry optimization with the density matrix renormalization group as applied to polyenes analytic gradients"),
 ("C", "Cane Miani Trombetti anharmonic force fields of naphthalene"),
 ("C", "Martin El-Yazal Francois structure and vibrational spectrum of some polycyclic aromatic compounds studied by density functional theory naphthalene azulene phenanthrene anthracene"),
 ("B", "Denzel Kastner gaussian process regression for geometry optimization Journal of Chemical Physics 2018"),
 ("G", "Maltseva Petrignani Candian Mackie Huang Lee Buma high-resolution IR absorption spectroscopy of polycyclic aromatic hydrocarbons the realm of anharmonicity"),
 ("G", "Piest von Helden Meijer infrared spectroscopy of jet-cooled cationic polyaromatic hydrocarbons naphthalene"),
 ("G", "Huneycutt Casaes McCall Chung Lee Saykally infrared cavity ringdown spectroscopy of jet-cooled polycyclic aromatic hydrocarbons"),
 ("G", "Pirali Goubet Huet Georges Soulard Asselin Courbe Roy Vervloet far infrared spectrum of naphthalene high resolution synchrotron FTIR anharmonic DFT"),
 ("G", "Albert Albert Lerch Quack synchrotron-based highest resolution Fourier transform infrared spectroscopy of naphthalene and indole astrophysical problems Faraday Discussions"),
 ("F", "Lazzeri Attaccalite Wirtz Mauri impact of the electron-electron correlation on phonon dispersion failure of LDA and GGA DFT functionals in graphene and graphite"),
 ("F", "Gruneis Serrano Bosak Lazzeri Mauri phonon surface mapping of graphite disentangling quasi-degenerate phonon dispersions"),
]
POINTED_QUERIES = {
 "A-i  OT-RSH / range-separation parameter + vibrational frequencies": "\"range-separation parameter\" \"vibrational frequencies\"",
 "A-ii tuned functional harmonic frequencies polycyclic": "\"optimally tuned\" \"harmonic frequencies\"",
 "A-iii Kekule mode benzene density functional failure": "\"Kekulé\" benzene \"density functional\" frequency b2u",
 "A-iv functional fitted to vibrational frequencies (new functional)": "\"vibrational frequencies\" \"fitted\" \"exchange-correlation functional\" training",
 "A-v ML functional trained on CCSD(T) vibrational": "\"machine-learned\" functional \"vibrational\" \"CCSD(T)\"",
 "A-vi PAH CCSD(T) harmonic frequencies naphthalene": "\"CCSD(T)\" \"harmonic frequencies\" naphthalene",
 "A-vii PAH infrared functional benchmark": "\"polycyclic aromatic hydrocarbons\" infrared \"functionals\" benchmark harmonic frequencies \"B3LYP\" comparison",
 "A-viii range-separated PAH infrared": "\"range-separated\" \"polycyclic aromatic\" \"infrared spectra\" functional assessment",
 "A-ix double hybrids harmonic frequencies aromatic": "\"double-hybrid\" \"harmonic frequencies\" aromatic benzene \"CCSD(T)\"",
 "D-i internal coordinate force constants transferability CC-DFT difference": "\"force constants\" \"internal coordinates\" difference \"coupled cluster\" \"density functional\" transferable",
 "E-i DMRG Hessian / harmonic frequencies electronic": "DMRG \"harmonic frequencies\" \"analytic\" Hessian",
 "E-ii pi-electron active space embedding acenes vibrational": "acenes \"active space\" \"vibrational frequencies\" \"multireference\"",
 "C-i infrared intensities naphthalene coupled cluster / MP2 vs DFT": "\"infrared intensities\" naphthalene \"MP2\" \"density functional\"",
 "B-i Bayesian optimal experimental design quantum chemistry Hessian": "\"optimal experimental design\" \"quantum chemistry\" \"Bayesian\"",
 "G-i naphthalene jet-cooled mid-infrared IR-UV": "naphthalene \"IR-UV\" \"ion dip\" mid-infrared",
 "F-i graphene phonon GW correction Kohn anomaly": "graphene phonon \"GW\" \"Kohn anomaly\"",
 "F-ii periodic coupled cluster phonon frequencies": "\"coupled cluster\" \"phonon\" periodic \"frequencies\" solid",
}


def get(url):
    for attempt in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception:  # noqa: BLE001
            if attempt == 2:
                raise
            time.sleep(2)


def abstract_of(inv):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def oa_rows(d):
    rows = []
    for it in d["results"]:
        venue = ((it.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        rows.append({"year": it.get("publication_year"), "title": it.get("title"), "venue": venue, "doi": (it.get("doi") or "").replace("https://doi.org/", ""),
                     "cited_by": it.get("cited_by_count"), "oa": (it.get("open_access") or {}).get("is_oa"), "abstract": abstract_of(it.get("abstract_inverted_index"))[:900]})
    return rows


def main():
    stamp = f"{datetime.now():%Y-%m-%d}"
    sel = "&select=id,title,publication_year,doi,cited_by_count,primary_location,abstract_inverted_index,open_access"
    titles = {}
    for k, q in TITLE_QUERIES.items():
        d = get("https://api.openalex.org/works?filter=title.search:" + urllib.parse.quote(q) + ",type:article&sort=cited_by_count:desc&per-page=7" + sel)
        titles[k] = {"query": q, "hits": oa_rows(d)}; print("title", k, len(titles[k]["hits"]), flush=True); time.sleep(0.4)
    json.dump({"date": stamp, "mode": "title.search, sorted by citations", "results": titles}, open(HERE / f"lit_search_titles_{stamp}.json", "w"), indent=1)
    cross = []
    for lead, q in CROSSREF_QUERIES:
        d = get("https://api.crossref.org/works?rows=2&select=DOI,title,author,container-title,issued,volume,page&query.bibliographic=" + urllib.parse.quote(q))
        for it in d["message"]["items"]:
            cross.append({"lead": lead, "query": q, "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0], "title": (it.get("title") or [""])[0],
                          "container": (it.get("container-title") or [""])[0], "volume": it.get("volume"), "page": it.get("page"), "doi": it["DOI"],
                          "authors": "; ".join(f"{a.get('family', '')}, {a.get('given', '')}" for a in it.get("author", []))})
        print("crossref", lead, q[:60], flush=True); time.sleep(0.3)
    json.dump(cross, open(HERE / f"lit_check_crossref_{stamp}.json", "w"), indent=1)
    pointed = {}
    for k, q in POINTED_QUERIES.items():
        d = get("https://api.openalex.org/works?search=" + urllib.parse.quote(q) + "&filter=type:article&per-page=6&sort=relevance_score:desc" + sel)
        pointed[k] = {"query": q, "count": d["meta"]["count"], "hits": oa_rows(d)}; print("pointed", k, pointed[k]["count"], flush=True); time.sleep(0.4)
    json.dump({"date": stamp, "results": pointed}, open(HERE / f"lit_search_pointed_{stamp}.json", "w"), indent=1)
    print("written three JSON files in", HERE)


if __name__ == "__main__":
    main()
