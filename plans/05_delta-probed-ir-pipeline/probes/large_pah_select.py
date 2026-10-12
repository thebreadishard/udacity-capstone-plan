"""Lever 5 (TASKS 49, 12 Oct 2026): pick the large PAHs from PAHdb v4.00 by a fixed rule, before any is computed.

Test set — the mandate's four shape molecules (jet-cooled spectra, Lemmens et al. 2021): coronene, peropyrene, ovalene and
hexa-peri-hexabenzocoronene. Each is found by its carbon skeleton, i.e. the graph without bond orders or hydrogens, against PubChem's
structure (CIDs 9115, 9103, 67446, 136001; SMILES fetched 12 Oct 2026). The formula alone does not identify them: C26H14 has 10 PAHdb
entries and C42H18 22.

Training set — one molecule per target size (34, 38, 42, 44, 48, 54 atoms). It must be:
- neutral, closed-shell (RB3LYP), carbon and hydrogen (no bare carbon clusters), no CH2 or CH3;
- free of a coronene skeleton. Three of the four test molecules contain coronene, so training on coronene derivatives would mix scaffold and
  size;
- not one of the four test skeletons.
Within each size, the first candidate by the sha1 of its uid is taken.

PAHdb's geometries are B3LYP/4-31G; the corpus re-optimises them at its own B3LYP/6-31G*. RDKit (system Python).

    python probes/large_pah_select.py [--xml modules/02_opponent_atlas/data/pahdb-complete-theoretical-v4.00_*.xml]
        → probes/results_m1/large_labels_price_2026-10-12/selection.json
"""
import argparse
import glob
import hashlib
import json
import os
import xml.etree.ElementTree as ET

from rdkit import Chem
from rdkit.Chem import rdDetermineBonds

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.dirname(HERE)
OUT = os.path.join(HERE, "results_m1", "large_labels_price_2026-10-12", "selection.json")
TEST = {"coronene": (9115, "C1=CC2=C3C4=C1C=CC5=C4C6=C(C=C5)C=CC7=C6C3=C(C=C2)C=C7"),
        "peropyrene": (9103, "C1=CC2=C3C(=C1)C=CC4=C3C(=C5C=CC6=C7C5=C4C=CC7=CC=C6)C=C2"),
        "ovalene": (67446, "C1=CC2=C3C4=C1C=CC5=CC6=C7C8=C(C=CC9=C8C1=C(C=C9)C=C(C3=C1C7=C54)C=C2)C=C6"),
        "hexa-peri-hexabenzocoronene": (136001, "C1=CC2=C3C=CC=C4C3=C5C6=C2C(=C1)C7=C8C6=C9C1=C(C8=CC=C7)C=CC=C1C1=CC=CC2=C1C9=C5C1=C4C=CC=C21")}
TRAIN_SIZES = (34, 38, 42, 44, 48, 54)


def skeleton(mol):
    """The carbon graph without bond orders, aromaticity or hydrogens, as a canonical SMILES."""
    m = Chem.RWMol(Chem.RemoveHs(mol, sanitize=False))
    for b in m.GetBonds():
        b.SetBondType(Chem.BondType.SINGLE)
        b.SetIsAromatic(False)
    for a in m.GetAtoms():
        a.SetIsAromatic(False)
        a.SetNoImplicit(True)
        a.SetNumExplicitHs(0)
    return Chem.MolToSmiles(m.GetMol(), canonical=True)


def skeleton_from_xyz(symbols, xyz):
    block = f"{len(symbols)}\n\n" + "\n".join(f"{s} {x:.6f} {y:.6f} {z:.6f}" for s, (x, y, z) in zip(symbols, xyz, strict=True))
    mol = Chem.MolFromXYZBlock(block)
    rdDetermineBonds.DetermineConnectivity(mol)
    return skeleton(mol)


def species(xml_path):
    """Neutral closed-shell species of carbon and hydrogen, 34–60 atoms, without CH2/CH3: dicts with uid, formula, symbols, xyz (Å)."""
    for _, el in ET.iterparse(xml_path, events=("end",)):
        if not el.tag.endswith("specie"):
            continue
        get = {c.tag.split("}")[-1]: c for c in el}
        try:
            charge = int(get["charge"].text)
            method = get["method"].text.strip()
            n_sat = sum(int(get[k].text) for k in ("n_ch2", "n_ch3") if k in get)
            atoms = [{c.tag.split("}")[-1]: c.text for c in a} for a in get["geometry"]]
        except (KeyError, AttributeError, ValueError):
            el.clear()
            continue
        Z = [int(a["type"]) for a in atoms]
        if charge == 0 and method == "RB3LYP" and n_sat == 0 and set(Z) == {1, 6} and 34 <= len(Z) <= 60:   # C and H both (no bare carbon clusters)
            yield {"uid": int(el.get("uid")), "formula": get["formula"].text.strip(), "symbols": ["H" if z == 1 else "C" for z in Z],
                   "xyz": [[float(a["x"]), float(a["y"]), float(a["z"])] for a in atoms]}
        el.clear()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--xml", default=glob.glob(os.path.join(PLAN, "modules", "02_opponent_atlas", "data", "pahdb-complete-theoretical-v4.00_*.xml"))[0])
    a = ap.parse_args()
    test_skel = {skeleton(Chem.MolFromSmiles(smi)): name for name, (_, smi) in TEST.items()}
    coronene = Chem.MolFromSmiles(skeleton(Chem.MolFromSmiles(TEST["coronene"][1])), sanitize=False)
    found = {name: [] for name in TEST}
    by_size = {n: [] for n in TRAIN_SIZES}
    n_seen = 0
    for sp in species(a.xml):
        n_seen += 1
        sk = skeleton_from_xyz(sp["symbols"], sp["xyz"])
        sp["skeleton"] = sk
        if sk in test_skel:
            found[test_skel[sk]].append(sp)
            continue
        n = len(sp["symbols"])
        if n in by_size:
            m = Chem.MolFromSmiles(sk, sanitize=False)
            m.UpdatePropertyCache(strict=False)
            if not m.HasSubstructMatch(coronene):
                by_size[n].append(sp)
    test = {}
    for name, hits in found.items():
        if not hits:
            raise SystemExit(f"{name}: no PAHdb entry with its skeleton")
        hits.sort(key=lambda s: s["uid"])
        test[name] = dict(hits[0], cid=TEST[name][0], pahdb_entries=[h["uid"] for h in hits])
    train = {}
    for n, cands in by_size.items():
        cands.sort(key=lambda s: hashlib.sha1(str(s["uid"]).encode()).hexdigest())
        if cands:
            train[n] = dict(cands[0], candidates=len(cands))
    out = {"rule": __doc__.split("Training set")[1].split("PAHdb's geometries")[0].strip(), "pahdb_xml": os.path.basename(a.xml),
           "species_screened": n_seen, "test": test, "train": train}
    json.dump(out, open(OUT, "w"), indent=1)
    for name, s in test.items():
        print(f"test  {name:30s} uid {s['uid']:6d} {s['formula']:8s} entries {s['pahdb_entries']}")
    for n, s in train.items():
        print(f"train {n:2d} atoms uid {s['uid']:6d} {s['formula']:8s} of {s['candidates']} candidates  {s['skeleton']}")
    print(f"{n_seen} species screened; {OUT}")


if __name__ == "__main__":
    main()
