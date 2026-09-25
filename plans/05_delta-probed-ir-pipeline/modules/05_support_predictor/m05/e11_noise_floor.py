"""E11.4 — the label noise floor (pre-registered 25 September 2026, PreRegistration_2026-09-25_E11_Proof_Strengthening_Desk_Tests.md).

On the corpus molecules that carry both the deck-v1 finite-difference Hessians (psi4) and the analytic second-route Hessians (pyscf, grid
99/590): per functional the RMS over vibrational modes of the frequency difference FD − analytic, and for the correction ΔH the RMS difference
of the B3LYP-mode-basis K diagonal between the two routes (the diagonal of the correction in cm⁻¹, the object the read-outs use). The K
difference × 3 is the plateau bound of the proof-of-learning pre-registration.

Usage: python e11_noise_floor.py <corpus/molecules dir> <out prefix>
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705


def freqs_cm(H, masses):
    """3N frequencies in cm-1 from a Cartesian Hessian (hartree/bohr^2) and masses (amu); imaginary as negative (as corpus/analytic_hessians.py)."""
    m = np.repeat(np.asarray(masses) * AMU2AU, 3); w = np.linalg.eigvalsh(H / np.sqrt(np.outer(m, m)))
    return np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM


def vib_only(f):
    f = np.asarray(f, float); return np.delete(f, np.argsort(np.abs(f))[:6])


def modes(H, masses):
    """Mass-weighted eigen-decomposition of a projected Hessian: frequencies (au ω) and eigenvectors, vibrational ones."""
    m = np.repeat(np.asarray(masses) * AMU2AU, 3); Minv = 1 / np.sqrt(m)
    w, V = np.linalg.eigh(H * np.outer(Minv, Minv)); keep = np.argsort(np.abs(w))[6:]; keep = keep[np.argsort(w[keep])]
    return w[keep], V[:, keep], Minv


def k_diag(dH, V, w, Minv):
    """Diagonal of the correction in the low-level mode basis, cm⁻¹: K_ii = (v_iᵀ ΔH_mw v_i) / (2 ω_i) × HARTREE2CM."""
    dHmw = dH * np.outer(Minv, Minv); om = np.sqrt(np.abs(w))
    return np.array([V[:, i] @ dHmw @ V[:, i] for i in range(len(w))]) / (2 * om) * HARTREE2CM


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("molecules"); ap.add_argument("out_prefix"); a = ap.parse_args(); t0 = time.time()
    rows = []
    for d in sorted(Path(a.molecules).iterdir()):
        fa, fb = d / "hessian_b3lyp_analytic.npz", d / "hessian_wb97x_analytic.npz"
        if not (fa.exists() and fb.exists() and (d / "hessian_b3lyp.npz").exists() and (d / "hessian_wb97x.npz").exists()):
            continue
        g = json.load(open(d / "geometry.json")); masses = np.asarray(g["masses_amu"])
        H = {k: np.load(d / f"hessian_{k}.npz")["H_projected"] for k in ("b3lyp", "wb97x")}
        A = {k: np.load(d / f"hessian_{k}_analytic.npz") for k in ("b3lyp", "wb97x")}
        HA = {k: (A[k]["H_projected"] if "H_projected" in A[k].files else A[k]["H_raw"]) for k in A}
        rec = {"id": d.name, "n_atoms": len(masses)}
        for k in ("b3lyp", "wb97x"):
            f_fd = np.sort(vib_only(freqs_cm(H[k], masses))); f_an = np.sort(vib_only(freqs_cm(HA[k], masses)))
            rec[f"freq_rms_{k}"] = float(np.sqrt(np.mean((f_fd - f_an) ** 2))); rec[f"freq_max_{k}"] = float(np.max(np.abs(f_fd - f_an)))
        # the correction's diagonal in the FD B3LYP mode basis, from the two routes
        w, V, Minv = modes(H["b3lyp"], masses)
        K_fd = k_diag(H["wb97x"] - H["b3lyp"], V, w, Minv); K_an = k_diag(HA["wb97x"] - HA["b3lyp"], V, w, Minv)
        rec["K_diag_rms"] = float(np.sqrt(np.mean((K_fd - K_an) ** 2))); rec["K_diag_max"] = float(np.max(np.abs(K_fd - K_an)))
        rows.append(rec)
    pooled = {k: float(np.sqrt(np.mean([r[k] ** 2 for r in rows]))) for k in ("freq_rms_b3lyp", "freq_rms_wb97x", "K_diag_rms")}
    med = {k: float(np.median([r[k] for r in rows])) for k in ("freq_rms_b3lyp", "freq_rms_wb97x", "K_diag_rms")}
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_molecules": len(rows), "pooled_rms": pooled, "median_per_molecule": med,
           "plateau_bound_3x_K": 3 * pooled["K_diag_rms"], "per_molecule": rows, "seconds": round(time.time() - t0, 1)}
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E11.4 — the label noise floor ({res['date']}); {len(rows)} molecules with both routes", "",
          "| quantity | pooled RMS (cm⁻¹) | median per molecule |", "|---|---|---|",
          f"| B3LYP frequencies, FD − analytic | {pooled['freq_rms_b3lyp']:.2f} | {med['freq_rms_b3lyp']:.2f} |",
          f"| ωB97X frequencies, FD − analytic | {pooled['freq_rms_wb97x']:.2f} | {med['freq_rms_wb97x']:.2f} |",
          f"| correction diagonal K_ii, FD − analytic | **{pooled['K_diag_rms']:.2f}** | {med['K_diag_rms']:.2f} |", "",
          f"Plateau bound of the proof-of-learning pre-registration (3 × the K noise): **{3 * pooled['K_diag_rms']:.2f} cm⁻¹**.", "",
          "| molecule | atoms | B3LYP freq RMS | ωB97X freq RMS | K diag RMS | K diag max |", "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -r["K_diag_rms"]):
        md.append(f"| {r['id']} | {r['n_atoms']} | {r['freq_rms_b3lyp']:.2f} | {r['freq_rms_wb97x']:.2f} | {r['K_diag_rms']:.2f} | {r['K_diag_max']:.1f} |")
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print(f"{len(rows)} molecules: pooled RMS B3LYP {pooled['freq_rms_b3lyp']:.2f}, wB97X {pooled['freq_rms_wb97x']:.2f}, K diag {pooled['K_diag_rms']:.2f} cm-1 -> plateau bound {3 * pooled['K_diag_rms']:.2f}; wrote {a.out_prefix}")


if __name__ == "__main__":
    main()
