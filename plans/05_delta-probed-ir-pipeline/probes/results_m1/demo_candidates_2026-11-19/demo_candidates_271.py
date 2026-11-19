"""TASKS 271: screen candidate demo molecules against the corpus, the v1.4 release and measurement networks, the gates and the time fit.
Run from PLAN/modules/08_industry_synthesis so `m08` imports. Read-only."""
from __future__ import annotations

import csv
import json
import sys

from m08 import pipeline as P
from m08 import runtime as RT
from m08 import seen as S
from m08.catalog import canonical
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

CANDIDATES = [
    ("toluene", "Cc1ccccc1"), ("anisole", "COc1ccccc1"), ("benzaldehyde", "O=Cc1ccccc1"), ("acetophenone", "CC(=O)c1ccccc1"),
    ("phenol", "Oc1ccccc1"), ("aniline", "Nc1ccccc1"), ("benzoic acid", "OC(=O)c1ccccc1"), ("o-xylene", "Cc1ccccc1C"),
    ("m-xylene", "Cc1cccc(C)c1"), ("p-xylene", "Cc1ccc(C)cc1"), ("ethylbenzene", "CCc1ccccc1"), ("styrene", "C=Cc1ccccc1"),
    ("benzonitrile", "N#Cc1ccccc1"), ("nitrobenzene", "O=[N+]([O-])c1ccccc1"), ("benzyl alcohol", "OCc1ccccc1"),
    ("methyl benzoate", "COC(=O)c1ccccc1"), ("acetanilide", "CC(=O)Nc1ccccc1"), ("o-cresol", "Cc1ccccc1O"), ("p-cresol", "Cc1ccc(O)cc1"),
    ("m-cresol", "Cc1cccc(O)c1"), ("catechol", "Oc1ccccc1O"), ("resorcinol", "Oc1cccc(O)c1"), ("hydroquinone", "Oc1ccc(O)cc1"),
    ("p-toluidine", "Cc1ccc(N)cc1"), ("N,N-dimethylaniline", "CN(C)c1ccccc1"), ("salicylaldehyde", "O=Cc1ccccc1O"),
    ("methyl salicylate", "COC(=O)c1ccccc1O"), ("mesitylene", "Cc1cc(C)cc(C)c1"), ("cumene", "CC(C)c1ccccc1"),
    ("phenylacetylene", "C#Cc1ccccc1"), ("4-hydroxybenzaldehyde", "O=Cc1ccc(O)cc1"), ("vanillin", "COc1cc(C=O)ccc1O"),
    ("paracetamol", "CC(=O)Nc1ccc(O)cc1"), ("aspirin", "CC(=O)Oc1ccccc1C(=O)O"), ("thymol", "Cc1ccc(C(C)C)c(O)c1"),
    ("eugenol", "C=CCc1ccc(O)c(OC)c1"), ("cinnamaldehyde", "O=C/C=C/c1ccccc1"), ("anthranilic acid", "Nc1ccccc1C(=O)O"),
    ("4-nitrophenol", "O=[N+]([O-])c1ccc(O)cc1"), ("benzophenone", "O=C(c1ccccc1)c1ccccc1"), ("diphenyl ether", "c1ccc(Oc2ccccc2)cc1"),
    ("2-picoline", "Cc1ccccn1"), ("3-picoline", "Cc1cccnc1"), ("4-picoline", "Cc1ccncc1"), ("2,6-lutidine", "Cc1cccc(C)n1"),
    ("2-aminopyridine", "Nc1ccccn1"), ("nicotinamide", "NC(=O)c1cccnc1"), ("nicotine", "CN1CCC[C@H]1c1cccnc1"),
    ("pyridine", "c1ccncc1"), ("pyrimidine", "c1cncnc1"), ("pyrazine", "c1cnccn1"), ("pyridazine", "c1ccnnc1"),
    ("quinoline", "c1ccc2ncccc2c1"), ("isoquinoline", "c1ccc2cnccc2c1"), ("quinoxaline", "c1ccc2nccnc2c1"),
    ("quinazoline", "c1ccc2ncncc2c1"), ("cinnoline", "c1ccc2nnccc2c1"), ("indole", "c1ccc2[nH]ccc2c1"), ("pyrrole", "c1cc[nH]c1"),
    ("furan", "c1ccoc1"), ("thiophene", "c1ccsc1"), ("benzofuran", "c1ccc2occc2c1"), ("benzothiophene", "c1ccc2sccc2c1"),
    ("benzimidazole", "c1ccc2[nH]cnc2c1"), ("benzoxazole", "c1ccc2ocnc2c1"), ("indazole", "c1ccc2[nH]ncc2c1"),
    ("carbazole", "c1ccc2c(c1)[nH]c1ccccc12"), ("dibenzofuran", "c1ccc2c(c1)oc1ccccc12"), ("coumarin", "O=c1ccc2ccccc2o1"),
    ("caffeine", "Cn1cnc2c1c(=O)n(C)c(=O)n2C"), ("purine", "c1ncc2[nH]cnc2n1"), ("adenine", "Nc1ncnc2[nH]cnc12"),
    ("naphthalene", "c1ccc2ccccc2c1"), ("1-methylnaphthalene", "Cc1cccc2ccccc12"), ("2-methylnaphthalene", "Cc1ccc2ccccc2c1"),
    ("1-naphthol", "Oc1cccc2ccccc12"), ("2-naphthol", "Oc1ccc2ccccc2c1"), ("biphenyl", "c1ccc(-c2ccccc2)cc1"),
    ("fluorene", "c1ccc2c(c1)Cc1ccccc12"), ("azulene", "c1ccc2cccc2cc1"), ("acenaphthylene", "C1=Cc2cccc3cccc1c23"),
    ("acenaphthene", "C1Cc2cccc3cccc1c23"), ("anthracene", "c1ccc2cc3ccccc3cc2c1"), ("phenanthrene", "c1ccc2c(c1)ccc1ccccc12"),
    ("indene", "C1=Cc2ccccc2C1"), ("tetralin", "c1ccc2c(c1)CCCC2"), ("chlorobenzene", "Clc1ccccc1"), ("fluorobenzene", "Fc1ccccc1"),
    ("1,2-dichlorobenzene", "Clc1ccccc1Cl"), ("4-fluorotoluene", "Cc1ccc(F)cc1"),
    ("benzene", "c1ccccc1"), ("ibuprofen", "CC(C)Cc1ccc(C(C)C(=O)O)cc1"), ("2-acetylpyridine", "CC(=O)c1ccccn1"),
    ("4-methylanisole", "COc1ccc(C)cc1"), ("phenetole", "CCOc1ccccc1"), ("benzamide", "NC(=O)c1ccccc1"),
    ("2-methylindole", "Cc1cc2ccccc2[nH]1"), ("3-methylindole (skatole)", "Cc1c[nH]c2ccccc12"), ("8-hydroxyquinoline", "Oc1cccc2cccnc12"),
    ("2,2'-bipyridine", "c1ccc(-c2ccccn2)nc1"), ("phenoxazine", "c1ccc2c(c1)Nc1ccccc1O2"), ("xanthene", "c1ccc2c(c1)Cc1ccccc1O2"),
    ("1,3,5-trifluorobenzene", "Fc1cc(F)cc(F)c1"), ("hexafluorobenzene", "Fc1c(F)c(F)c(F)c(F)c1F"), ("2-fluoropyridine", "Fc1ccccn1"),
    ("thioanisole", "CSc1ccccc1"), ("2-methylthiophene", "Cc1cccs1"), ("2-methylfuran", "Cc1ccco1"), ("furfural", "O=Cc1ccco1"),
    ("1-methylpyrrole", "Cn1cccc1"), ("imidazole", "c1c[nH]cn1"), ("1-methylimidazole", "Cn1ccnc1"), ("oxazole", "c1cocn1"),
    ("2,6-dimethylphenol", "Cc1cccc(C)c1O"), ("4-ethylphenol", "CCc1ccc(O)cc1"), ("4-methoxyphenol", "COc1ccc(O)cc1"),
    ("p-anisaldehyde", "COc1ccc(C=O)cc1"), ("4-methylbenzaldehyde", "Cc1ccc(C=O)cc1"), ("4-aminobenzoic acid", "Nc1ccc(C(=O)O)cc1"),
    ("phthalic anhydride", "O=C1OC(=O)c2ccccc21"), ("phthalimide", "O=C1NC(=O)c2ccccc21"), ("benzil", "O=C(C(=O)c1ccccc1)c1ccccc1"),
    ("trans-stilbene", "C(=C/c1ccccc1)\\c1ccccc1"), ("diphenylmethane", "c1ccc(Cc2ccccc2)cc1"), ("1-indanone", "O=C1CCc2ccccc21"),
]


