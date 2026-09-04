#!/usr/bin/env python3
"""Print max |B| on a state stack. Drop-B is forbidden until this is ~0.

  python b_numerically_zero.py state.npz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cube_io import die_not_run, load_state_stack, print_kv  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", nargs="?", default=None)
    args = p.parse_args()
    if args.path is None:
        die_not_run("no state npz; B cannot be dropped on a missing field")
    state = load_state_stack(Path(args.path))
    b = np.stack([state["B_x"], state["B_y"], state["B_z"]], axis=0)
    max_abs = float(np.max(np.abs(b)))
    rms = float(np.sqrt(np.mean(b * b)))
    print_kv(max_abs_B=max_abs, rms_B=rms, path=str(Path(args.path)))
    print("drop_B_forbidden 1")


if __name__ == "__main__":
    main()
