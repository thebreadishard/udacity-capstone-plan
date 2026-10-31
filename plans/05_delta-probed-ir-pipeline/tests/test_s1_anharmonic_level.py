"""probes/s1_anharmonic_level.py (13 Oct 2026): the optimiser S1 needs — BFGS, then Newton in the internal space. Water smoke showed why the
internal space matters: without grid response the gradient carries a net force, and a pseudo-inverse of the full Hessian turned it into
0.024-bohr translations while the internal gradient stayed. A model potential with a deliberate net force reproduces that case."""
import io
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import s1_anharmonic_level as S  # noqa: E402

X0 = np.array([[0.0, 0.0, 0.2], [0.0, 1.5, -0.9], [0.0, -1.4, -0.8]])
REST = {(0, 1): 1.81, (0, 2): 1.81, (1, 2): 2.86}
NET = np.array([3e-5, -2e-5, 1e-5])                                    # the same force on every atom: a pure translation no step removes


def model(x, with_net=True):
    """Pair springs (internal) plus, optionally, the same constant force on every atom (purely external, like the grid's net force). (E, g, H)."""
    n = len(x)
    e, g, H = 0.0, np.zeros((n, 3)), np.zeros((3 * n, 3 * n))
    for (i, j), r0 in REST.items():
        d = x[i] - x[j]
        r = np.linalg.norm(d)
        u = d / r
        e += 0.5 * 0.4 * (r - r0) ** 2
        g[i] += 0.4 * (r - r0) * u
        g[j] -= 0.4 * (r - r0) * u
        k = 0.4 * (np.outer(u, u) + (r - r0) / r * (np.eye(3) - np.outer(u, u)))
        for a, b, s in ((i, i, 1), (j, j, 1), (i, j, -1), (j, i, -1)):
            H[3 * a:3 * a + 3, 3 * b:3 * b + 3] += s * k
    if with_net:
        g += NET
        Te = S.external_basis(x)
        H += 1e-4 * (Te @ Te.T)                                         # the grid's spurious external stiffness (water: ~1e-4)
    return e, g, H


def test_internal_gradient_drops_rigid_motions():
    x = X0.copy()
    T = S.external_basis(x)
    assert T.shape[1] == 6
    rigid = (T @ np.arange(6.0)).reshape(3, 3)
    assert np.abs(S.internal_gradient(x, rigid)).max() < 1e-12


def test_newton_in_the_internal_space_converges_despite_a_net_force():
    x, _, gmax, steps = S.newton_polish(X0.copy(), model, gtol=1e-9, max_steps=8, log=lambda s: None)
    assert gmax <= 1e-9 and steps <= 6
    for (i, j), r0 in REST.items():
        assert abs(np.linalg.norm(x[i] - x[j]) - r0) < 1e-6
    assert np.abs(x.mean(axis=0) - X0.mean(axis=0)).max() < 1e-3         # no translation sprint


def test_bfgs_then_newton_reaches_the_s1_tolerance():
    def eg(x):
        e, g, _ = model(x)
        return e, g
    x, _, _, _ = S.optimise(["O", "H", "H"], X0.copy(), eg, log=lambda s: None)
    _, gmax, _ = S.newton_polish(x, model, log=lambda s: None)[1:]
    assert gmax <= S.GTOL


def test_bfgs_writes_one_line_per_evaluation():
    lines = []

    def eg(x):
        e, g, _ = model(x)
        return e, g
    _, _, _, evaluations = S.optimise(["O", "H", "H"], X0.copy(), eg, log=lines.append)
    per_evaluation = [s for s in lines if s.startswith("  BFGS evaluation ")]
    assert len(per_evaluation) == evaluations and per_evaluation[-1].startswith(f"  BFGS evaluation {evaluations}:")


@pytest.mark.parametrize("grid, threads, diis", [("75", 2, 10), ("75,abc", 2, 10), ("0,302", 2, 10), ("75,302", 0, 10), ("75,302", 2, 0)])
def test_a_setting_that_cannot_run_is_refused_before_any_computation(grid, threads, diis):
    with pytest.raises(ValueError):
        S.PyscfSetting("6-31g*", grid, threads, io.StringIO(), diis_cycles=diis)


def test_the_setting_names_its_functional_b3lyp_by_default():
    assert S.PyscfSetting("6-31g*", "75,302", 2, io.StringIO()).xc == "b3lyp"
    assert S.PyscfSetting("6-31g*", "75,302", 2, io.StringIO(), xc="wb97x").xc == "wb97x"
    with pytest.raises(ValueError, match="no functional"):
        S.PyscfSetting("6-31g*", "75,302", 2, io.StringIO(), xc=" ")


def test_a_valid_setting_gives_its_grid_as_integers():
    assert S.PyscfSetting("6-31g*", "75,302", 2, io.StringIO()).atom_grid == (75, 302)
