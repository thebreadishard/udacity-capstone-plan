"""Learning-curve fit for rung-C records (1 Oct 2026, target T2 of the Sherlock-day proposal): the hold-out read-outs of several `rungC_train.py`
records — one per pool size — fitted as a power law in the pool size with `e11_power_law.fit_predict` (seed-bootstrap, 68 % bands) and extrapolated to
the sizes a desktop year could label. Every number traces to the records named on the command line.

    python probes/rungC_learning_curve_fit.py <out_prefix> <record.json> [<record.json> ...] [--targets 1500,5000,20000]

A record contributes every size in its `curve`; the (a) and (b) hold-outs are fitted separately, for the ring-coupling ratio and the corrected ω rms.
--families (15 Oct 2026, TASKS 58) adds the diagonal error per band family (`diag_rms`: CH-stretch, CH-oop, ring-ip, other). Every fit also reports
the pool's layer shares at each point (from the record's `pool_ids`, the first n ids) and flags a curve whose shares differ by more than
COMPOSITION_TOL between points: the 2 Oct fit had put an A+A2-only 175 point beside B-heavy 449/750 points, a count curve that was not one.
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "modules" / "05_support_predictor" / "m05"))
import e11_power_law as E11  # noqa: E402

READOUTS = (("ring_coupling_ratio", lambda r: r["coupling_ratio"]), ("corrected_freq_rms", lambda r: r["corrected_freq_rms"]))
FAMILIES = ("CH-stretch", "CH-oop", "ring-ip", "other")
FAMILY_READOUTS = tuple((f"diag_rms_{f}", lambda r, f=f: r["diag_rms"][f]) for f in FAMILIES)
COMPOSITION_TOL = 0.05                                     # largest allowed difference of a layer's share between two points of one curve


def readouts(families: bool = False) -> tuple:
    return READOUTS + (FAMILY_READOUTS if families else ())


def points_from_records(paths: list[str], hold: str, which=READOUTS) -> list[tuple]:
    """[(n, values per seed for each read-out in `which`)], one entry per pool size found in the records, sorted by n; a size present twice is
    refused."""
    pts = {}
    for p in paths:
        rec = json.load(open(p, encoding="utf-8"))
        for n, row in rec["curve"].items():
            n = int(n)
            if n in pts:
                raise ValueError(f"pool size {n} appears in two records ({p} and an earlier one) — give one record per size")
            seeds = row["per_seed"]
            pts[n] = (n, *[[get(s[hold]) for s in seeds] for _, get in which])
    return [pts[n] for n in sorted(pts)]


def composition(paths: list[str]) -> dict:
    """Layer shares of the pool at each point (the first n of the record's pool_ids; the id prefix is the layer) and the largest spread of any
    layer's share between points; points whose record has no pool_ids are left out."""
    shares = {}
    for p in paths:
        rec = json.load(open(p, encoding="utf-8"))
        ids = rec.get("pool_ids") or []
        for n in rec["curve"]:
            take = ids[:int(n)]
            if take:
                layers = [i.split("_")[0] for i in take]
                shares[int(n)] = {L: round(layers.count(L) / len(layers), 3) for L in sorted(set(layers))}
    names = sorted({L for s in shares.values() for L in s})
    spread = max((max(s.get(L, 0.0) for s in shares.values()) - min(s.get(L, 0.0) for s in shares.values()) for L in names), default=0.0)
    return {"shares": {str(n): shares[n] for n in sorted(shares)}, "max_spread": round(spread, 3), "fixed": spread <= COMPOSITION_TOL}


def fit_curves(paths: list[str], targets: tuple, seed: int = 0, families: bool = False) -> dict:
    E11.TARGETS = tuple(targets)                          # the helper reads its extrapolation sizes from this module constant
    rng = np.random.default_rng(seed)
    which = readouts(families)
    out = {}
    for hold in ("a", "b"):
        pts = points_from_records(paths, hold, which)
        if len(pts) < 2:
            raise ValueError(f"hold-out ({hold}): {len(pts)} pool size(s) — a fit needs at least two")
        out[hold] = {"sizes": [p[0] for p in pts], "n_seeds": [len(p[1]) for p in pts]}
        for k, (name, _) in enumerate(which, start=1):
            out[hold][name] = E11.fit_predict(pts, k, rng)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_prefix")
    ap.add_argument("records", nargs="+")
    ap.add_argument("--targets", default="1500,5000,20000")
    ap.add_argument("--families", action="store_true", help="add the diagonal error per band family (diag_rms) as read-outs")
    a = ap.parse_args()
    t0 = time.time()
    targets = tuple(int(t) for t in a.targets.split(","))
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "records": a.records, "targets": list(targets),
           "curves": fit_curves(a.records, targets, families=a.families), "composition": composition(a.records)}
    res["seconds"] = round(time.time() - t0, 1)
    out = Path(a.out_prefix)
    json.dump(res, open(out.with_suffix(".json"), "w"), indent=1)
    lines = [f"# Rung-C learning-curve fit ({res['date']})", "", "Records: " + ", ".join(f"`{Path(p).name}`" for p in a.records), ""]
    comp = res["composition"]
    lines += ["Pool composition (layer shares): " + "; ".join(f"{n}: " + ", ".join(f"{L} {v:.2f}" for L, v in s.items()) for n, s in comp["shares"].items())
              + f" — largest spread {comp['max_spread']:.2f}" + ("" if comp["fixed"] else f" **> {COMPOSITION_TOL}: not a count curve at fixed composition**"), ""]
    for hold, c in res["curves"].items():
        lines += [f"## Hold-out ({hold}) — pool sizes {c['sizes']} (seeds {c['n_seeds']})", "",
                  "| read-out | fitted means | slope (68 %) | factor per decade | " + " | ".join(f"→ {t}" for t in targets) + " |",
                  "|---|---|---|---|" + "---|" * len(targets)]
        for name, _ in readouts(a.families):
            f = c[name]
            fitted = ", ".join(f"{int(float(n))}: {v:.3f}" for n, v in f["fitted_on"].items())
            pred = " | ".join(f"{f['predictions'][str(t)]['point']:.3f} ({f['predictions'][str(t)]['lo68']:.3f}–{f['predictions'][str(t)]['hi68']:.3f})" for t in targets)
            lines.append(f"| {name} | {fitted} | {f['slope']:.3f} ({f['slope_lo68']:.3f}, {f['slope_hi68']:.3f}) | {f['factor_per_decade']:.2f} | {pred} |")
        lines.append("")
    lines.append(f"{res['seconds']} s.")
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
