"""Module 06 — data freeze: fused-aromatic SMILES from PubChem (public domain), retrieved through PUG-REST and filtered with RDKit.

Query (recorded in data/README.md by this script): for each core in CORES, PubChem's fast substructure search (`fastsubstructure/smiles/<core>/cids`,
MaxRecords per core as given), the union of CIDs, their properties in batches (`ConnectivitySMILES`, `MolecularFormula`, `HeavyAtomCount`, `Charge`,
`IsotopeAtomCount`), then the filters: parses in RDKit; neutral (PubChem charge 0 and no charged atom); elements ⊆ {C, H, N, O, S, F, Cl}; heavy atoms
≤ 30; no isotopes; at least two aromatic rings that share a bond (fused); one canonical SMILES per molecule. Output: data/pubchem_aromatics_<date>.csv
(cid, smiles, formula, n_heavy, n_arom_rings, cores) + data/README.md with counts and SHA-256. Raw responses are cached in data/cache/ (git-ignored).

Not synthetic, not AI-generated, publicly available before the module, not used by modules 02–05. Rate: ≤ 5 requests per second (PubChem's policy).
Usage: python fetch_pubchem_aromatics.py [--max-per-core 50000] [--out-dir ../data]
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request

CORES = {
    "naphthalene": "c1ccc2ccccc2c1", "quinoline": "c1ccc2ncccc2c1", "isoquinoline": "c1ccc2cnccc2c1", "indole": "c1ccc2[nH]ccc2c1",
    "benzofuran": "c1ccc2occc2c1", "benzothiophene": "c1ccc2sccc2c1", "quinoxaline": "c1ccc2nccnc2c1", "benzimidazole": "c1ccc2[nH]cnc2c1",
    "azulene": "c1ccc2cccc-2cc1",
}
ELEMENTS = {"C", "H", "N", "O", "S", "F", "Cl"}
BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
_last = [0.0]


def get(url, data=None, tries=4):
    for k in range(tries):
        dt = time.time() - _last[0]
        if dt < 0.22:
            time.sleep(0.22 - dt)
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "spectrum-atlas-module06/0.1 (academic; frederic.petrignani@gmail.com)"})
            with urllib.request.urlopen(req, timeout=120) as r:
                _last[0] = time.time(); return r.read()
        except Exception as e:
            _last[0] = time.time()
            if k == tries - 1:
                raise
            time.sleep(2.0 * (k + 1))


def cids_for_core(name, smiles, max_records, cache):
    p = os.path.join(cache, f"cids_{name}.json")
    if os.path.exists(p):
        return json.load(open(p))
    url = f"{BASE}/compound/fastsubstructure/smiles/{urllib.parse.quote(smiles, safe='')}/cids/JSON?MaxRecords={max_records}"
    j = json.loads(get(url)); cids = j.get("IdentifierList", {}).get("CID", [])
    json.dump(cids, open(p, "w")); return cids


def properties(cids, cache, batch=500):
    out = {}
    for i in range(0, len(cids), batch):
        chunk = cids[i:i + batch]; key = hashlib.sha1(",".join(map(str, chunk)).encode()).hexdigest()[:16]
        p = os.path.join(cache, f"props_{key}.json")
        if os.path.exists(p):
            j = json.load(open(p))
        else:
            body = urllib.parse.urlencode({"cid": ",".join(map(str, chunk))}).encode()
            j = json.loads(get(f"{BASE}/compound/cid/property/ConnectivitySMILES,MolecularFormula,HeavyAtomCount,Charge,IsotopeAtomCount/JSON", data=body))
            json.dump(j, open(p, "w"))
        for r in j.get("PropertyTable", {}).get("Properties", []):
            out[r["CID"]] = r
        if (i // batch) % 50 == 0:
            print(f"  properties {min(i + batch, len(cids))}/{len(cids)}", flush=True)
    return out


def fused_aromatic_rings(mol):
    ri = mol.GetRingInfo(); arom = [set(r) for r in ri.BondRings() if all(mol.GetBondWithIdx(b).GetIsAromatic() for b in r)]
    fused = any(len(a & b) >= 1 for i, a in enumerate(arom) for b in arom[i + 1:])
    return len(arom), fused


def main():
    ap = argparse.ArgumentParser(); here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--max-per-core", type=int, default=50000); ap.add_argument("--out-dir", default=os.path.join(here, "..", "data")); a = ap.parse_args()
    from rdkit import Chem, RDLogger
    from rdkit.Chem import rdMolDescriptors
    RDLogger.DisableLog("rdApp.*")
    os.makedirs(a.out_dir, exist_ok=True); cache = os.path.join(a.out_dir, "cache"); os.makedirs(cache, exist_ok=True)
    date = time.strftime("%Y-%m-%d"); t0 = time.time()
    hits = {}
    for name, smi in CORES.items():
        cids = cids_for_core(name, smi, a.max_per_core, cache); print(f"{name}: {len(cids)} CIDs", flush=True)
        for c in cids:
            hits.setdefault(c, set()).add(name)
    all_cids = sorted(hits); print(f"union: {len(all_cids)} CIDs; fetching properties", flush=True)
    props = properties(all_cids, cache)
    rows = {}; counts = dict(union=len(all_cids), with_properties=len(props), parsed=0, neutral=0, elements=0, size=0, no_isotope=0, fused=0, unique=0)
    for cid in all_cids:
        r = props.get(cid)
        if not r:
            continue
        mol = Chem.MolFromSmiles(r.get("ConnectivitySMILES", ""))
        if mol is None:
            continue
        counts["parsed"] += 1
        if int(r.get("Charge", 0)) != 0 or any(at.GetFormalCharge() != 0 for at in mol.GetAtoms()):
            continue
        counts["neutral"] += 1
        if not {at.GetSymbol() for at in mol.GetAtoms()} <= ELEMENTS:
            continue
        counts["elements"] += 1
        if mol.GetNumHeavyAtoms() > 30:
            continue
        counts["size"] += 1
        if int(r.get("IsotopeAtomCount", 0)) != 0 or any(at.GetIsotope() for at in mol.GetAtoms()):
            continue
        counts["no_isotope"] += 1
        n_ar, fused = fused_aromatic_rings(mol)
        if n_ar < 2 or not fused:
            continue
        counts["fused"] += 1
        can = Chem.MolToSmiles(mol)
        if can in rows:
            rows[can]["cores"] |= hits[cid]; continue
        rows[can] = dict(cid=cid, smiles=can, formula=rdMolDescriptors.CalcMolFormula(mol), n_heavy=mol.GetNumHeavyAtoms(), n_arom_rings=n_ar, cores=set(hits[cid]))
    counts["unique"] = len(rows)
    out_csv = os.path.join(a.out_dir, f"pubchem_aromatics_{date}.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["cid", "smiles", "formula", "n_heavy", "n_arom_rings", "cores"])
        for r in sorted(rows.values(), key=lambda r: r["cid"]):
            w.writerow([r["cid"], r["smiles"], r["formula"], r["n_heavy"], r["n_arom_rings"], "|".join(sorted(r["cores"]))])
    sha = hashlib.sha256(open(out_csv, "rb").read()).hexdigest()
    readme = os.path.join(a.out_dir, "README.md")
    open(readme, "w", encoding="utf-8").write(f"""# Module 06 dataset — fused-aromatic SMILES from PubChem (frozen {date})

