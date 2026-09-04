"""Shared cube / field-stack I/O for Plan 03 probes.

Nothing here invents a teacher cube. Missing files print NOT_RUN and
exit 2. Gaussian cube is the interchange format until Octopus writers
are hashed.

A cube file is treated as rho_minus unless --channel is given.
A .npz with keys matching grid_spec.CHANNEL_ORDER is a full state.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from grid_spec import CHANNEL_ORDER

NOT_RUN = "NOT_RUN"


def die_not_run(reason: str, code: int = 2) -> None:
    print(f"{NOT_RUN} {reason}")
    raise SystemExit(code)


def add_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="cube or npz. Omit for an honest NOT_RUN.",
    )
    parser.add_argument(
        "--channel",
        default="rho_minus",
        help="npz key or cube interpretation (default rho_minus)",
    )


def load_cube(path: Path) -> tuple[np.ndarray, np.ndarray, float]:
    """Return (origin, density[nx,ny,nz], voxel_volume).

    Gaussian cube: after two comment lines, natom + origin, then three
    axis lines (n, ax, ay, az). Voxel volume is the scalar triple product.
    """
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(text) < 6:
        die_not_run(f"cube too short: {path}")
    natom_line = text[2].split()
    n_atom = abs(int(natom_line[0]))
    origin = np.array([float(x) for x in natom_line[1:4]], dtype=float)
    axes = []
    ns = []
    for i in range(3):
        parts = text[3 + i].split()
        ns.append(int(parts[0]))
        axes.append(np.array([float(x) for x in parts[1:4]], dtype=float))
    nx, ny, nz = ns
    vol = float(np.dot(axes[0], np.cross(axes[1], axes[2])))
    skip = 6 + n_atom
    vals = np.fromstring(" ".join(text[skip:]), sep=" ", dtype=float)
    need = nx * ny * nz
    if vals.size < need:
        die_not_run(f"cube has {vals.size} values, need {need}: {path}")
    density = vals[:need].reshape(nx, ny, nz)
    return origin, density, abs(vol)


def cell_centres(origin: np.ndarray, shape: tuple[int, int, int], vol: float) -> np.ndarray:
    """Midpoint-rule centres. Cube axes are assumed orthogonal equal spacing."""
    nx, ny, nz = shape
    h = abs(vol) ** (1.0 / 3.0)
    xs = origin[0] + (np.arange(nx) + 0.5) * h
    ys = origin[1] + (np.arange(ny) + 0.5) * h
    zs = origin[2] + (np.arange(nz) + 0.5) * h
    xx, yy, zz = np.meshgrid(xs, ys, zs, indexing="ij")
    return np.stack([xx, yy, zz], axis=-1)


def load_field(path: Path, channel: str = "rho_minus") -> dict:
    """Load one field. Returns origin, density, vol, and optional extra channels."""
    path = Path(path)
    if not path.is_file():
        die_not_run(f"missing file {path}")
    if path.suffix.lower() == ".npz":
        data = np.load(path)
        if channel not in data.files:
            die_not_run(f"npz missing channel {channel}; have {data.files}")
        density = np.asarray(data[channel], dtype=float)
        origin = np.asarray(data["origin"], dtype=float) if "origin" in data.files else np.zeros(3)
        if "voxel_volume" in data.files:
            vol = float(np.asarray(data["voxel_volume"]))
        else:
            die_not_run("npz missing voxel_volume")
        extra = {k: np.asarray(data[k]) for k in data.files}
        extra.update(origin=origin, density=density, vol=abs(vol), path=path)
        return extra
    origin, density, vol = load_cube(path)
    return {
        "origin": origin,
        "density": density,
        "vol": vol,
        "path": path,
        channel: density,
    }


def load_state_stack(path: Path) -> dict:
    """Full state stack (all of CHANNEL_ORDER, 11 channels), or fail closed."""
    path = Path(path)
    if not path.is_file():
        die_not_run(f"missing state stack {path}")
    if path.suffix.lower() != ".npz":
        die_not_run(f"state stack must be npz, got {path}")
    data = np.load(path)
    missing = [c for c in CHANNEL_ORDER if c not in data.files]
    if missing:
        die_not_run(f"state stack missing channels {missing}")
    if "voxel_volume" not in data.files:
        die_not_run("state stack missing voxel_volume")
    return {k: np.asarray(data[k]) for k in data.files}


def print_kv(**kwargs) -> None:
    for k, v in kwargs.items():
        if isinstance(v, float):
            print(f"{k} {v:.16e}")
        else:
            print(f"{k} {v}")
