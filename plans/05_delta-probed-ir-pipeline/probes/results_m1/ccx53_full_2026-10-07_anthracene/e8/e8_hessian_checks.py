"""Self-check of an assembled E8 Hessian, split by what went wrong (30 September 2026).

Before this module, e8_cc_hessian_fd.py called a Hessian invalid when the six lowest |frequencies| were not all below 10 cm⁻¹, assuming those
six are the projected translations and rotations. On benzonitrile (30 Sep) two genuinely imaginary bending vibrations at the B3LYP geometry
(−87.0 / −81.9 cm⁻¹, confirmed by an energy-only route: −86.7 / −81.3) took two of those six places, and a correctly computed Hessian was
reported as a computational failure. The check now keeps two questions apart:

* INVALID — the computation is wrong: FD asymmetry above ASYM_LIMIT, the translational sum rule violated (shifting the whole molecule must
  change no force, independent of the geometry; correct CC Hessians 3e-6…3e-5, the frozen-core incident of 27 Sep 6.8e-2), a
  translation/rotation mode not at zero after projection, or a non-finite element.
  What the sum rule cannot see (review of 30 Sep): an error that is the same at every displacement — a wrong density, e.g. the CCSD
  instead of the (T) lambda of the 29 Sep incident — still gives translation-invariant gradients. For that the energy route is added:
  every displaced calculation also yields E, and (E₊ + E₋ − 2E₀)/h² must equal the Hessian diagonal H_kk built from the gradients
  (|difference| ≤ ENERGY_DIAG_LIMIT); a gradient that is not dE/dx fails it. Gate 1 (water) checks the same thing independently.
* IMAGINARY — the computation is sound but the geometry is not a minimum on this surface: a vibrational frequency below −IMAG_LIMIT_CM.
  Such a Hessian is not used for any read-out (the user, 30 Sep 2026: "only use the results of correct calculations").
* VALID — neither.

Translations/rotations are identified by their overlap with the mass-weighted translation/rotation space, not by position in the sorted list.
Pure numpy, so tests run on any machine (tests/test_e8_hessian_checks.py).
"""
import numpy as np

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705
ASYM_LIMIT = 2e-3            # a.u.; benzene 2.7e-4 (full) / 4.4e-5 (symmetric); the invalid naphthalene 2.2e-2
TRANS_SUM_LIMIT = 1e-3       # E_h/bohr²; correct CC Hessians 3.2e-6 … 3.1e-5, the frozen-core incident 6.8e-2
NULL_SPACE_LIMIT_CM = 10.0   # cm⁻¹; the six projected translations/rotations must be ~0
IMAG_LIMIT_CM = 10.0         # cm⁻¹; a vibration below −10 cm⁻¹ means: not a minimum
ENERGY_DIAG_LIMIT = 1e-3     # E_h/bohr²; energy second difference vs gradient-built H_kk (energy noise ~1e-9 E_h / h² = 2.5e-5 bohr² ≈ 1e-4;
                             # the CCSD-lambda water Hessian differed from the correct one by up to 2.5e-3)


def tr_basis(x, masses):
    """Orthonormal mass-weighted translation/rotation basis (3N × 6); ValueError for a linear or degenerate geometry."""
    x = np.asarray(x, float).reshape(-1, 3)
    m = np.asarray(masses, float)
    n = len(m)
    r = x - (x * m[:, None]).sum(0) / m.sum()
    D = []
    for k in range(3):
        v = np.zeros((n, 3)); v[:, k] = 1.0
        D.append((v * np.sqrt(m)[:, None]).ravel())
    for k in range(3):
        e = np.zeros(3); e[k] = 1.0
        D.append((np.cross(np.tile(e, (n, 1)), r) * np.sqrt(m)[:, None]).ravel())
    D = np.array(D).T
    s = np.linalg.svd(D, compute_uv=False)
    if s[-1] < 1e-6 * s[0]:
        raise ValueError("linear or degenerate geometry: fewer than six independent translations/rotations")
    q, _ = np.linalg.qr(D)
    return q


