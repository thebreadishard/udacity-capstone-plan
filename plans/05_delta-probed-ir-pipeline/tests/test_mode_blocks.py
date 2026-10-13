"""m05/mode_blocks.py (13 Oct 2026): the pair rotation of R-C and the arm with the out-of-plane couplings from the low level, on a synthetic planar
molecule whose modes are built by hand (a known angle in, the same angle out)."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import mode_blocks as MB  # noqa: E402
from learning_curve_layerA import AMU2AU, HARTREE2CM  # noqa: E402
from rungC_intensities import mode_intensities  # noqa: E402

MASSES = np.array([12.0, 12.0, 14.0, 12.0, 12.0, 19.0])
COORDS = np.array([[2.6 * np.cos(t), 2.6 * np.sin(t), 0.0] for t in np.arange(6) * np.pi / 3]) * np.array([1.0, 1.1, 1.0])


def _basis():
    """Mass-weighted orthonormal vibrational modes of the planar hexagon, split into in-plane and out-of-plane."""
    sq = np.repeat(np.sqrt(MASSES * AMU2AU), 3)
    x = COORDS - (MASSES[:, None] * COORDS).sum(0) / MASSES.sum()
    ext = [np.tile(e, 6) * sq for e in np.eye(3)] + [np.cross(e, x).ravel() * sq for e in np.eye(3)]
    Q, _ = np.linalg.qr(np.array(ext).T)
    z = np.zeros((18, 6))
    z[2::3] = np.eye(6)
    xy = np.zeros((18, 12))
    xy[np.arange(18) % 3 != 2] = np.eye(12)
    out = []
    for S in (xy, z):
        S = S - Q @ (Q.T @ S)
        u, s, _ = np.linalg.svd(S, full_matrices=False)
        out.append(u[:, s > 1e-8])
    return out[0], out[1]                                              # 9 in plane, 3 out of plane


def _cartesian(Hmw):
    sq = np.repeat(np.sqrt(MASSES * AMU2AU), 3)
    return Hmw * np.outer(sq, sq)


def _lam(cm):
    return (np.asarray(cm, float) / HARTREE2CM) ** 2


IP, OOP = _basis()
F_IP = np.linspace(400.0, 3100.0, 9)
F_OOP = np.array([520.0, 700.0, 740.0])


def _truth():
    return _cartesian(IP @ np.diag(_lam(F_IP)) @ IP.T + OOP @ np.diag(_lam(F_OOP)) @ OOP.T)


def _vib_index(H, column):
    """Index of `column` (a mass-weighted vector) among H's vibrational modes as `mode_intensities` orders them."""
    _, _, L = mode_intensities(H, MASSES, np.zeros((3, 18)), return_modes=True)
    return int(np.argmax((L.T @ column) ** 2))


def test_basis_is_planar_and_complete():
    assert IP.shape[1] == 9 and OOP.shape[1] == 3
    _, _, L = mode_intensities(_truth(), MASSES, np.zeros((3, 18)), return_modes=True)
    assert MB.plane_split(L, COORDS).sum() == 3


@pytest.mark.parametrize("phi", [12.0, -7.5])
def test_a_known_turn_of_the_pair_is_read_back(phi):
    H = _truth()
    k, l = _vib_index(H, OOP[:, 1]), _vib_index(H, OOP[:, 2])
    p = np.radians(phi)
    U = OOP.copy()
    U[:, 1] = np.cos(p) * OOP[:, 1] + np.sin(p) * OOP[:, 2]
    U[:, 2] = -np.sin(p) * OOP[:, 1] + np.cos(p) * OOP[:, 2]
    H_test = _cartesian(IP @ np.diag(_lam(F_IP)) @ IP.T + U @ np.diag(_lam(F_OOP)) @ U.T)
    r = MB.pair_rotation(H, H_test, MASSES, k, l)
    assert abs(abs(r["theta_deg"]) - abs(phi)) < 1e-6                  # the sign depends on the truth's eigenvector signs; see the next test
    assert abs(r["theta_from_overlap_deg"] - abs(phi)) < 1e-6 and abs(r["captured"] - 1.0) < 1e-10
    assert MB.pair_rotation(H, H_test, MASSES, k, l)["theta_deg"] == r["theta_deg"]   # the truth's axes are the reference: deterministic


def test_opposite_turns_read_with_opposite_signs():
    H = _truth()
    k, l = _vib_index(H, OOP[:, 1]), _vib_index(H, OOP[:, 2])
    th = []
    for phi in (9.0, -9.0):
        p = np.radians(phi)
        U = OOP.copy()
        U[:, 1] = np.cos(p) * OOP[:, 1] + np.sin(p) * OOP[:, 2]
        U[:, 2] = -np.sin(p) * OOP[:, 1] + np.cos(p) * OOP[:, 2]
        th.append(MB.pair_rotation(H, _cartesian(IP @ np.diag(_lam(F_IP)) @ IP.T + U @ np.diag(_lam(F_OOP)) @ U.T), MASSES, k, l)["theta_deg"])
    assert abs(th[0] + th[1]) < 1e-9 and abs(abs(th[0]) - 9.0) < 1e-6


