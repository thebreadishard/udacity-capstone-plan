"""Module 06 — the pre-registered metrics (PRE_REGISTRATION.md, "Metrics"): validity, uniqueness, novelty, scaffold novelty, memorisation,
distribution match (Wasserstein-1 on heavy atoms, aromatic rings, heteroatoms), project fit, conditioning obedience."""
import re

import numpy as np

ELEMENTS = {"C", "H", "N", "O", "S", "F", "Cl"}


def canonical(smiles):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    m = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(m) if m is not None else None


def descriptors(smiles):
    from rdkit import Chem
    m = Chem.MolFromSmiles(smiles)
    ri = m.GetRingInfo(); arom = sum(1 for r in ri.BondRings() if all(m.GetBondWithIdx(b).GetIsAromatic() for b in r))
    het = sum(1 for a in m.GetAtoms() if a.GetSymbol() not in ("C", "H"))
    return m.GetNumHeavyAtoms(), arom, het


def project_fit(smiles):
    """Neutral, elements within the corpus set, ≤ 30 heavy atoms, ≥ 2 fused aromatic rings."""
    from rdkit import Chem
    m = Chem.MolFromSmiles(smiles)
    if m is None or any(a.GetFormalCharge() for a in m.GetAtoms()) or not {a.GetSymbol() for a in m.GetAtoms()} <= ELEMENTS or m.GetNumHeavyAtoms() > 30:
        return False
    ri = m.GetRingInfo(); arom = [set(r) for r in ri.BondRings() if all(m.GetBondWithIdx(b).GetIsAromatic() for b in r)]
    return len(arom) >= 2 and any(a & b for i, a in enumerate(arom) for b in arom[i + 1:])


def wasserstein1(a, b):
    a, b = np.sort(np.asarray(a, float)), np.sort(np.asarray(b, float))
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    q = np.linspace(0, 1, 201)
    return float(np.mean(np.abs(np.quantile(a, q) - np.quantile(b, q))))


def evaluate_samples(samples, train_smiles, train_scaffolds, test_rows, murcko):
    valid = [c for c in (canonical(s) for s in samples) if c]
    uniq = sorted(set(valid)); train_set = set(train_smiles); scaf_set = set(train_scaffolds)
    novel = [s for s in uniq if s not in train_set]
    scaf_novel = [s for s in novel if murcko(s) not in scaf_set]
    n = max(len(samples), 1)
    d_s = np.array([descriptors(s) for s in uniq]) if uniq else np.zeros((0, 3))
    d_t = np.array([descriptors(r["smiles"]) for r in test_rows])
    res = dict(n_samples=len(samples), validity=len(valid) / n, uniqueness=(len(uniq) / len(valid)) if valid else 0.0,
               novelty=(len(novel) / len(uniq)) if uniq else 0.0, scaffold_novelty=(len(scaf_novel) / len(uniq)) if uniq else 0.0,
               memorisation=(sum(1 for s in valid if s in train_set) / len(valid)) if valid else 0.0,
               project_fit=(sum(project_fit(s) for s in novel) / len(novel)) if novel else 0.0,
               w1_heavy=wasserstein1(d_s[:, 0], d_t[:, 0]) if len(d_s) else None, w1_arom_rings=wasserstein1(d_s[:, 1], d_t[:, 1]) if len(d_s) else None,
               w1_hetero=wasserstein1(d_s[:, 2], d_t[:, 2]) if len(d_s) else None)
    invalid = [s for s in samples if canonical(s) is None][:20]
    return res, dict(valid_unique=uniq, novel=novel, invalid_examples=invalid)


def obedience(samples_with_prefix, hetero_class, ring_class_of):
    """Fraction of valid samples whose ring class and heteroatom class equal the requested prefix."""
    ok = tot = 0
    for smi, (r_req, h_req) in samples_with_prefix:
        c = canonical(smi)
        if c is None:
            continue
        tot += 1; ok += int(ring_class_of(c) == r_req and ("<h" + hetero_class(c) + ">") == h_req)
    return ok / tot if tot else 0.0
