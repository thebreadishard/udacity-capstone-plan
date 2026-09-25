"""Module 06 — data: the frozen PubChem CSV, the scaffold split, the character tokenizer (PRE_REGISTRATION.md, "Data handling")."""
import csv
import hashlib
import os
import re
from dataclasses import dataclass

TOKEN_RE = re.compile(r"Cl|Br|\[[^\]]+\]|.", re.S)     # two-letter elements and bracket atoms are single tokens; everything else one character
SPECIAL = ["<pad>", "<bos>", "<eos>"]


def read_dataset(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    for r in rows:
        r["n_heavy"] = int(r["n_heavy"]); r["n_arom_rings"] = int(r["n_arom_rings"])
    return rows


def murcko(smiles):
    from rdkit import Chem
    from rdkit.Chem.Scaffolds import MurckoScaffold
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return ""
    try:
        return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(mol))
    except Exception:
        return ""


def split_of(scaffold_smiles):
    """Deterministic 80/10/10 by the sha1 of the Murcko scaffold: a scaffold never straddles splits."""
    h = int(hashlib.sha1(scaffold_smiles.encode("utf-8")).hexdigest()[:8], 16) % 100
    return "train" if h < 80 else "val" if h < 90 else "test"


def assign_splits(rows):
    for r in rows:
        r["scaffold"] = murcko(r["smiles"]); r["split"] = split_of(r["scaffold"])
    return rows


def tokenize(smiles):
    return TOKEN_RE.findall(smiles)


BRACKET_RE = re.compile(r"\[\d*([A-Z][a-z]?|[a-z]{1,2})")


def hetero_class(smiles):
    """Heteroatom class of a SMILES: none / N / O / S / mixed (F, Cl, Br, H, B and C do not count). 25 Sep 2026: the first version matched
    "[A-Z][a-z]?" on the raw string and read the aliphatic-aromatic pair "Cc" as an element (class "<hCC>", absent from the vocabulary);
    elements are now read per token: bracket atoms by their leading symbol (so [nH] is nitrogen), Cl/Br, and single organic-subset letters."""
    els = set()
    for tok in tokenize(smiles):
        if tok.startswith("["):
            m = BRACKET_RE.match(tok); e = m.group(1) if m else ""
        elif tok in ("Cl", "Br") or (len(tok) == 1 and tok.isalpha()):
            e = tok
        else:
            continue
        if e: els.add(e.capitalize())
    het = {e.lower() for e in els} - {"c", "h", "cl", "br", "f", "b"}
    if not het:
        return "none"
    return sorted(het)[0].upper() if len(het) == 1 else "mixed"


@dataclass
class Vocab:
    itos: list

    @property
    def stoi(self):
        return {t: i for i, t in enumerate(self.itos)}

    @classmethod
    def build(cls, smiles_list, conditioning=False):
        toks = set()
        for s in smiles_list:
            toks |= set(tokenize(s))
        cond = ["<r2>", "<r3>", "<r4+>", "<hN>", "<hO>", "<hS>", "<hnone>", "<hmixed>"] if conditioning else []
        return cls(SPECIAL + cond + sorted(toks))

    def encode(self, smiles, max_len=96, prefix=()):
        ids = [self.stoi["<bos>"]] + [self.stoi[p] for p in prefix] + [self.stoi[t] for t in tokenize(smiles)] + [self.stoi["<eos>"]]
        if len(ids) > max_len:
            return None
        return ids + [0] * (max_len - len(ids))

    def decode(self, ids):
        out = []
        for i in ids:
            t = self.itos[i]
            if t == "<eos>":
                break
            if t in SPECIAL or t.startswith("<"):
                continue
            out.append(t)
        return "".join(out)


def prefix_for(row):
    n = row["n_arom_rings"]; r = "<r2>" if n <= 2 else "<r3>" if n == 3 else "<r4+>"
    h = hetero_class(row["smiles"]); return (r, "<h" + h + ">")
