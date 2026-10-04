"""Step (b) of the candidate generator's batch route: the gate and the niche test (TASKS row 22;
`GoalGathering/notes/PreRegistration_2026-10-04_Candidate_Generator_Batch_Route.md`).

Reads the proposals of `m06/propose.py`, de-duplicates them on canonical SMILES and passes each through the enumeration's own gate — parses; neutral and
closed shell; elements C H N O S F Cl; ≤ 30 heavy atoms; at least two fused aromatic rings; not already in the corpus manifest — and then the niche test:
the molecule's largest fused aromatic ring system (substituents and linkers removed) is neither a listed core of `corpus/build_manifest.py` nor the ring
system of any manifest row — a new ring skeleton, not a new substituent on a known one. (Dated amendment 4 Oct 11:3x, before the registered run: the
Murcko scaffold, which keeps linkers and side rings, let ≈ 90 % of a 250-sample smoke through; it stays a column.) Columns, not gates: membership of the
frozen PubChem set, ring class, heteroatom class, Murcko scaffold, occurrences and runs. The passing list is sorted deterministically and its SHA-256
recorded, so it can be frozen as a candidate list (step c).

    python m06/gate.py out/proposals_2026-10-04.csv out/proposals_2026-10-04
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
PLAN = MOD.parents[1]
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus"
MANIFEST = CORPUS / "manifest.csv"
PUBCHEM = MOD / "data" / "pubchem_aromatics_2026-09-24.csv"
sys.path.insert(0, str(HERE))
from data import hetero_class  # noqa: E402
from evaluate import ELEMENTS, canonical  # noqa: E402

STAGES = ["parses", "neutral_closed_shell", "elements", "heavy_le_30", "fused_aromatic_2plus", "not_in_manifest", "new_ring_system"]
MAX_HEAVY = 30


def cores_of_manifest_builder() -> dict:
    """The listed cores, read from the builder itself (no second copy of the list)."""
    spec = importlib.util.spec_from_file_location("build_manifest", CORPUS / "build_manifest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(mod.CORES)


def scaffold(smiles: str) -> str:
    from rdkit import Chem
    from rdkit.Chem.Scaffolds import MurckoScaffold
    m = Chem.MolFromSmiles(smiles)
    s = MurckoScaffold.GetScaffoldForMol(m)
    return Chem.MolToSmiles(s) if s is not None and s.GetNumAtoms() else ""


def ring_system(smiles: str) -> str:
    """The largest fused aromatic ring system of a molecule as a canonical SMILES fragment: aromatic rings joined by shared atoms, substituents and linkers
    removed. Naphthalene+COOH → naphthalene; phenanthrene → itself; biphenyl → benzene (the rings are not fused). The niche test's object."""
    from rdkit import Chem
    m = Chem.MolFromSmiles(smiles)
    rings = [set(m.GetBondWithIdx(b).GetBeginAtomIdx() for b in r) | set(m.GetBondWithIdx(b).GetEndAtomIdx() for b in r)
             for r in m.GetRingInfo().BondRings() if all(m.GetBondWithIdx(b).GetIsAromatic() for b in r)]
    systems: list[set] = []
    for r in rings:
        joined = [s for s in systems if s & r]
        for s in joined:
            systems.remove(s)
            r = r | s
        systems.append(r)
    if not systems:
        return ""
    atoms = sorted(max(systems, key=len))
    frag = Chem.MolFragmentToSmiles(m, atomsToUse=atoms, canonical=True)
    fm = Chem.MolFromSmiles(frag)
    if fm is None:                                   # a cut aromatic system can lose a hydrogen count RDKit needs; keep an unsanitised canonical key
        fm = Chem.MolFromSmiles(frag, sanitize=False)
    return Chem.MolToSmiles(fm) if fm is not None else frag


