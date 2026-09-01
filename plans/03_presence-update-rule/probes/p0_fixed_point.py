#!/usr/bin/env python3
"""Q3 / P0. Relative N drift after T0 field-free steps of the linear stencil.

Needs a 12-channel state npz. Later, --rule learned.npz may be added;
until then only the untrained linear stencil runs.

  python p0_fixed_point.py state.npz
  python p0_fixed_point.py   # NOT_RUN
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cube_io import die_not_run, load_state_stack, print_kv  # noqa: E402
from grid_spec import T0_STEPS  # noqa: E402
from linear_stencil import electron_count, spacing_from_volume, step  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", nargs="?", default=None)
    p.add_argument("--steps", type=int, default=T0_STEPS)
    p.add_argument(
        "--rule",
        default="linear",
        help="linear (default). learned is NOT_RUN until a hashed rule exists",
    )
    args = p.parse_args()
    if args.path is None:
        die_not_run("no state npz; P0 waits on a field-free teacher frame")
    if args.rule != "linear":
        die_not_run(f"rule {args.rule} not hashed; only linear stencil is implemented")
    state = load_state_stack(Path(args.path))
    vol = float(np.asarray(state["voxel_volume"]))
    h = spacing_from_volume(vol)
    n0 = electron_count(state["rho_minus"], vol)
    current = state
    for _ in range(int(args.steps)):
        current = step(current, h=h)
    n_t = electron_count(current["rho_minus"], vol)
    if n0 == 0.0:
        rel = float("inf")
    else:
        rel = abs(n_t - n0) / abs(n0)
    print_kv(
        rule="linear",
        steps=int(args.steps),
        n0=n0,
        n_t=n_t,
        p0_rel=rel,
        h=h,
        gate_h2=1.0e-3,
        path=str(Path(args.path)),
    )
    print(f"p0_pass_h2 {int(rel < 1.0e-3)}")


if __name__ == "__main__":
    main()
