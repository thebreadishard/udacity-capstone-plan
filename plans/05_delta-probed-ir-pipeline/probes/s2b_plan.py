"""S2b's plan per server (registration GoalGathering/notes/PreRegistration_2026-10-19_S2b_Learning_Curve.md, 'Computation' and 'Price'): from
S2's measured times, each selected molecule's predicted wall time and first displaced Hessian, its stop rule (MAX_FIRST = 1.5 × the predicted
Hessian, at least MIN_MAX_FIRST_S), and the split of the list over N CPX62 servers, three molecules at a time each.

    python probes/s2b_plan.py --selection <s2b selection.json> --servers 2 3 --out <dir>

Fits (least squares of log time on log atoms over S2's molecules, from the fetched run probes/results_m1/s2_anharmonic_2026-10-18):
  per displaced Hessian: the median of a molecule's '<k>/<N> mode… in <s> s' lines in s2/<id>.log;
  per molecule: its start to its done or NOISY marker in dpir_s2/s2.log (the registration's hours ≈ exp(−11.82) · n^5.04).
Split: longest predicted first, each to the server whose slot frees first (three slots per server, as s2_batch.sh's xargs -P 3 starts the next
molecule of its list when a slot frees); each server's list in that order. Writes <out>/s2b_ids_<k>of<N>.tsv (id, geometry path, MAX_FIRST
seconds) and <out>/plan.json; prints per N the servers' predicted ends and the euros.
"""
from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import os
import re
import statistics
from datetime import datetime

from s2_select import CORPUS, HERE
from s2b_select import geometry_path

S2_RUN = os.path.join(HERE, "results_m1", "s2_anharmonic_2026-10-18")
SLOTS = 3                     # molecules at a time per CPX62 (S2: 5 threads each of 16)
EUR_PER_SERVER_HOUR = 0.208   # CPX62, Hetzner price of 3 Oct 2026 (memory 'Hetzner servers'; S2b registration)
STOP_FACTOR = 1.5             # the registration's stop rule
MIN_MAX_FIRST_S = 300         # below S2's smallest timed molecule (12 atoms) the fit extrapolates; a sub-minute stop would be noise
HESSIAN_LINE = re.compile(r"^\[\d\d:\d\d:\d\d\] \d+/\d+ mode\S+ E = \S+ in (\d+) s$")
MARKER = re.compile(r"^=== \(S2\) (\S+): (start|done|NOISY)\b.*?(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)$")


def hessian_seconds(log_dir: str) -> dict[str, float]:
    """Per molecule log <id>.log, the median wall time of its displaced Hessians."""
    out = {}
    for name in sorted(os.listdir(log_dir)):
        if not name.endswith(".log"):
            continue
        with open(os.path.join(log_dir, name), encoding="utf-8", errors="replace") as fh:
            times = [float(m.group(1)) for m in map(HESSIAN_LINE.match, fh) if m]
        if times:
            out[name[:-4]] = statistics.median(times)
    return out


def molecule_hours(batch_log: str) -> dict[str, float]:
    """Per molecule, start to done or NOISY in the batch log, in hours (a STOPPED or FAILED molecule has no time)."""
    starts, ends = {}, {}
    with open(batch_log, encoding="utf-8", errors="replace") as fh:
        for m in map(MARKER.match, fh):
            if m:
                (starts if m.group(2) == "start" else ends)[m.group(1)] = datetime.strptime(m.group(3), "%Y-%m-%d %H:%M:%S")
    return {i: (ends[i] - starts[i]).total_seconds() / 3600 for i in ends if i in starts}


def power_fit(points: list[tuple[int, float]]) -> tuple[float, float]:
    """(a, b) of log y = a + b · log n by least squares; at least three points of two sizes."""
    if len(points) < 3 or len({n for n, _ in points}) < 2:
        raise ValueError(f"{len(points)} points: too few to fit a power law")
    xs, ys = [math.log(n) for n, _ in points], [math.log(y) for _, y in points]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def atoms(ids: set[str]) -> dict[str, int]:
    with open(os.path.join(CORPUS, "manifest.csv"), encoding="utf-8") as fh:
        return {r["id"]: int(r["n_atoms"]) for r in csv.DictReader(fh) if r["id"] in ids}


