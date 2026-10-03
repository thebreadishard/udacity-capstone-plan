"""e8_symmetry.reconstruct_apt (3 Oct 2026): water's full finite-difference APT (B3LYP, probes/results_m1/water_dipole_fd_2026-10-02) is reproduced
from the two representative atoms' rows through the C2v group; the self-check is at the FD route's own symmetry error."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_symmetry as SYM  # noqa: E402

W = PLAN / "probes" / "results_m1" / "water_dipole_fd_2026-10-02"


@pytest.mark.skipif(not (W / "dipole_b3lyp_fd.npz").exists(), reason="water APT not on this machine")
def test_water_apt_from_representatives():
    g = json.load(open(W / "geometry.json"))
    P = np.load(W / "dipole_b3lyp_fd.npz")["apt"]                         # (3, 9): P[t, 3k + x]
    ops = SYM.point_group_ops(g["symbols"], np.asarray(g["coords_bohr"], float))
    assert len(ops) == 4                                                    # C2v
    ks, reps = SYM.unique_displacements(ops, 3)
    assert reps == [0, 1]
    D = P.reshape(3, 3, 3).transpose(1, 2, 0)                               # (atom, x, t)
    P_rec, spread = SYM.reconstruct_apt({i: D[i] for i in reps}, ops, 3)
    assert P_rec.shape == P.shape
    assert np.abs(P_rec - P).max() < 2e-5                                   # the FD route holds the symmetry to ~3e-6 itself
    assert spread < 2e-5 and SYM.apt_self_check(P_rec, ops, 3) < 2e-5


def test_reconstruct_apt_refuses_an_unreached_atom():
    ops = [(np.eye(3), [0, 1, 2])]                                          # identity only: atom 2 unreachable from {0, 1}
    with pytest.raises(ValueError):
        SYM.reconstruct_apt({0: np.eye(3), 1: np.eye(3)}, ops, 3)
