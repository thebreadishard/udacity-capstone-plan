"""E7 / T2 — the chemical null hypothesis: SQM scale factors per internal-coordinate type carry the couplings
(pre-registered 23 September 2026, PreRegistration_2026-09-23_E7_Couplings_in_Local_Coordinates.md).

For every molecule: redundant primitive internal coordinates from the B3LYP geometry (geomeTRIC PrimitiveInternalCoordinates), Wilson B,
internal force constants F = B⁺ᵀ H B⁺ for both Cartesian Hessians (H_projected; the high level's gradient term is not available and sits in
the residual). Each primitive gets a type (bond: element pair + ring; angle: centre, sorted neighbours, ring; dihedral: central bond elements
+ ring; out-of-plane / linear: centre element). Scale factors s_t (types seen ≥ 5 times in training; others 1) by Gauss–Newton least squares
over all elements i ≤ j of F: F_high,ij ≈ √(s_i s_j) F_low,ij (Pulay's SQM prescription). Prediction for held-out molecules:
ΔF = (√(s_i s_j) − 1) F_low, ΔH = Bᵀ ΔF B, mass-weighted and projected onto the B3LYP modes → K_pred; read with the E6 read-outs (diagonal per
family, ring coupling RMS and ratio to the zero rule, ring block vs the median rule) on hold-outs (a) and (b), plus the basis-free read-out
(corrected frequencies after diagonalisation, Duschinsky overlap). Also reported: the same scale factors applied to the diagonal only
("SQM-diag": couplings zero) to isolate what the couplings buy.

Usage: python e7_t2_sqm.py <corpus/molecules dir> <out prefix> [--sizes 45,all] [--min-count 5] [--iters 30] [--smoke]
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
from learning_curve_layerA import AMU2AU, FAMILIES, HARTREE2CM, normal_modes  # noqa: E402
from learning_curve_layerA_v2_descriptors import bond_graph, rings  # noqa: E402

RING = "ring-ip"
BOHR2ANG = 0.529177210903


# ------------------------------------------------------------------------------------------------------- internal coordinates
def internals(symbols, coords_bohr):
    from geometric.internal import Angle, Dihedral, Distance, LinearAngle, OutOfPlane, PrimitiveInternalCoordinates
    from geometric.molecule import Molecule
    symbols = [s.capitalize() for s in symbols]           # the corpus writes upper-case symbols ("CL"); geomeTRIC's table wants "Cl"
    M = Molecule(); M.elem = list(symbols); M.xyzs = [np.asarray(coords_bohr) * BOHR2ANG]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False)
    xyz = np.asarray(coords_bohr, float).flatten()
    B = np.asarray(ic.wilsonB(xyz))                      # (n_ic, 3N)
    adj = bond_graph(symbols, coords_bohr); R = rings(adj)
    ring_bonds = {frozenset((a, b)) for r in R for a in r for b in r if a < b and b in adj[a]}
    types = []
    for p in ic.Internals:
        if isinstance(p, Distance):
            e = tuple(sorted((symbols[p.a], symbols[p.b]))); types.append(("bond", *e, frozenset((p.a, p.b)) in ring_bonds))
        elif isinstance(p, Angle):
            e = tuple(sorted((symbols[p.a], symbols[p.c])))
            types.append(("angle", symbols[p.b], *e, frozenset((p.a, p.b)) in ring_bonds and frozenset((p.b, p.c)) in ring_bonds))
        elif isinstance(p, LinearAngle):
            types.append(("linear", symbols[p.b]))
        elif isinstance(p, Dihedral):
            e = tuple(sorted((symbols[p.b], symbols[p.c]))); types.append(("dihedral", *e, frozenset((p.b, p.c)) in ring_bonds))
        elif isinstance(p, OutOfPlane):
            types.append(("oop", symbols[p.a]))
        else:
            types.append((type(p).__name__,))
    return B, types


def to_internal(H, B):
    Bp = np.linalg.pinv(B)                               # (3N, n_ic)
    F = Bp.T @ H @ Bp
    rec = B.T @ F @ B
    return F, float(np.sqrt(np.mean((rec - H) ** 2)) / (np.sqrt(np.mean(H ** 2)) + 1e-30))


def load(mdir):
    mols = E6.load_corpus(Path(mdir))                    # tokens, family, freq, K, layer, core, imaginary
    for i, m in mols.items():
        d = Path(mdir) / i
        g = json.load(open(d / "geometry.json")); masses = np.asarray(g["masses_amu"]); coords = np.asarray(g["coords_bohr"])
        lo = np.load(d / "hessian_b3lyp.npz")["H_projected"]; hi = np.load(d / "hessian_wb97x.npz")["H_projected"]
        w, f, V, _ = normal_modes(lo, masses)
        B, types = internals(g["symbols"], coords)
        Fl, rec_l = to_internal(lo, B); Fh, rec_h = to_internal(hi, B)
        m.update(masses=masses, V=V, w=w, B=B, types=types, F_low=Fl, F_high=Fh, H_low=lo, dH_true=hi - lo, rec_err=max(rec_l, rec_h))
    return mols


# ------------------------------------------------------------------------------------------------------------------ SQM fit
def fit_scale_factors(mols, tr, min_count, iters):
    counts = {}
    for i in tr:
        for t in mols[i]["types"]:
            counts[t] = counts.get(t, 0) + 1
    fitted = sorted(t for t, c in counts.items() if c >= min_count); idx = {t: k for k, t in enumerate(fitted)}
    theta = np.zeros(len(fitted))                                     # s_t = exp(theta_t)
    # start from the diagonal ratios per type
    num = np.zeros(len(fitted)); den = np.zeros(len(fitted))
    for i in tr:
        m = mols[i]; dl = np.diag(m["F_low"]); dh = np.diag(m["F_high"])
        for k, t in enumerate(m["types"]):
            if t in idx and dl[k] > 1e-6:
                num[idx[t]] += dh[k] * dl[k]; den[idx[t]] += dl[k] * dl[k]
    theta = np.log(np.clip(num / np.maximum(den, 1e-30), 0.5, 2.0))
    theta[den == 0] = 0.0
    hist = []
    for it in range(iters):
        JtJ = np.zeros((len(fitted), len(fitted))); Jtr = np.zeros(len(fitted)); sse = 0.0; nres = 0
        for i in tr:
            m = mols[i]; tt = m["types"]; n = len(tt)
            ti = np.array([idx.get(t, -1) for t in tt])
            s = np.where(ti >= 0, np.exp(theta[np.maximum(ti, 0)]), 1.0)
            S = np.sqrt(np.outer(s, s)); pred = S * m["F_low"]; r = m["F_high"] - pred
            iu = np.triu_indices(n); rv = r[iu]; sse += float(np.sum(rv ** 2)); nres += rv.size
            # d pred_ij / d theta_t = ½ pred_ij (δ_{ti=t} + δ_{tj=t});  residual derivative = −that
            g = -0.5 * pred[iu]; a_i = ti[iu[0]]; a_j = ti[iu[1]]
            for a_idx, other in ((a_i, a_j), (a_j, a_i)):
                ok = a_idx >= 0
                np.add.at(Jtr, a_idx[ok], g[ok] * rv[ok])
                np.add.at(JtJ, (a_idx[ok], a_idx[ok]), g[ok] * g[ok])
                both = ok & (other >= 0)
                np.add.at(JtJ, (a_idx[both], other[both]), g[both] * g[both])
        hist.append(np.sqrt(sse / max(nres, 1)))
        step = np.linalg.solve(JtJ + 1e-8 * np.eye(len(fitted)), -Jtr)
        theta = np.clip(theta + step, np.log(0.5), np.log(2.0))
        if np.max(np.abs(step)) < 1e-6:
            break
    return {t: float(np.exp(theta[idx[t]])) for t in fitted}, counts, hist


def predict_dH(m, s_of_type):
    s = np.array([s_of_type.get(t, 1.0) for t in m["types"]])
    dF = (np.sqrt(np.outer(s, s)) - 1.0) * m["F_low"]
    return m["B"].T @ dF @ m["B"]


def K_from_dH(m, dH):
    mm = np.repeat(m["masses"] * AMU2AU, 3)
    dHmw = dH / np.sqrt(np.outer(mm, mm))
    Km = m["V"].T @ dHmw @ m["V"]; om = np.sqrt(np.abs(m["w"]))
    return (Km / (2 * np.sqrt(np.outer(om, om))) * HARTREE2CM).astype(np.float64)


def basis_free(P, mols, ids):
    """Corrected frequencies from Ω² + 2√(ω_i ω_j) K (cm⁻²) with K_pred against K_true, and the Duschinsky overlap of the corrected modes."""
    dfreq, dfreq_zero, overlap = [], [], []
    for i in ids:
        m = mols[i]; w = np.abs(m["freq"]); S = np.sqrt(np.outer(w, w)); fam = np.array(m["family"])
        same = fam[:, None] == fam[None, :]
        def corrected(K):
            Kb = np.where(same, K, 0.0); Kb = 0.5 * (Kb + Kb.T)
            ev, U = np.linalg.eigh(np.diag(w ** 2) + 2 * S * Kb); return np.sqrt(np.abs(ev)), U
        wt, Ut = corrected(m["K"]); wp, Up = corrected(P[i]); w0, U0 = corrected(np.zeros_like(m["K"]))
        dfreq.append(wp - wt); dfreq_zero.append(w0 - wt)
        overlap.append(np.max(np.abs(Up.T @ Ut), axis=1))
    return {"corrected_freq_rms": E6.rms(np.concatenate(dfreq)), "corrected_freq_rms_zero_rule": E6.rms(np.concatenate(dfreq_zero)),
            "duschinsky_overlap_median": float(np.median(np.concatenate(overlap))), "duschinsky_overlap_p10": float(np.percentile(np.concatenate(overlap), 10))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--sizes", default="45,all"); ap.add_argument("--min-count", type=int, default=5); ap.add_argument("--iters", type=int, default=30)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(); t0 = time.time()
    mols = load(a.molecules)
    test_a, test_b, cores, pool = E6.splits(mols)
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    test_a = [i for i in test_a if i in mols]; test_b = [i for i in test_b if i in mols]; pool = [i for i in pool if i in mols]
    sizes = sorted({min(int(s) if s != "all" else len(pool), len(pool)) for s in a.sizes.split(",")})
    if a.smoke:
        sizes = sizes[:1]; a.iters = 3
    rec = np.array([m["rec_err"] for m in mols.values()])
    n_ic = np.array([len(m["types"]) for m in mols.values()])
    print(f"{len(mols)} molecules; internals per molecule {n_ic.min()}–{n_ic.max()}; Cartesian reconstruction error Bᵀ F B vs H: median {np.median(rec):.2e}, max {rec.max():.2e}; "
          f"hold-out (a) {len(test_a)}, (b) {len(test_b)} ({cores}); pool {len(pool)}; sizes {sizes}", flush=True)
    tests = {"a": test_a, "b": test_b}
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "smoke": a.smoke, "n_molecules": len(mols), "reconstruction_error_median": float(np.median(rec)),
           "reconstruction_error_max": float(rec.max()), "holdout_a": test_a, "holdout_b": test_b, "scaffold_cores": cores, "pool": len(pool), "sizes": sizes,
           "min_count": a.min_count, "curve": {}}
    for n in sizes:
        tr = pool[:n]
        s_of, counts, hist = fit_scale_factors(mols, tr, a.min_count, a.iters)
        row = {"n": n, "n_types_fitted": len(s_of), "n_types_seen": len(counts), "fit_rms_history_au": [float(h) for h in hist],
               "scale_factors": {" ".join(str(x) for x in t): (v, counts[t]) for t, v in s_of.items()}}
        for h, ids in tests.items():
            P = {i: K_from_dH(mols[i], predict_dH(mols[i], s_of)) for i in ids}
            Pd = {i: np.diag(np.diag(P[i])) for i in ids}
            P0 = {i: np.zeros_like(mols[i]["K"]) for i in ids}
            row[h] = {"sqm": dict(E6.readout(P, mols, ids, tr), **basis_free(P, mols, ids)),
                      "sqm_diag_only": dict(E6.readout(Pd, mols, ids, tr), **basis_free(Pd, mols, ids)),
                      "zero": dict(E6.readout(P0, mols, ids, tr), **basis_free(P0, mols, ids)),
                      "dH_cartesian_rms_ratio": float(np.sqrt(np.mean([np.mean((predict_dH(mols[i], s_of) - mols[i]["dH_true"]) ** 2) for i in ids]) /
                                                              np.mean([np.mean(mols[i]["dH_true"] ** 2) for i in ids])))}
            r = row[h]["sqm"]
            print(f"n={n:3d} ({h}) SQM: diag " + " ".join(f"{F} {r['diag_rms'][F]:6.2f} |" for F in FAMILIES)
                  + f" ring couplings {r['coupling_rms']:.2f} vs zero {r['coupling_zero_rms']:.2f} (ratio {r['coupling_ratio']:.2f}) | block {r['block_rms']:.2f} vs median {r['block_median_rule_rms']:.2f}"
                  + f" | corrected ω RMS {r['corrected_freq_rms']:.2f} (zero rule {r['corrected_freq_rms_zero_rule']:.2f}) | overlap median {r['duschinsky_overlap_median']:.3f} | ΔH Cartesian residual ratio {row[h]['dH_cartesian_rms_ratio']:.2f} | types fitted {len(s_of)}", flush=True)
        res["curve"][str(n)] = row
        json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    nf = str(sizes[-1]); ra = res["curve"][nf]["a"]["sqm"]["coupling_ratio"]; rb = res["curve"][nf]["b"]["sqm"]["coupling_ratio"]
    verdict = "WIN" if (ra <= 0.8 and rb <= 0.9) else ("LOSE" if ra >= 1.0 else "between")
    res["verdict"] = {"ring_coupling_ratio_a": ra, "ring_coupling_ratio_b": rb, "verdict": verdict}; res["seconds"] = round(time.time() - t0)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E7 / T2 — SQM scale factors per internal-coordinate type ({res['date']}){' — SMOKE, NOT A RESULT' if a.smoke else ''}", "",
          f"{len(mols)} molecules (imaginary-mode molecules excluded after the E6 split); hold-out (a) {len(test_a)} layer-A molecules, (b) scaffold cores {cores} ({len(test_b)}); pool {len(pool)}. "
          f"Internals: geomeTRIC primitives, Bᵀ F B reconstruction error median {np.median(rec):.1e}. Types fitted (≥ {a.min_count} occurrences): "
          + ", ".join(str(res['curve'][str(n)]['n_types_fitted']) for n in sizes) + f" at n = {sizes}. RMS in cm⁻¹.", "",
          "| n | hold-out | model | " + " | ".join(f"diag {F}" for F in FAMILIES) + " | ring coupling RMS / zero | ratio | ring block / median | corrected ω RMS (zero rule) | overlap median |",
          "|---|---|---|" + "---|" * (len(FAMILIES) + 5)]
    for n in sizes:
        for h in ("a", "b"):
            for name in ("zero", "sqm_diag_only", "sqm"):
                r = res["curve"][str(n)][h][name]
                md.append(f"| {n} | ({h}) | {name} | " + " | ".join(f"{r['diag_rms'][F]:.2f}" for F in FAMILIES)
                          + f" | {r['coupling_rms']:.2f} / {r['coupling_zero_rms']:.2f} | **{r['coupling_ratio']:.2f}** | {r['block_rms']:.2f} / {r['block_median_rule_rms']:.2f} | {r['corrected_freq_rms']:.2f} ({r['corrected_freq_rms_zero_rule']:.2f}) | {r['duschinsky_overlap_median']:.3f} |")
    sf = res["curve"][nf]["scale_factors"]
    md += ["", f"## Scale factors at n = {nf} (type: s, count)", ""] + [f"- {t}: {v:.4f} ({c})" for t, (v, c) in sorted(sf.items())]
    md += ["", f"**Verdict (pre-registered, n = {nf}):** ring coupling ratio (a) {ra:.2f}, (b) {rb:.2f} → **{verdict}**.", "", f"Total {res['seconds']} s."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md", f"in {res['seconds']} s", flush=True)


if __name__ == "__main__":
    main()
