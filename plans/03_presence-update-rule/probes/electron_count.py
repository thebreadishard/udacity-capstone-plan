#!/usr/bin/env python3
"""Q1. Print int rho_minus dV on frame 0 vs nominal N.

Exit 2 and NOT_RUN if no cube/npz is given.
A residual that is not printed here is not a result.

  python electron_count.py path/to/rho.cube --n-electrons 2
  python electron_count.py path/to/state.npz --n-electrons 2 --channel rho_minus
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cube_io import add_input_args, die_not_run, load_field, print_kv  # noqa: E402
from linear_stencil import electron_count  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    add_input_args(p)
    p.add_argument("--n-electrons", type=float, required=False, default=None)
    args = p.parse_args()
    if args.path is None:
        die_not_run("no cube/npz; Q1 waits on a teacher frame 0")
    field = load_field(Path(args.path), args.channel)
    n_grid = electron_count(field["density"], field["vol"])
    print_kv(
        n_grid=n_grid,
        voxel_volume=float(field["vol"]),
        shape="x".join(str(s) for s in field["density"].shape),
        path=str(field["path"]),
    )
    if args.n_electrons is None:
        print("residual NOT_RUN --n-electrons omitted")
        return
    residual = n_grid - float(args.n_electrons)
    rel = residual / float(args.n_electrons) if args.n_electrons else float("nan")
    print_kv(n_nominal=float(args.n_electrons), residual=residual, residual_rel=rel)


if __name__ == "__main__":
    main()