def test_kappa_is_the_coupling_in_wavenumbers():
    H = _truth()
    k, l = _vib_index(H, OOP[:, 1]), _vib_index(H, OOP[:, 2])
    c = 2.0e-6                                                          # a.u., a small coupling put in by hand
    Hm = IP @ np.diag(_lam(F_IP)) @ IP.T + OOP @ np.diag(_lam(F_OOP)) @ OOP.T
    Hm = Hm + c * (np.outer(OOP[:, 1], OOP[:, 2]) + np.outer(OOP[:, 2], OOP[:, 1]))
    r = MB.pair_rotation(H, _cartesian(Hm), MASSES, k, l)
    assert abs(abs(r["kappa_cm"]) - c * HARTREE2CM ** 2 / (700.0 + 740.0)) < 1e-9
    assert abs(r["gap_cm"] + 40.0) < 1e-6
    assert abs(np.tan(2 * np.radians(r["theta_deg"])) - 2 * r["kappa_cm"] / r["gap_cm"]) < 1e-9


def test_characters_of_the_plane_reflection():
    _, _, L = mode_intensities(_truth(), MASSES, np.zeros((3, 18)), return_modes=True)
    ops = [(np.eye(3), list(range(6))), (np.diag([1.0, 1.0, -1.0]), list(range(6)))]
    chars = MB.mode_characters(L, ops)
    oop = MB.plane_split(L, COORDS)
    assert np.allclose(chars[0], 1.0) and np.allclose(chars[1][oop], -1.0) and np.allclose(chars[1][~oop], 1.0)


