"""The force-field assembly on a model quartic potential with known constants.

Central differences are exact for a polynomial of degree ≤ 4 at symmetric ±δ, so every recovered constant must equal the
model's to machine precision, both routes must agree, and the cubic spread must vanish. The model has one exactly
degenerate pair whose displacements are made in a rotated basis, which is the case that produced the spurious 47 cm⁻¹
route disagreement on 21 September 2026: the alignment step must recover the displacement basis exactly.
"""

import numpy as np
import pytest

from dpir.qff import HARTREE_CM, HessianRecord, assemble_qff, assign_displacements, harmonic, qff_from_records
from test_harmonic import vibrational_basis

OMEGA = np.array([0.004, 0.006, 0.006, 0.009, 0.012, 0.015])  # E_h; modes 1 and 2 exactly degenerate
PAIR = [1, 2]
DISP = 0.05


def model_constants(rng, n):
    phi3 = rng.uniform(-5e-4, 5e-4, size=(n, n, n))
    phi3 = (phi3 + phi3.transpose(1, 2, 0) + phi3.transpose(2, 0, 1) + phi3.transpose(0, 2, 1) + phi3.transpose(1, 0, 2) + phi3.transpose(2, 1, 0)) / 6
    phi4 = rng.uniform(-2e-4, 2e-4, size=(n, n))
    phi4 = 0.5 * (phi4 + phi4.T)
    return phi3, phi4


def hessian_Q(Q, omega, phi3, phi4):
    """Hessian of V = Σ½ω_iQ_i² + (1/6)Σφ_ijkQ_iQ_jQ_k + (1/24)Σφ_iiiiQ_i⁴ + (1/4)Σ_{i<j}φ_iijjQ_i²Q_j² in the Q basis."""
    n = len(omega)
    H = np.diag(omega) + np.einsum("abk,k->ab", phi3, Q)
    for a in range(n):
        H[a, a] += 0.5 * phi4[a, a] * Q[a] ** 2 + 0.5 * sum(phi4[a, j] * Q[j] ** 2 for j in range(n) if j != a)
        for b in range(n):
            if b != a:
                H[a, b] += phi4[a, b] * Q[a] * Q[b]
    return H


def model_records(model_molecule, theta):
    """13 records: reference plus ±δ along each of the six modes, displaced in a basis rotated by theta inside the pair."""
    symbols, geom, m, rng = model_molecule
    n = len(OMEGA)
    q = vibrational_basis(geom, m, rng)
    R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    q[:, PAIR] = q[:, PAIR] @ R  # the displacement program's basis
    Minvh = np.repeat(1.0 / np.sqrt(m), 3)
    Msqrt = 1.0 / Minvh
    A = (Minvh[:, None] * q) / np.sqrt(OMEGA)[None, :]
    phi3, phi4 = model_constants(rng, n)
    Om = np.diag(np.sqrt(OMEGA))

    def record(name, Q):
        HQ = hessian_Q(Q, OMEGA, phi3, phi4)
        Hx = Msqrt[:, None] * (q @ Om @ HQ @ Om @ q.T) * Msqrt[None, :]
        return HessianRecord(name, geom + A @ Q, Hx, symbols)

    recs = [record("ref", np.zeros(n))]
    for j in range(n):
        for s in (+1, -1):
            Q = np.zeros(n)
            Q[j] = s * DISP
            recs.append(record(f"mode{j}_{'p' if s > 0 else 'm'}", Q))
    rng.shuffle(recs)
    return recs, A, phi3, phi4


