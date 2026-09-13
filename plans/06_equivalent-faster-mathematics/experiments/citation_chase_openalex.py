"""Citation chase via OpenAlex (2026-09-13) — forward citations of the seed papers of plan 06's novelty question, screened by title
keywords, with the abstracts of the hits reconstructed from OpenAlex's inverted index so they can be read, not guessed.

Serves the novelty assessment §5 (what a real check requires) and the decision rule (no branch depends on it; it protects claims).
Seeds are passed as DOIs on the command line or taken from SEEDS. Output: `citation_chase_<date>.md` with, per seed, the citing count, the
title-screened hits (year, title, venue, DOI) and each hit's abstract (first 700 characters). OpenAlex is free and needs no login; a polite
mailto is sent in the User-Agent. Not a systematic review: OpenAlex misses some publishers' references and all unpublished work."""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = {"Coleman & Moré 1984 (sparse Hessians, colouring)": "10.1007/bf02612334", "Powell & Toint 1979 (substitution)": "10.1137/0716078",
         "Coleman & Cai 1986 (cyclic colouring)": "10.1137/0607026", "Hossain & Steihaug 2008 (colouring applications)": "10.1016/j.dam.2006.07.018",
         "Mata & Werner 2006 (frozen local domains, smooth PES)": "10.1063/1.2364487", "Russ & Crawford 2004 (local-correlation PES discontinuities)": "10.1063/1.1759322",
         "Sanders, Andrade & Aspuru-Guzik 2015 (compressed-sensing Hessians)": "10.1021/oc5000404", "Reiher & Neugebauer 2003 (mode tracking)": "10.1063/1.1523908",
         "Rai et al. 2019 (sparse low-rank PES)": "10.1007/s10910-019-01034-z", "Yang et al. 2024 (sparse numerical Hessian)": "10.1021/acs.jpca.3c07645",
         "Zhang et al. 2024 (PySCFAD local CC gradients)": "10.1063/5.0212274", "O1NumHess 2025": "10.1021/acs.jctc.5c01354",
         "Krasnoshchekov et al. 2014 (resonance criteria)": "10.1063/1.4903927", "Yagi, Hirata & Hirao 2007 (a-priori selection)": "10.1063/1.2748774"}
KEYWORDS = ["vibrat", "hessian", "spectr", "aromatic", "pah", "polycyclic", "frequenc", "infrared", "force constant", "coupled cluster", "coupled-cluster",
            "raman", "anharmonic", "gradient", "local correlation", "pno", "lno", "dlpno", "molecul"]
UA = {"User-Agent": "CapstonePlan citation chase (mailto:frederic.petrignani@gmail.com)"}


def oa(url):
    for attempt in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                raise
            time.sleep(2)


def abstract_of(inv):
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def chase(name, doi, extra_doi_seeds):
    w = oa(f"https://api.openalex.org/works/https://doi.org/{doi}")
    wid = w["id"].split("/")[-1]; total = oa(f"https://api.openalex.org/works?filter=cites:{wid}&per-page=1")["meta"]["count"]
    hits = []; page = 1
    while True:
        d = oa(f"https://api.openalex.org/works?filter=cites:{wid}&per-page=200&page={page}&select=id,title,publication_year,doi,primary_location,abstract_inverted_index")
        for it in d["results"]:
            t = (it.get("title") or ""); tl = t.lower()
            if any(k in tl for k in KEYWORDS):
                venue = ((it.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
                hits.append({"year": it.get("publication_year"), "title": t, "venue": venue, "doi": (it.get("doi") or "").replace("https://doi.org/", ""),
                             "abstract": abstract_of(it.get("abstract_inverted_index"))[:700]})
        if page * 200 >= total or page >= 10:
            break
        page += 1; time.sleep(0.5)
    return {"seed": name, "doi": doi, "openalex_id": wid, "citing_total": total, "hits": sorted(hits, key=lambda h: h["year"] or 0)}


def main():
    seeds = dict(SEEDS)
    for arg in sys.argv[1:]:
        seeds[f"extra seed {arg}"] = arg
    results = []
    for name, doi in seeds.items():
        try:
            r = chase(name, doi, None); results.append(r)
            print(f"{name}: {r['citing_total']} citing, {len(r['hits'])} title hits", flush=True)
        except Exception as e:  # noqa: BLE001
            results.append({"seed": name, "doi": doi, "error": str(e)}); print(f"{name}: ERROR {e}", flush=True)
    stamp = f"{datetime.now():%Y-%m-%d}"
    json.dump({"date": stamp, "keywords": KEYWORDS, "results": results}, open(HERE / f"citation_chase_{stamp}.json", "w"), indent=1)
    L = [f"# Citation chase via OpenAlex — {stamp}", "", f"Title keywords: {', '.join(KEYWORDS)}. Abstracts reconstructed from OpenAlex's inverted index (first 700 characters). Not a systematic review.", ""]
    for r in results:
        if "error" in r:
            L += [f"## {r['seed']} — ERROR {r['error']}", ""]; continue
        L += [f"## {r['seed']} — DOI {r['doi']} — {r['citing_total']} citing works, {len(r['hits'])} title hits", ""]
        for h in r["hits"]:
            L += [f"- **{h['year']}** — {h['title']} — *{h['venue']}* — {h['doi']}", f"  > {h['abstract'] or '(no abstract in OpenAlex)'}", ""]
    (HERE / f"citation_chase_{stamp}.md").write_text("\n".join(L), encoding="utf-8")
    print("written", HERE / f"citation_chase_{stamp}.md")


if __name__ == "__main__":
    main()
