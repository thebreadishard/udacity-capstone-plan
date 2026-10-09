"""TASKS 38 (9 Oct 2026): the five-membered-ring pool outside hold-out (b) — chain 38's consequence (without the acenaphthylene, carbazole,
dibenzofuran and dibenzothiophene children hold-out (b) went 0.317 → 0.410). Selects the pending A2 rows of those four families from the manifest
(decision 52: ~60 children finish a family; each has 13–16 done), refuses any id of the frozen hold-out (b), and prices the list from measured
runner times: the median hours per molecule by atom count of the 200-molecule pool (`shards_nextpool/*/ledger.csv`, one CPX62 with two runners of
8 threads, the setup pool 3 uses), interpolated over atom count, divided by two runners per box, at the CPX62's €/h.

    python five_ring_pool.py [--out five_ring_pool_candidates_<date>.txt] [--eur-per-hour 0.208]
"""
import argparse
import csv
import sys
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FAMILIES = ("acenaphthylene", "carbazole", "dibenzofuran", "dibenzothiophene")
RUNNERS_PER_BOX = 2


def scaffold(name: str) -> str:
    return name.split("+")[0]


def select(manifest: list[dict], frozen_b: set[str]) -> list[dict]:
    rows = [r for r in manifest if r["layer"] == "A2" and r["status"] == "pending" and scaffold(r["name"]) in FAMILIES]
    clash = sorted(r["id"] for r in rows if r["id"] in frozen_b)
    if clash:
        raise ValueError(f"candidates in the frozen hold-out (b): {clash}")
    return sorted(rows, key=lambda r: (scaffold(r["name"]), r["id"]))


def run_order(rows: list[dict]) -> list[dict]:
    """Breadth first (decision 52): round robin over the families, smallest molecule first within each — a runner stopped part-way (the
    laptop hands the rest to the pool 3 box, the user's option 3 of 9 Oct) leaves every family equally advanced."""
    queues = [sorted((r for r in rows if scaffold(r["name"]) == f), key=lambda r: (int(r["n_atoms"]), r["id"])) for f in FAMILIES]
    out = []
    for i in range(max((len(q) for q in queues), default=0)):
        out += [q[i] for q in queues if i < len(q)]
    return out


def hours_by_atoms(ledgers: list[Path], manifest: dict, machine: str = "ubuntu-32gb-hel1-2", since: str = "2026-10-02") -> dict[int, float]:
    """Median runner-hours per molecule by atom count over the done A2 rows the 200-molecule pool computed (its CPX62, from its start; the ledger
    copies also hold older records of other machines, and restart variants that are not manifest ids)."""
    last = {}
    for p in ledgers:
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if (r["status"] == "done" and r["id"] in manifest and r["id"].startswith("A2_") and r["seconds_total"] and r["machine"] == machine
                    and r["start"] >= since):
                last[r["id"]] = float(r["seconds_total"]) / 3600
    by = {}
    for i, h in last.items():
        by.setdefault(int(manifest[i]["n_atoms"]), []).append(h)
    return {n: float(np.median(v)) for n, v in sorted(by.items())}


def price(rows: list[dict], table: dict[int, float], eur_per_hour: float) -> dict:
    ns, hs = np.array(sorted(table)), np.array([table[n] for n in sorted(table)])
    runner_h = float(sum(np.interp(int(r["n_atoms"]), ns, hs) for r in rows))   # clamped at the measured ends
    box_h = runner_h / RUNNERS_PER_BOX
    return dict(n=len(rows), runner_hours=runner_h, box_hours=box_h, days_one_box=box_h / 24, eur=box_h * eur_per_hour)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=f"five_ring_pool_candidates_{date.today():%Y-%m-%d}.txt")
    ap.add_argument("--eur-per-hour", type=float, default=0.208, help="CPX62 (pool 3 design note, 3 Oct 2026)")
    a = ap.parse_args()
    manifest = list(csv.DictReader(open(HERE / "manifest.csv", encoding="utf-8")))
    frozen_b = {ln.strip() for ln in open(HERE / "holdout_b_frozen_2026-10-08.txt", encoding="utf-8") if ln.strip() and not ln.startswith("#")}
    rows = select(manifest, frozen_b)
    table = hours_by_atoms(sorted(HERE.glob("shards_nextpool/*/ledger.csv")), {r["id"]: r for r in manifest})
    p = price(rows, table, a.eur_per_hour)
    per_family = {f: sum(scaffold(r["name"]) == f for r in rows) for f in FAMILIES}
    print(f"{p['n']} candidates {per_family}; measured hours per molecule by atoms {table}")
    print(f"≈ {p['runner_hours']:.0f} runner-hours = {p['box_hours']:.0f} CPX62-hours ≈ {p['days_one_box']:.1f} days on one box ≈ €{p['eur']:.0f} (excl. VAT)")
    (HERE / a.out).write_text("".join(r["id"] + "\n" for r in run_order(rows)), encoding="utf-8")   # the file order is the run order
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
