"""probes/methyl_rotor_grid.py's reuse of a coarser τ grid (TASKS 176's 48-point grid on the 24-point one), on synthetic grids: every old
point lands on the new point at the same Δτ and q, and a grid that does not combine is refused."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
G = pytest.importorskip("methyl_rotor_grid")
LEVEL = ["b3lyp", "6-31g*", "75,302", 1e-11]


def old_grid(n_tau: int, n_q: int) -> tuple[dict, dict[str, float]]:
    points = G.grid_points(n_tau, n_q)
    return {"n_tau": n_tau, "n_q": n_q, "level": LEVEL, "points": points}, {str(p["index"]): -1.0 - p["index"] for p in points}


def test_every_old_point_lands_on_the_same_tau_and_q():
    meta, E = old_grid(4, 3)
    new = G.grid_points(8, 3)
    got = G.reused_energies(meta, E, new, 8, 3, LEVEL)
    assert len(got) == len(meta["points"])
    by_index = {p["index"]: p for p in new}
    for p in meta["points"]:
        q = next(n for n in new if n["dtau_deg"] == p["dtau_deg"] and n["i20"] == p["i20"] and n["i21"] == p["i21"])
        assert got[str(q["index"])] == E[str(p["index"])] and by_index[q["index"]]["k_tau"] == 2 * p["k_tau"]


@pytest.mark.parametrize("n_tau,n_q,level", [(6, 3, LEVEL), (4, 3, LEVEL), (8, 5, LEVEL), (8, 3, ["pbe", "6-31g*", "75,302", 1e-11])])
def test_a_grid_that_does_not_combine_is_refused(n_tau, n_q, level):
    meta, E = old_grid(4, 3)
    with pytest.raises(SystemExit):
        G.reused_energies(meta, E, G.grid_points(n_tau, n_q), n_tau, n_q, level)


def test_a_missing_old_energy_is_refused():
    meta, E = old_grid(4, 3)
    del E["5"]
    with pytest.raises(SystemExit):
        G.reused_energies(meta, E, G.grid_points(8, 3), 8, 3, LEVEL)


def test_reuse_and_smoke_and_the_same_directory_are_refused(tmp_path):
    with pytest.raises(SystemExit):
        G.parse_args([str(tmp_path / "g48"), "--reuse", str(tmp_path / "g24"), "--smoke"])
    with pytest.raises(SystemExit):
        G.parse_args([str(tmp_path / "g"), "--reuse", str(tmp_path / "g")])
