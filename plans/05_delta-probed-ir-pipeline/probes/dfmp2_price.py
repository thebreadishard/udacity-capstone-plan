"""Step 4 (P) of GoalGathering/notes/PreRegistration_2026-10-19_DFMP2_Composite_Step.md: the price of anchor set three's composite step by the
DF-MP2 route, from the run's own log — the median seconds per row of each molecule and basis, a power law in atoms per basis through them,
the five anchors' rows (unique displacements = FD gradients / 2, the registration table of set three) — and the peak RSS against the laptop.

    python probes/dfmp2_price.py <dfmp2_composite.log> [--threads 6] --out <prefix>
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

ATOMS = {"pyridine": 11, "naphthalene": 18}
ANCHORS = {"quinoxaline": (16, 48), "azulene": (18, 66), "acenaphthylene": (20, 66), "quinoline": (17, 102), "isoquinoline": (17, 102)}
BASES = ("cc-pvdz", "cc-pvtz")
LAPTOP_BUDGET_GB = 13.0      # tools/runspec.py LAPTOP_RUN_MEMORY_GB: all laptop runs together
HEADER = re.compile(r"^\[[0-9:]+\] \d+ rows of \S*mp2_rows_([a-z]+)_ccpv[dt]z\.npz at (cc-pv[dt]z)")
ROW = re.compile(r"^\[[0-9:]+\] df-mp2 (cc-pv[dt]z) k=\d+: H_kk \S+ \((\d+) s\)")
RSS = re.compile(r"^=== \(DF\) ([a-z]+) ccpv([dt])z done, peak RSS (\d+) kB")


def parse(log: str) -> tuple[dict[tuple[str, str], list[float]], dict[tuple[str, str], int]]:
    """Seconds per row and peak RSS (kB) per (molecule, basis)."""
    times: dict[tuple[str, str], list[float]] = {}
    rss: dict[tuple[str, str], int] = {}
    current = None
    for line in log.splitlines():
        if m := HEADER.match(line):
            current = (m.group(1), m.group(2))
        elif (m := ROW.match(line)) and current:
            if m.group(1) != current[1]:
                raise SystemExit(f"a {m.group(1)} row under a {current[1]} header: {line}")
            times.setdefault(current, []).append(float(m.group(2)))
        elif m := RSS.match(line):
            rss[(m.group(1), f"cc-pv{m.group(2)}z")] = int(m.group(3))
    return times, rss


def power_law(points: list[tuple[int, float]]) -> tuple[float, float]:
    """(a, b) of log t = a + b log n through the points; two sizes at least."""
    if len({n for n, _ in points}) < 2:
        raise SystemExit(f"{points}: one size only, no power law")
    xs, ys = [math.log(n) for n, _ in points], [math.log(t) for _, t in points]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def price(times: dict[tuple[str, str], list[float]]) -> dict:
    fits = {b: power_law([(ATOMS[mol], statistics.median(v)) for (mol, bb), v in times.items() if bb == b]) for b in BASES}
    anchors = {}
    for name, (n, grads) in ANCHORS.items():
        rows = grads // 2
        anchors[name] = {"atoms": n, "rows": rows, "hours": rows * sum(math.exp(fits[b][0]) * n ** fits[b][1] for b in BASES) / 3600}
    return {"fits": {b: {"a": a, "b": e} for b, (a, e) in fits.items()}, "anchors": anchors, "total_hours": sum(v["hours"] for v in anchors.values())}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("log")
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    times, rss = parse(Path(a.log).read_text(encoding="utf-8", errors="replace"))
    res = price(times)
    res["measured"] = {f"{m} {b}": {"rows": len(v), "median_s": statistics.median(v)} for (m, b), v in sorted(times.items())}
    res["peak_rss_gb"] = {f"{m} {b}": kb / 1e6 for (m, b), kb in sorted(rss.items())}
    res["threads"] = a.threads
    res["fits_laptop_budget"] = bool(rss) and max(rss.values()) / 1e6 <= LAPTOP_BUDGET_GB
    md = [f"# DF-MP2 composite step — price for anchor set three ({a.threads} threads per run)", "",
          "| measured | rows | median s per row | peak RSS GB |", "|---|---|---|---|"]
    md += [f"| {k} | {v['rows']} | {v['median_s']:.0f} | {res['peak_rss_gb'].get(k, float('nan')):.2f} |" for k, v in res["measured"].items()]
    md += ["", "| anchor | atoms | rows | predicted hours (DZ + TZ) |", "|---|---|---|---|"]
    md += [f"| {k} | {v['atoms']} | {v['rows']} | {v['hours']:.1f} |" for k, v in res["anchors"].items()]
    md += ["", f"**All five: {res['total_hours']:.1f} h at {a.threads} threads; the largest peak RSS "
           f"{max(res['peak_rss_gb'].values(), default=float('nan')):.2f} GB against the laptop's {LAPTOP_BUDGET_GB:g} GB for all runs.**"]
    Path(a.out + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    Path(a.out + ".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
