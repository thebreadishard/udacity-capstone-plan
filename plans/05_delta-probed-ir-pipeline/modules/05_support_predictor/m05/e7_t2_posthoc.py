"""E7 / T2 post-hoc checks (23 September 2026; NOT pre-registered — written after T2 read "between, at the lose end").

(i)  Upper bound of the multiplicative SQM form: the per-type scale factors are fitted on each held-out molecule *itself* (all its types, no
     transfer) and read on that molecule. If even this is weak, the form F_high = √(s_i s_j) F_low cannot represent ΔH, whatever the transfer.
(ii) The same transferable per-type factors as T2, but fitted in K-space: the objective is the squared error of the mode-basis correction
     matrix in cm⁻¹ (diagonal and within-family couplings, every mode weighted alike) instead of the internal force constants in atomic units.
     Gauss–Newton with the exact linear map ΔF -> K per molecule.
(iii) Per-type *additive* correction of the diagonal force constants (ΔF_ii = a_t) in addition to the multiplicative factor — the cheapest
     "rung B" step — to see whether the diagonal is the limiting part.

Usage: python e7_t2_posthoc.py <corpus/molecules dir> <out prefix> [--min-count 5] [--iters 20]
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
import e7_t2_sqm as T2  # noqa: E402
from learning_curve_layerA import AMU2AU, FAMILIES, HARTREE2CM  # noqa: E402

RING = "ring-ip"


def kmap(m):
    """Linear map ΔF (n_ic × n_ic) -> K (M × M) in cm⁻¹: K = C ΔF Cᵀ with C = D V^T M^{-1/2} B^T ... returned as the matrix C (M × n_ic)."""
    mm = np.repeat(m["masses"] * AMU2AU, 3)
    om = np.sqrt(np.abs(m["w"]))
    C = (m["V"].T / np.sqrt(mm)[None, :]) @ m["B"].T                 # (M, n_ic): Vᵀ M^{-1/2} Bᵀ
    scale = HARTREE2CM / (2 * np.sqrt(np.outer(om, om)))              # (M, M)
    return C, scale


def k_of(m, dF, C=None, scale=None):
    if C is None:
        C, scale = kmap(m)
    return (C @ dF @ C.T) * scale


def fit_types(mols, tr, min_count, iters, objective, additive=False):
    """Gauss–Newton fit of s_t (and a_t if additive) in the chosen objective: 'F' (a.u., all i<=j) or 'K' (cm⁻¹, diagonal + same-family pairs)."""
    counts = {}
    for i in tr:
        for t in mols[i]["types"]:
            counts[t] = counts.get(t, 0) + 1
    fitted = sorted(t for t, c in counts.items() if c >= min_count); idx = {t: k for k, t in enumerate(fitted)}; P = len(fitted)
    theta = np.zeros(P); alpha = np.zeros(P)
    pre = {}
    for i in tr:
        m = mols[i]; ti = np.array([idx.get(t, -1) for t in m["types"]])
        if objective == "K":
            C, scale = kmap(m); fam = np.array(m["family"]); same = fam[:, None] == fam[None, :]
            W = np.where(same, 1.0, 0.0); W = np.triu(W)                     # diagonal + same-family upper pairs
            pre[i] = (ti, C, scale, W)
        else:
            pre[i] = (ti,)
    hist = []
    for _ in range(iters):
        JtJ = np.zeros((2 * P, 2 * P)); Jtr = np.zeros(2 * P); sse = 0.0; nres = 0
        for i in tr:
            m = mols[i]; ti = pre[i][0]; n = len(ti)
            s = np.where(ti >= 0, np.exp(theta[np.maximum(ti, 0)]), 1.0)
            S = np.sqrt(np.outer(s, s)); predF = S * m["F_low"]
            if additive:
                predF = predF + np.diag(np.where(ti >= 0, alpha[np.maximum(ti, 0)], 0.0))
            # derivative of predF wrt theta_t: ½ (S F_low)_ij (δ_i + δ_j); wrt alpha_t: δ_ij δ_{ti=t}
            if objective == "F":
                r = m["F_high"] - predF; iu = np.triu_indices(n); rv = r[iu]
                g = -0.5 * (S * m["F_low"])[iu]; a_i = ti[iu[0]]; a_j = ti[iu[1]]
                cols, vals = [], []
                cols.append(a_i); vals.append(g); cols.append(a_j); vals.append(g)
                if additive:
                    diag_mask = iu[0] == iu[1]
                    cols.append(np.where(diag_mask & (a_i >= 0), P + np.maximum(a_i, 0), -1)); vals.append(np.where(diag_mask, -1.0, 0.0))
            else:
                ti_, C, scale, W = pre[i]
                r = (m["K"] - k_of(m, predF - m["F_low"], C, scale)) * W; rv = r[W > 0]
                # Jacobian columns: for each type t, dK/dtheta_t = C (½ (S F_low) ∘ (E_t 1ᵀ + 1 E_tᵀ)) Cᵀ ∘ scale
                cols, vals = [], []
                SF = S * m["F_low"]
                for t in range(P):
                    sel = (ti == t).astype(float)
                    if not sel.any():
                        continue
                    dF = 0.5 * SF * (sel[:, None] + sel[None, :])
                    dK = -(C @ dF @ C.T) * scale
                    cols.append(np.full(rv.size, t)); vals.append(dK[W > 0])
                    if additive:
                        dFa = np.diag(sel); dKa = -(C @ dFa @ C.T) * scale
                        cols.append(np.full(rv.size, P + t)); vals.append(dKa[W > 0])
            sse += float(np.sum(rv ** 2)); nres += rv.size
            for c_, v_ in zip(cols, vals):
                ok = c_ >= 0
                np.add.at(Jtr, c_[ok], v_[ok] * (rv[ok] if v_.shape == rv.shape else rv))
            # normal matrix: accumulate all pairs of columns
            M_ = len(cols)
            for a in range(M_):
                for b in range(M_):
                    ca, va = cols[a], vals[a]; cb, vb = cols[b], vals[b]
                    ok = (ca >= 0) & (cb >= 0)
                    np.add.at(JtJ, (ca[ok], cb[ok]), va[ok] * vb[ok])
        hist.append(float(np.sqrt(sse / max(nres, 1))))
        npar = 2 * P if additive else P
        A = JtJ[:npar, :npar] + 1e-9 * np.eye(npar); step = np.linalg.solve(A, -Jtr[:npar])
        theta = np.clip(theta + step[:P], np.log(0.5), np.log(2.0))
        if additive:
            alpha = np.clip(alpha + step[P:], -0.05, 0.05)
        if np.max(np.abs(step)) < 1e-7:
            break
    return {t: float(np.exp(theta[idx[t]])) for t in fitted}, {t: float(alpha[idx[t]]) for t in fitted}, hist


def predict(m, s_of, a_of=None):
    s = np.array([s_of.get(t, 1.0) for t in m["types"]])
    dF = (np.sqrt(np.outer(s, s)) - 1.0) * m["F_low"]
    if a_of:
        dF = dF + np.diag([a_of.get(t, 0.0) for t in m["types"]])
    return dF


def readouts(mols, ids, tr, pred_fn):
    P = {i: k_of(mols[i], pred_fn(mols[i])) for i in ids}
    return dict(E6.readout(P, mols, ids, tr), **T2.basis_free(P, mols, ids),
                dH_residual_ratio=float(np.sqrt(np.mean([np.mean((mols[i]["B"].T @ pred_fn(mols[i]) @ mols[i]["B"] - mols[i]["dH_true"]) ** 2) for i in ids])
                                                / np.mean([np.mean(mols[i]["dH_true"] ** 2) for i in ids]))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix"); ap.add_argument("--min-count", type=int, default=5); ap.add_argument("--iters", type=int, default=20)
    a = ap.parse_args(); t0 = time.time()
    mols = T2.load(a.molecules)
    test_a, test_b, cores, pool = E6.splits(mols)
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    test_a = [i for i in test_a if i in mols]; test_b = [i for i in test_b if i in mols]; pool = [i for i in pool if i in mols]
    tests = {"a": test_a, "b": test_b}; tr = pool
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "posthoc": True, "n_train": len(tr), "holdouts": {h: len(v) for h, v in tests.items()}}
    line = lambda name, x: (f"{name:34s} ring diag {x['diag_rms'][RING]:6.2f} | ring couplings ratio {x['coupling_ratio']:.2f} | block {x['block_rms']:.2f} vs median {x['block_median_rule_rms']:.2f} | "  # noqa: E731
                            f"corrected ω {x['corrected_freq_rms']:.2f} (zero {x['corrected_freq_rms_zero_rule']:.2f}) | ΔH residual {x['dH_residual_ratio']:.2f}")
    # (i) own-fit upper bound: fit on the held-out molecule itself (min_count 1)
    for h, ids in tests.items():
        recs = []
        for i in ids:
            s_of, _, _ = fit_types(mols, [i], 1, a.iters, "F")
            recs.append(readouts(mols, [i], tr, lambda m, s_of=s_of: predict(m, s_of)))
        agg = {k: (float(np.nanmean([r[k] for r in recs])) if not isinstance(recs[0][k], dict) else {F: float(np.nanmean([r[k][F] for r in recs])) for F in recs[0][k]}) for k in recs[0]}
        res[f"own_fit_F_{h}"] = agg; print(f"({h}) " + line("(i) own-fit, F objective", agg), flush=True)
    # (ii) transferable factors fitted in K-space
    s_K, _, hK = fit_types(mols, tr, a.min_count, a.iters, "K")
    for h, ids in tests.items():
        x = readouts(mols, ids, tr, lambda m: predict(m, s_K)); res[f"types_K_{h}"] = x; print(f"({h}) " + line("(ii) per-type, K objective", x), flush=True)
    res["fit_hist_K"] = hK
    # (iii) multiplicative + additive diagonal, K objective
    s_KA, a_KA, hKA = fit_types(mols, tr, a.min_count, a.iters, "K", additive=True)
    for h, ids in tests.items():
        x = readouts(mols, ids, tr, lambda m: predict(m, s_KA, a_KA)); res[f"types_K_additive_{h}"] = x; print(f"({h}) " + line("(iii) per-type + additive diag, K", x), flush=True)
    res["fit_hist_K_additive"] = hKA; res["seconds"] = round(time.time() - t0)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E7 / T2 post-hoc ({res['date']}) — NOT pre-registered", "", f"Training pool {len(tr)}; hold-outs (a) {len(test_a)}, (b) {len(test_b)}. RMS in cm⁻¹.", "",
          "| hold-out | variant | ring diag | ring coupling ratio | ring block / median | corrected ω RMS (zero rule) | ΔH residual ratio |", "|---|---|---|---|---|---|---|"]
    for h in ("a", "b"):
        for name, key in (("(i) own-fit upper bound (F objective)", f"own_fit_F_{h}"), ("(ii) per-type factors, K objective", f"types_K_{h}"), ("(iii) + additive diagonal, K objective", f"types_K_additive_{h}")):
            x = res[key]
            md.append(f"| ({h}) | {name} | {x['diag_rms'][RING]:.2f} | **{x['coupling_ratio']:.2f}** | {x['block_rms']:.2f} / {x['block_median_rule_rms']:.2f} | {x['corrected_freq_rms']:.2f} ({x['corrected_freq_rms_zero_rule']:.2f}) | {x['dH_residual_ratio']:.2f} |")
    md += ["", f"Total {res['seconds']} s."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md", flush=True)


if __name__ == "__main__":
    main()
