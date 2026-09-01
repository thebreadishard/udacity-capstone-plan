"""Frozen linear P4 / P0 baseline.

Continuity on rho_minus and j, discrete Maxwell on E and B.
No learned coefficients. Constitutive closure: j is an independent
channel (no Ohm / no Poisson). c = 137.035999 (au).

This is the untrained stencil. Changing it after Q0 is a §4 note.
"""

from __future__ import annotations

import numpy as np

from grid_spec import CHANNEL_ORDER, DT_TEACHER_AU

C_AU = 137.035999177


def _div(jx, jy, jz, h: float) -> np.ndarray:
    """Central differences, periodic. Conservative on a torus."""
    dx = (np.roll(jx, -1, 0) - np.roll(jx, 1, 0)) / (2.0 * h)
    dy = (np.roll(jy, -1, 1) - np.roll(jy, 1, 1)) / (2.0 * h)
    dz = (np.roll(jz, -1, 2) - np.roll(jz, 1, 2)) / (2.0 * h)
    return dx + dy + dz


def _curl(vx, vy, vz, h: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cx = (np.roll(vz, -1, 1) - np.roll(vz, 1, 1)) / (2.0 * h) - (
        np.roll(vy, -1, 2) - np.roll(vy, 1, 2)
    ) / (2.0 * h)
    cy = (np.roll(vx, -1, 2) - np.roll(vx, 1, 2)) / (2.0 * h) - (
        np.roll(vz, -1, 0) - np.roll(vz, 1, 0)
    ) / (2.0 * h)
    cz = (np.roll(vy, -1, 0) - np.roll(vy, 1, 0)) / (2.0 * h) - (
        np.roll(vx, -1, 1) - np.roll(vx, 1, 1)
    ) / (2.0 * h)
    return cx, cy, cz


def spacing_from_volume(vol: float) -> float:
    return abs(float(vol)) ** (1.0 / 3.0)


def step(state: dict, dt: float = DT_TEACHER_AU, h: float | None = None) -> dict:
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
    rho_m = rho_m - dt * _div(jx, jy, jz, h)
    # j held (no constitutive update). Point nuclei: rho_plus frozen.
    curl_b = _curl(bx, by, bz, h)
    curl_e = _curl(ex, ey, ez, h)
    # Maxwell in au: dE/dt = c curl B - 4 pi j ; dB/dt = -c curl E
    four_pi = 4.0 * np.pi
    ex = ex + dt * (C_AU * curl_b[0] - four_pi * jx)
    ey = ey + dt * (C_AU * curl_b[1] - four_pi * jy)
    ez = ez + dt * (C_AU * curl_b[2] - four_pi * jz)
    bx = bx - dt * C_AU * curl_e[0]
    by = by - dt * C_AU * curl_e[1]
    bz = bz - dt * C_AU * curl_e[2]

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
