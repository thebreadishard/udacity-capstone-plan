"""TASKS 257: does a trained cation's correction leak onto its neutral skeleton?

Usage: cation_leak.py <module 05 folder> [--threads 2] [--count]. Read-only; one molecule in memory at a time. --count prints the sets
and stops before any network is loaded (the dry run).

The comparison, fixed before any number was read (18 Nov 2026):
  Networks (module 05, out/v14/): WITH = the data arm v14s3full (pool 1,082, the 50 cations of layer P3c among them), seeds 0, 1, 2;
  WITHOUT = the probe v14s3nop3c (the same recipe and pool minus the P3c layer, 1,032), seed 0 only; CLEAN = v1.4's measurement networks
  v14s3clean (45 cations, none of a hold-out molecule's skeleton), seeds 0, 1, 2.
  Quantity: per molecule and family, the rms over the family's B3LYP modes (the record's family labels) of the first-order diagonal
  error of one seed's dH against the analytic wB97X - B3LYP labels — `product_error_read.molecule_read`, as in
  results_m1/v14_data_read_2026-11-17/probe_nop3c.py. d = rms(WITH seed s) - rms(WITHOUT seed 0); d > 0 means the cation-trained
  network is worse on that molecule.
  (1) PARENTS: neutral pool molecules whose cation twin (P3c_<hash> of <layer>_<hash>) is in the WITH pool; they are in both pools
      (in-sample). Per family: n, mean, sd, median of d and how many d > 0, for seed 0 (the primary pair) and seeds 1 and 2.
  (2) Hold-out (a)'s benzene (A_8448043181) and 2-naphthoic acid (A_07cadc7923), whose cations the WITH arm trained: per family the
      rms for WITH seeds 0-2, WITHOUT seed 0 and CLEAN seeds 0-2.
  (3) CONTROL: neutral molecules in both pools whose cation twin is not in the WITH pool, the same statistics; also restricted to the
      parents' layers. A shift common to (1) and (3) is the probe having trained 50 fewer molecules; only a difference of (1) from (3)
      is specific to cation parents.
  The seed spread inside WITH (seeds 1, 2 against seed 0 on the same molecules) is printed as the size a single-seed difference can
  have without any cause. WITHOUT has one seed: a single-seed difference cannot be told from seed noise beyond that spread.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]
sys.path.insert(0, str(PLAN / "probes"))
import product_error_read as R  # noqa: E402  the probes folder is not a package

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
HOLDOUT_PAIR = {"A_8448043181": "benzene", "A_07cadc7923": "2-naphthoic acid"}
STEMS = {"with": ("E7_rungC_v14s3full_c00_control", "n1082", (0, 1, 2)),
         "without": ("E7_rungC_v14s3nop3c_c00_control", "n1032", (0,)),
         "clean": ("E7_rungC_v14s3clean_c00_control", "n1082", (0, 1, 2))}


def checkpoints(out: Path, arm: str) -> tuple[Path, ...]:
    stem, n, seeds = STEMS[arm]
    paths = tuple(out / f"{stem}_model_{n}_seed{s}.pt" for s in seeds)
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise SystemExit(f"missing checkpoints: {missing}")
    return paths


def pool(out: Path, arm: str) -> set[str]:
    return set(json.loads((out / f"{STEMS[arm][0]}.json").read_text(encoding="utf-8"))["pool_ids"])


def has_labels(folder: Path) -> bool:
    return all((folder / name).is_file() for name in R.LABELS)


def family_rms(read: R.MoleculeRead, seed: int) -> dict[str, float]:
    """Per family with modes in this molecule, the rms of one seed's first-order error (the record's family labels)."""
    out = {}
    for f in FAMILIES:
        pick = read.record_family == f
        if pick.any():
            out[f] = float(np.sqrt(np.mean(read.first_order[seed][pick] ** 2)))
    return out


def stats(diffs: list[float]) -> str:
    if not diffs:
        return "n 0"
    d = np.array(diffs)
    sd = float(d.std(ddof=1)) if len(d) > 1 else float("nan")
    return (f"n {len(d):>4}  mean {d.mean():+7.3f}  sd {sd:6.3f}  median {np.median(d):+7.3f}  "
            f"d>0 {int((d > 0).sum()):>4}  min {d.min():+7.3f}  max {d.max():+7.3f}")


def sets(m05: Path) -> tuple[list[str], list[str], dict[str, str], dict[str, str]]:
    out = m05 / "out" / "v14"
    with (m05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
        rows = {row["id"]: row for row in csv.DictReader(handle)}
    with_pool, without_pool = pool(out, "with"), pool(out, "without")
    cations = sorted(i for i in with_pool if i.startswith("P3c_"))
    if without_pool & set(cations):
        raise SystemExit("the WITHOUT pool holds P3c cations")
    if with_pool - set(cations) != without_pool:
        print(f"note: the pools differ beyond P3c: {len(with_pool - set(cations) - without_pool)} only WITH, "
              f"{len(without_pool - with_pool)} only WITHOUT")
    by_hash: dict[str, list[str]] = {}
    for i in rows:
        if not i.startswith("P3c_"):
            by_hash.setdefault(i.split("_", 1)[1], []).append(i)
    neutral_both = sorted(i for i in with_pool & without_pool if not i.startswith("P3c_"))
    trained_hashes = {c.split("_", 1)[1] for c in cations}
    folder = m05 / "corpus" / "molecules"
    parents = [i for i in neutral_both if i.split("_", 1)[1] in trained_hashes and has_labels(folder / i)]
    control = [i for i in neutral_both if i.split("_", 1)[1] not in trained_hashes and has_labels(folder / i)]
    unlabelled = [i for i in neutral_both if not has_labels(folder / i)]
    print(f"WITH pool {len(with_pool)} ({len(cations)} P3c cations), WITHOUT pool {len(without_pool)}")
    print(f"neutral molecules in both pools {len(neutral_both)}, {len(unlabelled)} without both analytic labels (left out)")
    orphans = [c for c in cations if not any(p in with_pool for p in by_hash.get(c.split("_", 1)[1], []))]
    print(f"cations whose neutral parent is in both pools with labels: {len(parents)}; cations with no parent in the pool: "
          f"{len(orphans)} {[rows[c]['name'] for c in orphans]}")
    for h in HOLDOUT_PAIR:
        twin = "P3c_" + h.split("_", 1)[1]
        print(f"hold-out {h} {HOLDOUT_PAIR[h]}: cation twin {twin} in WITH pool: {twin in with_pool}, in CLEAN pool: "
              f"{twin in pool(out, 'clean')}; molecule in a pool: {h in with_pool or h in without_pool}")
    layer = {i: rows[i]["layer"] for i in parents + control}
    names = {i: rows[i]["name"] for i in rows}
    return parents, control, layer, names


def read_all(m05: Path, ids: list[str], models: dict[str, tuple[Path, ...]]) -> dict[str, dict[str, list[dict[str, float]]]]:
    """Per molecule and arm, each seed's family rms; one molecule's reads at a time."""
    out: dict[str, dict[str, list[dict[str, float]]]] = {}
    for k, i in enumerate(ids, 1):
        folder = m05 / "corpus" / "molecules" / i
        out[i] = {}
        for arm, paths in models.items():
            read = R.molecule_read(folder, paths)
            out[i][arm] = [family_rms(read, s) for s in range(len(paths))]
        if k % 25 == 0 or k == len(ids):
            print(f"cation-leak {k}/{len(ids)} read, peak {R.peak_memory_gb():.2f} GB", flush=True)
    return out


def differences(reads: dict, ids: list[str], family: str, seed: int, base: tuple[str, int] = ("without", 0)) -> list[float]:
    arm, s0 = base
    return [reads[i]["with"][seed][family] - reads[i][arm][s0][family] for i in ids if family in reads[i]["with"][seed]]


def report_group(title: str, reads: dict, ids: list[str]) -> None:
    print(f"\n=== {title}: d = rms(WITH seed s) - rms(WITHOUT seed 0), cm-1, {len(ids)} molecules")
    for f in FAMILIES:
        for s in (0, 1, 2):
            print(f"{f:<11} seed {s}  {stats(differences(reads, ids, f, s))}")
    print("  seed noise inside WITH: rms(WITH seed s) - rms(WITH seed 0)")
    for f in FAMILIES:
        for s in (1, 2):
            print(f"{f:<11} seed {s}  {stats(differences(reads, ids, f, s, base=('with', 0)))}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("m05", type=Path)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--count", action="store_true")
    a = ap.parse_args()
    m05 = a.m05.resolve()
    if not 1 <= a.threads <= 4:
        raise SystemExit(f"--threads {a.threads}: 1 to 4 (the read runs beside a training)")
    torch.set_num_threads(a.threads)
    started = time.time()
    parents, control, layer, names = sets(m05)
    parent_layers = sorted({layer[i] for i in parents})
    control_matched = [i for i in control if layer[i] in parent_layers]
    print(f"parents {len(parents)} (layers {parent_layers}); control {len(control)}, of them in the parents' layers {len(control_matched)}")
    if a.count:
        print("count only: no network loaded")
        return
    out = m05 / "out" / "v14"
    reads = read_all(m05, parents + control, {arm: checkpoints(out, arm) for arm in ("with", "without")})
    report_group("(1) PARENTS whose cation WITH trained (in-sample)", reads, parents)
    report_group("(3) CONTROL, neutral pool molecules whose cation was not trained (in-sample)", reads, control)
    report_group("(3') CONTROL in the parents' layers", reads, control_matched)
    print("\n=== (1) per parent, seed 0: rms WITH / WITHOUT per family, cm-1")
    for i in parents:
        r = reads[i]
        print(f"{i:<14} {names[i][:22]:<22}" + "".join(
            f"  {f} {r['with'][0][f]:5.2f}/{r['without'][0][f]:5.2f}" for f in FAMILIES if f in r["with"][0]))
    print("\n=== (2) hold-out (a), out of sample: rms per family, cm-1")
    models = {arm: checkpoints(out, arm) for arm in STEMS}
    for i, label in HOLDOUT_PAIR.items():
        pair = read_all(m05, [i], models)[i]
        for arm, seeds in pair.items():
            for s, fam in enumerate(seeds):
                print(f"{label:<17} {arm:<8} seed {STEMS[arm][2][s]}" + "".join(f"  {f} {fam[f]:5.2f}" for f in FAMILIES if f in fam))
    print(f"\ncation leak read: {len(parents)} parents, {len(control)} controls, 2 hold-out molecules, "
          f"{time.time() - started:.0f} s, peak {R.peak_memory_gb():.2f} GB, threads {a.threads}")


if __name__ == "__main__":
    main()
