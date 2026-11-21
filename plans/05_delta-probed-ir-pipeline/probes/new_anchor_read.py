"""The read rule of the new CC anchors (TASKS 291; `GoalGathering/notes/PreRegistration_2026-11-21_New_Anchors_Read_Rule.md`).

The user's principle (21 Nov 2026): train on the smallest molecules proven to reach the goal. This module holds the rule's mechanical
parts, so the read is a script and not a judgement made after the numbers are seen:

- `split` — which new anchors are test anchors: a fixed fifth chosen by the id's sha1 (`TEST_MODULUS`), never by size or by a result;
  the eleven anchors carried before 21 Nov are test anchors too (`frozen` writes both lists once);
- `milestones` — the training-anchor counts at which the curve is read (every `STEP`, plus all that are available);
- `decide` — the outcome from the per-family curves of seed-mean errors: REACHED, FLAT, FALLING, NO LEARNING or NO READING.

    python probes/new_anchor_read.py frozen --plan modules/05_support_predictor/out/anchor_plan/count_n167.json \\
        --out GoalGathering/notes/new_anchors_2026-11-21     → test_ids.txt, train_ids.txt (refused when they exist)
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
LINE_CM = 3.0            # decision 53 / decision 65: 3 cm⁻¹ per family
FLAT_CM = 0.1            # a family has stopped falling when two milestone steps together gain less than this
TEST_MODULUS = 5         # sha1(id) % 5 == 0 → test: a fifth of the new anchors
STEP = 20                # read every 20 training anchors


def is_test(mol_id: str) -> bool:
    """A new anchor is a test anchor when its id's sha1, read as an integer, is divisible by TEST_MODULUS."""
    return int(hashlib.sha1(mol_id.encode()).hexdigest(), 16) % TEST_MODULUS == 0


def split(new_ids: list[str], carried_before: set[str]) -> tuple[list[str], list[str]]:
    """(train, test): the carried anchors and a fixed fifth of the new ones test; the rest train, in the given order."""
    test = sorted(carried_before) + [i for i in new_ids if i not in carried_before and is_test(i)]
    train = [i for i in new_ids if i not in carried_before and not is_test(i)]
    return train, test


def milestones(n_train: int) -> list[int]:
    """Training counts read: STEP, 2·STEP, … up to n_train, and n_train itself; none below STEP."""
    if n_train < STEP:
        return []
    ks = list(range(STEP, n_train + 1, STEP))
    return ks if ks[-1] == n_train else [*ks, n_train]


@dataclass(frozen=True)
class Outcome:
    verdict: str                 # REACHED, FLAT, FALLING, NO LEARNING, NO READING
    k: int | None                # REACHED: the first k of the two consecutive milestones at the line
    families: dict[str, str]     # per family: 'at the line', 'flat above', 'falling' or 'no learning'
    reason: str


def _family_state(curve: dict[int, float], proxy_as_is: float) -> str:
    ks = sorted(curve)
    last = curve[ks[-1]]
    if last >= proxy_as_is:
        return "no learning"
    if last <= LINE_CM:
        return "at the line"
    if len(ks) >= 3 and curve[ks[-3]] - last < FLAT_CM:
        return "flat above"
    return "falling"


def _reached_at(curves: dict[str, dict[int, float]]) -> int | None:
    """The first milestone k from which every family is at the line at k and at the next milestone."""
    ks = sorted(next(iter(curves.values())))
    for a, b in itertools.pairwise(ks):
        if all(curves[f][a] <= LINE_CM and curves[f][b] <= LINE_CM for f in FAMILIES):
            return a
    return None


def unreadable(curves: dict[str, dict[int, float]], proxy_as_is: dict[str, float]) -> str | None:
    """Why the curves cannot be read, or None: a family missing, milestones that differ, fewer than two, a value not finite."""
    missing = [f for f in FAMILIES if f not in curves or f not in proxy_as_is]
    if missing:
        return f"families missing: {missing}"
    grids = {tuple(sorted(curves[f])) for f in FAMILIES}
    if len(grids) != 1:
        return "the families were read at different milestones"
    ks = next(iter(grids))
    if len(ks) < 2:
        return f"{len(ks)} milestone(s); two are needed"
    values = [curves[f][k] for f in FAMILIES for k in ks] + [proxy_as_is[f] for f in FAMILIES]
    if not all(math.isfinite(v) for v in values):
        return "a value is not finite"
    return None


def decide(curves: dict[str, dict[int, float]], proxy_as_is: dict[str, float]) -> Outcome:
    """The outcome of the read from each family's seed-mean error (cm⁻¹) per milestone k and the proxy model's error without a fine-tune.

    NO READING when `unreadable` names a reason; REACHED at k when every family is at the line at two consecutive milestones; otherwise
    NO LEARNING when a family's last value is not below the proxy model as it is; otherwise FLAT when every family above the line has
    stopped falling; otherwise FALLING."""
    reason = unreadable(curves, proxy_as_is)
    if reason:
        return Outcome("NO READING", None, {}, reason)
    states = {f: _family_state(curves[f], proxy_as_is[f]) for f in FAMILIES}
    k = _reached_at(curves)
    if k is not None:
        return Outcome("REACHED", k, states, f"every family ≤ {LINE_CM} cm⁻¹ at k = {k} and at the next milestone")
    if any(s == "no learning" for s in states.values()):
        return Outcome("NO LEARNING", None, states, "a family is not below the proxy model as it is")
    above = [f for f in FAMILIES if states[f] != "at the line"]
    if above and all(states[f] == "flat above" for f in above):
        return Outcome("FLAT", None, states, f"above the line and no longer falling: {above}")
    return Outcome("FALLING", None, states, "a family above the line is still falling: more anchors are worth computing")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    fr = sub.add_parser("frozen", help="write the test and train id lists once")
    fr.add_argument("--plan", required=True, type=Path)
    fr.add_argument("--registry", type=Path, default=Path("modules/05_support_predictor/out/ANCHORS_STATUS.json"))
    fr.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    test_file, train_file = args.out / "test_ids.txt", args.out / "train_ids.txt"
    if test_file.exists() or train_file.exists():
        raise SystemExit(f"{args.out} holds frozen lists already — they are written once")
    plan_ids = [i for ids in json.loads(args.plan.read_text(encoding="utf-8"))["chosen"].values() for i in ids]
    carried = {e["mol_id"] for e in json.loads(args.registry.read_text(encoding="utf-8"))["anchors"] if e["status"] == "carried"}
    train, test = split(plan_ids, carried)
    args.out.mkdir(parents=True, exist_ok=True)
    test_file.write_text("".join(i + "\n" for i in test), encoding="utf-8", newline="\n")
    train_file.write_text("".join(i + "\n" for i in train), encoding="utf-8", newline="\n")
    print(f"test {len(test)} ({len(carried)} carried + {len(test) - len(carried)} new), train {len(train)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