def split(hours: dict[str, float], n_servers: int, slots: int = SLOTS) -> tuple[list[list[str]], list[float]]:
    """Longest first, each molecule to the server whose earliest slot frees first (ties: the lower server); the lists and each server's end."""
    free = [[0.0] * slots for _ in range(n_servers)]
    lists: list[list[str]] = [[] for _ in range(n_servers)]
    for i in sorted(hours, key=lambda i: (-hours[i], i)):
        k = min(range(n_servers), key=lambda s: (free[s][0], s))
        start = heapq.heappop(free[k])
        heapq.heappush(free[k], start + hours[i])
        lists[k].append(i)
    return lists, [max(f) for f in free]


def plan(selected: list[dict], hess_fit: tuple[float, float], mol_fit: tuple[float, float], servers: list[int]) -> dict:
    """Per molecule its predictions and stop rule; per server count the split, the ends and the euros."""
    mols = {}
    for m in selected:
        n = m["n_atoms"]
        hess = math.exp(hess_fit[0]) * n ** hess_fit[1]
        mols[m["id"]] = {"n_atoms": n, "hours": math.exp(mol_fit[0]) * n ** mol_fit[1], "hessian_s": hess,
                         "max_first_s": max(MIN_MAX_FIRST_S, math.ceil(STOP_FACTOR * hess))}
    out = {"fits": {"hessian_s": {"a": hess_fit[0], "b": hess_fit[1]}, "molecule_h": {"a": mol_fit[0], "b": mol_fit[1]}}, "molecules": mols, "servers": {}}
    for n_servers in servers:
        lists, ends = split({i: v["hours"] for i, v in mols.items()}, n_servers)
        out["servers"][str(n_servers)] = {"lists": lists, "end_h": ends, "server_h": sum(ends), "eur": sum(ends) * EUR_PER_SERVER_HOUR}
    return out


def write_atomic(path: str, text: str) -> None:
    with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as fh:      # the lists are read by bash on the server: no CR
        fh.write(text)
    os.replace(path + ".tmp", path)


def write_lists(out_dir: str, result: dict) -> None:
    os.makedirs(out_dir, exist_ok=True)
    for n_servers, v in result["servers"].items():
        for k, ids in enumerate(v["lists"], 1):
            rows = "".join(f"{i}\t{geometry_path(i)}\t{result['molecules'][i]['max_first_s']}\n" for i in ids)
            write_atomic(os.path.join(out_dir, f"s2b_ids_{k}of{n_servers}.tsv"), rows)
    write_atomic(os.path.join(out_dir, "plan.json"), json.dumps(result, indent=1) + "\n")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selection", required=True)
    ap.add_argument("--servers", type=int, nargs="+", default=[2, 3])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if any(n < 1 for n in a.servers):
        raise SystemExit(f"--servers {a.servers}: each at least 1")
    with open(a.selection, encoding="utf-8") as fh:
        selected = json.load(fh)["selected"]
    hess, hours = hessian_seconds(os.path.join(S2_RUN, "s2")), molecule_hours(os.path.join(S2_RUN, "dpir_s2", "s2.log"))
    n = atoms(set(hess) | set(hours))
    hess_fit = power_fit([(n[i], t) for i, t in hess.items()])
    mol_fit = power_fit([(n[i], h) for i, h in hours.items()])
    result = plan(selected, hess_fit, mol_fit, a.servers)
    result["fitted_on"] = {"hessian_molecules": len(hess), "timed_molecules": len(hours)}
    write_lists(a.out, result)
    print(f"fits on S2: Hessian s ≈ exp({hess_fit[0]:.2f}) · n^{hess_fit[1]:.2f} ({len(hess)} molecules); "
          f"molecule h ≈ exp({mol_fit[0]:.2f}) · n^{mol_fit[1]:.2f} ({len(hours)} molecules)")
    for i, v in result["molecules"].items():
        print(f"  {i:15s} {v['n_atoms']:2d} atoms  {v['hours']:5.1f} h  Hessian {v['hessian_s']:5.0f} s  MAX_FIRST {v['max_first_s']} s")
    for n_servers, v in result["servers"].items():
        print(f"{n_servers} servers: ends " + ", ".join(f"{e:.0f} h" for e in v["end_h"]) + f"; {v['server_h']:.0f} server-h ≈ €{v['eur']:.0f}")


if __name__ == "__main__":
    main()
