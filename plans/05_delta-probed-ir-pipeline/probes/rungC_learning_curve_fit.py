"""Learning-curve fit for rung-C records (1 Oct 2026, target T2 of the Sherlock-day proposal): the hold-out read-outs of several `rungC_train.py`
records — one per pool size — fitted as a power law in the pool size with `e11_power_law.fit_predict` (seed-bootstrap, 68 % bands) and extrapolated to
the sizes a desktop year could label. Every number traces to the records named on the command line.

    python probes/rungC_learning_curve_fit.py <out_prefix> <record.json> [<record.json> ...] [--targets 1500,5000,20000]

A record contributes every size in its `curve`; the (a) and (b) hold-outs are fitted separately, for the ring-coupling ratio and the corrected ω rms.
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

READOUTS = (("ring_coupling_ratio", "coupling_ratio"), ("corrected_freq_rms", "corrected_freq_rms"))


def points_from_records(paths: list[str], hold: str) -> list[tuple]:
    """[(n, ratios per seed, ω per seed)], one entry per pool size found in the records, sorted by n; a size present twice is refused."""
    pts = {}
    for p in paths:
        rec = json.load(open(p, encoding="utf-8"))
        for n, row in rec["curve"].items():
            n = int(n)
            if n in pts:
                raise ValueError(f"pool size {n} appears in two records ({p} and an earlier one) — give one record per size")
            seeds = row["per_seed"]
            pts[n] = (n, [s[hold]["coupling_ratio"] for s in seeds], [s[hold]["corrected_freq_rms"] for s in seeds])
    return [pts[n] for n in sorted(pts)]


def fit_curves(paths: list[str], targets: tuple, seed: int = 0) -> dict:
    E11.TARGETS = tuple(targets)                          # the helper reads its extrapolation sizes from this module constant
    rng = np.random.default_rng(seed)
    out = {}
    for hold in ("a", "b"):
        pts = points_from_records(paths, hold)
        if len(pts) < 2:
            raise ValueError(f"hold-out ({hold}): {len(pts)} pool size(s) — a fit needs at least two")
        out[hold] = {"sizes": [p[0] for p in pts], "n_seeds": [len(p[1]) for p in pts]}
        for name, which in zip(("ring_coupling_ratio", "corrected_freq_rms"), (1, 2), strict=True):
            out[hold][name] = E11.fit_predict(pts, which, rng)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_prefix")
    ap.add_argument("records", nargs="+")
    ap.add_argument("--targets", default="1500,5000,20000")
    a = ap.parse_args()
    t0 = time.time()
    targets = tuple(int(t) for t in a.targets.split(","))
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "records": a.records, "targets": list(targets), "curves": fit_curves(a.records, targets)}
    res["seconds"] = round(time.time() - t0, 1)
    out = Path(a.out_prefix)
    json.dump(res, open(out.with_suffix(".json"), "w"), indent=1)
    lines = [f"# Rung-C learning-curve fit ({res['date']})", "", "Records: " + ", ".join(f"`{Path(p).name}`" for p in a.records), ""]
    for hold, c in res["curves"].items():
        lines += [f"## Hold-out ({hold}) — pool sizes {c['sizes']} (seeds {c['n_seeds']})", "",
                  "| read-out | fitted means | slope (68 %) | factor per decade | " + " | ".join(f"→ {t}" for t in targets) + " |",
                  "|---|---|---|---|" + "---|" * len(targets)]
        for name, _ in READOUTS:
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
