#!/usr/bin/env python3
"""Wall-clock of H / H2 / H2O Maxwell windows vs the 168 h cap.

Reads a JSON or CSV log of measured seconds. Does not invent times.
Without a log, prints NOT_RUN and exits 2.

Expected JSON:
  {"H": seconds, "H2": seconds, "H2O": seconds}

  python teacher_cost.py
  python teacher_cost.py cost_log.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cube_io import die_not_run, print_kv  # noqa: E402

CAP_H = 168.0
SPECIES = ("H", "H2", "H2O")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", nargs="?", default=None)
    args = p.parse_args()
    if args.log is None:
        die_not_run("no cost log; Octopus windows have not been run")
    path = Path(args.log)
    if not path.is_file():
        die_not_run(f"missing cost log {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    seconds = {}
    missing = []
    for key in SPECIES:
        if key not in raw or raw[key] is None:
            missing.append(key)
        else:
            seconds[key] = float(raw[key])
    if missing:
        die_not_run(f"cost log missing species {missing}")
    total_h = sum(seconds.values()) / 3600.0
    under = int(total_h <= CAP_H)
    print_kv(
        H_s=seconds["H"],
        H2_s=seconds["H2"],
        H2O_s=seconds["H2O"],
        total_h=total_h,
        cap_h=CAP_H,
        under_cap=under,
        path=str(path),
    )
    print(f"stop_rule {int(not under)}")
    raise SystemExit(0 if under else 1)


if __name__ == "__main__":
    main()
