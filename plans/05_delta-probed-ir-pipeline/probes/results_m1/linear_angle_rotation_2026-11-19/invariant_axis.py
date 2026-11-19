"""A rotation-invariant reference axis for geomeTRIC's LinearAngle (TASKS 287 probe; monkeypatch only)."""
import numpy as np


def invariant_reset(self, xyz):
    """Set e0 to the principal axis of the off-axis atoms' perpendicular second moment (weights 1/r² from atom b), sign by its third moment."""
    xyz = xyz.reshape(-1, 3)
    ev = xyz[self.c] - xyz[self.a]
    ev = ev / np.linalg.norm(ev)
    T = np.zeros((3, 3))
    held = []
    for j in range(len(xyz)):
        r = xyz[j] - xyz[self.b]
        p = r - np.dot(r, ev) * ev
        if np.linalg.norm(p) < 1e-3:
            continue
        w = 1.0 / np.dot(r, r)
        T += w * np.outer(p, p)
        held.append((w, p))
    _, vecs = np.linalg.eigh(T)
    e0 = vecs[:, -1]
    if sum(w * np.dot(p, e0) ** 3 for w, p in held) < 0:
        e0 = -e0
    self.e0 = e0
    self.stored_dot2 = 0.0
