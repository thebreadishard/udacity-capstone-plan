"""Two stored geometries of one molecule brought into one frame: the rotation, the distance left, and the refusal when they are
not the same molecule in the same atom order. For a record that was computed at another minimum than the one it is compared at
(a force field's modes against a pipeline result's bands).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Two minima of one molecule by two routes lie well inside this: S2's GFN2-xTB minimum of benzene is 0.030 bohr rms from the
# pipeline's B3LYP one, two B3LYP minima of benzonitrile 0.0006. Past it the modes are no longer the same displacements.
FRAME_TOLERANCE_BOHR = 0.05


@dataclass(frozen=True)
class Frame:
    """How a moving geometry lies on a fixed one: the rotation that brings it there and the rms distance left, in bohr."""
    rotation: np.ndarray
    rms_bohr: float

    def modes(self, q: np.ndarray) -> np.ndarray:
        """Cartesian modes of the moving geometry (3N × M, atom after atom) in the fixed geometry's frame."""
        n = q.shape[0] // 3
        return np.einsum("nim,ij->njm", q.reshape(n, 3, -1), self.rotation).reshape(3 * n, -1)


def kabsch(moving: np.ndarray, fixed: np.ndarray) -> tuple[np.ndarray, float]:
    """The rotation R with (moving − centroid) @ R closest to (fixed − centroid), and the rms distance left."""
    a, b = moving - moving.mean(axis=0), fixed - fixed.mean(axis=0)
    u, _, vt = np.linalg.svd(a.T @ b)
    r = u @ np.diag([1.0, 1.0, np.sign(np.linalg.det(u @ vt))]) @ vt
    return r, float(np.sqrt(((a @ r - b) ** 2).sum(axis=1).mean()))


def frame_onto(moving: tuple[list[str], np.ndarray], fixed: tuple[list[str], np.ndarray], what: str,
               tolerance: float = FRAME_TOLERANCE_BOHR) -> Frame:
    """The frame of `moving` (symbols, coordinates in bohr) on `fixed`; `what` names the moving record in the refusal.

    Refused: other atoms or another atom order (no permutation is tried: a record in another order is another record), and a
    distance past `tolerance` after rotation.
    """
    (symbols_m, coords_m), (symbols_f, coords_f) = moving, fixed
    if [s.capitalize() for s in symbols_m] != [s.capitalize() for s in symbols_f]:
        raise ValueError(f"{what}: its atoms {''.join(symbols_m)} are not the result's {''.join(symbols_f)} in the result's order")
    rotation, left = kabsch(np.asarray(coords_m, float).reshape(-1, 3), np.asarray(coords_f, float).reshape(-1, 3))
    if left > tolerance:
        raise ValueError(f"{what}: its geometry is {left:.3f} bohr rms from the result's after rotation (line {tolerance} bohr): "
                         "another geometry, so its modes are not compared")
    return Frame(rotation, left)
