"""probes/qc_common.py: project_tr reproduces its output from before `rigid_basis` was split out (tests/data/qc_common_project_tr_golden.npz,
pinned by tests/qc_common_golden.py), and rigid_basis spans exactly the mass-weighted rigid motions."""
import sys
from pathlib import Path

import numpy as np
import pytest

from qc_common_golden import GOLDEN, cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
from qc_common import project_tr, rigid_basis


@pytest.mark.parametrize("name", ["water", "ring", "random"])
def test_project_tr_is_unchanged(name):
    m, x, H = cases()[name]
    Hp, Hmw = project_tr(H, m, x)
    with np.load(GOLDEN) as z:
        np.testing.assert_allclose(Hp, z[f"{name}_Hp"], rtol=1e-12, atol=1e-14)
        np.testing.assert_allclose(Hmw, z[f"{name}_Hmw"], rtol=1e-12, atol=1e-14)


@pytest.mark.parametrize("name", ["water", "ring", "random"])
def test_rigid_basis_is_orthonormal_and_annihilated_by_a_projected_hessian(name):
    m, x, H = cases()[name]
    q = rigid_basis(m, x)
    np.testing.assert_allclose(q.T @ q, np.eye(6), atol=1e-12)
    Hp, _ = project_tr(H, m, x)
    sm = np.sqrt(np.repeat(m, 3))
    np.testing.assert_allclose((Hp / np.outer(sm, sm)) @ q, 0.0, atol=1e-10)
