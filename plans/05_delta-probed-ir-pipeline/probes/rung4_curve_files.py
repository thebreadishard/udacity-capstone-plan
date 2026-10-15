"""The id files of rung 4's learning curve (TASKS 61; GoalGathering/notes/PreRegistration_2026-10-14_Rung4_Broad_Set.md), written from the
frozen list (its sha256 is checked first):

  out/rung4_k{0,10,20}_exclude.txt   the training families' rows with curve_rank > k, dropped from the training pool (`--exclude-ids-file`)
  out/rung4_tetracene.txt            the test family's 30 ids, read with `--eval-ids-file tetracene=…`

k = 30 trains on every rung-4 training row and gets no exclude file: rungC_train refuses an exclude file none of whose ids is in the pool.
The test family is not in the exclude files either: since 15 Oct 2026 `E6.splits` holds it out of every pool (corpus/holdout_rung4_test.txt);
this script refuses to write when that file and the frozen list disagree.

    python probes/rung4_curve_files.py [--out-dir modules/05_support_predictor/out]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
FROZEN = M05 / "out" / "rung4_candidates_2026-10-14.csv"
HELD_OUT = M05 / "corpus" / "holdout_rung4_test.txt"
CURVE = (0, 10, 20)                        # k = 30 is the full set: no exclude file
PER_FAMILY = 30


def frozen_rows(path: Path = FROZEN) -> list[dict]:
    want = path.with_suffix(path.suffix + ".sha256").read_text(encoding="utf-8").split()[0]
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != want:
        raise SystemExit(f"{path.name}: sha256 {got[:12]} is not the frozen {want[:12]}")
    return list(csv.DictReader(open(path, encoding="utf-8", newline="")))


def bare_ids(path: Path) -> list[str]:
    return [line.split()[0] for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]


def curve_files(rows: list[dict], held_out: list[str]) -> dict[str, list[str]]:
    """{file name: ids}. Each training family contributes its ranks 1..k to the pool at k, so the curve's subsets are nested."""
    test = [r["id"] for r in rows if r["test_family"] == "1"]
    if sorted(test) != sorted(held_out):
        raise SystemExit("the frozen list's test family and corpus/holdout_rung4_test.txt disagree — not written")
    train = [r for r in rows if r["test_family"] == "0"]
    for fam in {r["family"] for r in train}:
        ranks = sorted(int(r["curve_rank"]) for r in train if r["family"] == fam)
        if ranks != list(range(1, PER_FAMILY + 1)):
            raise SystemExit(f"family {fam}: curve ranks are not 1..{PER_FAMILY}")
    out = {f"rung4_k{k}_exclude.txt": [r["id"] for r in train if int(r["curve_rank"]) > k] for k in CURVE}
    out["rung4_tetracene.txt"] = test
    return out


def write(files: dict[str, list[str]], out_dir: Path) -> None:
    head = "# written by probes/rung4_curve_files.py from out/rung4_candidates_2026-10-14.csv (TASKS 61)\n"
    for name, ids in files.items():
        (out_dir / name).write_text(head + "".join(i + "\n" for i in ids), encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", type=Path, default=M05 / "out")
    a = ap.parse_args()
    files = curve_files(frozen_rows(), bare_ids(HELD_OUT))
    write(files, a.out_dir)
    for name, ids in files.items():
        print(f"{name}: {len(ids)} ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