**Source.** PubChem (public domain; NIH/NLM), through PUG-REST on {date}: for each core below, `fastsubstructure/smiles/<core>/cids` with
MaxRecords = {a.max_per_core}; the union of CIDs; properties `ConnectivitySMILES, MolecularFormula, HeavyAtomCount, Charge, IsotopeAtomCount` in
batches of 500. Cores: {", ".join(f"{k} (`{v}`)" for k, v in CORES.items())}. Raw responses are cached in `cache/` (not committed; the CSV is the frozen dataset).

**Filters (RDKit {Chem.rdBase.rdkitVersion}).** parses; neutral (PubChem charge 0, no charged atom); elements within C H N O S F Cl; heavy atoms ≤ 30; no isotopes;
at least two aromatic rings that share an atom (fused); one row per canonical SMILES.

| step | molecules |
|---|---|
| union of the core searches | {counts['union']:,} |
| with properties returned | {counts['with_properties']:,} |
| parsed by RDKit | {counts['parsed']:,} |
| neutral | {counts['neutral']:,} |
| elements within C H N O S F Cl | {counts['elements']:,} |
| ≤ 30 heavy atoms | {counts['size']:,} |
| no isotopes | {counts['no_isotope']:,} |
| ≥ 2 fused aromatic rings | {counts['fused']:,} |
| **unique canonical SMILES (the dataset)** | **{counts['unique']:,}** |

**File.** `{os.path.basename(out_csv)}` — columns `cid, smiles, formula, n_heavy, n_arom_rings, cores`; SHA-256 `{sha}`.

**Rubric statement.** Publicly available before this module started (PubChem, deposited records), appropriate for academic use, real deposited chemistry —
not synthetic, not AI-generated — and not the dataset of modules 02 (PAHdb computed library), 03 (PAHdb laboratory bands), 04 (matched pairs) or
05 (Hessian QM9 and the project's own corpus). The core list biases the sample toward fused aromatics on purpose (the atlas's domain); the bias is
reported in the module's ethics section. Retrieval took {time.time() - t0:.0f} s.
""")
    print(json.dumps(counts, indent=1)); print("wrote", out_csv, sha[:16], "and", readme)


if __name__ == "__main__":
    main()
