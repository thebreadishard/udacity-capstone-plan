"""Read the second route of the imaginary-mode molecules (24 September 2026; corpus README dated note of 23 September, second artefact class).

For every molecule directory that has an analytic check, compare the lowest vibrational frequency of the corpus (deck v1 finite differences) with
the analytic Hessian per functional and classify each imaginary mode:
  healed   — corpus imaginary, analytic real (≥ +10 cm-1): the deck's grid noise flipped a soft mode; the analytic Hessian replaces the corpus one
  genuine  — corpus imaginary, analytic imaginary too: the geometry is not a minimum for that functional; the molecule stays excluded
  unclear  — analytic within ±10 cm-1 of zero
Also reports, for the modes that were real in both, the max |Δω| (the deck's noise level on that molecule) and whether the two-route agreement
holds elsewhere. Writes a table (md) and a json with the list of molecules whose release row should take the analytic second route.

Usage: python read_imaginary_second_route.py [--molecules <dir>] [--ids id1 id2 ...] [--out <prefix>]
"""
import argparse
import csv
import glob
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def vib_only(f):
    f = np.asarray(f, float); keep = np.argsort(np.abs(f))[6:]
    return np.sort(f[keep])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--molecules", default=os.path.join(HERE, "molecules")); ap.add_argument("--ids", nargs="*")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "data", "second_route", "imaginary_second_route_2026-09-24")); a = ap.parse_args()
    names = {r["id"]: r["name"] for r in csv.DictReader(open(os.path.join(HERE, "manifest.csv"), encoding="utf-8"))}
    dirs = [os.path.join(a.molecules, i) for i in a.ids] if a.ids else sorted(os.path.dirname(p) for p in glob.glob(os.path.join(a.molecules, "*", "analytic_check.json")))
    rows = []; take_analytic = []
    for d in dirs:
        mid = os.path.basename(d); cp = os.path.join(d, "analytic_check.json")
        if not os.path.exists(cp):
            rows.append(dict(id=mid, name=names.get(mid, "?"), status="no analytic check yet")); continue
        res = json.load(open(os.path.join(d, "result.json"), encoding="utf-8")); chk = json.load(open(cp, encoding="utf-8"))
        row = dict(id=mid, name=names.get(mid, "?"), status="ok", functionals={})
        any_imag = False; healed_all = True
        for tag in ("b3lyp", "wb97x"):
            n_im = int(res.get(f"n_imaginary_{tag}", 0)); fc = vib_only(np.load(os.path.join(d, f"hessian_{tag}.npz"))["freq_cm"])
            fa = np.sort(np.asarray(chk[tag]["freq_analytic"], float)) if tag in chk else None
            if fa is None:
                row["functionals"][tag] = dict(status="analytic missing"); continue
            fa_v = fa if len(fa) == len(fc) else vib_only(np.load(os.path.join(d, f"hessian_{tag}_analytic.npz"))["freq_cm"])
            both_real = (fc > 0) & (fa_v > 0); noise = float(np.abs(fa_v[both_real] - fc[both_real]).max()) if both_real.any() else None
            entry = dict(corpus_lowest=round(float(fc[0]), 1), analytic_lowest=round(float(fa_v[0]), 1), n_imaginary_corpus=n_im, n_imaginary_analytic=int((fa_v < 0).sum()),
                         max_abs_dfreq_real_modes=None if noise is None else round(noise, 1))
            if n_im > 0 or fc[0] < 0:
                any_imag = True
                if fa_v[0] >= 10:
                    entry["verdict"] = "healed"
                elif fa_v[0] < 0:
                    entry["verdict"] = "genuine"; healed_all = False
                else:
                    entry["verdict"] = "unclear"; healed_all = False
            else:
                entry["verdict"] = "real in both" if fa_v[0] > 0 else "analytic imaginary, corpus real"
                if fa_v[0] <= 0:
                    healed_all = False
            row["functionals"][tag] = entry
        row["molecule_verdict"] = ("healed — analytic route replaces the corpus Hessians" if any_imag and healed_all else
                                   "genuine imaginary mode(s) — stays excluded" if any_imag else "no imaginary mode in the corpus")
        if any_imag and healed_all:
            take_analytic.append(mid)
        rows.append(row)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(dict(date="2026-09-24", rows=rows, take_analytic=take_analytic), open(a.out + ".json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    md = ["# Imaginary-mode molecules — second route (analytic pyscf Hessians, grid 99/590) against deck v1 finite differences", "",
          "| molecule | B3LYP lowest: corpus → analytic | ωB97X lowest: corpus → analytic | noise on real modes (max |Δω|) | verdict |", "|---|---|---|---|---|"]
    for r in rows:
        if r["status"] != "ok":
            md.append(f"| {r['name']} ({r['id']}) | — | — | — | {r['status']} |"); continue
        f = r["functionals"]
        def cell(tag):
            e = f.get(tag, {})
            return f"{e.get('corpus_lowest', '?')} → {e.get('analytic_lowest', '?')} ({e.get('verdict', '?')})" if "corpus_lowest" in e else e.get("status", "?")
        noise = ", ".join(f"{t} {f[t].get('max_abs_dfreq_real_modes')}" for t in ("b3lyp", "wb97x") if t in f and "max_abs_dfreq_real_modes" in f[t])
        md.append(f"| {r['name']} ({r['id']}) | {cell('b3lyp')} | {cell('wb97x')} | {noise} | {r['molecule_verdict']} |")
    n_ok = sum(1 for r in rows if r["status"] == "ok")
    md += ["", f"{n_ok} molecules read; {len(take_analytic)} healed (analytic route replaces the corpus Hessians in the next release), "
           f"{sum(1 for r in rows if r['status'] == 'ok' and r['molecule_verdict'].startswith('genuine'))} genuine, "
           f"{sum(1 for r in rows if r['status'] != 'ok')} not yet available."]
    open(a.out + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n"); print("\n".join(md))


if __name__ == "__main__":
    main()
