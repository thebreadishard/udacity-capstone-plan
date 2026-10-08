"""The labels server's first-day read (registration 1 of Design_2026-10-05_Analytic_Labels_and_Stepping_Stone.md: "a first-day read of the lane
throughput corrects this estimate on record before the second day; below 0.8 molecules per lane-hour a second CCX53 is proposed, not assumed").

Reads the lane logs fetched from the server (`lane_<n>_molecules.log`: one line per functional, "molecules/<id> <tag>: <seconds> s; ...") and the
lanes' id lists (largest molecules first), takes atom counts from the local corpus, and projects the rest of each lane with t(n) = t_ref·(n/n_ref)^p
per functional: p is fitted when the measured molecules span ≥ 5 atoms, otherwise bracketed by p = 3 and p = 4 (an analytic DFT Hessian scales
between the two at this size). A functional not yet measured on a lane takes the ratio to B3LYP measured elsewhere, else 1.5 (bracketed 1.0–2.0).

    python probes/labels_throughput.py <dir with lane logs and id lists> <out stem> [--fetch] [--lists 'small_ids_*.txt'] [--started …]

Since 8 Oct 2026 07:1x the lanes run smallest-first lists (`small_ids_<n>.txt`; the original largest-first `labels_ids_<n>.txt` are kept).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
MOLS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
SERVER = "root@157.180.32.149"
KEY = Path.home() / ".ssh" / "hetzner_g_measure"
EUR_PER_H = 0.855                       # CCX53, as registered
LINE_MOL_PER_LANE_H = 0.8               # the registered line for proposing a second server
LINE = re.compile(r"molecules/(\S+) (\w+): (\d+(?:\.\d+)?) s;")


def parse_molecule_log(text: str) -> dict:
    """{id: {functional: seconds}} from a lane's molecules log."""
    out: dict = {}
    for m in LINE.finditer(text):
        out.setdefault(m.group(1), {})[m.group(2)] = float(m.group(3))
    return out


def ids_of(lanes: dict, done: dict) -> set:
    """Every id the read needs an atom count for: the lanes' current lists and the molecules already timed (8 Oct 2026: after the switch to the
    smallest-first lists, the five molecules finished before it are on no list)."""
    return {i for ids in lanes.values() for i in ids} | set(done)


def n_atoms(mol_id: str) -> int:
    return len(json.loads((MOLS / mol_id / "geometry.json").read_text(encoding="utf-8"))["symbols"])


def fit_exponent(ns, ts) -> float | None:
    """Least-squares p in log t = c + p log n; None when the sizes span fewer than 5 atoms."""
    ns, ts = np.asarray(ns, float), np.asarray(ts, float)
    if ns.size < 3 or ns.max() - ns.min() < 5:
        return None
    return float(np.polyfit(np.log(ns), np.log(ts), 1)[0])


def predict(n: float, n_ref, t_ref, p: float) -> float:
    """Seconds for an n-atom molecule from measured (n_ref, t_ref) pairs: the mean of each pair's scaled value."""
    return float(np.mean([t * (n / nr) ** p for nr, t in zip(n_ref, t_ref)]))


