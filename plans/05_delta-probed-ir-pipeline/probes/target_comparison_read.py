"""The registered read of the target comparison (TASKS 66; GoalGathering/notes/PreRegistration_2026-10-15_Target_Comparison.md), written and
tested on synthetic records before the registration was committed.

Arms P (projected target, the carried recipe) and R (ridge target); records are rungC_train JSONs (`curve → <size> → per_seed → <hold-out>`).
Arms are compared paired by seed, d = P − R (positive: R better).

    python probes/target_comparison_read.py --c-full P.json R.json --c-half P.json R.json --f P.json R.json [--out <prefix>]

Each pair is (P record, R record); --c-* are setting C (hold-out s), --f is setting F (hold-outs a and b).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import floor_lines as FL  # noqa: E402  (the band families)

SEEDS = (0, 1, 2)
RING = "ring-ip"
LINE_1 = {"ring-ip": 0.5, "coupling_ratio": 0.05}       # mean d (cm⁻¹; ratio), and mean d > 2 SE
LINE_2_FAMILY_FACTOR, LINE_2_COUPLING_MARGIN = 1.10, 0.03
READOUTS = tuple(LINE_1)


def per_seed(record: dict, hold: str, readout: str) -> dict[int, float]:
    """{seed: value} of one read-out on one hold-out, from the record's single pool size; refuses a record of several sizes."""
    if len(record["curve"]) != 1:
        raise SystemExit(f"a record of {len(record['curve'])} pool sizes; give one record per size")
    seeds = next(iter(record["curve"].values()))["per_seed"]
    get = (lambda s: s[hold]["coupling_ratio"]) if readout == "coupling_ratio" else (lambda s: s[hold]["diag_rms"][readout])
    return {int(s["seed"]): float(get(s)) for s in seeds}


def paired(p: dict, r: dict, hold: str, readout: str) -> tuple[float, float]:
    """(mean, SE) of d = P − R over the registered seeds; both records must hold every seed (a missing seed stops the read)."""
    a, b = per_seed(p, hold, readout), per_seed(r, hold, readout)
    missing = [s for s in SEEDS if s not in a or s not in b]
    if missing:
        raise SystemExit(f"seed(s) {missing} missing on hold-out ({hold}) — the comparison is read on every registered seed or not at all")
    d = np.array([a[s] - b[s] for s in SEEDS])
    return float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d)))


def line_1(c_full: tuple[dict, dict]) -> dict:
    out = {}
    for ro in READOUTS:
        mean, se = paired(*c_full, "s", ro)
        out[ro] = {"d": mean, "se": se, "met": bool(mean >= LINE_1[ro] and mean > 2 * se)}
    return out


def still_growing(c_full: tuple[dict, dict], c_half: tuple[dict, dict], readout: str) -> bool:
    (df, sef), (dh, seh) = paired(*c_full, "s", readout), paired(*c_half, "s", readout)
    return bool(df > dh + 2 * np.hypot(sef, seh))


def seed_mean(record: dict, hold: str, readout: str) -> float:
    return float(np.mean(list(per_seed(record, hold, readout).values())))


def line_2(f: tuple[dict, dict]) -> dict:
    p, r = f
    out = {}
    for hold in ("a", "b"):
        for fam in FL.FAMILIES:
            mp, mr = seed_mean(p, hold, fam), seed_mean(r, hold, fam)
            out[f"{hold}:{fam}"] = {"P": mp, "R": mr, "met": bool(mr <= LINE_2_FAMILY_FACTOR * mp)}
        cp, cr = seed_mean(p, hold, "coupling_ratio"), seed_mean(r, hold, "coupling_ratio")
        out[f"{hold}:coupling_ratio"] = {"P": cp, "R": cr, "met": bool(cr <= cp + LINE_2_COUPLING_MARGIN)}
    return out


def read(c_full: tuple[dict, dict], c_half: tuple[dict, dict], f: tuple[dict, dict]) -> dict:
    l1, l2 = line_1(c_full), line_2(f)
    met1, met2 = any(x["met"] for x in l1.values()), all(x["met"] for x in l2.values())
    growing = {ro: still_growing(c_full, c_half, ro) for ro in READOUTS if not l1[ro]["met"]}
    if met1 and met2:
        verdict = "R becomes the recipe candidate (decision 57's promotion checklist)"
    elif met1:
        failed = [k for k, x in l2.items() if not x["met"]]
        verdict = f"R pays on large molecules but costs elsewhere ({', '.join(failed)}): a combined target is designed and registered"
    elif any(growing.values()):
        verdict = "line 1 missed while R's advantage is still growing: data-limited, repeated after the next data step"
    else:
        verdict = "line 1 missed, flat: the third target (read-out-metric least squares, ridge-anchored) is registered"
    return {"verdict": verdict, "line_1": l1, "line_2": l2, "still_growing": growing}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for name in ("c-full", "c-half", "f"):
        ap.add_argument(f"--{name}", nargs=2, type=Path, required=True, metavar=("P", "R"))
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    load = lambda pair: tuple(json.loads(p.read_text(encoding="utf-8")) for p in pair)  # noqa: E731
    res = read(load(a.c_full), load(a.c_half), load(a.f))
    text = json.dumps(res, indent=1)
    if a.out:
        Path(f"{a.out}.json").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