def test_characters_follow_the_permutation():
    """A C2 rotation about z that swaps two atoms: a mode symmetric under it has χ = +1, an antisymmetric one −1."""
    x = np.array([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
    ops = [(np.diag([-1.0, -1.0, 1.0]), [1, 0])]
    sym = np.array([1.0, 0, 0, -1.0, 0, 0]) / np.sqrt(2)               # stretch along x: atom 0 +x, atom 1 −x → invariant
    anti = np.array([1.0, 0, 0, 1.0, 0, 0]) / np.sqrt(2)               # both +x → odd
    assert x.shape == (2, 3)
    assert np.allclose(MB.mode_characters(np.stack([sym, anti], axis=1), ops), [[1.0, -1.0]])


def test_the_pair_is_the_strongest_mode_and_its_nearest_partner_of_its_species():
    freq = np.array([500.0, 670.0, 700.0, 769.0, 902.0, 1200.0])
    inten = np.array([1.0, 4.5, 60.0, 74.0, 20.0, 9.0])
    oop = np.array([True, True, False, True, True, False])
    chars = np.array([[1, 1, 1, 1, 1, 1], [1, -1, 1, -1, -1, 1]], float)
    assert MB.oop_pair_from(freq, inten, oop, chars) == (1, 3)          # 769 is the strongest oop mode; 670 is nearer than 902
    chars[1, 1] = 1.0                                                   # 670 in another species: it cannot mix with 769
    assert MB.oop_pair_from(freq, inten, oop, chars) == (3, 4)
    chars[1, 4] = 1.0
    assert MB.oop_pair_from(freq, inten, oop, chars) is None            # no partner of its species


def test_the_arm_removes_only_out_of_plane_couplings():
    H_low = _truth()
    rng = np.random.default_rng(1)
    A = rng.normal(size=(12, 12)) * 1e-6
    A[:9, 9:] = A[9:, :9] = 0.0                                         # a planar molecule's correction does not couple the plane to its normal
    Bv = np.hstack([IP, OOP])
    dH = _cartesian(Bv @ (A + A.T) @ Bv.T)
    arm = MB.oop_couplings_from_low(dH, H_low, MASSES, COORDS)
    D0, D1 = (Bv.T @ MB.mass_weighted(x, MASSES) @ Bv for x in (dH, arm))
    o = np.arange(9, 12)
    assert np.allclose(D1[9:, 9:], np.diag(np.diag(D0[9:, 9:])), atol=1e-18)    # out-of-plane block: diagonal kept, couplings gone
    mask = np.ones((12, 12), bool)
    mask[np.ix_(o, o)] = False
    assert np.allclose(D1[mask], D0[mask], atol=1e-18)                             # everything else untouched
    _, _, L0 = mode_intensities(H_low, MASSES, np.zeros((3, 18)), return_modes=True)
    _, _, L1 = mode_intensities(H_low + arm, MASSES, np.zeros((3, 18)), return_modes=True)
    oop0, oop1 = MB.plane_split(L0, COORDS), MB.plane_split(L1, COORDS)
    ov = (L0[:, oop0].T @ L1[:, oop1]) ** 2
    assert np.allclose(np.sort(ov.max(axis=1)), 1.0, atol=1e-10)                   # out-of-plane shapes are the low level's


def test_the_arm_is_the_identity_without_out_of_plane_couplings():
    H_low = _truth()
    dH = _cartesian(IP @ np.diag(_lam(F_IP) * 0.01) @ IP.T + OOP @ np.diag(_lam(F_OOP) * -0.02) @ OOP.T)
    assert np.allclose(MB.oop_couplings_from_low(dH, H_low, MASSES, COORDS), dH, rtol=0, atol=1e-14)


def test_a_mode_mixed_between_the_plane_and_its_normal_is_refused():
    L = np.hstack([IP, OOP])
    L[:, 0] = (IP[:, 0] + OOP[:, 0]) / np.sqrt(2.0)                    # what a non-planar molecule's modes look like
    with pytest.raises(ValueError, match="not planar"):
        MB.plane_split(L, COORDS)


def test_the_arm_in_internal_coordinates_round_trips():
    """`rungC_train.predictor` hands the read B⁺ᵀ ΔH B⁺; the arm goes through Cartesian and back. With redundant internals whose rows are
    orthogonal to translations and rotations (as real internal coordinates are), Bᵀ ΔF_arm B is the Cartesian arm exactly."""
    sq = np.repeat(np.sqrt(MASSES * AMU2AU), 3)
    Bv = np.hstack([IP, OOP])
    rng = np.random.default_rng(2)
    B = rng.normal(size=(16, 12)) @ (Bv * sq[:, None]).T                # 16 redundant rows, Euclidean-orthogonal to translations and rotations
    A = rng.normal(size=(12, 12)) * 1e-6
    A[:9, 9:] = A[9:, :9] = 0.0
    dH = _cartesian(Bv @ (A + A.T) @ Bv.T)
    Bp = np.linalg.pinv(B)
    dF = Bp.T @ dH @ Bp
    assert np.allclose(B.T @ dF @ B, dH, rtol=0, atol=1e-12)
    dF_arm = MB.oop_couplings_from_low_internal(dF, B, _truth(), MASSES, COORDS)
    assert np.allclose(B.T @ dF_arm @ B, MB.oop_couplings_from_low(dH, _truth(), MASSES, COORDS), rtol=0, atol=1e-12)


def test_the_model_arm_sets_the_out_of_plane_diagonal_and_drops_its_couplings():
    H_low = _truth()
    symbols = ["C", "C", "N", "C", "C", "F"]
    rng = np.random.default_rng(3)
    A = rng.normal(size=(12, 12)) * 1e-6
    A[:9, 9:] = A[9:, :9] = 0.0
    Bv = np.hstack([IP, OOP])
    dH = _cartesian(Bv @ (A + A.T) @ Bv.T)
    coef = np.array([-8.0, -50.0, 60.0])
    arm = MB.oop_block_from_model(dH, H_low, MASSES, COORDS, symbols, coef)
    Vo, fo, h = MB.oop_modes(H_low, MASSES, COORDS, symbols)
    assert np.allclose(h, 0.0)                                          # no hydrogen in this stand-in: h = 0
    assert np.allclose(MB.oop_shifts(arm, Vo, fo, MASSES), coef[0] + coef[1] * fo / 1000.0, atol=1e-9)
    D0, D1 = (Bv.T @ MB.mass_weighted(x, MASSES) @ Bv for x in (dH, arm))
    assert np.allclose(D1[9:, 9:] - np.diag(np.diag(D1[9:, 9:])), 0.0, atol=1e-18)
    assert np.allclose(D1[:9, :9], D0[:9, :9], atol=1e-18)            # the in-plane block is the network's


def test_fit_oop_shift_recovers_its_coefficients():
    rng = np.random.default_rng(4)
    coef = np.array([-8.4, -53.7, 63.8])
    tr = []
    for _ in range(3):
        f, h = rng.uniform(100, 1000, 9), rng.uniform(0, 1, 9)
        tr.append((f, h, MB.oop_shift_design(f, h) @ coef))
    assert np.allclose(MB.fit_oop_shift(tr), coef)


def test_both_arms_remove_the_couplings_sigma_h_forbids():
    """A planar molecule's correction cannot couple the plane to its normal; a prediction that does (the network's, up to 2.4 cm⁻¹) loses them."""
    H_low = _truth()
    rng = np.random.default_rng(5)
    A = rng.normal(size=(12, 12)) * 1e-6                                # with in-plane/out-of-plane couplings
    Bv = np.hstack([IP, OOP])
    dH = _cartesian(Bv @ (A + A.T) @ Bv.T)
    for arm in (MB.oop_couplings_from_low(dH, H_low, MASSES, COORDS),
                MB.oop_block_from_model(dH, H_low, MASSES, COORDS, ["C"] * 6, np.zeros(3))):
        D0, D1 = (Bv.T @ MB.mass_weighted(x, MASSES) @ Bv for x in (dH, arm))
        assert np.allclose(D1[:9, 9:], 0.0, atol=1e-18) and np.allclose(D1[:9, :9], D0[:9, :9], atol=1e-18)
