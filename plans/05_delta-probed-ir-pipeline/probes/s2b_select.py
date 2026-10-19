"""S2b's training set (registration GoalGathering/notes/PreRegistration_2026-10-19_S2b_Learning_Curve.md, 'Training set'): one rigid molecule
for every Murcko scaffold that S2 did not cover. The rule is the registration's, fixed before this script chose anything; it reads sizes,
elements and SMILES from the corpus manifest, never a label.

Rule:
  1. Universe: corpus manifest rows with status done and n_atoms ≤ 28, neutral, elements C, N and O besides H, not in hold-out (b)
     (corpus/holdout_b_frozen_2026-10-08.txt), not already in S2 (probes/results_m1/s2_training_set_2026-10-14/selection.json).
     Neutral is the deck in the molecule's job.json: charge 0 and multiplicity 1 (a pool 3 cation's manifest SMILES is its neutral parent's, and S2's
     runner has no charge input).
  2. Rigid only: no rotatable bond (RDKit), no acyclic linker between ring systems, no CH₃, no H on N or O (all five of S2's NOISY
     molecules carried one of these). The linker clause catches what RDKit's count misses next to a triple bond: diphenylacetylene's
     rings turn almost freely about the C≡C axis.
  3. One molecule per Murcko scaffold that none of S2's selected molecules has: the smallest rigid member, ties by the sha1 of the id.
Writes <out>/selection.json (the rule, the universe's size, every member with its scaffold) and <out>/s2b_ids.tsv (id, geometry path).

    python probes/s2b_select.py --out probes/results_m1/s2b_training_set_<date>
"""
import argparse
import csv
import json
import os
from collections.abc import Callable, Iterable
from typing import Any

from corpus_state import NEUTRAL_SINGLET, recorded_state
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
from s2_select import CORPUS, HERE, HOLDOUT_B, sha

S2_SELECTION = os.path.join(HERE, "results_m1", "s2_training_set_2026-10-14", "selection.json")
MAX_ATOMS = 28
ELEMENTS = frozenset({"C", "N", "O"})
LABILE = ("N", "O")          # an H on these wags and inverts with large amplitude (S2 amendment 3)
METHYL_H = 3


def geometry_path(mol_id: str) -> str:
    """The geometry's path relative to the plan, as the server-side runner reads it."""
    return f"modules/05_support_predictor/corpus/molecules/{mol_id}/geometry.json"


def has_linker(mol: Chem.Mol) -> bool:
    """An acyclic bond between two non-terminal atoms of the Murcko scaffold joins two ring systems (an exocyclic C=O is terminal)."""
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    return any(not b.IsInRing() and b.GetBeginAtom().GetDegree() > 1 and b.GetEndAtom().GetDegree() > 1 for b in scaffold.GetBonds())


def is_rigid(mol: Chem.Mol) -> bool:
    """No rotatable bond, no linker between ring systems, no CH₃, no H on N or O."""
    if rdMolDescriptors.CalcNumRotatableBonds(mol) > 0 or has_linker(mol):
        return False
    for atom in mol.GetAtoms():
        n_h = atom.GetTotalNumHs()
        if (atom.GetSymbol() == "C" and n_h >= METHYL_H) or (atom.GetSymbol() in LABILE and n_h >= 1):
            return False
    return True


def candidate(row: dict[str, str], excluded: set[str], state: Callable[[str], tuple[int, int]] = recorded_state) -> dict[str, Any] | None:
    """The universe's member for one manifest row (rule 1), or None when the row is outside it."""
    if row["status"] != "done" or not row["n_atoms"] or int(row["n_atoms"]) > MAX_ATOMS or row["id"] in excluded:
        return None
    mol = Chem.MolFromSmiles(row["smiles"])
    if mol is None or not {a.GetSymbol() for a in mol.GetAtoms()} <= ELEMENTS or state(row["id"]) != NEUTRAL_SINGLET:
        return None
    return {"id": row["id"], "smiles": row["smiles"], "n_atoms": int(row["n_atoms"]), "rigid": is_rigid(mol),
            "scaffold": Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(mol))}


def universe(rows: Iterable[dict[str, str]], excluded: set[str],
             state: Callable[[str], tuple[int, int]] = recorded_state) -> list[dict[str, Any]]:
    return [c for c in (candidate(r, excluded, state) for r in rows) if c is not None]


def select(members: list[dict[str, Any]], s2_scaffolds: set[str]) -> list[dict[str, Any]]:
    """Rules 2–3: per new scaffold its smallest rigid member (ties by the sha1 of the id); the list smallest first."""
    best: dict[str, dict[str, Any]] = {}
    for m in members:
        if not m["rigid"] or m["scaffold"] in s2_scaffolds:
            continue
        held = best.get(m["scaffold"])
        if held is None or (m["n_atoms"], sha(m["id"])) < (held["n_atoms"], sha(held["id"])):
            best[m["scaffold"]] = m
    return sorted(best.values(), key=lambda m: (m["n_atoms"], sha(m["id"])))


def read_holdout(path: str) -> set[str]:
    with open(path, encoding="utf-8") as fh:
        return {ln.split()[0] for ln in fh if ln.strip() and not ln.startswith("#")}


def read_s2(path: str) -> tuple[set[str], set[str]]:
    """S2's selected ids and their scaffolds."""
    with open(path, encoding="utf-8") as fh:
        selected = json.load(fh)["selected"]
    return {m["id"] for m in selected}, {m["scaffold"] for m in selected}


def write_outputs(out: str, members: list[dict[str, Any]], chosen: list[dict[str, Any]]) -> None:
    """selection.json and s2b_ids.tsv, each through a temp file moved over the target."""
    missing = [m["id"] for m in chosen if not os.path.isfile(os.path.join(HERE, "..", geometry_path(m["id"])))]
    if missing:
        raise SystemExit(f"no geometry.json for {missing}: the runner could not start them")
    os.makedirs(out, exist_ok=True)
    record = {"rule": __doc__.split("Rule:")[1].split("Writes")[0].strip(), "universe": len(members),
              "universe_rigid": sum(m["rigid"] for m in members), "universe_scaffolds": len({m["scaffold"] for m in members}),
              "selected": chosen}
    for name, text in (("selection.json", json.dumps(record, indent=1, ensure_ascii=False) + "\n"),
                       ("s2b_ids.tsv", "".join(f"{m['id']}\t{geometry_path(m['id'])}\n" for m in chosen))):
        target = os.path.join(out, name)
        with open(target + ".tmp", "w", encoding="utf-8", newline="\n") as fh:   # read by bash on the server: no CR
            fh.write(text)
        os.replace(target + ".tmp", target)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    s2_ids, s2_scaffolds = read_s2(S2_SELECTION)
    with open(os.path.join(CORPUS, "manifest.csv"), encoding="utf-8") as fh:
        members = universe(csv.DictReader(fh), read_holdout(HOLDOUT_B) | s2_ids)
    chosen = select(members, s2_scaffolds)
    write_outputs(a.out, members, chosen)
    for m in chosen:
        print(f"{m['id']}  {m['n_atoms']:2d}  {m['smiles']:36s} {m['scaffold']}")
    print(f"universe {len(members)} molecules ({sum(m['rigid'] for m in members)} rigid), "
          f"{len({m['scaffold'] for m in members})} scaffolds; selected {len(chosen)} new scaffolds")


if __name__ == "__main__":
    main()