def classify_hessian(H, x, masses, asym=0.0, energy_diag=None):
    """Status and numbers of a Cartesian Hessian H (E_h/bohr², 3N × 3N, symmetrised) at geometry x (bohr) with masses (amu).

    asym is the FD consistency measure of the run (max |G − Gᵀ|, or the symmetry spread). Returns a dict with status ('VALID', 'INVALID',
    'IMAGINARY'), reasons (list of str), trans_sum_rule, energy_diag_max, energy_diag_n, tr_max_cm, vib_cm (sorted vibrational frequencies,
    imaginary as negative),
    imaginary_cm, H_projected (Cartesian, translations/rotations projected out) and freq_cm (all 3N, sorted). energy_diag, optional:
    {Cartesian index k: (E₊ + E₋ − 2E₀)/h²} for the displacements whose energies were stored."""
    H = np.asarray(H, float)
    m = np.asarray(masses, float)
    n = len(m)
    reasons = []
    if not np.all(np.isfinite(H)):
        return {"status": "INVALID", "reasons": ["non-finite Hessian element"], "trans_sum_rule": float("nan"), "tr_max_cm": float("nan"),
                "energy_diag_max": float("nan"), "energy_diag_n": 0,
                "vib_cm": np.array([]), "imaginary_cm": [], "H_projected": H, "freq_cm": np.array([])}
    trans = max(float(np.abs(H @ np.tile(np.eye(3)[k], n)).max()) for k in range(3))
    energy_diag = energy_diag or {}
    ediff = [abs(H[k, k] - v) for k, v in energy_diag.items()]
    energy_max = float(max(ediff)) if ediff else float("nan")
    q = tr_basis(x, m)
    sm = np.sqrt(np.repeat(m * AMU2AU, 3))
    P = np.eye(3 * n) - q @ q.T
    Hmw_p = P @ (H / np.outer(sm, sm)) @ P
    Hmw_p = 0.5 * (Hmw_p + Hmw_p.T)
    w, v = np.linalg.eigh(Hmw_p)
    overlap = np.sum((q.T @ v) ** 2, axis=0)
    is_tr = np.zeros(len(w), bool)
    is_tr[np.argsort(-overlap)[:6]] = True
    f = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    tr_max = float(np.abs(f[is_tr]).max())
    vib = np.sort(f[~is_tr])
    if not asym <= ASYM_LIMIT:
        reasons.append(f"FD asymmetry {asym:.2e} a.u. (limit {ASYM_LIMIT:.0e})")
    if not trans <= TRANS_SUM_LIMIT:
        reasons.append(f"translational sum rule {trans:.1e} E_h/bohr² (limit {TRANS_SUM_LIMIT:.0e})")
    if ediff and not energy_max <= ENERGY_DIAG_LIMIT:
        reasons.append(f"gradient/energy mismatch: max |H_kk − (E₊+E₋−2E₀)/h²| {energy_max:.1e} E_h/bohr² over {len(ediff)} coordinates "
                       f"(limit {ENERGY_DIAG_LIMIT:.0e}) — the gradient is not dE/dx")
    if not tr_max <= NULL_SPACE_LIMIT_CM or overlap[is_tr].min() < 0.99:
        reasons.append(f"translations/rotations not at zero after projection: {tr_max:.1f} cm⁻¹, overlap {overlap[is_tr].min():.3f}")
    imaginary = [float(x_) for x_ in vib if x_ < -IMAG_LIMIT_CM]
    if reasons:
        status = "INVALID"
    elif imaginary:
        status = "IMAGINARY"
        reasons.append(f"{len(imaginary)} imaginary vibration(s) {np.round(imaginary, 1).tolist()} cm⁻¹ (limit −{IMAG_LIMIT_CM:.0f}): not a minimum")
    else:
        status = "VALID"
    return {"status": status, "reasons": reasons, "trans_sum_rule": trans, "energy_diag_max": energy_max, "energy_diag_n": len(ediff),
            "tr_max_cm": tr_max, "vib_cm": vib, "imaginary_cm": imaginary,
            "H_projected": Hmw_p * np.outer(sm, sm), "freq_cm": np.sort(f)}
