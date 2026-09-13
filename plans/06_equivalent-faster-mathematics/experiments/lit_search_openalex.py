"""Literature search via OpenAlex (2026-09-13) for the reflection's leads A–G: keyword searches over titles/abstracts, ranked by relevance
and citations, with the abstracts reconstructed so they can be read. Records are OpenAlex/Crossref records (verified by DOI when cited later);
nothing here is a claim about content beyond what the abstract says. Output: lit_search_<date>.md/.json. Free API, polite mailto in the UA."""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "CapstonePlan literature check (mailto:frederic.petrignani@gmail.com)"}
QUERIES = {
 "A1 tuned range-separated hybrid vibrational frequencies": "optimally tuned range-separated hybrid functional vibrational frequencies",
 "A2 tuned RSH conjugated / PAH": "optimally tuned range-separated hybrid polycyclic aromatic hydrocarbons",
 "A3 functional tuned to CCSD(T) harmonic force constants": "density functional parameters fitted to CCSD(T) harmonic frequencies force constants",
 "A4 delocalization error bond length alternation vibrational": "delocalization error bond length alternation Kekule mode vibrational frequency density functional",
 "A5 machine-learned exchange-correlation functional": "machine learned exchange-correlation functional trained on coupled cluster",
 "A6 DFT vs CCSD(T) harmonic frequencies benchmark aromatic": "CCSD(T) harmonic vibrational frequencies benzene naphthalene density functional benchmark",
 "D1 scaled quantum mechanical force field internal coordinates": "scaled quantum mechanical force field internal coordinate scale factors transferable",
 "D2 transferable force constant corrections internal coordinates": "transferability of force constants internal coordinates polycyclic aromatic hydrocarbons",
 "E1 DMRG in DFT embedding": "density matrix renormalization group embedding density functional theory pi system",
 "E2 DMRG vibrational frequencies / Hessian": "density matrix renormalization group vibrational frequencies Hessian",
 "C1 MP2 CCSD(T) infrared intensities vs DFT PAH": "infrared intensities coupled cluster density functional polycyclic aromatic hydrocarbons comparison",
 "B1 Bayesian experimental design force field / Hessian": "Bayesian experimental design active learning force constants Hessian quantum chemistry",
 "G1 jet-cooled PAH infrared spectra gas phase": "jet-cooled gas-phase infrared spectra polycyclic aromatic hydrocarbons IR-UV ion dip",
 "F1 graphene phonons coupled cluster / beyond DFT": "graphene phonon frequencies coupled cluster beyond density functional theory",
}


def oa(url):
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


def main(per_query=8):
    stamp = f"{datetime.now():%Y-%m-%d}"; results = {}
    for key, q in QUERIES.items():
        url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(q) + "&filter=type:article&per-page=" + str(per_query) +
               "&select=id,title,publication_year,doi,cited_by_count,primary_location,abstract_inverted_index,open_access")
        d = oa(url); rows = []
        for it in d["results"]:
            venue = ((it.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            rows.append({"year": it.get("publication_year"), "title": it.get("title"), "venue": venue, "doi": (it.get("doi") or "").replace("https://doi.org/", ""),
                         "cited_by": it.get("cited_by_count"), "oa": (it.get("open_access") or {}).get("is_oa"), "oa_url": (it.get("open_access") or {}).get("oa_url"),
                         "abstract": abstract_of(it.get("abstract_inverted_index"))[:900]})
        results[key] = {"query": q, "hits": rows}; print(key, len(rows), flush=True); time.sleep(0.5)
    json.dump({"date": stamp, "results": results}, open(HERE / f"lit_search_{stamp}.json", "w"), indent=1)
    L = [f"# Literature search via OpenAlex — {stamp} (leads A–G of the reflection)", "", "Relevance-ranked OpenAlex results, abstracts truncated to 900 characters. Records only; verify DOIs before citing.", ""]
    for key, r in results.items():
        L += [f"## {key} — query: *{r['query']}*", ""]
        for h in r["hits"]:
            L += [f"- **{h['year']}** — {h['title']} — *{h['venue']}* — {h['doi']} — cited {h['cited_by']} — {'OA' if h['oa'] else 'closed'}", f"  > {h['abstract'] or '(no abstract)'}", ""]
    (HERE / f"lit_search_{stamp}.md").write_text("\n".join(L), encoding="utf-8")
    print("written", HERE / f"lit_search_{stamp}.md")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
