#!/usr/bin/env python
"""Builds / extends corpus/manifest.csv from the DESIGN lists. Deterministic: canonical SMILES via RDKit, order inside a
layer = SHA-1 of the canonical SMILES (or QM9 label). Existing rows keep their id, priority and status; new molecules are
appended. Run:  python build_manifest.py"""
import csv, hashlib
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Descriptors

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.csv"
QM9_CONJ = HERE.parent / "data" / "hessian_qm9" / "conjugated_ring_labels.txt"
FIELDS = ["id", "layer", "priority", "name", "smiles", "qm9_label", "n_heavy", "n_atoms", "status", "machine", "deck", "note"]

# ---- layer A: the size bridge (explicit; names are conventional)
LAYER_A = [
    ("benzene", "c1ccccc1"), ("naphthalene", "c1ccc2ccccc2c1"), ("azulene", "c1ccc2cccc2cc1"), ("quinoline", "c1ccc2ncccc2c1"),
    ("biphenyl", "c1ccc(cc1)-c1ccccc1"), ("isoquinoline", "c1ccc2cnccc2c1"), ("indole", "c1ccc2[nH]ccc2c1"), ("benzofuran", "c1ccc2occc2c1"),
    ("benzothiophene", "c1ccc2sccc2c1"), ("quinoxaline", "c1ccc2nccnc2c1"), ("quinazoline", "c1ccc2ncncc2c1"), ("1-naphthol", "Oc1cccc2ccccc12"),
    ("2-naphthylamine", "Nc1ccc2ccccc2c1"), ("1-methylnaphthalene", "Cc1cccc2ccccc12"), ("2-methylnaphthalene", "Cc1ccc2ccccc2c1"),
    ("1-naphthonitrile", "N#Cc1cccc2ccccc12"), ("acenaphthylene", "c1cc2cccc3C=Cc(c1)c23"), ("acenaphthene", "c1cc2cccc3CCc(c1)c23"),
    ("fluorene", "c1ccc2c(c1)Cc1ccccc1-2"), ("biphenylene", "c1ccc2c(c1)-c1ccccc1-2"), ("anthracene", "c1ccc2cc3ccccc3cc2c1"),
    ("phenanthrene", "c1ccc2c(c1)ccc1ccccc12"), ("acridine", "c1ccc2nc3ccccc3cc2c1"), ("phenazine", "c1ccc2nc3ccccc3nc2c1"),
    ("phenanthridine", "c1ccc2c(c1)cnc1ccccc12"), ("carbazole", "c1ccc2c(c1)[nH]c1ccccc12"), ("dibenzofuran", "c1ccc2c(c1)oc1ccccc12"),
    ("dibenzothiophene", "c1ccc2c(c1)sc1ccccc12"), ("pyrene", "c1cc2ccc3cccc4ccc(c1)c2c34"), ("fluoranthene", "c1ccc2c(c1)-c1cccc3cccc-2c13"),
    ("4-phenylpyridine", "c1ccc(cc1)-c1ccncc1"), ("2-phenylpyridine", "c1ccc(cc1)-c1ccccn1"), ("stilbene_E", "C(=C/c1ccccc1)\\c1ccccc1"),
    ("diphenylacetylene", "C(#Cc1ccccc1)c1ccccc1"), ("diphenyl_ether", "O(c1ccccc1)c1ccccc1"), ("benzophenone", "O=C(c1ccccc1)c1ccccc1"),
    ("1-aminoanthracene", "Nc1cccc2cc3ccccc3cc12"), ("9-methylanthracene", "Cc1c2ccccc2cc2ccccc12"), ("2-naphthoic_acid", "OC(=O)c1ccc2ccccc2c1"),
    ("1,8-naphthalimide-free_diimide_model_1,8-naphthalic_anhydride", "O=C1OC(=O)c2cccc3cccc1c23"), ("quinoline-N-oxide", "[O-][n+]1cccc2ccccc12"),
    ("indene", "C1C=Cc2ccccc12"), ("styrene", "C=Cc1ccccc1"), ("phenylacetylene", "C#Cc1ccccc1"), ("benzonitrile", "N#Cc1ccccc1"),
]
TIMING_FIRST = ["benzene", "naphthalene", "azulene", "quinoline", "biphenyl"]   # forced to the front of layer A (DESIGN: timing test)

