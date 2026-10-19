"""probes/dfmp2_swap_check.py on synthetic Hessians before any DF-MP2 number (CLAUDE.md, 'Evidence'): an identical step shifts nothing, a step
difference of 1e-6 a.u. stays far inside the line while one of 1e-2 a.u. crosses it, the verdict's edges sit where the registration puts them, a rotated corpus
geometry is the same molecule while a swapped atom order is not, and DF rows at another geometry or step are refused."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
S = pytest.importorskip("dfmp2_swap_check")

X0 = np.array([[0.0, 0.0, 0.0], [0.0, 1.43, 1.11], [0.0, -1.43, 1.11]])     # water-like, bohr
MASSES = np.array([15.995, 1.008, 1.008])


def base_hessian(seed=0):
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(9, 9))
    return 0.05 * (a @ a.T) + 0.3 * np.eye(9)


def test_an_identical_step_shifts_nothing():
    M, D = base_hessian(), 0.01 * base_hessian(1)
    w_conv, w_df = S.swap_shift(M, D, D.copy(), MASSES, X0)
    assert np.allclose(w_conv, w_df, atol=1e-9)


def test_a_small_step_difference_shifts_the_frequencies_by_little_and_a_large_one_by_more():
    M, D = base_hessian(), 0.01 * base_hessian(1)
    small = S.swap_shift(M, D, D + 1e-6 * base_hessian(2), MASSES, X0)
    large = S.swap_shift(M, D, D + 1e-2 * base_hessian(2), MASSES, X0)
    assert np.abs(small[1] - small[0]).max() < 0.5 < np.abs(large[1] - large[0]).max()


@pytest.mark.parametrize(("shift", "word"), [(0.0, "adopt"), (0.5, "adopt"), (0.5001, "noted"), (2.0, "noted"), (2.0001, "refused")])
def test_the_verdict_edges(shift, word):
    assert S.verdict(shift) == word


def test_a_rotated_geometry_is_the_same_molecule_and_a_swapped_order_is_not():
    c, s = np.cos(0.7), np.sin(0.7)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    S.check_same_molecule(X0, X0 @ R.T + 3.0)
    with pytest.raises(SystemExit, match="same atom order"):
        S.check_same_molecule(X0, X0[[1, 0, 2]])


def rows_file(path, coords, step=0.005, basis="cc-pvdz"):
    np.savez(path, ks=np.array([0]), reps=np.array([0]), step=step, basis=basis, frozen=1, cart=False, coords_bohr=coords, row_00=np.zeros(9))
    return path


def test_rows_at_another_geometry_or_step_are_refused(tmp_path):
    good = {k: rows_file(tmp_path / f"{k}.npz", X0, basis="cc-pvtz" if k.endswith("tz") else "cc-pvdz")
            for k in ("conv_dz", "conv_tz", "df_dz", "df_tz")}
    S.load_rows(good)
    moved = dict(good, df_tz=rows_file(tmp_path / "moved.npz", X0 + 1e-6, basis="cc-pvtz"))
    with pytest.raises(SystemExit, match="another geometry"):
        S.load_rows(moved)
    stepped = dict(good, df_dz=rows_file(tmp_path / "stepped.npz", X0, step=0.01))
    with pytest.raises(SystemExit, match="step"):
        S.load_rows(stepped)
