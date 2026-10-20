"""E8 between-branch (pre-registration PreRegistration_2026-09-23_E8_CC_Correction_Locality.md, section "Between-branch"): extend the pattern and
repeat the projection; and read each pattern by its least-squares fit as well as by the masked minimum-norm projection.

Reuses e8_cc_locality.py (same directory): the DFT references (pyscf analytic B3LYP / ωB97X Hessians at the CC basis, grid 99/590), normal modes,
families, geomeTRIC primitives and patterns, the read-out; the CC Hessian is read from the saved npz.

Patterns: (c) diagonal + atom-sharing + ring bond–bond pairs (control); (d) (c) + pairs two bonds apart; (e) all pairs of primitives inside one ring;
(f) all pairs. Read-outs per pattern: mask (zero the minimum-norm ΔF outside the pattern) and fit (least-squares ΔF supported on the pattern that best
reproduces ΔH in Cartesian norm). Decision rule: the smallest pattern whose *fit* gives residual ≤ 0.35 and ring coupling ratio ≤ 0.5 on CC − B3LYP.

Usage: python e8_between_extension.py <geometry.json> <hessian_ccsd_t.npz> <out prefix> [--threads 16] [--basis cc-pvdz]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e8_cc_locality as E

FIT_KEY = f"{E.CC_KEY} | fit"


def extended_patterns(symbols, coords_bohr):
    """B, the pattern masks (c), (d), (e), (f) over geomeTRIC primitives, the number of primitives and of bonds among them."""
    from geometric.internal import Distance
    prims, B = E.primitives(symbols, coords_bohr)
    n = len(prims)
    atoms = E.primitive_atoms(prims)
    adj = E.bond_graph([s.capitalize() for s in symbols], coords_bohr)
    # (d): pairs whose atom sets are disjoint but connected by one bond ("two bonds apart" for bond–bond pairs)
    two_apart = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i + 1, n):
            if not atoms[i] & atoms[j] and any(b in adj[a] for a in atoms[i] for b in atoms[j]):
                two_apart[i, j] = two_apart[j, i] = True
    # (e): all pairs of primitives whose atoms all lie inside the same ring
    ring_sets = [set(r) for r in E.rings(adj)]
    prim_rings = [{k for k, r in enumerate(ring_sets) if atoms[i] <= r} for i in range(n)]
    in_ring = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i, n):
            if prim_rings[i] & prim_rings[j]:
                in_ring[i, j] = in_ring[j, i] = True
    c = E.pattern_masks(prims, symbols, coords_bohr)[E.PATTERN_C]
    pats = {"(c) control": c, "(d) (c) + pairs two bonds apart": c | two_apart, "(e) all pairs inside a ring": c | in_ring,
            "(f) all pairs": np.ones((n, n), bool)}
    return B, pats, n, sum(isinstance(p, Distance) for p in prims)


def mask_projection(dH, B, Bp, pat):
    dF = Bp.T @ dH @ Bp
    return B.T @ (dF * pat) @ B


def fit_projection(dH, B, pat):
    """Least-squares ΔF supported on the (symmetric) pattern: minimise ||Bᵀ ΔF B − ΔH||_F over the free upper-triangle entries."""
    n = B.shape[0]
    iu = [(i, j) for i in range(n) for j in range(i, n) if pat[i, j]]
    cols = []
    for i, j in iu:
        Eij = np.outer(B[i], B[j])
        cols.append((Eij + Eij.T).ravel() if i != j else Eij.ravel())
    x, *_ = np.linalg.lstsq(np.array(cols).T, dH.ravel(), rcond=None)
    dF = np.zeros((n, n))
    for (i, j), v in zip(iu, x, strict=True):
        dF[i, j] = v
        dF[j, i] = v
    return B.T @ dF @ B, len(iu)


def pattern_reads(pats: dict, dHs: dict, B: np.ndarray, modes: tuple, H_low: np.ndarray, masses: np.ndarray) -> tuple[dict, list[str]]:
    """Per pattern its pair count and the read of every correction by mask and by fit; the md rows beside."""
    w, freq, V, fam = modes
    Bp = np.linalg.pinv(B)
    reads, rows = {}, []
    for pname, pat in pats.items():
        reads[pname] = {"n_pairs": int(np.triu(pat).sum())}
        for k, dH in dHs.items():
            for mode in ("mask", "fit"):
                pred = mask_projection(dH, B, Bp, pat) if mode == "mask" else fit_projection(dH, B, pat)[0]
                r = E.readout(pred, dH, H_low, masses, freq, V, fam, w)
                reads[pname][f"{k} | {mode}"] = r
                rows.append(f"| {pname} ({reads[pname]['n_pairs']} pairs) | {k} | {mode} | {r['dH_residual_ratio']:.2f} | {r['ring_coupling_ratio']:.2f} | "
                            f"{r['ring_diag_rms']:.2f} | {r['corrected_freq_rms']:.2f} ({r['corrected_freq_rms_zero_rule']:.2f}) |")
                print(rows[-1], flush=True)
    return reads, rows


def target_pattern(reads: dict) -> str | None:
    """The pre-registered rule: the smallest pattern whose fit meets E8's WIN lines on CC − B3LYP."""
    for pname, r in reads.items():
        if r[FIT_KEY]["dH_residual_ratio"] <= E.WIN_RESIDUAL and r[FIT_KEY]["ring_coupling_ratio"] <= E.WIN_RING:
            return pname
    return None


