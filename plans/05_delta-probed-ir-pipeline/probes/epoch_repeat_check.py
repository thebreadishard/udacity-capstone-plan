"""A re-run of one seed with only a higher epoch cap must repeat the first run epoch for epoch (TASKS 169).

The trainer has no epoch-dependent learning-rate schedule, so with the same inputs and seed the logged epoch lines up to the old cap are
the same; a difference means the inputs moved (the corpus, the pool, a default) and the re-run is not the same recipe. Compares every
logged `seed <s> epoch <e>/<cap>: ... val <v>` line of the old log with the new one for e ≤ the old cap.

    python probes/epoch_repeat_check.py <old.log> <new.log> --seed 2 [--rtol 1e-3]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EPOCH_LINE = re.compile(r"seed (\d+) epoch (\d+)/(\d+): .* val ([0-9.eE+-]+) ")


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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old", type=Path)
    ap.add_argument("new", type=Path)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--rtol", type=float, default=1e-3, help="relative tolerance on the logged (rounded) values")
    a = ap.parse_args()
    old, old_cap = val_by_epoch(a.old, a.seed)
    new, new_cap = val_by_epoch(a.new, a.seed)
    if new_cap <= old_cap:
        raise SystemExit(f"the new run's cap {new_cap} is not above the old cap {old_cap}")
    shared = sorted(e for e in old if e <= old_cap and e in new)
    if not shared:
        raise SystemExit("no logged epoch in common")
    if old_cap in old and old_cap not in new:   # the same inputs cannot stop earlier than the run they repeat
        raise SystemExit(f"the new log skips epoch {old_cap}, the old run's last")
    bad = [(e, old[e], new[e]) for e in shared if abs(old[e] - new[e]) > a.rtol * abs(old[e])]
    for e in shared:
        print(f"epoch {e}: old {old[e]:.5g} new {new[e]:.5g}")
    if bad:
        print(f"REPEAT FAILED: {len(bad)} of {len(shared)} epochs differ beyond rtol {a.rtol}; first: epoch {bad[0][0]} "
              f"old {bad[0][1]:.5g} new {bad[0][2]:.5g}", flush=True)
        return 1
    print(f"REPEAT OK: seed {a.seed}, {len(shared)} logged epochs up to {max(shared)} repeat within rtol {a.rtol}; "
          f"the new run went on to epoch {max(new)} of {new_cap}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
