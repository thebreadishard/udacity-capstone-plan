"""Spectrum Atlas — mechanical export of the pipeline repository to the site's JSON (BACKLOG step 1, 24 September 2026).

Sources (read-only): the corpus manifest and ledger, every corpus molecule directory with a result, the release manifests, the second-route
checks, the E8 results, and the fixed list of anchored / validated molecules below (each with the file that carries the evidence). Outputs:
  out/catalog.json           one row per manifest molecule: identity, size, rung, flags, release membership, formula and InChIKey (RDKit)
  out/molecules/<id>.json    per computed molecule: geometry, frequency lists per functional, imaginary counts, timings, deck, second route, releases
  out/summary.json           rung counts, layer counts, data freshness, source hashes
The script fails (non-zero exit) when an invariant breaks: a catalog id without a manifest row, a frequency list whose length is not 3N, rung
counts that do not add up, a computed molecule without both Hessians. Nothing here is typed by hand; the anchored/validated list names its files.

Usage: python build_catalog.py [--repo <CapstonePlan root>] [--out <dir>] [--limit N]
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np

RUNGS = ["listed", "cheap_level_done", "correction_predicted", "spectrum_predicted", "anchored", "validated"]

# The molecules whose rung is set by evidence outside the corpus factory. Each entry names the file that carries it (relative to plan 05).
ANCHORED = {
    "A_8448043181": ["probes/results_m1/e8_benzene_ccpvdz/E8_locality_benzene.md", "probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md"],
    "A_01f3186607": ["probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md", "probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md"],
}
VALIDATED = {
    "A_8448043181": ["probes/results_vpt2/benzene_benchmark_2026-09-22.md"],
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def formula_and_key(smiles):
    """(formula, InChIKey, n_atoms with hydrogens, n_heavy) from RDKit; Nones when RDKit is absent or the SMILES does not parse."""
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import rdMolDescriptors
        RDLogger.DisableLog("rdApp.*")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None, None, None, None
        try:
            key = Chem.MolToInchiKey(mol) or None
        except Exception:
            key = None
        return rdMolDescriptors.CalcMolFormula(mol), key, Chem.AddHs(mol).GetNumAtoms(), mol.GetNumHeavyAtoms()
    except ImportError:
        return None, None, None, None


def read_changelog(ledger_md):
    """The obstacle ledger's dated entries ('- **23 Sep, 14:4x — title.** body…'): date, time, title (the bold head up to its first full stop) and the
    first 300 characters of the body, newest first as the ledger keeps them. Mechanical; nothing is rewritten."""
    import re
    if not os.path.exists(ledger_md):
        return []
    months = {"Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12", "Aug": "08"}
    out = []
    for line in open(ledger_md, encoding="utf-8"):
        m = re.match(r"- \*\*(\d{1,2}) (Sep|Oct|Nov|Dec|Aug),? ([0-9:x]+) — (.+?)\*\*\s*(.*)", line.strip())
        if not m:
            continue
        day, mon, hhmm, title, body = m.groups()
        out.append(dict(date=f"2026-{months[mon]}-{int(day):02d}", time=hhmm, title=title.strip(), body=body.strip()[:300]))
    out.sort(key=lambda e: (e["date"], e["time"].replace("x", "0")), reverse=True)   # the ledger's day blocks are not strictly ordered; the site is
    return out


def vib_only(freq):
    f = np.asarray(freq, float); keep = np.argsort(np.abs(f))[6:]
    return np.sort(f[keep])


def build(repo, out, limit=None):
    plan = os.path.join(repo, "plans", "05_delta-probed-ir-pipeline"); corpus = os.path.join(plan, "modules", "05_support_predictor", "corpus")
    manifest_p = os.path.join(corpus, "manifest.csv"); ledger_p = os.path.join(corpus, "ledger.csv")
    manifest = list(csv.DictReader(open(manifest_p, encoding="utf-8")))
    if limit:
        done_first = sorted(manifest, key=lambda r: (r["status"] != "done", r["layer"] != "A", r["id"])); manifest = done_first[:limit]   # layer A (benzene, naphthalene) first
    ledger = {}
    for r in csv.DictReader(open(ledger_p, encoding="utf-8")):
        if r["status"] == "done":
            ledger[r["id"]] = r
    releases = {}; replaced = set()
    for rp in sorted(glob.glob(os.path.join(plan, "modules", "05_support_predictor", "data", "corpus_release", "*_manifest.json"))):
        m = json.load(open(rp, encoding="utf-8")); name = os.path.basename(rp).replace("_manifest.json", "")
        for row in m["molecules"]:
            releases.setdefault(row["id"], []).append(name)
        for mid in m.get("analytic_second_route", []):
            replaced.add(mid)
    sr_dir = os.path.join(plan, "modules", "05_support_predictor", "data", "second_route")
    verdicts = {}                                   # the imaginary-mode read-out of 24 Sep: healed / genuine per molecule
    for vp in sorted(glob.glob(os.path.join(sr_dir, "imaginary_second_route_*.json"))):
        for row in json.load(open(vp, encoding="utf-8"))["rows"]:
            v = row.get("molecule_verdict", "")
            if v.startswith("healed"):
                verdicts[row["id"]] = "second_route_healed"
            elif v.startswith("genuine"):
                verdicts[row["id"]] = "imaginary_mode_genuine"
    screen = {}
    sp = os.path.join(sr_dir, "corpus_screen_2026-09-23.json")
    if os.path.exists(sp):
        screen = {r["id"]: r for r in json.load(open(sp, encoding="utf-8"))["rows"]}
    for k, files in list(ANCHORED.items()) + list(VALIDATED.items()):
        for f in files:
            if not os.path.exists(os.path.join(plan, f)):
                raise SystemExit(f"evidence file missing for {k}: {f}")
    os.makedirs(os.path.join(out, "molecules"), exist_ok=True)
    catalog = []; counts = {r: 0 for r in RUNGS}; layer_counts = {}; problems = []
    for r in manifest:
        mid = r["id"]; mdir = os.path.join(corpus, "molecules", mid)
        result_p = os.path.join(mdir, "result.json"); computed = r["status"] == "done" and os.path.exists(result_p)
        formula, ikey, n_atoms_rd, n_heavy_rd = formula_and_key(r["smiles"])
        N = int(r["n_atoms"]) if r.get("n_atoms") else n_atoms_rd          # pending rows of layers B/C carry no atom counts yet
        n_heavy = int(r["n_heavy"]) if r.get("n_heavy") else n_heavy_rd
        if computed and n_atoms_rd is not None and N != n_atoms_rd:
            problems.append(f"{mid}: manifest n_atoms {N} differs from the SMILES count {n_atoms_rd}")
        row = dict(id=mid, name=r["name"], smiles=r["smiles"], formula=formula, inchikey=ikey, layer=r["layer"], n_heavy=n_heavy, n_atoms=N,
                   rung=0, rung_label="listed", flags=[], releases=releases.get(mid, []), manifest_status=r["status"])
        if computed:
            res = json.load(open(result_p, encoding="utf-8"))
            for tag in ("b3lyp", "wb97x"):
                hp = os.path.join(mdir, f"hessian_{tag}.npz")
                if not os.path.exists(hp):
                    problems.append(f"{mid}: computed but no {tag} Hessian"); continue
            row["rung"] = 1
            n_im = {tag: int(res.get(f"n_imaginary_{tag}", 0)) for tag in ("b3lyp", "wb97x")}
            if any(n_im.values()):
                row["flags"].append(verdicts.get(mid, "imaginary_mode_under_review"))
            if os.path.exists(os.path.join(mdir, "analytic_check.json")):
                chk = json.load(open(os.path.join(mdir, "analytic_check.json"), encoding="utf-8"))
                worst = max(float(np.abs(np.array(v["freq_analytic"]) - np.array(v["freq_corpus"])).max()) for v in chk.values())
                row["flags"].append("second_route_agrees" if worst <= 15 else "second_route_disagrees")
            if mid in replaced:
                row["flags"].append("replaced_by_second_route")
            if mid in screen and screen[mid]["max_abs_shift"] > 80:
                row["flags"].append("screen_flagged")
            mol = dict(id=mid, name=r["name"], smiles=r["smiles"], formula=formula, layer=r["layer"], n_atoms=N,
                       geometry=json.load(open(os.path.join(mdir, "geometry.json"), encoding="utf-8")), deck=res.get("deck"), timings_s=res.get("timings_s"),
                       energies=dict(b3lyp=res.get("e_b3lyp"), wb97x=res.get("e_wb97x")), n_imaginary=n_im, frequencies_cm={}, releases=releases.get(mid, []),
                       ledger=ledger.get(mid), second_route=None)
            for tag in ("b3lyp", "wb97x"):
                z = np.load(os.path.join(mdir, f"hessian_{tag}.npz")); fr = np.asarray(z["freq_cm"], float)
                if len(fr) != 3 * N:
                    problems.append(f"{mid}: {tag} frequency list has {len(fr)} entries, 3N = {3 * N}")
                mol["frequencies_cm"][tag] = dict(all=fr.round(2).tolist(), vibrational=vib_only(fr).round(2).tolist())
            if os.path.exists(os.path.join(mdir, "analytic_check.json")):
                chk = json.load(open(os.path.join(mdir, "analytic_check.json"), encoding="utf-8"))
                mol["second_route"] = {tag: dict(max_abs_dfreq_cm=float(np.abs(np.array(v["freq_analytic"]) - np.array(v["freq_corpus"])).max()), dH_max=v["dH_max"]) for tag, v in chk.items()}
            json.dump(mol, open(os.path.join(out, "molecules", mid + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
        if mid in ANCHORED:
            row["rung"] = 4; row["evidence"] = ANCHORED[mid]
        if mid in VALIDATED:
            row["rung"] = 5; row["evidence"] = ANCHORED.get(mid, []) + VALIDATED[mid]
        row["rung_label"] = RUNGS[row["rung"]]; counts[row["rung_label"]] += 1; layer_counts[r["layer"]] = layer_counts.get(r["layer"], 0) + 1
        catalog.append(row)
    # invariants
    ids = {r["id"] for r in manifest}
    if any(row["id"] not in ids for row in catalog):
        problems.append("catalog id without a manifest row")
    if sum(counts.values()) != len(catalog):
        problems.append("rung counts do not add up")
    if problems:
        for p in problems:
            print("INVARIANT:", p, file=sys.stderr)
        raise SystemExit(1)
    json.dump(catalog, open(os.path.join(out, "catalog.json"), "w", encoding="utf-8"), ensure_ascii=False)
    changelog = read_changelog(os.path.join(plan, "GoalGathering", "notes", "Mandate_2026-09-13_Affordable_Plan_Obstacle_Ledger.md"))
    json.dump(changelog, open(os.path.join(out, "changelog.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    summary = dict(built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), n_molecules=len(catalog), rung_counts=counts, layer_counts=layer_counts,
                   rungs=RUNGS, sources=dict(manifest=sha256(manifest_p), ledger=sha256(ledger_p)), releases=sorted({n for v in releases.values() for n in v}),
                   n_changelog=len(changelog))
    json.dump(summary, open(os.path.join(out, "summary.json"), "w", encoding="utf-8"), indent=1)
    return summary


def main():
    ap = argparse.ArgumentParser(); here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--repo", default=os.path.abspath(os.path.join(here, "..", ".."))); ap.add_argument("--out", default=os.path.join(here, "out")); ap.add_argument("--limit", type=int)
    a = ap.parse_args(); s = build(a.repo, a.out, a.limit)
    print(json.dumps({k: v for k, v in s.items() if k != "sources"}, indent=1))


if __name__ == "__main__":
    main()
