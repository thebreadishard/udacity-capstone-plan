"""src/dpir/symmetry.py (TASKS 204): the promoted point_group_ops reproduces the probe's operations on six point groups
(tests/data/point_group_ops_golden.json, written by tests/symmetry_golden.py with probes/e8_symmetry.py before the move); the operations
form a group and leave the molecule in place; degenerate_pairs reads degeneracy from the group: benzene ten pairs, also when noise splits
them beyond the old 0.5 cm⁻¹ gap; ideal tetracene none however close two modes lie (the defect of 12 Nov: the gap rule paired them);
the pairs do not depend on the atom order, orientation or position; noise that mixes a pair with a near mode of another representation
keeps the pairs; a geometry too far from its symmetry is refused rather than losing pairs; mixed or non-orthonormal modes are refused."""
import json

import numpy as np
import pytest

from dpir.qff import DEGENERACY_CM, HARTREE_CM, atomic_masses_me, harmonic
from dpir.symmetry import degenerate_pairs, point_group_ops, rep_matrices, symmetrize
from symmetry_golden import GOLDEN, molecules


@pytest.fixture(scope="module")
def golden():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["benzene", "tetracene", "water", "triazine", "water_cs", "c1"])
def test_reproduces_the_probe_operations(golden, name):
    symbols, x = molecules()[name]
    ours = sorted(({"perm": list(p), "improper": bool(np.linalg.det(R) < 0), "R": R} for R, p in point_group_ops(symbols, x)),
                  key=lambda o: (o["perm"], o["improper"]))
    assert [(o["perm"], o["improper"]) for o in ours] == [(o["perm"], o["improper"]) for o in golden[name]]
    for o, g in zip(ours, golden[name], strict=True):
        np.testing.assert_allclose(o["R"], np.array(g["R"]), atol=1e-12)


@pytest.mark.parametrize("name", ["benzene", "triazine", "water_cs"])
def test_operations_form_a_group_and_keep_the_molecule(name):
    symbols, x = molecules()[name]
    ops = point_group_ops(symbols, x)
    keys = {tuple(p) for _R, p in ops}
    xc = x - x.mean(0)
    for R, p in ops:
        np.testing.assert_allclose(xc @ R.T, xc[p], atol=0.02)
        for _R2, p2 in ops:
            assert tuple(p[k] for k in p2) in keys


def _symmetric_hessian(symbols, x, seed=1, noise=0.0):
    x = symmetrize(symbols, x)
    D = rep_matrices(point_group_ops(symbols, x, tol=1e-6), len(symbols))
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((3 * len(symbols), 3 * len(symbols)))
    H = sum(d @ (A @ A.T / A.shape[0] * 0.5) @ d.T for d in D) / len(D)
    if noise:
        E = rng.standard_normal(H.shape)
        H = H + noise * np.abs(H).max() * (E + E.T) / 2
    return x, H


def test_benzene_has_ten_pairs_also_when_noise_splits_and_mixes_them():
    """Ten pairs at every seed, also at a noise that splits pairs beyond the old 0.5 cm⁻¹ gap and mixes them with near modes of other
    representations (the review of 12 Nov: the orbit test raised at seeds 2, 4 and 7 of 8 at 5e-4)."""
    symbols, x = molecules()["benzene"]
    split = []
    for seed in range(1, 9):
        for noise in (0.0, 2e-4, 5e-4):
            xs, H = _symmetric_hessian(symbols, x, seed=seed, noise=noise)
            h = harmonic(H, symbols, xs)
            pairs = degenerate_pairs(symbols, xs, h.q, h.omega_cm)
            assert len(pairs) == 10, (seed, noise)
            split.append(max(h.omega_cm[b] - h.omega_cm[a] for a, b in pairs))
    assert max(split) > 0.5, "no case split a pair beyond the old gap"


def test_triazine_keeps_its_pairs_under_noise():
    symbols, x = molecules()["triazine"]
    counts = set()
    for seed in range(1, 5):
        for noise in (0.0, 5e-4):
            xs, H = _symmetric_hessian(symbols, x, seed=seed, noise=noise)
            h = harmonic(H, symbols, xs)
            counts.add(len(degenerate_pairs(symbols, xs, h.q, h.omega_cm)))
    assert len(counts) == 1 and counts.pop() > 0


def _with_frequency(symbols, x, H, k, omega_cm_new):
    """H with mode k's frequency set to omega_cm_new and every mode kept (a symmetric H stays symmetric: the eigenvectors are untouched)."""
    h = harmonic(H, symbols, x)
    sqrt_m = np.repeat(np.sqrt(atomic_masses_me(symbols)), 3)
    lam = (h.omega_cm / HARTREE_CM) ** 2
    lam[k] = (omega_cm_new / HARTREE_CM) ** 2
    K = h.q @ np.diag(lam) @ h.q.T
    return sqrt_m[:, None] * K * sqrt_m[None, :]