def main():
    ap = argparse.ArgumentParser()
    for name in ("geometry", "cc_hessian", "out_prefix"):
        ap.add_argument(name)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--basis", default="cc-pvdz")
    a = ap.parse_args()
    from pyscf import lib
    lib.num_threads(a.threads)
    t0 = time.time()
    g = json.loads(Path(a.geometry).read_text())
    sym, x, masses = g["symbols"], np.array(g["coords_bohr"]), np.array(g["masses_amu"])
    with np.load(a.cc_hessian) as z:
        Hcc = z["H_projected"]
    syms = [s.capitalize() for s in sym]
    H = E.dft_hessians(syms, x, masses, a.basis)
    w, freq, V = E.normal_modes(H["b3lyp"], masses)
    fam = E.families(freq, V, syms, masses, x)
    dHs = {E.CC_KEY: Hcc - H["b3lyp"], E.PROXY_KEY: H["wb97x"] - H["b3lyp"]}
    B, pats, n_ic, n_bonds = extended_patterns(sym, x)
    res = {"date": time.strftime("%Y-%m-%d %H:%M"), "basis": a.basis, "n_internals": n_ic, "n_bonds": n_bonds, "patterns": {}}
    res["patterns"], rows = pattern_reads(pats, dHs, B, (w, freq, V, fam), H["b3lyp"], masses)
    target = target_pattern(res["patterns"])
    res["target_pattern_by_rule"] = target
    res["seconds"] = round(time.time() - t0)
    E.write_text(a.out_prefix + ".json", json.dumps(res, indent=1, ensure_ascii=False))
    md = [f"# E8 between-branch — pattern extension and least-squares ceilings, {a.basis} ({res['date']})", "",
          f"Internals: {n_ic} ({n_bonds} bonds). mask = minimum-norm ΔF zeroed outside the pattern; fit = least-squares ΔF on the pattern.", "",
          "| pattern | correction | read | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |",
          "|---|---|---|---|---|---|---|", *rows]
    md += ["", "**Target pattern by the pre-registered rule (smallest with fit residual ≤ 0.35 and ring coupling ratio ≤ 0.5 on CC − B3LYP): "
           f"{target}.**", f"Total {res['seconds']} s."]
    E.write_text(a.out_prefix + ".md", "\n".join(md) + "\n")
    print("wrote", a.out_prefix, "target:", target)


if __name__ == "__main__":
    main()
