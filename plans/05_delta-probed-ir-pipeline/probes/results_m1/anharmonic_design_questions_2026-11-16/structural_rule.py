"""What a label-free structural mark would cost, read from marks.json's rows (window modes in the reads' main scope).

    python structural_rule.py

Every G-marked mode in hand is in family 'other' with an out-of-plane share o of 0.83 or more. For each line on o, the rule
"family 'other' and o at or above the line gets no step" is counted: the G-marked modes it catches, the sound modes it refuses, and
what refusing those costs - their harmonic rms against the step's rms on the same modes. Also sums the bytes of the force-field
files the refit needs and git does not hold. Writes structural_rule.json beside itself.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
from s2_read import rms, write_atomic  # noqa: E402

O_LINES = (0.5, 0.8, 0.95, 0.99)
FAMILY = "other"


def rule_rows(rows: list[dict]) -> list[dict]:
    """Per line on o: caught G marks, refused sound modes, and the cost of refusing them."""
    usable = [r for r in rows if r["family"] == FAMILY and np.isfinite(r["pred"])]
    out = []
    for line in O_LINES:
        hit = [r for r in usable if r["o"] >= line]
        sound = [r for r in hit if not r["g_mark"]]
        d, p = np.array([r["delta"] for r in sound]), np.array([r["pred"] for r in sound])
        out.append({"o_line": line, "family_modes": len(usable), "g_marked": sum(r["g_mark"] for r in usable),
                    "caught": sum(r["g_mark"] for r in hit), "sound_refused": len(sound),
                    "molecules_touched": len({r["id"] for r in sound}),
                    "harmonic_rms_of_refused": rms(d) if len(d) else None, "step_rms_of_refused": rms(p - d) if len(d) else None})
    return out


def untracked_bytes() -> dict[str, int]:
    """The bytes of ref.json and qff_report.npz the refit reads and git does not track, from inventory.json."""
    with open(os.path.join(HERE, "inventory.json"), encoding="utf-8") as fh:
        inv = json.load(fh)["molecules"]
    total = {"ref.json": 0, "qff_report.npz": 0}
    for row in inv.values():
        for side in ("G", "X"):
            for name in total:
                if row[f"{side}/{name}"] == "disk":
                    total[name] += os.path.getsize(os.path.join(PLAN, row[side], name))
    return total


def main() -> int:
    """Read marks.json and print the rule's table."""
    with open(os.path.join(HERE, "marks.json"), encoding="utf-8") as fh:
        rows = json.load(fh)["rows"]
    res = {"rule": rule_rows(rows), "untracked_bytes": untracked_bytes(),
           "g_marked_window_rows": [{k: r[k] for k in ("id", "mode", "omega", "o", "delta", "pred", "xtb", "x_strain", "x_share")}
                                    for r in rows if r["g_mark"]]}
    write_atomic(os.path.join(HERE, "structural_rule.json"), json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
