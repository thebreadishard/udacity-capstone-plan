"""Forward citation chase (2026-09-13, evening; the user: "Jaag") for lead A's literature: do later works apply optimally tuned
range-separated hybrids (or double hybrids) to VIBRATIONAL properties, and in particular to aromatic molecules? Seeds = the records of
the leads A-G reading note §1; citing works from OpenAlex, screened on title+abstract with NARROW vibrational keywords (the generic chase
script's keywords would flag every spectroscopy paper). Output: citation_chase_otrsh_<date>.md/.json. Abstract level; not a systematic review."""
import json, time, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "CapstonePlan literature check (mailto:frederic.petrignani@gmail.com)"}
SEEDS = {"Tamblyn, Refaely-Abramson, Neaton & Kronik 2014 (scOT-RSH, vibrations)": "10.1021/jz5010939",
         "Körzdörfer, Sears, Sutton & Brédas 2011 (omega vs conjugation length)": "10.1063/1.3663856",
         "Karolewski, Kronik & Kümmel 2013 (tuning in ground-state calculations)": "10.1063/1.4807325",
         "Jiménez-Hoyos, Janesko & Scuseria 2008 (RSH for frequencies/intensities)": "10.1039/b810877c",
         "Kesharwani, Brauer & Martin 2015 (double-hybrid frequency scale factors)": "10.1021/jp508422u"}
KEYWORDS = ["vibrat", "frequenc", "infrared", " ir ", "raman", "phonon", "hessian", "force constant", "harmonic", "anharmonic", "zero-point", "zpve"]
AROMATIC = ["aromatic", "polycyclic", "pah", "acene", "benzene", "naphthalene", "pyrene", "coronene", "conjugated"]

def get(url):
    for a in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception:
            if a == 2: raise
            time.sleep(2)

def ab(inv):
    if not inv: return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs: pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))

def main():
    stamp = f"{datetime.now():%Y-%m-%d}"; res = {}
    for name, doi in SEEDS.items():
        w = get(f"https://api.openalex.org/works/https://doi.org/{doi}?select=id,cited_by_count"); wid = w["id"].split("/")[-1]; hits = []; cursor = "*"; n = 0
        while cursor:
            d = get(f"https://api.openalex.org/works?filter=cites:{wid}&per-page=200&cursor={cursor}&select=title,publication_year,doi,cited_by_count,primary_location,abstract_inverted_index")
            for it in d["results"]:
                n += 1; text = ((it.get("title") or "") + " " + ab(it.get("abstract_inverted_index"))).lower()
                kw = [k for k in KEYWORDS if k in text]
                if kw:
                    hits.append({"year": it.get("publication_year"), "title": it.get("title"), "venue": ((it.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
                                 "doi": (it.get("doi") or "").replace("https://doi.org/", ""), "cited_by": it.get("cited_by_count"), "keywords": kw,
                                 "aromatic": [a for a in AROMATIC if a in text], "abstract": ab(it.get("abstract_inverted_index"))[:700]})
            cursor = d["meta"].get("next_cursor"); time.sleep(0.3)
        res[name] = {"doi": doi, "citing_total": w["cited_by_count"], "screened": n, "hits": sorted(hits, key=lambda h: (-len(h["aromatic"]), -(h["cited_by"] or 0)))}
        print(name, "cited", w["cited_by_count"], "screened", n, "hits", len(hits), flush=True)
    json.dump({"date": stamp, "keywords": KEYWORDS, "aromatic_markers": AROMATIC, "results": res}, open(HERE / f"citation_chase_otrsh_{stamp}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    L = [f"# Forward citation chase, lead A seeds — {stamp}", "", f"Keywords (title+abstract): {', '.join(KEYWORDS)}; aromatic markers: {', '.join(AROMATIC)}. Hits sorted by aromatic markers, then citations. Abstract level; not a systematic review.", ""]
    for name, r in res.items():
        L += [f"## {name} — DOI {r['doi']} — cited by {r['citing_total']} (screened {r['screened']}), vibrational hits {len(r['hits'])}", ""]
        for h in r["hits"]:
            L += [f"- **{h['year']}** — {h['title']} — *{h['venue']}* — {h['doi']} — cited {h['cited_by']} — keywords {', '.join(h['keywords'])}" + (f" — **aromatic: {', '.join(h['aromatic'])}**" if h['aromatic'] else ""), f"  > {h['abstract'] or '(no abstract)'}", ""]
    (HERE / f"citation_chase_otrsh_{stamp}.md").write_text("\n".join(L), encoding="utf-8"); print("written")

if __name__ == "__main__":
    main()
