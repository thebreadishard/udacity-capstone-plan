"""E7 / T2 post-hoc (iv)-(v), 23 September 2026 (NOT pre-registered): capacity ceilings of local representations of ΔH.

Per held-out molecule, ΔH_true is fitted by least squares with ΔH ≈ Bᵀ ΔF B where ΔF is restricted to a sparsity pattern in the primitive
internals — no transfer, so these are ceilings of what a perfect local model of that form could reach:
  (iv) diagonal ΔF (one additive constant per internal coordinate);
  (v)  diagonal + pairs of internals that share at least one atom (local interaction constants);
  (vi) diagonal + pairs sharing an atom + bond–bond pairs in the same ring (Kekulé-type interaction constants two bonds apart).
Read-outs as T2: ΔH residual ratio, ring coupling ratio, ring diagonal RMS, corrected-frequency RMS. Reference: T2's per-type multiplicative
own-fit ceiling (post-hoc (i)) was 0.71 residual, ratio 0.93.
Usage: python e7_t2_ceilings.py <corpus/molecules dir> <out prefix>
"""
import argparse, json, sys, time
from datetime import datetime
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
import e7_t2_posthoc as PH  # noqa: E402
from learning_curve_layerA_v2_descriptors import bond_graph, rings  # noqa: E402
RING = "ring-ip"


def atoms_of(p):
    return [getattr(p, k) for k in ("a", "b", "c", "d") if hasattr(p, k)]


def patterns(m, symbols_coords):
    from geometric.internal import Distance, PrimitiveInternalCoordinates
    from geometric.molecule import Molecule
    symbols, coords = symbols_coords
    symbols = [s.capitalize() for s in symbols]
    M = Molecule(); M.elem = list(symbols); M.xyzs = [np.asarray(coords) * T2.BOHR2ANG]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False)
    prims = ic.Internals; n = len(prims); assert n == len(m["types"])
    at = [set(atoms_of(p)) for p in prims]
    adj = bond_graph(symbols, coords); R = rings(adj)
    ring_of_bond = {}
    for k, p in enumerate(prims):
        if isinstance(p, Distance):
            for ri, r in enumerate(R):
                if p.a in r and p.b in r:
                    ring_of_bond.setdefault(k, set()).add(ri)
    share = np.zeros((n, n), bool); ringpair = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i, n):
            if at[i] & at[j]:
                share[i, j] = share[j, i] = True
            if i in ring_of_bond and j in ring_of_bond and (ring_of_bond[i] & ring_of_bond[j]):
                ringpair[i, j] = ringpair[j, i] = True
    diag = np.eye(n, dtype=bool)
    return {"iv_diag": diag, "v_share_atom": share | diag, "vi_share_or_ringbond": share | ringpair | diag}


def fit_pattern(m, pat):
    """Least squares for ΔF on the pattern (symmetric): vec(ΔH) = A x, A columns = Bᵀ E_ij B (+ transpose)."""
    B = m["B"]; n = B.shape[0]; iu = [(i, j) for i in range(n) for j in range(i, n) if pat[i, j]]
    cols = []
    for i, j in iu:
        E = np.outer(B[i], B[j]); cols.append((E + E.T).ravel() if i != j else E.ravel())
    A = np.stack(cols, 1); y = m["dH_true"].ravel()
    x, *_ = np.linalg.lstsq(A, y, rcond=None)
    dF = np.zeros((n, n))
    for (i, j), v in zip(iu, x):
        dF[i, j] = v; dF[j, i] = v
    return dF, len(iu)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("molecules"); ap.add_argument("out_prefix"); a = ap.parse_args(); t0 = time.time()
    mols = T2.load(a.molecules)
    test_a, test_b, cores, pool = E6.splits(mols)
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    tests = {"a": [i for i in test_a if i in mols], "b": [i for i in test_b if i in mols]}; tr = [i for i in pool if i in mols]
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "posthoc": True}
    for h, ids in tests.items():
        fits = {}
        for i in ids:
            g = json.load(open(Path(a.molecules) / i / "geometry.json"))
            pats = patterns(mols[i], (g["symbols"], np.asarray(g["coords_bohr"])))
            for name, pat in pats.items():
                dF, npar = fit_pattern(mols[i], pat); fits.setdefault(name, {})[i] = (dF, npar)
        for name in fits:
            recs = [dict(E6.readout({i: PH.k_of(mols[i], fits[name][i][0])}, mols, [i], tr), **T2.basis_free({i: PH.k_of(mols[i], fits[name][i][0])}, mols, [i]),
                         dH_residual_ratio=float(np.sqrt(np.mean((mols[i]["B"].T @ fits[name][i][0] @ mols[i]["B"] - mols[i]["dH_true"]) ** 2) / np.mean(mols[i]["dH_true"] ** 2))),
                         n_par=fits[name][i][1], n_cart=mols[i]["dH_true"].shape[0] * (mols[i]["dH_true"].shape[0] + 1) // 2) for i in ids]
            agg = {k: (float(np.nanmean([r[k] for r in recs])) if not isinstance(recs[0][k], dict) else {F: float(np.nanmean([r[k][F] for r in recs])) for F in recs[0][k]}) for k in recs[0]}
            res[f"{name}_{h}"] = agg
            print(f"({h}) {name:22s} params/cart {agg['n_par']:.0f}/{agg['n_cart']:.0f} | ΔH residual {agg['dH_residual_ratio']:.2f} | ring diag {agg['diag_rms'][RING]:6.2f} | ring couplings ratio {agg['coupling_ratio']:.2f} | corrected ω {agg['corrected_freq_rms']:.2f} (zero {agg['corrected_freq_rms_zero_rule']:.2f}) | overlap {agg['duschinsky_overlap_median']:.3f}", flush=True)
    res["seconds"] = round(time.time() - t0); json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E7 / T2 post-hoc ceilings ({res['date']}) — NOT pre-registered; per-molecule own fits, no transfer", "",
          "| hold-out | pattern | parameters / Cartesian elements | ΔH residual ratio | ring diag | ring coupling ratio | corrected ω RMS (zero rule) | overlap median |", "|---|---|---|---|---|---|---|---|"]
    for h in ("a", "b"):
        for name in ("iv_diag", "v_share_atom", "vi_share_or_ringbond"):
            x = res[f"{name}_{h}"]
            md.append(f"| ({h}) | {name} | {x['n_par']:.0f} / {x['n_cart']:.0f} | {x['dH_residual_ratio']:.2f} | {x['diag_rms'][RING]:.2f} | **{x['coupling_ratio']:.2f}** | {x['corrected_freq_rms']:.2f} ({x['corrected_freq_rms_zero_rule']:.2f}) | {x['duschinsky_overlap_median']:.3f} |")
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n"); print("wrote", a.out_prefix, f"in {res['seconds']} s")


if __name__ == "__main__":
    main()
