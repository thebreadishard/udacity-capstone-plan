"""Compare two Hessian npz files (H_raw, freq_cm) — the two-route check of a symmetry-reduced run against a full one.

Usage: python e8_compare_hessians.py <a.npz> <b.npz> <geometry.json> [--tol-cm 0.5]   → prints max|ΔH|, max |Δfreq| and PASS/FAIL.
"""
import argparse
import json

import numpy as np


def freqs(H, masses):
    sm = np.sqrt(np.repeat(masses, 3)); w = np.linalg.eigvalsh(H / np.outer(sm, sm))
    f = np.sqrt(np.abs(w) / 1822.888486209) * 219474.6313705
    return np.sort(np.where(w < 0, -f, f))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("geometry"); ap.add_argument("--tol-cm", type=float, default=0.5)
    a = ap.parse_args(); m = np.array(json.load(open(a.geometry))["masses_amu"])
    A, B = np.load(a.a), np.load(a.b); dH = float(np.abs(A["H_raw"] - B["H_raw"]).max())
    fa, fb = freqs(A["H_projected"], m), freqs(B["H_projected"], m); df = float(np.abs(fa - fb)[6:].max())
    print(f"max|dH| {dH:.2e} a.u.; max|dfreq| {df:.3f} cm-1 (tol {a.tol_cm}); {'PASS' if df <= a.tol_cm else 'FAIL'}")
    raise SystemExit(0 if df <= a.tol_cm else 1)


if __name__ == "__main__":
    main()
