#!/usr/bin/env python
"""Module 02 — the opponent atlas: parse the public NASA Ames PAHdb computed libraries into tidy tables.

This table is parsed from the public NASA Ames PAHdb v4.00 computed library (DOI
10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it is the *opponent* of
this project's pipeline, not its training data. (Capstone_Mapping, Module 02 — the required sentence.)

Input: the XML files the PAHdb download form delivers (theoretical 4.00, ≈ 47 MB; anharmonic 1.00,
≈ 0.9 MB; experimental 3.10, ≈ 3.9 MB — the last is Module 03's, parsed here for the same table shape).
They are obtained by the user through the site's form (e-mail address and the citation agreement) and
placed in ./data/, which is git-ignored; every output records the input file's sha256 and the XML root
attributes (database, version, date, full).

Schema (from the AmesPAHdbPythonSuite parser and its cutdown test file, read 2026-09-10):
  <pahdatabase database= version= date= full=>
    <species><specie uid=>
      <comments><comment type=>…</comment></comments>   (the Gaussian route line: method, basis, grid)
      <references><reference>…</reference></references>
      <formula> <charge> <symmetry> <weight> <total_e> <vib_e> <method>
      <n_solo> <n_duo> <n_trio> <n_quartet> <n_quintet> <n_ch2> <n_chx>
      <geometry><atom><position><x><y><z></position><type/></atom>…</geometry>
      <transitions><mode><frequency scale=>ν</frequency><intensity>I</intensity><symmetry>Γ</symmetry></mode>…</transitions>
      <laboratory><frequency>base64</frequency><intensity>base64</intensity></laboratory>   (experimental library only)
Unknown scalar tags are kept as text columns, never dropped silently; the run prints which tags it saw.

Outputs (./out/<database>_<version>/):
  species.csv   one row per species: uid, formula, charge, n_c, n_h, n_n, n_o, n_atoms, symmetry, method,
                basis (parsed from the route comment), scale factors seen, n_modes, weight, total_e, vib_e,
                the CH-adjacency counts, the references' DOIs
  bands.csv.gz  one row per transition: uid, formula, charge, n_c, frequency_cm (as stored), scale,
                frequency_unscaled_cm (= frequency/scale), intensity_km_mol, symmetry, family (a
                frequency-range label, printed as a rule, pilot-note candidate)
  SUMMARY.md    counts, coverage by size and charge, where the 4-31G regime starts, which ladder rungs
                have entries, the C384H48-class list (frozen-lines debt 6), the tag inventory, hashes.
Nothing is trained. Figures are the notebook's job (Module 02 EDA), not this script's.
"""
import argparse, csv, gzip, hashlib, json, re, sys
from collections import Counter
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
LADDER = {  # rungs of the frozen Ladder §2 — presence check by formula (all charges listed, charge printed)
    "R0": ["C6H6"], "R1": ["C10H8"], "R2": ["C16H10", "C18H12"], "R3": ["C24H12"],
    "R4-R5 class": "54 <= n_c <= 216", "R6 class": "n_c >= 300",
}
FAMILY_RULE = [  # pilot-note candidate: a frequency-range label for PAH bands (cm⁻¹, as stored)
    (0.0, 650.0, "low / skeletal"), (650.0, 950.0, "CH-oop (10.5-15 um; benzene nu11 at 673 included)"), (950.0, 1100.0, "ring / CH-ip (9-10.5 um)"),
    (1100.0, 1250.0, "CH-ip-bend (8.6 um)"), (1250.0, 1500.0, "CC-stretch/CH-ip (7.7 um)"), (1500.0, 1650.0, "CC-stretch (6.2 um)"),
    (1650.0, 2950.0, "overtone / combination region"), (2950.0, 3200.0, "CH-stretch"), (3200.0, 1e9, "above 3200"),
]
CONTAINERS = {"comments", "references", "geometry", "transitions", "laboratory"}

def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def strip(tag): return tag.split("}", 1)[-1]
def family(nu):
    for lo, hi, lab in FAMILY_RULE:
        if lo <= nu < hi: return lab
    return "?"

