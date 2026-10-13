"""The out-of-plane block of a corrected Hessian (13 Oct 2026, TASKS 51; on the user's word: 'begin met 1 en 2').

Lever 6b found the TZ standard's intensity error in one place: the strongest out-of-plane pair of each low-symmetry anchor, turned inside its own
two-dimensional space (`probes/results_m1/cc_apt_field_2026-10-12/mode_shape_diagnosis.md`). Two tools follow from it.

1. **`pair_rotation`** — R-C of anchor set three as a function (the pair: `oop_pair`, the strongest out-of-plane mode and its nearest
   neighbour of the same symmetry species): in the truth's normal-mode basis, the 2 × 2 block of a test Hessian on a pair of
   truth modes; the angle that diagonalises it (signed, the truth's own eigenvectors as the reference, so a prediction and the zero rule are read
   on the same axes), the coupling κ in cm⁻¹ that turns it (tan 2θ = 2κ / Δω), and how much of the test's two matched eigenvectors the pair's
   plane captures (the 2 × 2 picture holds when that is close to 1).
2. **`oop_couplings_from_low`** — the arm prepared for R-B's fail branch: the network's correction with every coupling that involves an
   out-of-plane mode removed in the low level's normal-mode basis — between two out-of-plane modes, and between an in-plane and an out-of-plane
   mode (which σ_h forbids; the network's prediction carries them up to 2.4 cm⁻¹ on the six anchors, the truth ≤ 0.19). The out-of-plane shapes are then the low level's (B3LYP's) exactly; the out-of-plane positions
   keep the network's diagonal; everything else is untouched. Parameter-free: no knob to choose.

3. **`oop_block_from_model`** — R-A's fail branch: the out-of-plane *diagonal* from a three-number model fitted on the training anchors
   (`fit_oop_shift`: first-order shift = a + b·ω/1000 + c·h per out-of-plane mode of the low level, h its mass-weighted share on hydrogen), the
   out-of-plane couplings from the low level, the rest the network's. Why: on the six-anchor baseline the couplings carry no position (the arm
   moves the out-of-plane ω by ≤ 0.8 cm⁻¹), and the network's out-of-plane diagonal does not follow the truth (slopes 0.03–0.19, one −0.4;
   `probes/results_m1/oop_block_2026-10-13/`). The form was chosen among five on that baseline, so it is tested on anchor set three.

Both need a planar molecule (every vibration in or out of the plane by σ_h); `plane_split` refuses one that is not.
"""
import numpy as np
from learning_curve_layerA import AMU2AU, HARTREE2CM
from rungC_intensities import match_modes, mode_intensities

VIB_MIN_CM = 20.0          # the read-out's own threshold (`rungC_intensities.mode_intensities`)
PLANAR_TOL = 1e-3          # a planar molecule's modes are pure: out-of-plane fraction within 1e-3 of 0 or 1


def mass_weighted(H: np.ndarray, masses: np.ndarray) -> np.ndarray:
    mm = np.repeat(np.asarray(masses, float) * AMU2AU, 3)
    return H / np.sqrt(np.outer(mm, mm))


def plane_normal(coords: np.ndarray) -> np.ndarray:
    x = np.asarray(coords, float) - np.mean(coords, axis=0)
    return np.linalg.svd(x)[2][-1]


def plane_split(L: np.ndarray, coords: np.ndarray, tol: float = PLANAR_TOL) -> np.ndarray:
    """True for the columns of L (mass-weighted eigenvectors) that move out of the plane. Refuses a molecule whose modes are not pure."""
    n = plane_normal(coords)
    frac = (np.einsum("aim,i->am", L.reshape(len(coords), 3, -1), n) ** 2).sum(axis=0)
    mixed = np.minimum(frac, 1.0 - frac)
    if mixed.max() > tol:
        raise ValueError(f"not planar: a mode is {mixed.max():.1e} mixed between in and out of the plane (tolerance {tol:g})")
    return frac > 0.5


def mode_characters(L: np.ndarray, ops: list) -> np.ndarray:
    """χ_k(g) = L_kᵀ D(g) L_k for each point-group operation g = (R, perm) of `probes/e8_symmetry.point_group_ops` (R x_i = x_perm[i]): ±1 for a
    non-degenerate mode, the species' character in general. Rows: operations; columns: the modes (mass-weighted eigenvectors, masses equal
    within an orbit so D acts the same on them)."""
    n = L.shape[0] // 3
    U = L.reshape(n, 3, -1)
    chars = []
    for R, perm in ops:
        DU = np.zeros_like(U)
        DU[np.asarray(perm)] = np.einsum("xy,aym->axm", R, U)
        chars.append(np.einsum("axm,axm->m", U, DU))
    return np.array(chars)


