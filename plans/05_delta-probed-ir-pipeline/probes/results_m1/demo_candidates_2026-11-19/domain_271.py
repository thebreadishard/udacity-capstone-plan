"""How the release pool covers the shortlist's families: small molecules, monocyclic five-rings, azines, fluorine/sulfur, N-H/O-H groups."""
from collections import Counter

from m08 import pipeline as P
from m08 import seen as S
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")
neutral, cation = S.manifest_smiles()
ids = P.train_ids(P.carried_models(P.NK.RELEASE))
mols = {i: Chem.AddHs(Chem.MolFromSmiles(neutral[i])) for i in ids if i in neutral}
print("release ids", len(ids), "neutral", len(mols), "cations", len(ids) - len(mols))
sizes = Counter(m.GetNumAtoms() for m in mols.values())
print("atoms <= 12:", sum(v for k, v in sizes.items() if k <= 12), " <= 16:", sum(v for k, v in sizes.items() if k <= 16))
PAT = {
    "monocyclic 5-ring aromatic only": None,
    "aromatic 5-ring any": "[a;r5]",
    "pyrrole-type [nH]": "[nH]",
    "furan-type o": "o",
    "thiophene-type s": "s",
    "azine n:c:n / n:n": "[n;r6]~[c,n;r6]~[n;r6]",
    "n:n adjacent": "n:n",
    "F": "[F]", "S non-aromatic": "[S;!a]", "N(C)C dimethylamino": "[CH3][NX3]([CH3])c",
    "amide NC(=O)": "[NX3][CX3](=O)", "isopropyl": "[CH3][CH]([CH3])c", "ethyl on arene": "[CH3][CH2]c", "ethoxy": "[CH3][CH2]O",
    "aldehyde": "[CX3H1](=O)", "vinyl conj": "C=Cc", "methyl on arene": "[CH3]c", "methoxy": "[CH3]Oc", "sp3 CH2": "[CH2;X4]",
    "pyrimidine n:c:n": "n:c:n", "pyrazine 6-ring n:c:c:n": "[n;r6]:[c;r6]:[c;r6]:[n;r6]",
    "imidazole/oxazole n:c:X": "[n;r5]:c:[n,o,s;r5]", "trimethyl 1,3,5": "[CH3]c1cc([CH3])cc([CH3])c1", "acetamido": "CC(=O)Nc",
    "ring C=O ketone": "[C;R](=O)([#6;R])[#6;R]", "SCH3": "[CH3]S", "C=C-C=O conj": "C=CC=O",
}
counts = {}
for name, smarts in PAT.items():
    if smarts is None:
        counts[name] = sum(1 for m in mols.values() if m.GetRingInfo().NumRings() == 1
                           and len(m.GetRingInfo().AtomRings()[0]) == 5)
        continue
    q = Chem.MolFromSmarts(smarts)
    counts[name] = sum(1 for m in mols.values() if m.HasSubstructMatch(q))
for k, v in counts.items():
    print(f"{k}: {v}")
small = sorted((m.GetNumAtoms(), Chem.MolToSmiles(Chem.RemoveHs(m))) for m in mols.values() if m.GetNumAtoms() <= 12)
print("smallest:", small[:25])