def test_negative_control_a_mode_beside_a_pair_is_not_averaged_into_it():
    """The defect of 12 Nov in its symmetric-top form (coronene's G labels): a non-degenerate mode 0.2 cm⁻¹ from a pair. The old builder's
    rule (consecutive modes within 0.5 cm⁻¹) chains it to the pair; the group keeps the ten pairs and leaves it alone, also when noise
    mixes it with the pair."""
    symbols, x = molecules()["benzene"]
    xs, H = _symmetric_hessian(symbols, x)
    h = harmonic(H, symbols, xs)
    pairs = degenerate_pairs(symbols, xs, h.q, h.omega_cm)
    single = sorted(set(range(len(h.omega_cm))) - {i for p in pairs for i in p})
    k, (a, _b) = single[len(single) // 2], pairs[len(pairs) // 2]
    H2 = _with_frequency(symbols, xs, H, k, h.omega_cm[a] + 0.2)
    rng = np.random.default_rng(11)
    E = rng.standard_normal(H2.shape)
    for noise in (0.0, 1e-5):
        h2 = harmonic(H2 + noise * np.abs(H2).max() * (E + E.T) / 2, symbols, xs)
        w = h2.omega_cm
        gap_rule = [(i, i + 1) for i in range(len(w) - 1) if abs(w[i] - w[i + 1]) < DEGENERACY_CM]
        new = degenerate_pairs(symbols, xs, h2.q, w)
        assert len(new) == 10, noise
        near = int(np.argmin(np.abs(w - (h.omega_cm[a] + 0.2))))
        assert all(near not in p for p in new), noise
        assert any(near in p for p in gap_rule), "the old rule must pair the single mode, or the control shows nothing"


def test_negative_control_tetracene_has_no_pair_although_the_gap_rule_finds_some():
    symbols, x = molecules()["tetracene"]
    xs, H = _symmetric_hessian(symbols, x)
    h = harmonic(H, symbols, xs)
    k = len(h.omega_cm) // 2
    H2 = _with_frequency(symbols, xs, H, k, h.omega_cm[k + 1] + 0.2)
    h2 = harmonic(H2, symbols, xs)
    w = h2.omega_cm
    assert any(abs(w[i] - w[i + 1]) < DEGENERACY_CM for i in range(len(w) - 1)), "the old rule must find a pair here"
    assert degenerate_pairs(symbols, xs, h2.q, w) == []


def test_pairs_do_not_depend_on_atom_order_orientation_or_position():
    symbols, x = molecules()["triazine"]
    xs, H = _symmetric_hessian(symbols, x)
    h = harmonic(H, symbols, xs)
    base = degenerate_pairs(symbols, xs, h.q, h.omega_cm)
    rng = np.random.default_rng(5)
    perm = rng.permutation(len(symbols))
    Q, _ = np.linalg.qr(rng.standard_normal((3, 3)))
    idx = np.ravel([[3 * i, 3 * i + 1, 3 * i + 2] for i in perm])
    q_rot = np.kron(np.eye(len(symbols)), Q) @ h.q[idx]
    moved = degenerate_pairs([symbols[i] for i in perm], xs[perm] @ Q.T + np.array([3.0, -1.0, 2.5]), q_rot, h.omega_cm)
    assert moved == base and len(base) > 0


def test_a_geometry_too_far_from_its_symmetry_never_loses_pairs_silently():
    """Benzene with 3e-3 bohr geometry noise: the operations at 0.02 bohr can be a subset of D6h (the review found 0 pairs returned
    without an error). Every outcome is now the ten pairs or a refusal."""
    symbols, x = molecules()["benzene"]
    xs, H = _symmetric_hessian(symbols, x)
    h = harmonic(H, symbols, xs)
    for seed in range(10):
        noisy = xs + np.random.default_rng(seed).normal(scale=3e-3, size=xs.shape)
        try:
            assert len(degenerate_pairs(symbols, noisy, h.q, h.omega_cm)) == 10, seed
        except ValueError as exc:
            assert "group" in str(exc) or "invariant" in str(exc) or "carried" in str(exc), exc


def test_mixed_modes_and_bad_columns_are_refused():
    symbols, x = molecules()["benzene"]
    xs, H = _symmetric_hessian(symbols, x)
    h = harmonic(H, symbols, xs)
    mix, _ = np.linalg.qr(np.random.default_rng(3).standard_normal((h.q.shape[1], h.q.shape[1])))
    with pytest.raises(ValueError, match="not carried clearly"):
        degenerate_pairs(symbols, xs, h.q @ mix, h.omega_cm)
    with pytest.raises(ValueError, match="orthonormal"):
        degenerate_pairs(symbols, xs, 2.0 * h.q, h.omega_cm)