@pytest.mark.parametrize("theta", [0.0, 0.7, np.pi / 3])
def test_constants_recovered_exactly_with_rotated_degenerate_basis(model_molecule, theta):
    recs, A_true, phi3, phi4 = model_records(model_molecule, theta)
    qff, harm, ref, info = qff_from_records(recs, DISP)
    assert ref.file == "ref"
    assert info["subspaces_aligned"] == 1
    assert info["assignment_residual_max"] < 1e-9
    # the analysis basis equals the displacement basis up to the sign of each mode and the order inside the pair
    # (A_analysis = A_true @ P with P a signed permutation, so the constants transform by P in every index)
    S = np.linalg.pinv(A_true) @ harm.A
    P = np.rint(S)
    np.testing.assert_allclose(S, P, atol=1e-8)
    np.testing.assert_allclose(P.T @ P, np.eye(6), atol=0)
    assert np.array_equal(np.abs(P)[np.ix_([0, 3, 4, 5], [0, 3, 4, 5])], np.eye(4)), "non-degenerate modes keep their place"
    expected3 = np.einsum("abc,ai,bj,ck->ijk", phi3, P, P, P) * HARTREE_CM
    expected4 = np.einsum("ab,ai,bj->ij", phi4, P**2, P**2) * HARTREE_CM  # φ_iijj is even in each index: signs drop out
    np.testing.assert_allclose(qff.phi3, expected3, rtol=1e-7, atol=1e-6)
    np.testing.assert_allclose(qff.phi4, expected4, rtol=1e-7, atol=1e-6)
    np.testing.assert_allclose(qff.route_a, qff.route_b, atol=1e-6)
    assert qff.route_disagreement.max() < 1e-6
    assert qff.cubic_spread.max() < 1e-6
    assert qff.pairs == [(1, 2)]


def test_without_alignment_the_assignment_fails(model_molecule):
    """Negative control: this is the 21 September defect. Skipping the alignment leaves a rotated basis in the pair."""
    recs, _A_true, _phi3, _phi4 = model_records(model_molecule, 0.7)
    i0 = next(k for k, r in enumerate(recs) if r.file == "ref")
    harm = harmonic(recs[i0].H, recs[i0].symbols, recs[i0].geom)
    asg = assign_displacements(recs, i0, harm.A, DISP)
    worst = max(v[3] for v in asg.values())
    assert worst > 1e-3, "an unaligned degenerate basis must show up in the assignment residual"


def _transform_records(recs, R=None, shift=None, perm=None):
    """Rigidly rotate (R), translate (shift, bohr) and/or renumber the atoms (perm) of every record."""
    out = []
    for r in recs:
        x = r.geom.reshape(-1, 3)
        H = r.H
        symbols = list(r.symbols)
        if R is not None:
            x = x @ R.T
            Rb = np.kron(np.eye(len(x)), R)
            H = Rb @ H @ Rb.T
        if shift is not None:
            x = x + shift
        if perm is not None:
            x = x[perm]
            idx = np.concatenate([3 * p + np.arange(3) for p in perm])
            H = H[np.ix_(idx, idx)]
            symbols = [symbols[p] for p in perm]
        out.append(HessianRecord(r.file, x.ravel(), H, symbols))
    return out


def _signature(recs):
    qff, harm, ref, info = qff_from_records(recs, DISP)
    return qff, np.sort(np.abs(qff.phi3).ravel()), np.sort(np.abs(qff.phi4).ravel())


def test_invariant_under_rotation_translation_and_atom_permutation(model_molecule):
    """Checklist item 3: a rigid motion of the whole set, or a renumbering of the atoms, changes no derived quantity
    (up to the sign and pair-order freedom of the normal modes, hence the sorted magnitudes)."""
    recs, _A, _p3, _p4 = model_records(model_molecule, 0.4)
    q0, a3, a4 = _signature(recs)
    rng = np.random.default_rng(3)
    Rm, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    if np.linalg.det(Rm) < 0:
        Rm[:, 0] *= -1
    variants = {
        "rotated": _transform_records(recs, R=Rm),
        "translated": _transform_records(recs, shift=np.array([3.0, -1.5, 0.7])),
        "permuted": _transform_records(recs, perm=[2, 0, 3, 1]),
        "all three": _transform_records(recs, R=Rm, shift=np.array([-2.0, 0.3, 5.0]), perm=[3, 1, 0, 2]),
    }
    for name, v in variants.items():
        q1, b3, b4 = _signature(v)
        np.testing.assert_allclose(q1.omega_cm, q0.omega_cm, rtol=1e-10, err_msg=name)
        np.testing.assert_allclose(b3, a3, rtol=1e-7, atol=1e-6, err_msg=name)
        np.testing.assert_allclose(b4, a4, rtol=1e-7, atol=1e-6, err_msg=name)
        assert q1.route_disagreement.max() < 1e-6, name


