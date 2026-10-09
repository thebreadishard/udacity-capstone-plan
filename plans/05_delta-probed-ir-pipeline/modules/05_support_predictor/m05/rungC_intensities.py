"""Lever 5, step 2 (registered 2 Oct 2026 06:5x): the intensity read-out — does the predicted correction reproduce the *spectrum*, not only the frequencies?

Double-harmonic IR intensities from one atomic polar tensor P (3 × 3N, ∂μ/∂R in e, `probes/dipole_derivs_fd.py`) and the modes of a Hessian:
A_k = 974.88 km/mol · |P L_k / √m|² with L_k the mass-weighted eigenvector. Three spectra per molecule from the same P: the truth (H_low + ΔH_true),
the prediction (H_low + ΔH_pred) and the zero rule (H_low). Read-outs: the cosine overlap of Lorentzian-broadened spectra (FWHM 10 cm⁻¹, 500–3500 cm⁻¹)
prediction vs truth and zero rule vs truth, and the intensity-weighted rms of the per-mode relative intensity error (modes paired in sorted order, as
`e7_t2_sqm.basis_free` pairs frequencies). The APT itself is the low level's; its own level dependence is a later term (E8 stores no dipoles yet).
9 Oct 2026: sorted pairing fails where two modes cross (benzene's bright C–H out-of-plane mode and a dark neighbour swap order between B3LYP
and CC/TZ: the zero rule read 0.73 with every intensity within 2 %); `intensity_rel_rms_matched` pairs the modes by their mass-weighted
eigenvectors (maximum squared overlap) and is the number to read; the sorted keys stay for the records written before.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705
KM_PER_MOL = 974.8802                    # (4.80320 D/Å per e)² × 42.2561 km/mol per (D/Å)²/amu
GRID = np.arange(500.0, 3500.0, 1.0)
FWHM = 10.0


def mode_intensities(H_projected: np.ndarray, masses: np.ndarray, apt: np.ndarray, vib_min_cm: float = 20.0, return_modes: bool = False):
    """(frequencies cm⁻¹, intensities km/mol[, mass-weighted eigenvectors]) of the vibrational modes of a projected Cartesian Hessian."""
    mm = np.repeat(masses * AMU2AU, 3)
    w, L = np.linalg.eigh(H_projected / np.sqrt(np.outer(mm, mm)))
    freq = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    vib = np.abs(freq) > vib_min_cm
    dmu_dQ = apt @ (L[:, vib] / np.sqrt(np.repeat(masses, 3))[:, None])
    inten = KM_PER_MOL * (dmu_dQ ** 2).sum(axis=0)
    return (freq[vib], inten, L[:, vib]) if return_modes else (freq[vib], inten)


def match_modes(L_ref: np.ndarray, L: np.ndarray) -> np.ndarray:
    """Index into L's columns for each column of L_ref: the assignment of maximum total squared overlap (degenerate partners may swap,
    which leaves their intensities unchanged when they carry the same irrep)."""
    return linear_sum_assignment(-(L_ref.T @ L) ** 2)[1]


def broadened(freq: np.ndarray, inten: np.ndarray, grid: np.ndarray = GRID, fwhm: float = FWHM) -> np.ndarray:
    g = 0.5 * fwhm
    return (inten[:, None] * g / np.pi / ((grid[None, :] - freq[:, None]) ** 2 + g ** 2)).sum(axis=0)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else float("nan")


def intensity_readout(H_low: np.ndarray, dH_true: np.ndarray, dH_pred: np.ndarray, masses: np.ndarray, apt: np.ndarray) -> dict:
    """The registered read-outs for one molecule: spectrum overlap (prediction, zero rule) against the truth and the weighted relative intensity errors."""
    ft, it, Lt = mode_intensities(H_low + dH_true, masses, apt, return_modes=True)
    fp, ip, Lp = mode_intensities(H_low + dH_pred, masses, apt, return_modes=True)
    f0, i0, L0 = mode_intensities(H_low, masses, apt, return_modes=True)
    if not (len(ft) == len(fp) == len(f0)):
        raise ValueError(f"mode counts differ ({len(ft)}, {len(fp)}, {len(f0)}): a near-zero mode crossed the vibrational threshold")
    st, sp, s0 = broadened(ft, it), broadened(fp, ip), broadened(f0, i0)
    wgt = it / max(it.sum(), 1e-30)
    rel = lambda i: float(np.sqrt(np.sum(wgt * ((i - it) / np.maximum(it, 1.0)) ** 2)))   # noqa: E731 — modes below 1 km/mol enter on an absolute scale
    return {"spectrum_overlap": cosine(sp, st), "spectrum_overlap_zero_rule": cosine(s0, st),
            "intensity_rel_rms": rel(ip), "intensity_rel_rms_zero_rule": rel(i0),
            "intensity_rel_rms_matched": rel(ip[match_modes(Lt, Lp)]), "intensity_rel_rms_zero_rule_matched": rel(i0[match_modes(Lt, L0)]),
            "n_modes": int(len(ft))}


def aggregate(per_molecule: dict) -> dict:
    """Means over the molecules that have an APT (the others contribute nothing); the count says how many."""
    rows = [v for v in per_molecule.values() if v.get("spectrum_overlap") is not None]
    if not rows:
        return {"intensity_n": 0}
    keys = ("spectrum_overlap", "spectrum_overlap_zero_rule", "intensity_rel_rms", "intensity_rel_rms_zero_rule", "intensity_rel_rms_matched",
            "intensity_rel_rms_zero_rule_matched")
    rows = [r for r in rows if all(k in r for k in keys)] or rows               # records written before 9 Oct carry no matched keys
    keys = tuple(k for k in keys if all(k in r for r in rows))
    return {"intensity_n": len(rows), **{k: float(np.nanmean([r[k] for r in rows])) for k in keys}}
