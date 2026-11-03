"""A re-run of one seed with only a higher epoch cap must train on the same inputs as the run it repeats (TASKS 169).

Training on the laptop's CPU threads is not bit-reproducible (chain 35's seed 2 re-run, 3 Nov 2026: epoch 1's inner validation equal to
four digits, epoch 10's 0.1321 against 0.1319), so the logged epochs cannot prove the inputs equal past the first. The proof is the two
training records (`<log stem>.json`, written by `m05/rungC_train.py`): the same pool in the same order, the same hold-outs and analytic
substitutions, the same inner-validation molecules for the seed, every setting the same except the epoch cap, and the new record keeping
the hold-out twins (the old run trained before they were dropped). Epoch 1, before thread-order noise accumulates, must agree within rtol;
the later logged epochs are printed as the drift between the two runs, not tested.

    python probes/epoch_repeat_check.py <old.log> <new.log> --seed 2 [--rtol 1e-3]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EPOCH_LINE = re.compile(r"seed (\d+) epoch (\d+)/(\d+): .* val ([0-9.eE+-]+) ")
SAME_LISTS = ("pool_ids", "holdout_a", "holdout_b", "holdout_s", "excluded_ids", "scaffold_cores", "substituted_analytic",
              "pair_class_names", "sizes")
# Settings the trainer records since a change, with the value it used before then, unrecorded: weight decay was AdamW's literal 1e-4 at
# chain 35's commit 4cb6140ad1 (m05/rungC_train.py) before it became a setting.
SETTINGS_ADDED = {"weight_decay": 1e-4}
ABSENT = "<absent>"
NOT_SETTINGS = {"date", "provenance", "seconds", "curve", "zero_rule", "epochs", "seeds", "holdout_twins", "holdout_twins_dropped",
                *SAME_LISTS}


def val_by_epoch(log: Path, seed: int) -> tuple[dict[int, float], int]:
    """The logged inner-validation value per epoch of one seed, and that run's epoch cap."""
    vals: dict[int, float] = {}
    caps = set()
    with log.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = EPOCH_LINE.search(line)
            if m and int(m.group(1)) == seed:
                vals[int(m.group(2))] = float(m.group(4))
                caps.add(int(m.group(3)))
    if not vals:
        raise SystemExit(f"{log}: no epoch lines for seed {seed}")
    if len(caps) != 1:
        raise SystemExit(f"{log}: seed {seed} logs epoch caps {sorted(caps)}, expected one")
    return vals, caps.pop()


def load_record(log: Path) -> dict:
    path = log.with_suffix(".json")
    if not path.is_file():
        raise SystemExit(f"no training record {path} beside {log}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def seed_entry(rec: dict, seed: int) -> dict:
    hits = [e for size in rec["curve"].values() for e in size["per_seed"] if e["seed"] == seed]
    if len(hits) != 1:
        raise SystemExit(f"{len(hits)} per-seed entries for seed {seed}, expected one")
    return hits[0]


def input_differences(old: dict, new: dict, seed: int) -> list[str]:
    """Every way the new record's inputs differ from the old one's; empty when the re-run trained on the same inputs."""
    diffs = [f"{k} differs" for k in SAME_LISTS if old.get(k) != new.get(k)]
    old = SETTINGS_ADDED | old
    for k in sorted((set(old) | set(new)) - NOT_SETTINGS):
        if old.get(k, ABSENT) != new.get(k, ABSENT):
            diffs.append(f"setting {k}: {old.get(k, ABSENT)!r} -> {new.get(k, ABSENT)!r}")
    if new.get("holdout_twins") != "keep" or new.get("holdout_twins_dropped"):
        diffs.append(f"the new run dropped hold-out twins ({new.get('holdout_twins')!r}, {new.get('holdout_twins_dropped')!r})")
    if seed_entry(old, seed)["inner_val_ids"] != seed_entry(new, seed)["inner_val_ids"]:
        diffs.append(f"seed {seed}'s inner-validation molecules differ")
    return diffs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old", type=Path)
    ap.add_argument("new", type=Path)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--rtol", type=float, default=1e-3, help="relative tolerance on epoch 1's logged (rounded) inner validation")
    a = ap.parse_args()
    old, old_cap = val_by_epoch(a.old, a.seed)
    new, new_cap = val_by_epoch(a.new, a.seed)
    if new_cap <= old_cap:
        raise SystemExit(f"the new run's cap {new_cap} is not above the old cap {old_cap}")
    if 1 not in old or 1 not in new:
        raise SystemExit("epoch 1 is not logged in both runs")
    diffs = input_differences(load_record(a.old), load_record(a.new), a.seed)
    for e in sorted(e for e in old if e in new):
        print(f"epoch {e}: old {old[e]:.5g} new {new[e]:.5g} ({(new[e] - old[e]) / old[e]:+.2%})")
    for d in diffs:
        print(f"inputs: {d}")
    first_ok = abs(old[1] - new[1]) <= a.rtol * abs(old[1])
    if diffs or not first_ok:
        print(f"REPEAT FAILED: {len(diffs)} input differences; epoch 1 old {old[1]:.5g} new {new[1]:.5g}", flush=True)
        return 1
    print(f"REPEAT OK: seed {a.seed} trained on the same inputs (pool, hold-outs, inner validation, settings but the cap); epoch 1 within "
          f"rtol {a.rtol}; the new run went on to epoch {max(new)} of {new_cap}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
