"""The read rule of the new CC anchors (TASKS 291; `GoalGathering/notes/PreRegistration_2026-11-21_New_Anchors_Read_Rule.md`).

The user's principle (21 Nov 2026): train on the smallest molecules proven to reach the goal. This module holds the rule's mechanical
parts, so the read is a script and not a judgement made after the numbers are seen:

- `split` — which anchors are test anchors: the eleven carried before 21 Nov and a fixed fifth of the new ones chosen by the id's sha1
  (`TEST_MODULUS`), never by size or by a result; the training anchors in one fixed order, cheapest first by the plan's hour rule;
- `milestones` — the training counts read: STEP, 2·STEP, … as long as the first k anchors of the fixed order are all finished, so the
  training sets of a curve are nested and a later read sees the same sets;
- `decide` — the outcome from one table: every milestone recomputed at this read with one test set and one network, per family the
  seed-mean error and its 95 % bootstrap interval over molecules.

    python probes/new_anchor_read.py frozen --plan modules/05_support_predictor/out/anchor_plan/count_n167.json \\
        --out GoalGathering/notes/new_anchors_2026-11-21     → test_ids.txt, train_ids.txt (refused when they exist)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
LINE_CM = 3.0            # decision 53 / decision 65: 3 cm⁻¹ per family
MIN_GAIN_CM = 0.1        # a gain smaller than this, or than the noise, over two milestone steps is no longer falling
MIN_TEST = 30            # no verdict on fewer test anchors (of 49)
TEST_MODULUS = 5         # sha1(id) % 5 == 0 → test: a fifth of the new anchors
STEP = 20                # read every 20 training anchors


@dataclass(frozen=True)
class Point:
    mean: float          # seed-mean rms (cm⁻¹) over the test anchors' bands of the family
    lo: float            # 95 % bootstrap interval over molecules
    hi: float


@dataclass(frozen=True)
class Outcome:
    verdict: str         # REACHED, AT THE LINE UNCONFIRMED, FALLING, FLAT, NO LEARNING, NO READING
    k: int | None        # REACHED: the first milestone of the run at the line
    families: dict[str, str]
    reason: str


def is_test(mol_id: str) -> bool:
    """A new anchor is a test anchor when its id's sha1, read as an integer, is divisible by TEST_MODULUS."""
    return int(hashlib.sha1(mol_id.encode()).hexdigest(), 16) % TEST_MODULUS == 0


def split(new_ids: list[str], carried_before: set[str], hours: dict[str, float]) -> tuple[list[str], list[str]]:
    """(train, test): the carried anchors and a fixed fifth of the new ones test; the rest train, cheapest first (ties: the id)."""
    test = sorted(carried_before) + sorted(i for i in new_ids if i not in carried_before and is_test(i))
    train = sorted((i for i in new_ids if i not in carried_before and not is_test(i)), key=lambda i: (hours[i], i))
    return train, test


def milestones(train_order: list[str], finished: set[str]) -> list[int]:
    """STEP, 2·STEP, … while the first k anchors of the fixed order are all finished."""
    k_done = next((j for j, i in enumerate(train_order) if i not in finished), len(train_order))
    return list(range(STEP, k_done + 1, STEP))


def shape_problem(curves: dict[str, dict[int, Point]], proxy_as_is: dict[str, float], n_test: int) -> str | None:
    """Too few test anchors, a family missing, or milestones that differ, skip a step or number fewer than two; else None."""
    if n_test < MIN_TEST:
        return f"{n_test} test anchors read; at least {MIN_TEST} are needed for a verdict"
    missing = [f for f in FAMILIES if f not in curves or f not in proxy_as_is]
    if missing:
        return f"families missing: {missing}"
    grids = {tuple(sorted(curves[f])) for f in FAMILIES}
    if len(grids) != 1:
        return "the families were read at different milestones"
    ks = next(iter(grids))
    if list(ks) != list(range(STEP, STEP * len(ks) + 1, STEP)):
        return f"milestones {list(ks)} are not {STEP}, {2 * STEP}, …"
    return f"{len(ks)} milestone(s); two are needed" if len(ks) < 2 else None


def value_problem(curves: dict[str, dict[int, Point]], proxy_as_is: dict[str, float]) -> str | None:
    """A value negative or not finite, or an interval whose lower end lies above its upper end; else None. (A percentile bootstrap of
    an rms may, on a skewed sample, leave the point value outside its interval; that is reported, not refused.)"""
    numbers = [x for f in FAMILIES for p in curves[f].values() for x in (p.mean, p.lo, p.hi)] + list(proxy_as_is.values())
    if not all(math.isfinite(x) and x >= 0 for x in numbers):
        return "a value is negative or not finite"
    if any(p.lo > p.hi for f in FAMILIES for p in curves[f].values()):
        return "an interval's lower end lies above its upper end"
    return None


