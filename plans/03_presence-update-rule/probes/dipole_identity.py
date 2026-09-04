#!/usr/bin/env python3
"""Q2. Print residual of mu_teacher + int r rho_minus dV.

Sign convention: electron density rho_minus > 0, so the electronic
dipole piece is -int r rho_minus dV in atomic units if nuclei are
handled separately. This script prints the *grid* moment
M = int r rho_minus dV
and, if --mu mx my mz is given, the vector residual
R = mu + M
(i.e. teacher dipole plus the electronic grid moment).

  python dipole_identity.py rho.cube --mu 0 0 0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cube_io import (  # noqa: E402
    add_input_args,
    cell_centres,
    die_not_run,
    load_field,
    print_kv,
)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    add_input_args(p)
    p.add_argument(
        "--mu",
        nargs=3,
        type=float,
        default=None,
        metavar=("MX", "MY", "MZ"),
        help="teacher dipole in au",
    )
    args = p.parse_args()
    if args.path is None:
        die_not_run("no cube/npz; Q2 waits on a teacher frame 0")
    field = load_field(Path(args.path), args.channel)
    rho = field["density"]
    vol = float(field["vol"])
    origin = np.asarray(field["origin"], dtype=float)
    centres = cell_centres(origin, rho.shape, vol)
    moment = np.array(
        [
            float(np.sum(centres[..., 0] * rho) * vol),
            float(np.sum(centres[..., 1] * rho) * vol),
            float(np.sum(centres[..., 2] * rho) * vol),
        ]
    )
    print_kv(
        M_x=moment[0],
        M_y=moment[1],
        M_z=moment[2],
        M_norm=float(np.linalg.norm(moment)),
        path=str(field["path"]),
    )
    if args.mu is None:
        print("residual NOT_RUN --mu omitted")
        return
    mu = np.array(args.mu, dtype=float)
    residual = mu + moment
    print_kv(
        mu_x=mu[0],
        mu_y=mu[1],
        mu_z=mu[2],
        R_x=residual[0],
        R_y=residual[1],
        R_z=residual[2],
        R_norm=float(np.linalg.norm(residual)),
    )


if __name__ == "__main__":
    main()