def ring_class(smiles: str) -> str:
    from rdkit import Chem
    m = Chem.MolFromSmiles(smiles)
    if m is None:                                    # an unsanitised ring-system key: count its rings without aromaticity perception
        m = Chem.MolFromSmiles(smiles, sanitize=False)
        if m is None:
            return "r?"
        m.UpdatePropertyCache(strict=False)
        Chem.FastFindRings(m)
        n = len(m.GetRingInfo().BondRings())
        return "r2" if n <= 2 else "r3" if n == 3 else "r4+"
    n = sum(1 for r in m.GetRingInfo().BondRings() if all(m.GetBondWithIdx(b).GetIsAromatic() for b in r))
    return "r2" if n <= 2 else "r3" if n == 3 else "r4+"


def stage_of(smiles: str, manifest_smiles: set, known_systems: set) -> tuple[str, dict]:
    """The first gate a canonical SMILES fails, or 'pass'; with the descriptors used along the way."""
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    m = Chem.MolFromSmiles(smiles) if smiles else None
    if m is None:
        return "parses", {}
    if any(a.GetFormalCharge() for a in m.GetAtoms()) or Descriptors.NumRadicalElectrons(m) > 0:
        return "neutral_closed_shell", {}
    if not {a.GetSymbol() for a in m.GetAtoms()} <= ELEMENTS:
        return "elements", {}
    nh = m.GetNumHeavyAtoms()
    if nh > MAX_HEAVY:
        return "heavy_le_30", {"n_heavy": nh}
    ri = m.GetRingInfo()
    arom = [set(r) for r in ri.BondRings() if all(m.GetBondWithIdx(b).GetIsAromatic() for b in r)]
    if not (len(arom) >= 2 and any(a & b for i, a in enumerate(arom) for b in arom[i + 1:])):
        return "fused_aromatic_2plus", {"n_heavy": nh, "n_arom_rings": len(arom)}
    d = {"n_heavy": nh, "n_arom_rings": len(arom), "ring_class": ring_class(smiles), "hetero_class": hetero_class(smiles), "scaffold": scaffold(smiles),
         "ring_system": ring_system(smiles)}
    if smiles in manifest_smiles:
        return "not_in_manifest", d
    if d["ring_system"] in known_systems:
        return "new_ring_system", d
    return "pass", d