def unreadable(curves: dict[str, dict[int, Point]], proxy_as_is: dict[str, float], n_test: int) -> str | None:
    """Why the table cannot be read, or None."""
    return shape_problem(curves, proxy_as_is, n_test) or value_problem(curves, proxy_as_is)


def family_state(curve: dict[int, Point], proxy_as_is: float) -> str:
    """'at the line', 'no learning', 'flat above' or 'falling', from the family's last milestones."""
    ks = sorted(curve)
    last = curve[ks[-1]]
    if last.mean <= LINE_CM:
        return "at the line"
    if last.mean >= proxy_as_is:
        return "no learning"
    if len(ks) >= 3:
        gain = curve[ks[-3]].mean - last.mean
        if gain < max(MIN_GAIN_CM, (last.hi - last.lo) / 2):
            return "flat above"
    return "falling"


def reached_from(curves: dict[str, dict[int, Point]]) -> int | None:
    """The first milestone from which every family stays at the line through the last, when that run holds two milestones or more."""
    ks = sorted(next(iter(curves.values())))
    run = []                                  # the trailing milestones at which every family is at the line, last first
    for k in reversed(ks):
        if not all(curves[f][k].mean <= LINE_CM for f in FAMILIES):
            break
        run.append(k)
    return run[-1] if len(run) >= 2 else None


def decide(curves: dict[str, dict[int, Point]], proxy_as_is: dict[str, float], n_test: int, n_train: int) -> Outcome:
    """The outcome of one read (rules in the registration's order); n_train is the length of the frozen training order, from which
    `decide` itself works out whether a next milestone can exist (the last k + STEP ≤ n_train)."""
    reason = unreadable(curves, proxy_as_is, n_test)
    if not reason and max(next(iter(curves.values()))) > n_train:
        reason = f"a milestone beyond the {n_train} training anchors of the order"
    if reason:
        return Outcome("NO READING", None, {}, reason)
    states = {f: family_state(curves[f], proxy_as_is[f]) for f in FAMILIES}
    k = reached_from(curves)
    if k is not None:
        return Outcome("REACHED", k, states, f"every family ≤ {LINE_CM} cm⁻¹ from k = {k} through the last milestone")
    if all(s == "at the line" for s in states.values()):
        next_exists = max(next(iter(curves.values()))) + STEP <= n_train
        what = "the next milestone confirms or not" if next_exists else "no next milestone exists to confirm it"
        return Outcome("AT THE LINE UNCONFIRMED", None, states, f"every family at the line at the last milestone only; {what}")
    if any(s == "no learning" for s in states.values()):
        return Outcome("NO LEARNING", None, states, "a family above the line is not below the proxy model as it is")
    above = [f for f in FAMILIES if states[f] != "at the line"]
    if all(states[f] == "flat above" for f in above):
        return Outcome("FLAT", None, states, f"above the line and no longer falling beyond the noise: {above}")
    return Outcome("FALLING", None, states, "a family above the line is still falling")


def main(argv: list[str] | None = None) -> int:
    import anchor_plan as A

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    fr = sub.add_parser("frozen", help="write the test and train id lists once")
    fr.add_argument("--plan", required=True, type=Path)
    fr.add_argument("--registry", type=Path, default=A.M05 / "out" / "ANCHORS_STATUS.json")
    fr.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    test_file, train_file = args.out / "test_ids.txt", args.out / "train_ids.txt"
    if test_file.exists() or train_file.exists():
        raise SystemExit(f"{args.out} holds frozen lists already — they are written once")
    plan_ids = [i for ids in json.loads(args.plan.read_text(encoding="utf-8"))["chosen"].values() for i in ids]
    carried = {e["mol_id"] for e in json.loads(args.registry.read_text(encoding="utf-8"))["anchors"] if e["status"] == "carried"}
    rows = A.corpus_cells()
    hours = {i: rows[i]["hours"] for i in plan_ids}
    train, test = split(plan_ids, carried, hours)
    args.out.mkdir(parents=True, exist_ok=True)
    test_file.write_text("".join(i + "\n" for i in test), encoding="utf-8", newline="\n")
    train_file.write_text("".join(i + "\n" for i in train), encoding="utf-8", newline="\n")
    print(f"test {len(test)} ({len(carried)} carried + {len(test) - len(carried)} new), train {len(train)}, cheapest first")
    return 0


if __name__ == "__main__":
    sys.exit(main())
