"""Frozen linear P4 / P0 baseline.

Continuity on rho_minus and j, discrete Maxwell on E and B.
No learned coefficients. Constitutive closure: j is an independent
channel (no Ohm / no Poisson). c = 137.035999 (au).

Boundaries match the frozen box (molecule + >=6 a0 vacuum + rim), so the
default is NON-periodic: differences are taken against zero outside the
grid, and charge may leave through the rim. A periodic variant is kept
behind a flag for a periodic teacher deck only.

Maxwell is leapfrogged (B uses the updated E) and sub-cycled so that
c*ds/h stays under the explicit 3-D limit 1/sqrt(3). The frozen teacher
step is c*dt/h = 34.3, i.e. 59x past that limit; a single forward-Euler
step at that ratio reaches NaN inside the 200-step P2 horizon.

This is the untrained stencil. Changing it after Q0 is a §4 note.
"""

from __future__ import annotations

import math

import numpy as np

from grid_spec import (
    CHANNEL_ORDER,
    DT_TEACHER_AU,
    MAXWELL_COURANT_SAFETY,
    PERIODIC_BOX,
)

C_AU = 137.035999177

# Explicit 3-D stencil stability limit for c*ds/h.
COURANT_LIMIT_3D = 1.0 / math.sqrt(3.0)


def _shift(f: np.ndarray, axis: int, offset: int, periodic: bool) -> np.ndarray:
    """f shifted by +offset cells along axis; zero outside a finite box."""
    if periodic:
        return np.roll(f, -offset, axis)
    out = np.zeros_like(f)
    src = [slice(None)] * f.ndim
    dst = [slice(None)] * f.ndim
    if offset > 0:
        src[axis] = slice(offset, None)
        dst[axis] = slice(None, -offset)
    else:
        src[axis] = slice(None, offset)
        dst[axis] = slice(-offset, None)
    out[tuple(dst)] = f[tuple(src)]
    return out


def _d(f: np.ndarray, axis: int, h: float, periodic: bool) -> np.ndarray:
    return (_shift(f, axis, 1, periodic) - _shift(f, axis, -1, periodic)) / (2.0 * h)


def _div(jx, jy, jz, h: float, periodic: bool) -> np.ndarray:
    return _d(jx, 0, h, periodic) + _d(jy, 1, h, periodic) + _d(jz, 2, h, periodic)


def _curl(vx, vy, vz, h: float, periodic: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cx = _d(vz, 1, h, periodic) - _d(vy, 2, h, periodic)
    cy = _d(vx, 2, h, periodic) - _d(vz, 0, h, periodic)
    cz = _d(vy, 0, h, periodic) - _d(vx, 1, h, periodic)
    return cx, cy, cz


def courant_number(h: float, dt: float = DT_TEACHER_AU) -> float:
    return C_AU * dt / h


def maxwell_substeps(h: float, dt: float = DT_TEACHER_AU) -> int:
    """Maxwell sub-steps per teacher step needed to satisfy the CFL limit."""
    target = MAXWELL_COURANT_SAFETY * COURANT_LIMIT_3D
    return max(1, int(math.ceil(courant_number(h, dt) / target)))


def spacing_from_volume(vol: float) -> float:
    return abs(float(vol)) ** (1.0 / 3.0)


def step(
    state: dict,
    dt: float = DT_TEACHER_AU,
    h: float | None = None,
    periodic: bool = PERIODIC_BOX,
) -> dict:
    """One linear teacher-sized step. Returns a new dict of arrays."""
    if h is None:
        h = spacing_from_volume(float(np.asarray(state["voxel_volume"])))
    rho_p = np.array(state["rho_plus"], dtype=float, copy=True)
    rho_m = np.array(state["rho_minus"], dtype=float, copy=True)
    jx = np.array(state["j_x"], dtype=float, copy=True)
    jy = np.array(state["j_y"], dtype=float, copy=True)
    jz = np.array(state["j_z"], dtype=float, copy=True)
    ex = np.array(state["E_x"], dtype=float, copy=True)
    ey = np.array(state["E_y"], dtype=float, copy=True)
    ez = np.array(state["E_z"], dtype=float, copy=True)
    bx = np.array(state["B_x"], dtype=float, copy=True)
    by = np.array(state["B_y"], dtype=float, copy=True)
    bz = np.array(state["B_z"], dtype=float, copy=True)

    # Continuity: d rho_minus / dt = - div j  (rho_minus is electron density).
    # On a finite box this does not conserve N by construction: what leaves
    # through the rim is a real drift and P0 must be able to see it.
    rho_m = rho_m - dt * _div(jx, jy, jz, h, periodic)
    # j held (no constitutive update). Point nuclei: rho_plus frozen.
    n_sub = maxwell_substeps(h, dt)
    ds = dt / n_sub
    four_pi = 4.0 * np.pi
    for _ in range(n_sub):
        # Maxwell in au: dE/dt = c curl B - 4 pi j ; dB/dt = -c curl E.
        # Leapfrog: B uses the updated E, which is what makes it stable.
        cbx, cby, cbz = _curl(bx, by, bz, h, periodic)
        ex = ex + ds * (C_AU * cbx - four_pi * jx)
        ey = ey + ds * (C_AU * cby - four_pi * jy)
        ez = ez + ds * (C_AU * cbz - four_pi * jz)
        cex, cey, cez = _curl(ex, ey, ez, h, periodic)
        bx = bx - ds * C_AU * cex
        by = by - ds * C_AU * cey
        bz = bz - ds * C_AU * cez

    out = dict(state)
    out.update(
        {
            "rho_plus": rho_p,
            "rho_minus": rho_m,
            "j_x": jx,
            "j_y": jy,
            "j_z": jz,
            "E_x": ex,
            "E_y": ey,
            "E_z": ez,
            "B_x": bx,
            "B_y": by,
            "B_z": bz,
        }
    )
    return out


def electron_count(rho_minus: np.ndarray, vol: float) -> float:
    return float(np.sum(rho_minus) * vol)


def empty_state(shape: tuple[int, int, int], vol: float) -> dict:
    z = np.zeros(shape, dtype=float)
    st = {name: z.copy() for name in CHANNEL_ORDER}
    st["voxel_volume"] = np.array(vol)
    st["origin"] = np.zeros(3)
    return st