def oop_pair_from(freq: np.ndarray, inten: np.ndarray, oop: np.ndarray, chars: np.ndarray, tol: float = 0.5) -> tuple[int, int] | None:
    """R-C's pair, fixed before anchor set three is read: the out-of-plane mode with the largest truth intensity, and the out-of-plane mode of
    the same symmetry species (all characters within tol) nearest to it in frequency. Lower frequency first; None when it has no such partner."""
    cand = np.flatnonzero(oop)
    if len(cand) < 2:
        return None
    k = int(cand[np.argmax(inten[cand])])
    same = [j for j in cand if j != k and np.all(np.abs(chars[:, j] - chars[:, k]) < tol)]
    if not same:
        return None
    l = int(min(same, key=lambda j: abs(freq[j] - freq[k])))
    return (k, l) if freq[k] < freq[l] else (l, k)


def oop_pair(H_true: np.ndarray, masses: np.ndarray, apt: np.ndarray, coords: np.ndarray, ops: list) -> tuple[int, int] | None:
    """`oop_pair_from` on the truth: indices into its vibrational modes as `mode_intensities` orders them."""
    f, inten, L = mode_intensities(H_true, masses, apt, return_modes=True)
    return oop_pair_from(f, inten, plane_split(L, coords), mode_characters(L, ops))


def pair_rotation(H_true: np.ndarray, H_test: np.ndarray, masses: np.ndarray, k: int, l: int) -> dict:
    """R-C for one pair (k, l) of the truth's vibrational modes (indices as `mode_intensities` returns them). θ > 0 and θ < 0 are directions on
    the truth's own axes; a prediction and the zero rule turned the same way have the same sign."""
    w, V = np.linalg.eigh(mass_weighted(H_true, masses))
    freq = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    Lt = V[:, np.abs(freq) > VIB_MIN_CM]
    ft = freq[np.abs(freq) > VIB_MIN_CM]
    P = Lt[:, [k, l]]
    Hm = mass_weighted(H_test, masses)
    a, c, d = (float(x) for x in (P[:, 0] @ Hm @ P[:, 0], P[:, 0] @ Hm @ P[:, 1], P[:, 1] @ Hm @ P[:, 1]))
    if a == d:
        raise ValueError("the pair's diagonal is degenerate in the test Hessian; the rotation is not defined")
    theta = 0.5 * np.arctan(2.0 * c / (a - d))                        # the small rotation that diagonalises the block
    om = np.sqrt(np.abs([a, d])) * HARTREE2CM                          # the test's frequencies on the truth's two axes
    kappa = c * HARTREE2CM ** 2 / (om[0] + om[1])                      # tan 2θ = 2κ / (ω_k − ω_l), κ in cm⁻¹
    wt, Vt = np.linalg.eigh(Hm)
    fp = np.sign(wt) * np.sqrt(np.abs(wt)) * HARTREE2CM
    Lp = Vt[:, np.abs(fp) > VIB_MIN_CM]
    m = match_modes(Lt, Lp)[[k, l]]
    captured = float(((P.T @ Lp[:, m]) ** 2).sum() / 2.0)
    overlap_k = float((Lt[:, k] @ Lp[:, m[0]]) ** 2)
    return {"modes": [int(k), int(l)], "freq_true": [round(float(ft[k]), 1), round(float(ft[l]), 1)], "theta_deg": float(np.degrees(theta)),
            "kappa_cm": float(kappa), "gap_cm": float(om[0] - om[1]), "captured": captured, "overlap_k": overlap_k,
            "theta_from_overlap_deg": float(np.degrees(np.arccos(np.sqrt(min(overlap_k, 1.0)))))}


def oop_couplings_from_low(dH: np.ndarray, H_low: np.ndarray, masses: np.ndarray, coords: np.ndarray) -> np.ndarray:
    """dH with every coupling that involves an out-of-plane vibration of the low level set to zero (out-of-plane/out-of-plane and in-plane/
    out-of-plane; the diagonal and the in-plane block kept), back in Cartesian form. With nothing removed the transform is the identity (the low
    level's full eigenbasis is orthonormal)."""
    mm = np.repeat(np.asarray(masses, float) * AMU2AU, 3)
    w, V = np.linalg.eigh(mass_weighted(H_low, masses))
    vib = np.abs(np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM) > VIB_MIN_CM
    oop = np.zeros(len(w), bool)
    oop[vib] = plane_split(V[:, vib], coords)
    D = V.T @ (dH / np.sqrt(np.outer(mm, mm))) @ V
    D[_oop_couplings(oop, vib)] = 0.0
    return (V @ D @ V.T) * np.sqrt(np.outer(mm, mm))


