"""Chain 41's half-control arms (14 Oct 2026, the learning-curve amendment in the rung C pre-registration): per fold, two training molecules
per trained scaffold instead of all (fold 1: 15 → 6, fold 2: 12 → 6), so that r_K is read at 0 (the size arm), ≈ 6 and 12–15 five-ring
training molecules. Kept: per scaffold (the candidate list's parent), the first two of the fold's training molecules in the order of the sha1
of their id. Writes out/chain41_fold{1,2}_half_exclude.txt under module 05 = the fold's own exclude list plus the dropped training molecules.

    python probes/chain41_half_folds.py
"""
import csv
import hashlib
import json
from pathlib import Path

M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor"
FOLDS = M05 / "out" / "chain41_size5_folds_2026-10-11.json"
CANDIDATES = M05 / "out" / "pool3_candidates_2026-10-03.csv"
KEEP = 2


def scaffold_name(rows: dict, i: str) -> str:
    """The scaffold of a candidate: its parent's name, or for the five-ring neutrals (no parent_id) the name before '+'."""
    r = rows[i]
    return rows[r["parent_id"]]["name"] if r["parent_id"] in rows else r["name"].split("+")[0]   # cations' parents are corpus ids


def half(fold: dict, parent_of: dict) -> tuple[list, list]:
    """(kept, dropped) training molecules of a fold."""
    by_scaffold = {}
    for i in fold["train_extra"]:
        by_scaffold.setdefault(parent_of[i], []).append(i)
    kept, dropped = [], []
    for ids in by_scaffold.values():
        ids = sorted(ids, key=lambda i: hashlib.sha1(i.encode()).hexdigest())
        kept += ids[:KEEP]
        dropped += ids[KEEP:]
    return sorted(kept), sorted(dropped)


def main() -> None:
    d = json.loads(FOLDS.read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in csv.DictReader(open(CANDIDATES, encoding="utf-8"))}
    parent_of = {i: scaffold_name(rows, i) for n in (1, 2) for i in d[f"control_fold{n}"]["train_extra"]}
    for n in (1, 2):
        fold = d[f"control_fold{n}"]
        kept, dropped = half(fold, parent_of)
        out = M05 / "out" / f"chain41_fold{n}_half_exclude.txt"
        lines = [f"# chain 41 (fold{n} half-control, 14 Oct 2026): the fold's exclude list plus {len(dropped)} dropped training molecules; "
                 f"kept {len(kept)}: {' '.join(kept)}"] + sorted(set(fold["exclude"]) | set(dropped))
        out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"fold {n}: {len(fold['train_extra'])} training five-ring molecules → {len(kept)} kept; {out.name} has {len(lines) - 1} ids")


if __name__ == "__main__":
    main()
