"""Hold-out (a) without its trained twins (TASKS 157, 30 Oct 2026): v1.3's first-order diagonal error per family (each seed's, averaged
over the seeds: the evaluation records' diag_rms) on the ten molecules of hold-out (a), on the eight that the network never trained on
under any id ('a8': without 2-naphthoic acid and benzonitrile, whose layer-B twins are in all three seeds' training sets,
`m08.seen.leaks`), and on hold-out (b); and whether that first-order quantity is within the licence line of 3 cm⁻¹ on both hold-outs,
under (a) as stored and under the clean (a8) — the quantity decision 65 read until its amendment of 16 Nov 2026. The licence itself is
read on the error of the corrected band positions of the seed-mean correction since then (`m08/licence.py`), which this read does not
print. Read from `rungC_eval_saved.py` records that carry
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
    """Per family: the seeds' mean first-order diagonal error on (a), (a8) and (b), and whether it is within the line on both hold-outs
    with (a) as stored and with the clean (a8) — decision 65's reading until 16 Nov 2026."""
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
             f"First-order diagonal error of each seed's correction, averaged over {len(paths)} seeds, cm⁻¹ (the evaluation records' "
             f"diag_rms); line {T1_FAMILY_LINE} cm⁻¹ on both hold-outs. Decision 65 read the licence on this quantity until its amendment of "
             "16 Nov 2026; since then the licence is read on the error of the corrected band positions of the seed-mean correction "
             "(m08/licence.py), which is not in this table.", "",
             "| family | (a), 10 | (a8), 8 clean | (b) | first order within the line, (a) as stored | first order within the line, clean (a8) |",
             "|---|---|---|---|---|---|"]
    lines += [f"| {r['family']} | {r['a']} | {r['a8']} | {r['b']} | {yes(r['licensed_stored'])} | {yes(r['licensed_clean'])} |" for r in rows]
    changed = [r["family"] for r in rows if r["licensed_stored"] != r["licensed_clean"]]
    lines += ["", f"Changed by the clean (a8): {', '.join(changed) if changed else 'none'}.", "",
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