def project(lanes: dict, done: dict, atoms: dict, p: float, wratio: float) -> dict:
    """lanes = {lane: [ids in order]}; done = {id: {functional: s}}. Remaining lane-hours per lane (current molecule counted whole, a bound)."""
    b = [(atoms[i], f["b3lyp"]) for i, f in done.items() if "b3lyp" in f]
    w = [(atoms[i], f["wb97x"]) for i, f in done.items() if "wb97x" in f]
    if not b:
        raise ValueError("no B3LYP timing yet")
    nb, tb = zip(*b)
    rem = {}
    for lane, ids in lanes.items():
        s = 0.0
        for i in ids:
            f = done.get(i, {})
            if "b3lyp" not in f:
                s += predict(atoms[i], nb, tb, p)
            if "wb97x" not in f:
                s += predict(atoms[i], *zip(*w), p) if w else wratio * predict(atoms[i], nb, tb, p)
        rem[lane] = s / 3600
    return rem


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir")
    ap.add_argument("out")
    ap.add_argument("--fetch", action="store_true", help="scp the lane logs and id lists from the labels server into <dir> first")
    ap.add_argument("--started", default="2026-10-07 16:46,2026-10-07 18:47,2026-10-07 18:47,2026-10-07 18:47",
                    help="UTC start per lane, comma list (lane 0 began ungated at 16:46; the server's cost is counted from the earliest)")
    ap.add_argument("--lists", default="small_ids_*.txt", help="the lanes' current id lists in <dir> (8 Oct: smallest first)")
    a = ap.parse_args()
    d = Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    if a.fetch:
        subprocess.run(["scp", "-q", "-o", "BatchMode=yes", "-i", str(KEY), f"{SERVER}:/root/labels/lane_*.log", f"{SERVER}:/root/labels/labels_ids_*.txt", f"{SERVER}:/root/labels/small_ids_*.txt",
                        str(d)], check=True)
    lanes = {int(f.stem[-1]): [x.strip() for x in f.read_text().splitlines() if x.strip()] for f in sorted(d.glob(a.lists))}
    done: dict = {}
    for f in sorted(d.glob("lane_?_molecules.log")):
        done.update(parse_molecule_log(f.read_text(encoding="utf-8", errors="replace")))
    atoms = {i: n_atoms(i) for i in ids_of(lanes, done)}
    complete = [i for i, f in done.items() if {"b3lyp", "wb97x"} <= set(f)]
    rb = [done[i]["wb97x"] / done[i]["b3lyp"] for i in complete]
    pb = fit_exponent([atoms[i] for i in done if "b3lyp" in done[i]], [f["b3lyp"] for f in done.values() if "b3lyp" in f])
    ps = [pb] if pb is not None else [3.0, 4.0]
    wr = [float(np.mean(rb))] if rb else [1.0, 1.5, 2.0]
    now = datetime.now(UTC).replace(tzinfo=None)
    lane_h = [(now - datetime.strptime(s.strip(), "%Y-%m-%d %H:%M")).total_seconds() / 3600 for s in a.started.split(",")]
    elapsed_h = max(lane_h)                                            # the server's hours so far (from the earliest lane)
    cases = []
    for p in ps:
        for r in wr:
            rem = project(lanes, done, atoms, p, r)
            total_lane_h = sum(rem.values()) + sum(lane_h)
            cases.append(dict(p=p, wb97x_over_b3lyp=r, remaining_lane_h=rem, finish_days_from_now=max(rem.values()) / 24,
                              server_days_total=(max(rem.values()) + elapsed_h) / 24, eur_total=(max(rem.values()) + elapsed_h) * EUR_PER_H,
                              mol_per_lane_h=len({i for v in lanes.values() for i in v} | set(complete)) / total_lane_h))
    md = [f"# Labels server throughput — {datetime.now():%Y-%m-%d %H:%M} (lanes started {a.started} UTC; the first {elapsed_h:.1f} h ago)", "",
          f"Measured: {len(done)} molecules with at least one functional, {len(complete)} complete. "
          + "; ".join(f"{i} ({atoms[i]} atoms): " + ", ".join(f"{k} {v:.0f} s" for k, v in done[i].items()) for i in done), "",
          f"Exponent: {'fitted ' + format(pb, '.2f') if pb is not None else 'bracketed 3–4 (sizes measured span < 5 atoms)'}; ωB97X/B3LYP: "
          + (f"measured {np.mean(rb):.2f} over {len(rb)}" if rb else "not yet measured, bracketed 1.0–2.0"), "",
          "| p | ωB97X/B3LYP | finish (days from now) | server days in all | € in all | molecules per lane-hour |", "|---|---|---|---|---|---|"]
    md += [f"| {c['p']:.2f} | {c['wb97x_over_b3lyp']:.2f} | {c['finish_days_from_now']:.1f} | {c['server_days_total']:.1f} | {c['eur_total']:.0f} | "
           f"{c['mol_per_lane_h']:.2f} |" for c in cases]
    lo, hi = min(c["mol_per_lane_h"] for c in cases), max(c["mol_per_lane_h"] for c in cases)
    md += ["", f"Registered: ≈ 8–10 days, €165–205; the line for proposing a second server is {LINE_MOL_PER_LANE_H} molecules per lane-hour. "
           f"Projected throughput {lo:.2f}–{hi:.2f} → " + ("**below the line**" if hi < LINE_MOL_PER_LANE_H else
                                                           "above the line" if lo >= LINE_MOL_PER_LANE_H else "straddles the line") + "."]
    Path(a.out + ".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    Path(a.out + ".json").write_text(json.dumps(dict(date=f"{datetime.now():%Y-%m-%d %H:%M}", started_utc=a.started, done=done,
                                                     atoms={i: atoms[i] for i in done}, cases=cases), indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
