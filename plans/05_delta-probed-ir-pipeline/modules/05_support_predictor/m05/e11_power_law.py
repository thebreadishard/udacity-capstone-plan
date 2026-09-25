"""E11.5 — power-law prediction of the layer-B learning curve, fixed before the 300-table (pre-registered 25 September 2026).

Fits log(metric) = a + b log(n) by least squares on the existing curve points (E7 rung B: n = 45, 100, 175, hold-outs (a) and (b); the size
split of 25 September: n = 45, 100, 161, size hold-out (a) and its control (b)), metrics = ring coupling ratio and corrected-frequency RMS,
using the per-seed means where they exist and a seed bootstrap (resampling seeds with replacement at every n) for a 68 % band. Predicts the
values at 300, 600 and 1,200. Descriptive: the pass/fail of the proof lives in the proof-of-learning pre-registration.

Usage: python e11_power_law.py <E7_rungB json> <size-split json> <out prefix>
"""
import argparse
import json
import time
from datetime import datetime

import numpy as np

TARGETS = [300, 600, 1200]


def curve_points(res, hold):
    """(n, per-seed values of ratio, per-seed values of corrected RMS) for one hold-out of a rung-B result file."""
    out = []
    for n in res["sizes"]:
        seeds = res["curve"][str(n)]["B1_mlp"]["per_seed"]
        out.append((n, [s[hold]["coupling_ratio"] for s in seeds], [s[hold]["corrected_freq_rms"] for s in seeds]))
    return out


def fit_predict(points, which, rng, nboot=2000):
    ns = np.array([p[0] for p in points], float); vals = [np.array(p[which], float) for p in points]
    def fit(ys):
        b, a = np.polyfit(np.log(ns), np.log(ys), 1); return a, b
    a0, b0 = fit(np.array([v.mean() for v in vals]))
    boots = []
    for _ in range(nboot):
        ys = np.array([rng.choice(v, size=len(v), replace=True).mean() for v in vals])
        boots.append(fit(np.maximum(ys, 1e-6)))
    boots = np.array(boots)
    pred = {}
    for t in TARGETS:
        p = np.exp(boots[:, 0] + boots[:, 1] * np.log(t))
        pred[str(t)] = dict(point=float(np.exp(a0 + b0 * np.log(t))), lo68=float(np.percentile(p, 16)), hi68=float(np.percentile(p, 84)))
    return dict(slope=float(b0), slope_lo68=float(np.percentile(boots[:, 1], 16)), slope_hi68=float(np.percentile(boots[:, 1], 84)),
                factor_per_decade=float(10 ** (-b0)), fitted_on={str(int(n)): float(v.mean()) for n, v in zip(ns, vals)}, predictions=pred)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("rungb"); ap.add_argument("size"); ap.add_argument("out_prefix"); a = ap.parse_args(); t0 = time.time()
    rng = np.random.default_rng(0); R = json.load(open(a.rungb)); S = json.load(open(a.size))
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "sources": {"rungB": a.rungb, "size_split": a.size}, "curves": {}}
    for name, src, hold in (("E7 hold-out (a) bare parents", R, "a"), ("E7 hold-out (b) unseen scaffolds", R, "b"), ("size split: > 26 atoms", S, "a"), ("size split control: ≤ 26 scaffolds", S, "b")):
        pts = curve_points(src, hold)
        res["curves"][name] = {"ring_coupling_ratio": fit_predict(pts, 1, rng), "corrected_freq_rms": fit_predict(pts, 2, rng)}
    res["seconds"] = round(time.time() - t0, 1); json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E11.5 — power-law predictions for the layer-B curve ({res['date']}); fixed before the 300-table", "",
          "Fit log(metric) = a + b·log(n) on the existing points; 68 % band from a seed bootstrap. 'factor per decade' = 10^(−b): how much the metric shrinks per tenfold data.", "",
          "| curve | metric | fitted points | slope b | factor per decade | predicted at 300 | 600 | 1,200 |", "|---|---|---|---|---|---|---|---|"]
    for name, c in res["curves"].items():
        for metric, m in c.items():
            fp = ", ".join(f"{k}: {v:.2f}" for k, v in m["fitted_on"].items()); p = m["predictions"]
            md.append(f"| {name} | {metric} | {fp} | {m['slope']:+.3f} [{m['slope_lo68']:+.3f}, {m['slope_hi68']:+.3f}] | {m['factor_per_decade']:.2f}× | "
                      + " | ".join(f"{p[t]['point']:.2f} [{p[t]['lo68']:.2f}, {p[t]['hi68']:.2f}]" for t in ("300", "600", "1200")) + " |")
    md += ["", "Reading aid: the proof-of-learning pre-registration asks ≥ 1.5× per decade on the bare-parent and size hold-outs; the factors above say what the short curves extrapolate to if nothing changes."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n"); print("\n".join(md[4:]))


if __name__ == "__main__":
    main()