# ---- layer B: cores x substituents (mono, and di for the three main cores), deduplicated
CORES = {"benzene": "c1ccccc1", "naphthalene": "c1ccc2ccccc2c1", "pyridine": "c1ccncc1", "pyrimidine": "c1cncnc1", "pyrazine": "c1cnccn1",
         "pyrrole": "c1cc[nH]c1", "furan": "c1ccoc1", "thiophene": "c1ccsc1", "imidazole": "c1c[nH]cn1", "oxazole": "c1cocn1", "thiazole": "c1cscn1",
         "indole": "c1ccc2[nH]ccc2c1", "benzofuran": "c1ccc2occc2c1", "benzothiophene": "c1ccc2sccc2c1", "quinoline": "c1ccc2ncccc2c1",
         "isoquinoline": "c1ccc2cnccc2c1", "azulene": "c1ccc2cccc2cc1", "biphenyl": "c1ccc(cc1)-c1ccccc1", "styrene": "C=Cc1ccccc1"}
SUBS = {"CH3": "C", "OH": "O", "NH2": "N", "F": "F", "Cl": "Cl", "CN": "C#N", "CHO": "C=O", "COOH": "C(=O)O", "OCH3": "OC", "NO2": "[N+](=O)[O-]",
        "CF3": "C(F)(F)F", "vinyl": "C=C", "ethynyl": "C#C", "CONH2": "C(N)=O", "SH": "S"}
DI_CORES = ["benzene", "naphthalene", "pyridine"]
MAX_ATOMS_B = 26

# ---- layer A2 (A′, added 2026-09-12 on the user's decision): substituted three- and four-ring cores, the size bridge as a
# distribution rather than a list of parents; mono-substituted for every core, di-substituted for the three all-carbon PAHs
BIG_CORES = {"anthracene": "c1ccc2cc3ccccc3cc2c1", "phenanthrene": "c1ccc2c(c1)ccc1ccccc12", "pyrene": "c1cc2ccc3cccc4ccc(c1)c2c34",
             "fluoranthene": "c1ccc2c(c1)-c1cccc3cccc-2c13", "acridine": "c1ccc2nc3ccccc3cc2c1", "phenazine": "c1ccc2nc3ccccc3nc2c1",
             "carbazole": "c1ccc2c(c1)[nH]c1ccccc12", "dibenzofuran": "c1ccc2c(c1)oc1ccccc12", "dibenzothiophene": "c1ccc2c(c1)sc1ccccc12",
             "fluorene": "c1ccc2c(c1)Cc1ccccc1-2", "biphenylene": "c1ccc2c(c1)-c1ccccc1-2", "acenaphthylene": "c1cc2cccc3C=Cc(c1)c23",
             "phenanthridine": "c1ccc2c(c1)cnc1ccccc12", "quinoxaline": "c1ccc2nccnc2c1"}
DI_BIG = []   # mono-substituted only: di-substitution of the three PAHs alone gave 11,000 rows at 1-2 h each (build of 2026-09-12 09:58), out of proportion to any machine we will have; the size axis is served by ~1,000 mono products
MAX_ATOMS_A2 = 34


def canon(smi):
    m = Chem.MolFromSmiles(smi)
    return Chem.MolToSmiles(m) if m else None


def substituted(core_smi, sub_smi, positions=1):
    """All distinct products of attaching one substituent to each aromatic C-H (and a second, for di) — via SMILES edits on
    explicit atom maps is fragile; instead enumerate by RDKit atom replacement."""
    core = Chem.MolFromSmiles(core_smi); out = set()
    sub = Chem.MolFromSmiles(sub_smi)
    hs = [a.GetIdx() for a in core.GetAtoms() if a.GetIsAromatic() and a.GetSymbol() == "C" and a.GetTotalNumHs() == 1]
    hs += [a.GetIdx() for a in core.GetAtoms() if not a.GetIsAromatic() and a.GetSymbol() == "C" and a.GetTotalNumHs() >= 1 and any(n.GetIsAromatic() for n in a.GetNeighbors())]
    def attach(mol, idx):
        rw = Chem.RWMol(Chem.CombineMols(mol, sub)); n0 = mol.GetNumAtoms()
        rw.AddBond(idx, n0, Chem.BondType.SINGLE)
        try:
            Chem.SanitizeMol(rw); return Chem.MolToSmiles(rw)
        except Exception:
            return None
    for i in hs:
        s = attach(core, i)
        if s: out.add(s)
    return out