def _oop_couplings(oop: np.ndarray, vib: np.ndarray) -> np.ndarray:
    """Mask of the couplings that involve an out-of-plane vibration: out-of-plane pairs and in-plane/out-of-plane pairs (off the diagonal)."""
    ip = vib & ~oop
    return (np.outer(oop, oop) | np.outer(ip, oop) | np.outer(oop, ip)) & ~np.eye(len(oop), dtype=bool)


def oop_modes(H_low: np.ndarray, masses: np.ndarray, coords: np.ndarray, symbols: list) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(mass-weighted eigenvectors, ω cm⁻¹, hydrogen share h) of the low level's out-of-plane vibrations."""
    w, V = np.linalg.eigh(mass_weighted(H_low, masses))
    f = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    vib = np.abs(f) > VIB_MIN_CM
    oop = plane_split(V[:, vib], coords)
    Vo, fo = V[:, vib][:, oop], f[vib][oop]
    hm = np.repeat([s.upper() == "H" for s in symbols], 3)
    return Vo, fo, (Vo[hm] ** 2).sum(axis=0)


def oop_shift_design(freq: np.ndarray, hshare: np.ndarray) -> np.ndarray:
    return np.c_[np.ones_like(freq), freq / 1000.0, hshare]


def oop_shifts(dH: np.ndarray, Vo: np.ndarray, fo: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """First-order frequency shifts ΔH_kk / 2ω_k (cm⁻¹) of a correction on the given out-of-plane modes."""
    return np.einsum("ik,ij,jk->k", Vo, mass_weighted(dH, masses), Vo) * HARTREE2CM ** 2 / (2.0 * fo)


def fit_oop_shift(training: list) -> np.ndarray:
    """(a, b, c) by least squares over the out-of-plane modes of the training anchors; training = [(freq, hshare, true shift), ...]."""
    X = np.vstack([oop_shift_design(f, h) for f, h, _ in training])
    y = np.concatenate([t for _, _, t in training])
    return np.linalg.lstsq(X, y, rcond=None)[0]


def oop_block_from_model(dH: np.ndarray, H_low: np.ndarray, masses: np.ndarray, coords: np.ndarray, symbols: list, coef: np.ndarray) -> np.ndarray:
    """The arm of R-A's fail branch: the low level's couplings for every out-of-plane mode, the model's out-of-plane diagonal, the network's
    in-plane block."""
    mm = np.repeat(np.asarray(masses, float) * AMU2AU, 3)
    w, V = np.linalg.eigh(mass_weighted(H_low, masses))
    f = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    vib = np.abs(f) > VIB_MIN_CM
    oop = np.zeros(len(w), bool)
    oop[vib] = plane_split(V[:, vib], coords)
    hm = np.repeat([s.upper() == "H" for s in symbols], 3)
    D = V.T @ (dH / np.sqrt(np.outer(mm, mm))) @ V
    D[_oop_couplings(oop, vib)] = 0.0
    idx = np.flatnonzero(oop)
    shift = oop_shift_design(f[idx], (V[hm][:, idx] ** 2).sum(axis=0)) @ coef
    D[idx, idx] = 2.0 * f[idx] * shift / HARTREE2CM ** 2
    return (V @ D @ V.T) * np.sqrt(np.outer(mm, mm))


def oop_couplings_from_low_internal(dF: np.ndarray, B: np.ndarray, H_low: np.ndarray, masses: np.ndarray, coords: np.ndarray) -> np.ndarray:
    """The arm on a prediction in the pair model's internal coordinates (what `rungC_train.predictor` returns, B⁺ᵀ ΔH B⁺): Cartesian Bᵀ ΔF B, the
    arm, and back. The arm leaves translations and rotations alone, so the round trip is exact."""
    return internal(dF, B, lambda dH: oop_couplings_from_low(dH, H_low, masses, coords))


def internal(dF: np.ndarray, B: np.ndarray, arm) -> np.ndarray:
    """Any Cartesian arm (dH → dH) on a prediction in the pair model's internal coordinates: Bᵀ ΔF B, the arm, and B⁺ᵀ · B⁺ back."""
    Bp = np.linalg.pinv(B)
    return Bp.T @ arm(B.T @ dF @ B) @ Bp