def corpus_rows() -> dict[str, list[tuple[str, str, str]]]:
    """Canonical SMILES -> (id, layer, status) of every manifest row, any layer and status (a P3c row carries its parent's SMILES)."""
    out: dict[str, list[tuple[str, str, str]]] = {}
    with S.MANIFEST.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            c = canonical(r["smiles"])
            if c is not None:
                out.setdefault(c, []).append((r["id"], r["layer"], r["status"]))
    return out


def main() -> None:
    nets = P.product_networks()
    measurement = P.carried_models(P.NK.MEASUREMENT)
    release = P.carried_models(P.NK.RELEASE)
    print("product kind", nets.kind, "held_back", nets.held_back, file=sys.stderr)
    print("release", [p.name for p in release], file=sys.stderr)
    print("measurement", [p.name for p in measurement], file=sys.stderr)
    elements, sizes = P.training_set(release)
    print("release training elements", elements, "atoms", sizes, file=sys.stderr)
    rel = S.release_index(release)
    meas = S.load(measurement)
    n_rel = len(P.train_ids(release))
    print("release train ids", n_rel, file=sys.stderr)
    corpus = corpus_rows()
    fit = RT.estimate_or_other("c1ccccc1", threads=6, pyscf=P.WSL_PYSCF_VERSION)
    print("fit", {k: v for k, v in fit.items() if k not in ("basis_functions", "seconds", "within_half_hour")}, file=sys.stderr)
    print("runs", [r for r in RT.timed_runs(6) if r[3] == fit["pyscf"]], file=sys.stderr)
    rows = []
    for name, smi in CANDIDATES:
        c = canonical(smi)
        m = Chem.AddHs(Chem.MolFromSmiles(smi))
        els = sorted({a.GetSymbol().upper() for a in m.GetAtoms()})
        gates = []
        if sum(a.GetFormalCharge() for a in m.GetAtoms()) != 0:
            gates.append("charge")
        if any(a.GetNumRadicalElectrons() for a in m.GetAtoms()):
            gates.append("radical")
        if not any(a.GetIsAromatic() for a in m.GetAtoms()):
            gates.append("no aromatic ring")
        bad = sorted(set(els) - set(elements))
        if bad:
            gates.append("elements " + ",".join(bad))
        n = m.GetNumAtoms()
        est = RT.estimate_or_other(smi, threads=6, pyscf=P.WSL_PYSCF_VERSION)
        rows.append({
            "name": name, "smiles": c, "atoms": n, "inside_sizes": sizes[0] <= n <= sizes[1], "gates": gates,
            "nbf": est["basis_functions"], "seconds": est["seconds"], "half_hour": est["within_half_hour"],
            "corpus": corpus.get(c, []), "release": rel.trained.get(c, []), "release_cation": rel.cations.get(c, []),
            "meas_trained": meas.trained.get(c, []), "holdout": list(meas.holdout[c]) if c in meas.holdout else None,
            "meas_cation": meas.cations.get(c, []),
        })
    json.dump({"elements": elements, "sizes": sizes, "n_release_ids": n_rel, "fit": fit, "rows": rows}, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
