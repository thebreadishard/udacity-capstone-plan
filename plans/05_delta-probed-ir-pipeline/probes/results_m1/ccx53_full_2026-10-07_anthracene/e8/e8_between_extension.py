"""E8 between-branch (pre-registration PreRegistration_2026-09-23_E8_CC_Correction_Locality.md, section "Between-branch"): extend the pattern and
repeat the projection; and read each pattern by its least-squares fit as well as by the masked minimum-norm projection.

Reuses e8_cc_locality.py (same directory): normal modes, families, geomeTRIC primitives, the read-out. Recomputes the DFT references (pyscf analytic
B3LYP / ωB97X Hessians at the CC basis, grid 99/590) exactly as e8_cc_locality did; the CC Hessian is read from the saved npz.

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

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e8_cc_locality as E  # noqa: E402


def extended_patterns(symbols, coords_bohr):
    """Return B and the pattern masks (c), (d), (e), (f) over geomeTRIC primitives."""
    from geometric.internal import Distance
    B, base, n = E.internals(symbols, coords_bohr)
    from geometric.internal import PrimitiveInternalCoordinates
    from geometric.molecule import Molecule
    syms = [s.capitalize() for s in symbols]
    M = Molecule(); M.elem = list(syms); M.xyzs = [np.asarray(coords_bohr) * E.BOHR]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False); prims = ic.Internals
    atoms = [set(getattr(p, k) for k in ("a", "b", "c", "d") if hasattr(p, k)) for p in prims]
    adj = E.bond_graph(syms, coords_bohr); R = E.rings(adj)
    # (d): pairs whose atom sets are disjoint but connected by one bond ("two bonds apart" for bond–bond pairs)
    two_apart = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i + 1, n):
            if atoms[i] & atoms[j]:
                continue
            if any(b in adj[a] for a in atoms[i] for b in atoms[j]):
                two_apart[i, j] = two_apart[j, i] = True
    # (e): all pairs of primitives whose atoms all lie inside the same ring
    in_ring = np.zeros((n, n), bool)
    ring_sets = [set(r) for r in R]
    prim_rings = [[k for k, r in enumerate(ring_sets) if atoms[i] <= r] for i in range(n)]
    for i in range(n):
        for j in range(i, n):
            if set(prim_rings[i]) & set(prim_rings[j]):
                in_ring[i, j] = in_ring[j, i] = True
    c = base["(c) + ring bond-bond pairs"]
    pats = {"(c) control": c, "(d) (c) + pairs two bonds apart": c | two_apart, "(e) all pairs inside a ring": c | in_ring, "(f) all pairs": np.ones((n, n), bool)}
    return B, pats, n, sum(isinstance(p, Distance) for p in prims)


def mask_projection(dH, B, Bp, pat):
    dF = Bp.T @ dH @ Bp
    return B.T @ (dF * pat) @ B


def fit_projection(dH, B, pat):
    """Least-squares ΔF supported on the (symmetric) pattern: minimise ||Bᵀ ΔF B − ΔH||_F over the free upper-triangle entries."""
    n = B.shape[0]; iu = [(i, j) for i in range(n) for j in range(i, n) if pat[i, j]]
    cols = []
    for i, j in iu:
        Eij = np.outer(B[i], B[j]); cols.append((Eij + Eij.T).ravel() if i != j else Eij.ravel())
    A = np.array(cols).T; x, *_ = np.linalg.lstsq(A, dH.ravel(), rcond=None)
    dF = np.zeros((n, n))
    for (i, j), v in zip(iu, x):
        dF[i, j] = v; dF[j, i] = v
    return B.T @ dF @ B, len(iu)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("geometry"); ap.add_argument("cc_hessian"); ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=16); ap.add_argument("--basis", default="cc-pvdz"); a = ap.parse_args()
    from pyscf import lib
    lib.num_threads(a.threads); t0 = time.time()
    g = json.load(open(a.geometry)); sym = g["symbols"]; x = np.array(g["coords_bohr"]); masses = np.array(g["masses_amu"])
    Hcc = np.load(a.cc_hessian)["H_projected"]
    from pyscf import dft, gto
    syms = [s.capitalize() for s in sym]
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(syms, x)], unit="Bohr", basis=a.basis, symmetry=False, verbose=0, max_memory=26000)
    H = {}
    for tag, xc in (("b3lyp", "b3lyp"), ("wb97x", "wb97x")):   # exactly as e8_cc_locality.main
        t1 = time.time(); mf = dft.RKS(mol); mf.xc = xc; mf.grids.atom_grid = (99, 590); mf.grids.prune = None; mf.conv_tol = 1e-11; mf.kernel()
        Hh = mf.Hessian().kernel(); n = len(sym); Hc = Hh.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n); Hc = 0.5 * (Hc + Hc.T)
        H[tag] = E.project_tr(Hc, masses, x); print(f"{tag}/{a.basis} analytic Hessian: {time.time() - t1:.0f} s", flush=True)
    w, freq, V = E.normal_modes(H["b3lyp"], masses); fam = E.families(freq, V, syms, masses, x)
    dHs = {"CC − B3LYP": Hcc - H["b3lyp"], "proxy ωB97X − B3LYP": H["wb97x"] - H["b3lyp"]}
    B, pats, n_ic, n_bonds = extended_patterns(sym, x); Bp = np.linalg.pinv(B)
    res = {"date": time.strftime("%Y-%m-%d %H:%M"), "basis": a.basis, "n_internals": n_ic, "n_bonds": n_bonds, "patterns": {}}
    rows = []
    for pname, pat in pats.items():
        res["patterns"][pname] = {"n_pairs": int(np.triu(pat).sum())}
        for k, dH in dHs.items():
            for mode in ("mask", "fit"):
                pred = mask_projection(dH, B, Bp, pat) if mode == "mask" else fit_projection(dH, B, pat)[0]
                r = E.readout(pred, dH, H["b3lyp"], masses, freq, V, fam, w); res["patterns"][pname][f"{k} | {mode}"] = r
                rows.append(f"| {pname} ({res['patterns'][pname]['n_pairs']} pairs) | {k} | {mode} | {r['dH_residual_ratio']:.2f} | {r['ring_coupling_ratio']:.2f} | "
                            f"{r['ring_diag_rms']:.2f} | {r['corrected_freq_rms']:.2f} ({r['corrected_freq_rms_zero_rule']:.2f}) |")
                print(rows[-1], flush=True)
    # decision rule
    target = None
    for pname in pats:
        r = res["patterns"][pname]["CC − B3LYP | fit"]
        if r["dH_residual_ratio"] <= 0.35 and r["ring_coupling_ratio"] <= 0.5:
            target = pname; break
    res["target_pattern_by_rule"] = target; res["seconds"] = round(time.time() - t0)
    json.dump(res, open(a.out_prefix + ".json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    md = [f"# E8 between-branch — pattern extension and least-squares ceilings, {a.basis} ({res['date']})", "",
          f"Internals: {n_ic} ({n_bonds} bonds). mask = minimum-norm ΔF zeroed outside the pattern; fit = least-squares ΔF on the pattern.", "",
          "| pattern | correction | read | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |", "|---|---|---|---|---|---|---|"] + rows
    md += ["", f"**Target pattern by the pre-registered rule (smallest with fit residual ≤ 0.35 and ring coupling ratio ≤ 0.5 on CC − B3LYP): {target}.**", f"Total {res['seconds']} s."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix, "target:", target)


if __name__ == "__main__":
    main()