def test_result_does_not_depend_on_record_order_or_starting_basis(model_molecule):
    """Conventions are the package's, not the input order's or the backend's: shuffling the records, or starting from a
    differently signed and rotated basis, gives identical arrays (not just identical magnitudes)."""
    recs, _A, _p3, _p4 = model_records(model_molecule, 0.7)
    q1, *_ = qff_from_records(sorted(recs, key=lambda r: r.file), DISP)
    q2, *_ = qff_from_records(sorted(recs, key=lambda r: r.file, reverse=True), DISP)
    np.testing.assert_allclose(q1.phi3, q2.phi3, rtol=1e-9, atol=1e-9)  # same signs and order; round-off from the SVD may differ
    np.testing.assert_allclose(q1.phi4, q2.phi4, rtol=1e-9, atol=1e-9)
    _qff, harm, *_ = qff_from_records(recs, DISP)
    for j in range(harm.q.shape[1]):
        assert harm.q[np.argmax(np.abs(harm.q[:, j])), j] > 0, j


def test_route_labels_are_not_swapped():
    """Route a reads H_ii in the files displaced along j; route b reads H_jj in the files displaced along i.
    Perturb exactly one of those entries and only the matching route may move."""
    n = 3
    w = np.array([500.0, 800.0, 1200.0])
    H0 = np.diag(w) / HARTREE_CM
    Hp = {i: H0.copy() for i in range(n)}
    Hn = {i: H0.copy() for i in range(n)}
    base = assemble_qff(w, H0, Hp, Hn, DISP)
    assert base.route_disagreement.max() == 0.0
    Hp[2][0, 0] += 1e-6  # file "mode 2, +", entry H_00: route a for (i=0, j=2) and, by definition, route b for (i=2, j=0)
    pert = assemble_qff(w, H0, Hp, Hn, DISP)
    assert np.argwhere(~np.isclose(pert.route_a, base.route_a)).tolist() == [[0, 2]]
    assert np.argwhere(~np.isclose(pert.route_b, base.route_b)).tolist() == [[2, 0]]
    np.testing.assert_allclose(pert.route_a[0, 2] - base.route_a[0, 2], 1e-6 / DISP**2 * HARTREE_CM)
    np.testing.assert_array_equal(pert.route_a, pert.route_b.T)  # the two routes are each other's transpose
    assert pert.route_disagreement.max() > 80.0  # and the disagreement shows the inconsistency


def test_missing_partner_and_duplicate_file_are_errors(model_molecule):
    recs, _A, _p3, _p4 = model_records(model_molecule, 0.0)
    without = [r for r in recs if r.file != "mode3_m"]
    with pytest.raises(ValueError, match="without a ± pair"):
        qff_from_records(without, DISP)
    duplicated = recs + [next(r for r in recs if r.file == "mode1_p")]
    with pytest.raises(ValueError, match="already taken"):
        qff_from_records(duplicated, DISP)


def test_imaginary_mode_is_an_error(model_molecule):
    symbols, geom, m, rng = model_molecule
    q = vibrational_basis(geom, m, rng)
    lam = np.array([-1e-5, 0.006**2, 0.006**2, 0.009**2, 0.012**2, 0.015**2])
    Msqrt = np.repeat(np.sqrt(m), 3)
    H = Msqrt[:, None] * (q @ np.diag(lam) @ q.T) * Msqrt[None, :]
    with pytest.raises(ValueError, match="imaginary"):
        harmonic(H, symbols, geom)