def parse_formula(f):
    counts = Counter()
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", f or ""):
        counts[el] += int(n) if n else 1
    return counts

def basis_from_comments(comments):
    txt = " ".join(comments).lower()
    m = re.search(r"/\s*([0-9]-[0-9]+g\*{0,2}|6-311\+*g\**|cc-pv[dtq]z|aug-cc-pv[dtq]z|n07d|def2-\w+)", txt)
    return m.group(1) if m else ("?" if txt else "")

def child(el, name):
    c = el.find("./{*}" + name)
    return c if c is not None else el.find(name)

def species_row(el, comments, refs, modes, natoms):
    cur = {"uid": el.attrib.get("uid")}
    cur.update({k: v for k, v in el.attrib.items() if k != "uid"})
    for ch in el:                      # direct scalar children only (<symmetry> also occurs inside <mode>)
        ct = strip(ch.tag)
        if ct in CONTAINERS: continue
        cur[ct] = (ch.text or "").strip()
    fc = parse_formula(cur.get("formula", ""))
    cur["n_c"] = int(cur.get("n_c") or fc["C"]); cur["n_h"] = int(cur.get("n_h") or fc["H"])
    cur["n_n"] = int(cur.get("n_n") or fc["N"]); cur["n_o"] = int(cur.get("n_o") or fc["O"])
    cur["n_atoms"] = natoms or sum(fc.values())
    cur["basis"] = basis_from_comments(comments)
    cur["route"] = " | ".join(c for c in comments if c)[:300]
    cur["scales_seen"] = ",".join(sorted({f"{m['scale']:.4f}" for m in modes if m["scale"] == m["scale"]}))
    cur["n_modes"] = len(modes)
    cur["dois"] = ";".join(sorted({d for r in refs for d in re.findall(r"doi:\s*(\S+)", r, re.I)}))
    return cur

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml", help="a PAHdb XML library file (theoretical / anharmonic / experimental)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    src = Path(a.xml)
    if not src.exists(): print(f"NOT_RUN: {src} not found (obtain it through the PAHdb download form)"); sys.exit(1)
    h = sha256(src)
    species, bands, tags_seen, root_attrib = [], [], Counter(), {}
    in_specie = False; comments = []; refs = []; modes = []; natoms = 0
    for ev, el in ET.iterparse(str(src), events=("start", "end")):
        t = strip(el.tag)
        if ev == "start":
            if t == "pahdatabase": root_attrib = dict(el.attrib)
            elif t == "specie": in_specie = True; comments, refs, modes, natoms = [], [], [], 0
            continue
        tags_seen[t] += 1
        if not in_specie: continue
        if t == "comment": comments.append((el.text or "").strip())
        elif t == "reference": refs.append((el.text or "").strip())
        elif t == "atom": natoms += 1
        elif t == "mode":
            f, i, s = child(el, "frequency"), child(el, "intensity"), child(el, "symmetry")
            sc = f.attrib.get("scale") if f is not None else None
            modes.append({"frequency": float(f.text), "scale": float(sc) if sc else float("nan"),
                          "intensity": float(i.text) if i is not None and i.text else float("nan"),
                          "symmetry": (s.text or "").strip() if s is not None else ""})
        elif t == "specie":
            cur = species_row(el, comments, refs, modes, natoms)
            species.append(cur)
            for m in modes:
                nu = m["frequency"]
                bands.append({"uid": cur["uid"], "formula": cur.get("formula", ""), "charge": cur.get("charge", ""), "n_c": cur["n_c"],
                              "frequency_cm": nu, "scale": m["scale"],
                              "frequency_unscaled_cm": nu / m["scale"] if m["scale"] == m["scale"] and m["scale"] else float("nan"),
                              "intensity_km_mol": m["intensity"], "symmetry": m["symmetry"], "family": family(nu)})
            in_specie = False; el.clear()
    db = root_attrib.get("database", "unknown").replace("/", "-"); ver = root_attrib.get("version", "?")
    out = Path(a.out) if a.out else HERE / "out" / f"{db}_{ver}"; out.mkdir(parents=True, exist_ok=True)
    scols = ["uid", "formula", "charge", "n_c", "n_h", "n_n", "n_o", "n_atoms", "symmetry", "method", "basis", "scales_seen", "n_modes",
             "weight", "total_e", "vib_e", "n_solo", "n_duo", "n_trio", "n_quartet", "n_quintet", "n_ch2", "n_chx", "dois", "route"]
    extra = sorted({k for s in species for k in s} - set(scols))
    with open(out / "species.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=scols + extra, extrasaction="ignore"); w.writeheader(); w.writerows(species)
    with gzip.open(out / "bands.csv.gz", "wt", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(bands[0].keys()) if bands else ["uid"]); w.writeheader(); w.writerows(bands)
    neutral = [s for s in species if str(s.get("charge")) == "0"]
    by_basis = Counter(s["basis"] for s in species); by_charge = Counter(str(s.get("charge")) for s in species)
    bins = [(1, 20), (21, 50), (51, 100), (101, 200), (201, 400), (401, 10_000)]
    size_rows = [(f"{lo}–{hi}", sum(1 for s in species if lo <= s["n_c"] <= hi),
                  Counter(s["basis"] for s in species if lo <= s["n_c"] <= hi).most_common(3)) for lo, hi in bins]
    min_431 = min([s["n_c"] for s in species if s["basis"] == "4-31g"] or [None])
    max_631 = max([s["n_c"] for s in species if s["basis"].startswith("6-31g")] or [None])
    rung_rows = []
    for r, want in LADDER.items():
        if isinstance(want, list): hits = [(s["uid"], s["formula"], s.get("charge")) for s in species if s.get("formula") in want]
        elif "54" in want: hits = [(s["uid"], s["formula"], s.get("charge")) for s in species if 54 <= s["n_c"] <= 216]
        else: hits = [(s["uid"], s["formula"], s.get("charge")) for s in species if s["n_c"] >= 300]
        rung_rows.append((r, want, len(hits), hits[:12]))
    c384 = [(s["uid"], s["formula"], s.get("charge"), s.get("symmetry"), s["basis"]) for s in species if 300 <= s["n_c"] <= 400]
    exact_384 = [x for x in c384 if x[1] == "C384H48"]
    L = [f"# Opponent atlas — {root_attrib.get('database')} library version {ver} ({root_attrib.get('date')}, full={root_attrib.get('full')}) — {datetime.now():%Y-%m-%d %H:%M}", "",
         "This table is parsed from the public NASA Ames PAHdb v4.00 computed library (DOI 10.3847/1538-4365/ae1c38). It is computed "
         "science data, not AI-generated, and it is the *opponent* of this project's pipeline, not its training data.", "",
         f"Source `{src.name}`, sha256 `{h}`, {src.stat().st_size:,} bytes. Root attributes: {json.dumps(root_attrib)}.", "",
         f"**Species: {len(species):,}** ({len(neutral):,} neutral) · **bands: {len(bands):,}** · tag inventory: {dict(tags_seen)}", "",
         f"Charge: {dict(by_charge)} · basis (from the route comment): {dict(by_basis)} · smallest 4-31G species n_c = {min_431} · largest 6-31G* species n_c = {max_631}", "",
         "| n_c bin | species | basis sets |", "|---|---|---|"] + [f"| {b} | {n} | {bb} |" for b, n, bb in size_rows] + ["",
         "| ladder rung | looked for | entries | first hits (uid, formula, charge) |", "|---|---|---|---|"] + \
        [f"| {r} | {w} | {n} | {hits} |" for r, w, n, hits in rung_rows] + ["",
         f"**Debt 6 (C₃₈₄H₄₈-class, 300 ≤ n_c ≤ 400): {len(c384)} species**; C384H48 itself: {exact_384 if exact_384 else 'absent'}. Full list in `c384_class.csv`.", "",
         f"Scale factors seen: {Counter(b['scale'] for b in bands).most_common(8)}", "",
         "Family labels are a frequency-range rule printed in the script (pilot-note candidate); nothing is trained here."]
    (out / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(out / "c384_class.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["uid", "formula", "charge", "symmetry", "basis"]); w.writerows(c384)
    print("\n".join(L))

if __name__ == "__main__":
    main()