def manifest_sets(manifest: Path, cores: dict) -> tuple[set, set]:
    """The manifest's canonical SMILES and the known ring systems: those of every manifest row with a SMILES plus the listed cores themselves."""
    smiles, systems = set(), set()
    for c in cores.values():
        systems.add(ring_system(c) or canonical(c))
    with open(manifest, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("smiles"):
                c = canonical(r["smiles"])
                if c:
                    smiles.add(c)
                    systems.add(ring_system(c))
    systems.discard("")
    return smiles, systems


def pubchem_set(path: Path) -> set:
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        return {canonical(r["smiles"]) for r in csv.DictReader(f) if r.get("smiles")} - {None}


def gate(rows: list[dict], manifest_smiles: set, known_systems: set, known_molecules: set) -> tuple[list[dict], dict]:
    """rows: the proposals (run, request, smiles). Returns the de-duplicated table with a stage per canonical SMILES and the summary."""
    occ, runs, first = Counter(), defaultdict(set), {}
    for r in rows:
        key = r["smiles"] or f"__unparsed__{r['run']}:{r['request']}:{r['index']}"
        occ[key] += 1
        runs[key].add(f"{r['run']}{(' ' + r['request']) if r['request'] else ''}")
        first.setdefault(key, r)
    table = []
    for key, n in occ.items():
        smi = "" if key.startswith("__unparsed__") else key
        stage, d = stage_of(smi, manifest_smiles, known_systems)
        table.append(dict(smiles=smi, stage=stage, occurrences=n, runs="; ".join(sorted(runs[key])), in_pubchem_set=bool(smi) and smi in known_molecules, **d))
    by_stage = Counter(t["stage"] for t in table)
    passing = [t for t in table if t["stage"] == "pass"]
    systems = defaultdict(list)
    for t in passing:
        systems[t["ring_system"]].append(t)
    per_class = Counter((t["ring_class"], t["hetero_class"]) for t in passing)
    per_class_systems = Counter((ring_class(s), hetero_class(s)) for s in systems)     # the system's own class, not its first molecule's
    summary = dict(n_samples=len(rows), n_distinct=len(table), by_stage={s: by_stage.get(s, 0) for s in STAGES}, n_pass=len(passing),
                   n_new_ring_systems=len(systems), n_new_ring_systems_in_pubchem_set=sum(1 for s in systems if s in known_molecules),
                   n_pass_in_pubchem_set=sum(1 for t in passing if t["in_pubchem_set"]),
                   per_class={f"{r} {h}": dict(molecules=n, ring_systems=per_class_systems[(r, h)]) for (r, h), n in sorted(per_class.items())},
                   per_run={run: dict(samples=sum(1 for r in rows if f"{r['run']}{(' ' + r['request']) if r['request'] else ''}" == run))
                            for run in sorted({f"{r['run']}{(' ' + r['request']) if r['request'] else ''}" for r in rows})})
    return table, summary


def frozen_list(table: list[dict]) -> list[dict]:
    """The passing rows in a deterministic order: PubChem-known first, then by occurrences, then by SMILES."""
    return sorted((t for t in table if t["stage"] == "pass"), key=lambda t: (not t["in_pubchem_set"], -t["occurrences"], t["smiles"]))


def write_outputs(out_prefix: str, table: list[dict], summary: dict, meta: dict) -> dict:
    cols = ["smiles", "stage", "occurrences", "runs", "in_pubchem_set", "n_heavy", "n_arom_rings", "ring_class", "hetero_class", "ring_system", "scaffold"]
    staged = Path(out_prefix + "_staged.csv")
    with open(staged, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(table, key=lambda t: (STAGES.index(t["stage"]) if t["stage"] in STAGES else len(STAGES), t["smiles"])))
    gated = Path(out_prefix + "_gated.csv")
    with open(gated, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(frozen_list(table))
    summary = dict(summary, gated_csv=gated.name, gated_sha256=hashlib.sha256(gated.read_bytes()).hexdigest(), **meta)
    Path(out_prefix + "_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    md = [f"# Gate and niche test on `{meta['proposals']}` — {meta['date']}", "",
          f"{summary['n_samples']} samples, {summary['n_distinct']} distinct canonical SMILES. Manifest: {meta['n_manifest_smiles']} molecules, "
          f"{meta['n_known_systems']} known fused aromatic ring systems (incl. the listed cores); PubChem set: {meta['n_pubchem']} molecules.", "",
          "| stage (first failed) | distinct SMILES |", "|---|---|"]
    md += [f"| {s} | {summary['by_stage'][s]} |" for s in STAGES] + [f"| **pass** | **{summary['n_pass']}** |", "",
           f"**New ring systems:** {summary['n_new_ring_systems']} distinct, of which {summary['n_new_ring_systems_in_pubchem_set']} are themselves molecules "
           f"of the PubChem set; {summary['n_pass_in_pubchem_set']} of the {summary['n_pass']} passing molecules are in the PubChem set.", "",
           "| class | passing molecules | new ring systems |", "|---|---|---|"]
    md += [f"| {k} | {v['molecules']} | {v['ring_systems']} |" for k, v in summary["per_class"].items()]
    md += ["", f"Frozen list `{gated.name}`, SHA-256 `{summary['gated_sha256']}`."]
    Path(out_prefix + ".md").write_text("\n".join(md), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("proposals", help="the csv of m06/propose.py")
    ap.add_argument("out_prefix")
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--pubchem", default=str(PUBCHEM), help="the frozen PubChem set (a column, not a gate); '' to skip")
    a = ap.parse_args(argv)
    t0 = time.time()
    with open(a.proposals, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cores = cores_of_manifest_builder()
    manifest_smiles, known_systems = manifest_sets(Path(a.manifest), cores)
    known = pubchem_set(Path(a.pubchem)) if a.pubchem else set()
    table, summary = gate(rows, manifest_smiles, known_systems, known)
    meta = dict(date=time.strftime("%Y-%m-%d %H:%M"), proposals=Path(a.proposals).name, n_manifest_smiles=len(manifest_smiles), n_known_systems=len(known_systems),
                n_cores=len(cores), n_pubchem=len(known), seconds=round(time.time() - t0))
    summary = write_outputs(a.out_prefix, table, summary, meta)
    print(Path(a.out_prefix + ".md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
