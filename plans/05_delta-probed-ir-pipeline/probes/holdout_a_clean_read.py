"""Hold-out (a) without its trained twins (TASKS 157, 30 Oct 2026): v1.3's measured error per family on the ten molecules of hold-out (a), on
the eight that the network never trained on under any id ('a8': without 2-naphthoic acid and benzonitrile, whose layer-B twins are in all
three seeds' training sets, `m08.seen.leaks`), and on hold-out (b); and the licence (decision 65: a family is licensed where the seed-mean
error is within 3 cm⁻¹ on both hold-outs) under (a) as stored and under the clean (a8). Read from `rungC_eval_saved.py` records that carry
the extra test set 'a8' (`--eval-ids-file a8=…`), one per seed, through module 05's own aggregation (`promotion_read.load_eval_arm`).

    python probes/holdout_a_clean_read.py <eval_seed0.json> <eval_seed1.json> <eval_seed2.json>      # markdown on stdout
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
from chain35_read import T1_FAMILY_LINE  # noqa: E402
from promotion_read import FAMILIES, load_eval_arm, reported  # noqa: E402

CLEAN = "a8"


def table(paths: list[Path]) -> list[dict]:
    """Per family: the seed-mean error on (a), (a8) and (b), and whether it is licensed with (a) as stored and with the clean (a8)."""
    arm = load_eval_arm(paths, holdouts=("a", CLEAN, "b"))
    rows = []
    for f in FAMILIES:
        a, a8, b = (reported(arm.mean(h, f), f) for h in ("a", CLEAN, "b"))
        rows.append({"family": f, "a": a, "a8": a8, "b": b, "licensed_stored": max(a, b) <= T1_FAMILY_LINE,
                     "licensed_clean": max(a8, b) <= T1_FAMILY_LINE})
    return rows


def markdown(rows: list[dict], paths: list[Path]) -> str:
    def yes(x: bool) -> str:
        return "yes" if x else "no"

    lines = ["# Hold-out (a) without its trained twins (TASKS 157)", "",
             f"Seed means over {len(paths)} seeds, cm⁻¹; licence line {T1_FAMILY_LINE} cm⁻¹ on both hold-outs (decision 65).", "",
             "| family | (a), 10 | (a8), 8 clean | (b) | licensed, (a) as stored | licensed, clean (a8) |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['family']} | {r['a']} | {r['a8']} | {r['b']} | {yes(r['licensed_stored'])} | {yes(r['licensed_clean'])} |" for r in rows]
    changed = [r["family"] for r in rows if r["licensed_stored"] != r["licensed_clean"]]
    lines += ["", f"Licence changed by the clean (a8): {', '.join(changed) if changed else 'none'}.", "",
              "Records: " + ", ".join(p.name for p in paths)]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("records", type=Path, nargs="+")
    paths = ap.parse_args(argv).records
    sys.stdout.write(markdown(table(paths), paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
