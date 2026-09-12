#!/usr/bin/env python
"""Rewrites corpus/STATUS.md from manifest.csv and ledger.csv: counts per layer and status, hours spent, hours to go at the
measured rate per layer (median seconds per molecule from the ledger; 'not yet measured' until a layer has a done row).
Run:  python status.py"""
import csv, statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    rows = list(csv.DictReader(open(HERE / "manifest.csv", newline="", encoding="utf-8")))
    led = list(csv.DictReader(open(HERE / "ledger.csv", newline="", encoding="utf-8"))) if (HERE / "ledger.csv").exists() else []
    layers = sorted({r["layer"] for r in rows})
    counts = {L: Counter(r["status"] for r in rows if r["layer"] == L) for L in layers}
    secs = defaultdict(list)
    for l in led:
        if l["status"] == "done" and l["seconds_total"]:
            secs[l["layer"]].append(float(l["seconds_total"]))
    spent_h = sum(float(l["seconds_total"] or 0) for l in led) / 3600
    L = [f"# Corpus status — {datetime.now():%Y-%m-%d %H:%M}", "", f"Manifest rows: {len(rows):,}; ledger entries: {len(led)}; compute spent so far: {spent_h:.1f} h (from the ledger).", "",
         "| layer | pending | running | done | failed | median s/molecule (measured) | hours to go at that rate |", "|---|---|---|---|---|---|---|"]
    for Ly in layers:
        c = counts[Ly]; med = statistics.median(secs[Ly]) if secs[Ly] else None
        togo = f"{c['pending'] * med / 3600:.1f}" if med else "not yet measured"
        L.append(f"| {Ly} | {c['pending']:,} | {c['running']} | {c['done']} | {c['failed']} | {f'{med:.0f}' if med else '—'} | {togo} |")
    L += ["", "Last ten ledger entries:", "", "| id | name | machine | start | total s | status |", "|---|---|---|---|---|---|"]
    for l in led[-10:]:
        L.append(f"| {l['id']} | {l['name']} | {l['machine']} | {l['start']} | {l['seconds_total']} | {l['status']} |")
    if not led:
        L.append("| — | — | — | — | — | nothing computed yet |")
    (HERE / "STATUS.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
