"""Where are the low modes, and where is their finite-difference noise? (8 Oct 2026; the user: the low-mode requirement becomes hard only when the large
molecules have clean labels — checked here before chain 35's half read is registered.)

For the molecules of the labels server's list (the training pool that gets analytic labels), split at the smallest-first half (`--split-atoms`, ≤ 22
atoms = the first 405): (1) how many 'other-low' modes (uncorrected ω < --low, the group of `rungC_low_modes_noise.py`) each half holds; (2) on the
molecules that already carry both routes, the FD-against-analytic error of the corrected ω per group (the target noise the analytic labels remove),
pooled per half.

    python probes/low_modes_by_size.py <out prefix> --ids-dir out/labels_lanes_2026-10-08   (run from modules/05_support_predictor)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import e7_t2_sqm as T2  # noqa: E402
import rungC_low_modes_noise as LN  # noqa: E402
from rungC_train import load_corpus  # noqa: E402


def half_of(n_atoms: int, split: int) -> str:
    return "small" if n_atoms <= split else "large"


def pooled_group_rms(rows: list[dict], group: str) -> tuple[float, int]:
    """rms over all modes of a group, pooled across molecules (each row carries per-group rms and counts)."""
    sq = sum(r["floor"][group] ** 2 * r["n"][group] for r in rows if group in r["floor"])
    n = sum(r["n"][group] for r in rows if group in r["floor"])
    return (float(np.sqrt(sq / n)) if n else float("nan")), n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("--ids-dir", required=True, help="directory with the labels lists (labels_ids_*.txt)")
    ap.add_argument("--molecules", default="corpus/molecules")
    ap.add_argument("--low", type=float, default=700.0)
    ap.add_argument("--split-atoms", type=int, default=22)
    ap.add_argument("--exclude-floor", default="", help="comma ids left out of the FD floor (benzene A_8448043181: its corpus psi4 row is known noise, 29 Sep)")
    a = ap.parse_args()
    ids = sorted({x.strip() for f in Path(a.ids_dir).glob("labels_ids_*.txt") for x in f.read_text().splitlines() if x.strip()})
    mols, _, _, _, _, substituted = load_corpus(a.molecules, True, log=lambda *_: None)
    counts = {"small": {g: 0 for g in LN.GROUPS}, "large": {g: 0 for g in LN.GROUPS}}
    nmol = {"small": 0, "large": 0}
    for i in ids:
        if i not in mols:
            continue
        m = mols[i]
        _, grp = LN.mode_errors(m, np.zeros_like(m["K"]), a.low)
        h = half_of(len(m["masses"]), a.split_atoms)
        nmol[h] += 1
        for g, c in LN.counts(grp).items():
            counts[h][g] += c
    floor = {"small": [], "large": []}
    skip = {s for s in a.exclude_floor.split(",") if s}
    for i in substituted:
        if i not in mols or i in skip:
            continue
        m = mols[i]
        d = Path(a.molecules) / i
        dH_fd = np.load(d / "hessian_wb97x.npz")["H_projected"] - np.load(d / "hessian_b3lyp.npz")["H_projected"]
        fe, fg = LN.mode_errors(m, T2.K_from_dH(m, dH_fd), a.low)
        floor[half_of(len(m["masses"]), a.split_atoms)].append({"id": i, "n_atoms": len(m["masses"]), "n": LN.counts(fg), "floor": LN.rms_by_group(fe, fg)})
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "split_atoms": a.split_atoms, "low": a.low, "molecules": nmol, "mode_counts": counts,
           "floor_excluded": sorted(skip), "floor_rows": floor, "floor_pooled": {h: {g: pooled_group_rms(floor[h], g) for g in LN.GROUPS} for h in floor}}
    tot_low = counts["small"]["other-low"] + counts["large"]["other-low"]
    md = [f"# Low modes by molecule size — {res['date']}", "",
          f"Labels list split at ≤ {a.split_atoms} atoms (small) / larger; 'other-low' = 'other' modes below {a.low:.0f} cm⁻¹.", "",
          "| half | molecules | other-low modes | share of all other-low | other-low per molecule |", "|---|---|---|---|---|"]
    for h in ("small", "large"):
        c = counts[h]["other-low"]
        md.append(f"| {h} | {nmol[h]} | {c} | {c / tot_low:.0%} | {c / max(nmol[h], 1):.1f} |")
    md += ["", "FD against analytic, corrected ω (cm⁻¹), pooled over the molecules with both routes" + (f" (left out: {', '.join(sorted(skip))})" if skip else "") + ":", "",
           "| half | molecules | " + " | ".join(LN.GROUPS) + " |", "|---|---|" + "---|" * len(LN.GROUPS)]
    for h in ("small", "large"):
        md.append(f"| {h} | {len(floor[h])} | " + " | ".join(f"{res['floor_pooled'][h][g][0]:.2f} ({res['floor_pooled'][h][g][1]})" for g in LN.GROUPS) + " |")
    Path(a.out + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    Path(a.out + ".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
