"""The pipeline show's batch (TASKS 146): about 30 molecules the carried network never trained on, spread over the carbon counts, each one
a corpus folder the pipeline reuses (steps 2–3 from the corpus, so a run takes seconds). Read from the reuse survey
(`probes/pipeline_reuse_survey.py`) and the network's own record of what it saw (`m08.seen`): every clean hold-out (a) molecule first,
then hold-out (b) and catalogue molecules round-robin over the scaffold cores (the name before the first '+'), one isomer per name,
hold-out (b) and the lowest id first within a core. Cation rows stay out: the survey gives them their neutral parent's SMILES, and the
pipeline refuses a charge.

    python probes/show_batch_select.py --survey <pipeline_reuse_survey.json> --out <folder> [--n 30]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P  # noqa: E402
from m08 import seen as S  # noqa: E402
from m08.show import carbon_count  # noqa: E402

KEEP = ("a", "b", "catalogue")          # never trained on; 'trained' and 'trained_and_held_out' stay out
FILL_ORDER = ("b", "catalogue")


def formula(smiles: str) -> str:
    from rdkit import Chem
    from rdkit.Chem.rdMolDescriptors import CalcMolFormula

    return CalcMolFormula(Chem.AddHs(Chem.MolFromSmiles(smiles)))


def candidates(survey: dict, seen: S.Seen, names: dict[str, str]) -> list[dict]:
    """Every reused survey row within the start limit whose molecule the network never trained on, with its role and carbon count."""
    limit = survey["summary"]["limit_angstrom"]
    out = []
    for row in survey["molecules"]:
        if not row["reused"] or row.get("start_rmsd_angstrom", 0.0) > limit or row["layer"] == S.CATION_LAYER:
            continue
        role = S.status(row["smiles"], seen, row["id"])["role"]
        if role in KEEP:
            f = formula(row["smiles"])
            out.append({"id": row["id"], "name": names.get(row["id"], row["id"]), "smiles": row["smiles"], "formula": f,
                        "n_c": carbon_count(f), "role": role})
    return out


def core(name: str) -> str:
    return name.split("+")[0]


def select(pool: list[dict], n: int) -> list[dict]:
    """The clean hold-out (a) molecules, then (b) and catalogue ones round-robin over the scaffold cores, one isomer per name."""
    chosen = sorted((m for m in pool if m["role"] == "a"), key=lambda m: (m["n_c"], m["id"]))[:n]
    names = {m["name"] for m in chosen}
    by_core: dict[str, list[dict]] = defaultdict(list)
    for m in sorted((m for m in pool if m["role"] in FILL_ORDER), key=lambda m: (FILL_ORDER.index(m["role"]), m["id"])):
        by_core[core(m["name"])].append(m)
    while len(chosen) < n and any(by_core.values()):
        for c in sorted(by_core, key=lambda k: (-len(by_core[k]), k)):
            while by_core[c] and by_core[c][0]["name"] in names:
                by_core[c].pop(0)
            if by_core[c] and len(chosen) < n:
                m = by_core[c].pop(0)
                chosen.append(m)
                names.add(m["name"])
    return sorted(chosen, key=lambda m: (m["n_c"], m["role"], m["id"]))


def slug(name: str, mol_id: str) -> str:
    """A result folder's name: the molecule's name in safe characters, with its id so two writings never collide."""
    safe = "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")[:40]
    return f"{safe}_{mol_id}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--survey", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n", type=int, default=30)
    a = ap.parse_args()
    if a.out.exists():
        raise SystemExit(f"{a.out} exists: a selection is never overwritten")
    survey = json.loads(a.survey.read_text(encoding="utf-8"))
    with S.MANIFEST.open(newline="", encoding="utf-8") as f:
        names = {r["id"]: r["name"] for r in csv.DictReader(f)}
    pool = candidates(survey, S.load(P.carried_models()), names)
    chosen = select(pool, a.n)
    a.out.mkdir(parents=True)
    with open(a.out / "batch.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        for m in chosen:
            w.writerow([slug(m["name"], m["id"]), m["smiles"], m["id"], m["role"], m["n_c"]])
    counts = {r: sum(m["role"] == r for m in pool) for r in KEEP}
    lines = [f"# The pipeline show's batch ({len(chosen)} molecules)", "",
             f"From {a.survey.name}: {len(pool)} reused molecules the network never trained on ({counts}).", "",
             "| C | id | name | formula | role |", "|---|---|---|---|---|"]
    lines += [f"| {m['n_c']} | {m['id']} | {m['name']} | {m['formula']} | {m['role']} |" for m in chosen]
    (a.out / "selection.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (a.out / "selection.json").write_text(json.dumps({"survey": str(a.survey), "pool": counts, "chosen": chosen}, indent=1), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