def enumerate_layer(cores, di_cores, max_atoms, exclude=()):
    mols = {}
    for cname, csmi in cores.items():
        for sname, ssmi in SUBS.items():
            for s in substituted(csmi, ssmi):
                mols.setdefault(canon(s), f"{cname}+{sname}")
    # di-substituted on the named cores: attach a second substituent to each mono product
    monos = {k: v for k, v in mols.items() if v.split("+")[0] in di_cores}
    for smi, name in list(monos.items()):
        for sname, ssmi in SUBS.items():
            for s in substituted(smi, ssmi):
                c = canon(s)
                if c and c not in mols:
                    mols[c] = f"{name}+{sname}"
    rows = []
    for smi, name in mols.items():
        if smi in exclude:
            continue
        m = Chem.AddHs(Chem.MolFromSmiles(smi)); na = m.GetNumAtoms(); nh = m.GetNumHeavyAtoms()
        if na <= max_atoms:
            rows.append((name, smi, nh, na))
    return rows


def layer_b():
    return enumerate_layer(CORES, DI_CORES, MAX_ATOMS_B)


def layer_a2(exclude):
    return enumerate_layer(BIG_CORES, DI_BIG, MAX_ATOMS_A2, exclude=exclude)


def main():
    existing = {}
    if MANIFEST.exists():
        with open(MANIFEST, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                existing[(r["layer"], r["smiles"] or r["qm9_label"])] = r
    rows = list(existing.values())
    def add(layer, name, smiles, qm9_label, nh, na, note=""):
        key = (layer, smiles or qm9_label)
        if key in existing:
            return
        pr = hashlib.sha1((smiles or qm9_label).encode()).hexdigest()
        rows.append(dict(id=f"{layer}_{pr[:10]}", layer=layer, priority=pr, name=name, smiles=smiles, qm9_label=qm9_label, n_heavy=nh, n_atoms=na, status="pending", machine="", deck="", note=note))
        existing[key] = rows[-1]
    for name, smi in LAYER_A:
        c = canon(smi); m = Chem.AddHs(Chem.MolFromSmiles(c))
        add("A", name, c, "", m.GetNumHeavyAtoms(), m.GetNumAtoms(), note="timing-test" if name in TIMING_FIRST else "")
    for name, smi, nh, na in layer_b():
        add("B", name, smi, "", nh, na)
    a_smiles = {canon(s) for _, s in LAYER_A}
    for name, smi, nh, na in layer_a2(exclude=a_smiles):
        add("A2", name, smi, "", nh, na)
    if QM9_CONJ.exists():
        for lab in QM9_CONJ.read_text().split():
            add("C", lab, "", lab, "", "", note="B3LYP only at the Hessian-QM9 geometry")
    # file order: layer (A, A2, B, C), timing-test rows first inside A, then priority hash; the RUN order (A, then B and A2
    # alternating, then C) is the runner's business, see run_corpus.queue_order
    rows.sort(key=lambda r: (r["layer"], 0 if r.get("note") == "timing-test" else 1, r["priority"]))
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for r in rows: w.writerow({k: r.get(k, "") for k in FIELDS})
    import collections
    c = collections.Counter(r["layer"] for r in rows)
    print("manifest rows:", len(rows), dict(sorted(c.items())))
    b = [r for r in rows if r["layer"] == "B"]
    if b:
        import statistics
        print("layer B atoms: min", min(int(r["n_atoms"]) for r in b), "median", statistics.median(int(r["n_atoms"]) for r in b), "max", max(int(r["n_atoms"]) for r in b))


if __name__ == "__main__":
    main()
