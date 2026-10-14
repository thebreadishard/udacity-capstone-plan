"""S2's training set (14 Oct 2026, TASKS 53; the user: 'Akkoord' to S2 on the server s1) — the molecules whose GVPT2 at G trains and reads a
per-mode anharmonic shift (route (b)) against family constants (route (c)). The rule is fixed here, before any molecule is chosen; the
registration is GoalGathering/notes/PreRegistration_2026-10-14_S2_Anharmonic_Shift.md.

Rule:
  1. Universe: corpus manifest rows with status done and n_atoms ≤ 20, neutral, elements C and N besides H (the large targets are C/H; the
     aza families of pool 3 are the next nearest), not in hold-out (b) (corpus/holdout_b_frozen_2026-10-08.txt).
  2. Every pure hydrocarbon of the universe is taken (the targets' own chemistry).
  3. The rest up to N_TOTAL = 20 are nitrogen-containing members, breadth first over Murcko scaffolds (decision 52): scaffolds in the order of
     the sha1 of their SMILES, one molecule per scaffold per round, within a scaffold in the order of the sha1 of the molecule id.
  4. Benzene's GVPT2 at G exists (S1, 13 Oct) and is reused, not recomputed.
Writes <out>/selection.json (the universe's size, the scaffold of every member, the order) and <out>/s2_ids.tsv (id, geometry path).

    python probes/s2_select.py [--out probes/results_m1/s2_training_set_2026-10-14]
"""
import argparse
import csv
import hashlib
import json
import os

from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus")
HOLDOUT_B = os.path.join(CORPUS, "holdout_b_frozen_2026-10-08.txt")
N_TOTAL = 20
MAX_ATOMS = 20
BENZENE = "A_8448043181"


def sha(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def universe(rows, holdout):
    out = []
    for r in rows:
        if r["status"] != "done" or not r["n_atoms"] or int(r["n_atoms"]) > MAX_ATOMS or r["id"] in holdout:
            continue
        m = Chem.MolFromSmiles(r["smiles"])
        if m is None or Chem.GetFormalCharge(m) != 0:
            continue
        el = {a.GetSymbol() for a in m.GetAtoms()}
        if not el <= {"C", "N"}:
            continue
        out.append({"id": r["id"], "smiles": r["smiles"], "n_atoms": int(r["n_atoms"]), "has_n": "N" in el,
                    "scaffold": Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))})
    return out


def select(U):
    chosen = [u for u in U if not u["has_n"]]
    by_scaffold = {}
    for u in U:
        if u["has_n"]:
            by_scaffold.setdefault(u["scaffold"], []).append(u)
    queues = [sorted(v, key=lambda u: sha(u["id"])) for _k, v in sorted(by_scaffold.items(), key=lambda kv: sha(kv[0]))]
    while len(chosen) < N_TOTAL and any(queues):
        for q in queues:
            if q and len(chosen) < N_TOTAL:
                chosen.append(q.pop(0))
    return chosen


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(HERE, "results_m1", "s2_training_set_2026-10-14"))
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(os.path.join(CORPUS, "manifest.csv"), encoding="utf-8")))
    holdout = {ln.split()[0] for ln in open(HOLDOUT_B, encoding="utf-8") if ln.strip() and not ln.startswith("#")}
    U = universe(rows, holdout)
    S = select(U)
    os.makedirs(a.out, exist_ok=True)
    json.dump({"rule": __doc__.split("Rule:")[1].split("Writes")[0].strip(), "universe": len(U),
               "universe_scaffolds": len({u["scaffold"] for u in U}), "selected": S},
              open(os.path.join(a.out, "selection.json"), "w", encoding="utf-8"), indent=1)
    with open(os.path.join(a.out, "s2_ids.tsv"), "w", encoding="utf-8", newline="\n") as fh:   # read by bash on the server: no CR
        for u in S:
            if u["id"] != BENZENE:
                fh.write(f"{u['id']}\tmodules/05_support_predictor/corpus/molecules/{u['id']}/geometry.json\n")
    for u in S:
        print(f"{u['id']}  {u['n_atoms']:2d}  {'N ' if u['has_n'] else 'CH'}  {u['smiles']:32s} {u['scaffold']}")
    print(f"universe {len(U)} molecules, {len({u['scaffold'] for u in U})} scaffolds; selected {len(S)} "
          f"({sum(not u['has_n'] for u in S)} hydrocarbons, {len({u['scaffold'] for u in S})} scaffolds)")


if __name__ == "__main__":
    main()
