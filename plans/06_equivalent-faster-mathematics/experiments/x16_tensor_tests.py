"""X16 (written 2026-09-13, before the naphthalene tensor exists) — the pre-registered test battery for a Δ₂ tensor: X10 (P25's licence
test), X11 (products on the selected patterns), X9 (correction vs mean-field profile by bond-graph distance) and X8 (real-pattern rows),
run unchanged on any molecule's dry-run stage-A output. Serves the decision rule: P25's licence (branch C) and T3/X9 beyond one ring (branch M).

Input: plan 05 `probes/results_dryrun/<molecule>/stageA_hessians.npz` (H_low, H_high, L, omega_au, D2_direct_Q, Minv, coords) and
`stageA.json` (symbols, freq_low_cm, families). Irreps: from `stageC_symmetry_prior.json` when present (benzene, the dry run's own D6h
labels), otherwise from a D2h character analysis of the stage-A modes (planar molecules; the operations are checked to be symmetries).

Self-test (today): `--molecule benzene` must reproduce X10 (19 / 17 / 6 pairs at 0.5 cm⁻¹), X11 (4 / 3 / 2 products) and X9's ratio profile
(0.027 on-atom → 0.065 at three bonds) from the stored benzene tensor; the assertions are in the code. The naphthalene run
(`--molecule naphthalene`) is the licence test of draft P25 with its pre-stated winning/losing conditions (P25 §3), printed verbatim.
Every number printed comes from the files; constants in CONSTANTS."""
import argparse
import json
import sys
from collections import deque
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from x1c_triangular_substitution import (smallest_last_order, lower_pattern, intersection_graph,  # noqa: E402
                                         sequential_colouring, is_proper, recover_by_substitution)
from x13_naphthalene_mode_table import OPS, D2H, inertial_frame  # noqa: E402

PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
HARTREE_TO_CM = 219474.63
CONSTANTS = {"tolerances_cm": [0.5, 0.1], "bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "retention_levels": [0.9, 0.99, 0.999, 0.9999], "random_seed": 0,
             "p25_licence": {"win": "DFT-only ranking reaches 0.5 cm-1 with at most half the eligible pairs AND within a factor 1.5 of the oracle-magnitude count",
                             "lose": "more than half the eligible pairs, or a factor above 1.5"},
             "benzene_expected": {"x10_n_needed": [19, 17, 6], "x11_products": [4, 3, 2], "x9_ratio_d0_d3": [0.0268, 0.0647], "x8_first_row": [20, 41.69]}}


def freqs_from_W2(W2):
    w2 = np.linalg.eigvalsh((W2 + W2.T) / 2); return np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM


def freqs_from_Hmw(Hmw, nzero=6):
    w2 = np.linalg.eigvalsh((Hmw + Hmw.T) / 2); w2 = w2[np.argsort(np.abs(w2))][nzero:]
    return np.sort(np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM)


def graph_distance(sym, X):
    n = len(sym); D = np.linalg.norm(X[:, None] - X[None], axis=2)
    adj = [[j for j in range(n) if j != i and D[i, j] < CONSTANTS["bond_cutoff_bohr"].get("".join(sorted(sym[i] + sym[j])), 0.0)] for i in range(n)]
    G = np.full((n, n), 99, int)
    for s in range(n):
        G[s, s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if G[s, v] == 99:
                    G[s, v] = G[s, u] + 1; q.append(v)
    return G


def irreps_d2h(sym, X, m, L, freq):
    """D2h labels of the mode vectors L (3N × M, mass-weighted, in the input frame): rotate into the inertial frame, apply the eight operations."""
    nat = len(sym); Y, R = inertial_frame(X, m)
    Lf = (np.kron(np.eye(nat), R).T @ L)
    perms = {}
    for op, Rm in OPS.items():
        Yt = Y @ Rm.T; perm = []
        for a in range(nat):
            d = np.linalg.norm(Y - Yt[a], axis=1); b = int(np.argmin(d))
            if d[b] > 1e-2 or sym[b] != sym[a]:
                raise RuntimeError(f"operation {op} is not a symmetry (atom {a}, residual {d[b]:.2e}); D2h labels unavailable")
            perm.append(b)
        perms[op] = perm
    labels = []
    for k in range(L.shape[1]):
        v = Lf[:, k].reshape(nat, 3); ch = []
        for op, Rm in OPS.items():
            Rv = np.zeros_like(v)
            for a in range(nat):
                Rv[perms[op][a]] = Rm @ v[a]
            ch.append(int(round(float((v * Rv).sum()))))
        labels.append([next((nm for nm, c in D2H.items() if ch == c), "?")])
    return labels


def count_products(P, rng):
    M = P.shape[0]; H = P.copy(); np.fill_diagonal(H, False)
    pos = smallest_last_order(H); Lp = lower_pattern(P, pos); Gu = intersection_graph(Lp)
    maxr = int(Lp.sum(1).max())
    c_lf = sequential_colouring(Gu, list(np.argsort(-Gu.sum(1)))); pos_gu = smallest_last_order(Gu)
    c_sl = sequential_colouring(Gu, sorted(range(M), key=lambda v: pos_gu[v]))
    cands = [(int(c.max() + 1), nm, c) for c, nm in ((c_lf, "largest-first"), (c_sl, "smallest-last")) if is_proper(Gu, c)]
    k, nm, colour = min(cands, key=lambda t: t[0])
    Rm = rng.standard_normal((M, M)); Rm = (Rm + Rm.T) / 2; Rm[~P] = 0.0
    probes = [Rm @ (colour == q).astype(float) for q in range(k)]
    err = float(np.abs(recover_by_substitution(P, pos, colour, probes) - Rm).max())
    return maxr, k, err


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--molecule", default="benzene"); args = ap.parse_args()
    d = PLAN05 / f"probes/results_dryrun/{args.molecule}"
    z = np.load(d / "stageA_hessians.npz"); a = json.load(open(d / "stageA.json"))
    L, w, DQ, Minv, X = z["L"], z["omega_au"], z["D2_direct_Q"], z["Minv"], z["coords"]
    sym = a["symbols"]; nat = len(sym); M = len(w); m_amu = np.array(a["masses_amu"])
    rng = np.random.default_rng(CONSTANTS["random_seed"])
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "molecule": args.molecule, "M": M, "constants": CONSTANTS}
    # ---- irreps
    sp = d / "stageC_symmetry_prior.json"
    if sp.exists():
        spj = json.load(open(sp)); labels = [set(l) for l in spj["labels"]]; grp = {mm: gi for gi, g in enumerate(spj["groups"]) for mm in g}
        def is_partner(i, j): return grp[i] == grp[j] and len(labels[i]) == 1 and next(iter(labels[i])).startswith("E")
        out["irreps_source"] = "stageC_symmetry_prior.json"
    else:
        labels = [set(l) for l in irreps_d2h(sym, X, m_amu, L, w * HARTREE_TO_CM)]
        def is_partner(i, j): return False
        out["irreps_source"] = "D2h character analysis of stage-A modes"
    eligible = [(i, j) for i in range(M) for j in range(i + 1, M) if (labels[i] & labels[j]) and not is_partner(i, j) and "?" not in labels[i]]
    # ---- X10: rankings and pairs needed
    W2 = np.diag(w ** 2) + DQ; f0 = freqs_from_W2(W2)
    def shift_keep(pairs):
        Wk = np.diag(np.diag(W2))
        for i, j in pairs: Wk[i, j] = Wk[j, i] = W2[i, j]
        return float(np.abs(freqs_from_W2(Wk) - f0).max())
    den = np.array([1.0 / abs(w[i] ** 2 - w[j] ** 2) for i, j in eligible]); mag = np.array([abs(DQ[i, j]) for i, j in eligible])
    eff = []
    for i, j in eligible:
        Wk = W2.copy(); Wk[i, j] = Wk[j, i] = 0.0; eff.append(float(np.abs(freqs_from_W2(Wk) - f0).max()))
    eff = np.array(eff); preds = {"P1 DFT-only": den, "P2 oracle magnitude": mag, "P3 oracle effect": eff}
    x10 = {"n_eligible": len(eligible), "max_shift_all_eligible_kept_cm": shift_keep(eligible), "max_shift_no_offdiag_cm": shift_keep([])}
    sel = {}
    for name, p in preds.items():
        order = np.argsort(-p); need = {}
        for tol in CONSTANTS["tolerances_cm"]:
            n = next((k for k in range(len(eligible) + 1) if shift_keep([eligible[t] for t in order[:k]]) <= tol), None); need[str(tol)] = n
        x10[name] = need; sel[name] = [eligible[t] for t in order[: (need["0.5"] or 0)]]
    rx = np.argsort(np.argsort(den)); ry = np.argsort(np.argsort(eff)); x10["spearman_P1_vs_P3"] = float(np.corrcoef(rx, ry)[0, 1])
    n1, n2 = x10["P1 DFT-only"]["0.5"], x10["P2 oracle magnitude"]["0.5"]
    x10["p25_licence"] = {"half_eligible": len(eligible) / 2, "n_P1": n1, "n_P2": n2,
                          "verdict": ("WIN" if (n1 is not None and n2 and n1 <= len(eligible) / 2 and n1 <= 1.5 * n2) else "LOSE")}
    out["x10"] = x10
    # ---- X11: products on the selected patterns (+ symmetry prior, dense)
    x11 = {}
    for name, pairs in list(sel.items()) + [("symmetry prior (all eligible)", eligible), ("dense", [(i, j) for i in range(M) for j in range(i + 1, M)])]:
        P = np.eye(M, dtype=bool)
        for i, j in pairs: P[i, j] = P[j, i] = True
        maxr, k, err = count_products(P, rng); x11[name] = {"pairs": len(pairs), "maxr": maxr, "k": k, "gradients": 2 * k, "recovery_err": err}
    out["x11"] = x11
    # ---- X9: correction vs mean field by bond-graph distance (Cartesian, mass-weighted)
    Hlo = Minv[:, None] * z["H_low"] * Minv[None, :]; Dl = Minv[:, None] * (z["H_high"] - z["H_low"]) * Minv[None, :]
    G = graph_distance(sym, X)
    blk = lambda H: np.array([[np.linalg.norm(H[3 * p:3 * p + 3, 3 * q:3 * q + 3]) for q in range(nat)] for p in range(nat)])
    Bl, Bd = blk(Hlo), blk(Dl); x9 = []
    for dd in sorted(set(G[np.triu_indices(nat)].tolist())):
        idx = [(i, j) for i in range(nat) for j in range(i, nat) if G[i, j] == dd]
        x9.append({"d": int(dd), "pairs": len(idx), "median_ratio_Delta_over_H": float(np.median([Bd[i, j] for i, j in idx]) / np.median([Bl[i, j] for i, j in idx]))})  # X9's statistic: ratio of medians
    f_low_full = freqs_from_Hmw(Hlo); f_tot_full = freqs_from_Hmw(Hlo + Dl); band9 = {}
    for dstar in (2, 3, 4, 5):
        if dstar <= G[G < 99].max():
            P = np.kron(G < dstar, np.ones((3, 3), bool))
            band9[str(dstar)] = {"H_low": float(np.abs(freqs_from_Hmw(Hlo * P) - f_low_full).max()), "Delta": float(np.abs(freqs_from_Hmw(Hlo + Dl * P) - f_tot_full).max())}
    out["x9"] = {"profile": x9, "band_shift_zeroing_far_blocks": band9}
    # ---- X8: real-pattern rows (blocks kept by Frobenius retention) at band level
    sw = np.sqrt(w); Hy = L @ (sw[:, None] * z["D2_direct"] * sw[None, :]) @ L.T      # X8/X5's object: the correction projected on the vibrational subspace
    By = blk(Hy); Wf = By ** 2; tot = Wf.sum(); x8 = []
    for f in CONSTANTS["retention_levels"]:
        P = np.eye(nat, dtype=bool); acc = float(np.trace(Wf))
        for wij, i, j in sorted(((Wf[i, j], i, j) for i in range(nat) for j in range(i + 1, nat)), reverse=True):
            if acc / tot >= f: break
            P[i, j] = P[j, i] = True; acc += 2 * wij
        Pc = np.kron(P, np.ones((3, 3), bool)); W2t = np.diag(w ** 2) + L.T @ (Hy * Pc) @ L; sh = float(np.abs(freqs_from_W2(W2t) - f0).max())   # X8's band rule
        x8.append({"retention": f, "blocks_kept_upper": int(P[np.triu_indices(nat)].sum()), "of": nat * (nat + 1) // 2, "max_band_shift_cm": sh})
    out["x8"] = x8
    json.dump(out, open(HERE / f"x16_tensor_tests_{args.molecule}.json", "w"), indent=1)
    # ---- report
    Lns = [f"# X16 — tensor test battery on {args.molecule} ({out['date']}; irreps from {out['irreps_source']})", "",
           f"## X10 — eligible pairs {len(eligible)}; all kept → {x10['max_shift_all_eligible_kept_cm']:.3f} cm⁻¹; none → {x10['max_shift_no_offdiag_cm']:.2f} cm⁻¹; Spearman P1 vs P3 {x10['spearman_P1_vs_P3']:.3f}", "",
           "| ranking | pairs for 0.5 cm⁻¹ | for 0.1 cm⁻¹ |", "|---|---|---|"] + [f"| {n} | **{x10[n]['0.5']}** | {x10[n]['0.1']} |" for n in preds]
    Lns += ["", f"**P25 licence:** n(P1) = {n1}, n(P2) = {n2}, half of eligible = {len(eligible)/2:.1f} → **{x10['p25_licence']['verdict']}** (win: {CONSTANTS['p25_licence']['win']}; lose: {CONSTANTS['p25_licence']['lose']}).", "",
            "## X11 — substitution products", "", "| pattern | pairs | maxr | k | gradients 2k | recovery error |", "|---|---|---|---|---|---|"]
    Lns += [f"| {n} | {r['pairs']} | {r['maxr']} | **{r['k']}** | {r['gradients']} | {r['recovery_err']:.1e} |" for n, r in x11.items()]
    Lns += ["", "## X9 — correction / mean field by bond-graph distance (median block-norm ratio)", "", "| d | pairs | ratio |", "|---|---|---|"] + [f"| {r['d']} | {r['pairs']} | {r['median_ratio_Delta_over_H']:.4f} |" for r in x9]
    Lns += ["", "Band shift from zeroing blocks at graph distance ≥ d*: " + "; ".join(f"d*={k}: H_low {v['H_low']:.1f}, Δ {v['Delta']:.1f} cm⁻¹" for k, v in band9.items()), "",
            "## X8 — real-pattern rows (Frobenius retention → band shift)", "", "| retention | blocks kept | max band shift (cm⁻¹) |", "|---|---|---|"] + [f"| {r['retention']} | {r['blocks_kept_upper']} of {r['of']} | {r['max_band_shift_cm']:.2f} |" for r in x8]
    (HERE / f"x16_tensor_tests_{args.molecule}.md").write_text("\n".join(Lns), encoding="utf-8")
    print("\n".join(Lns).encode("ascii", "replace").decode())
    if args.molecule == "benzene":   # self-test against X10/X11/X9
        exp = CONSTANTS["benzene_expected"]
        got10 = [x10[n]["0.5"] for n in preds]; got11 = [x11[n]["k"] for n in preds]
        r0 = next(r["median_ratio_Delta_over_H"] for r in x9 if r["d"] == 0); r3 = next(r["median_ratio_Delta_over_H"] for r in x9 if r["d"] == 3)
        ok = (got10 == exp["x10_n_needed"] and got11 == exp["x11_products"] and abs(r0 - exp["x9_ratio_d0_d3"][0]) < 1e-3 and abs(r3 - exp["x9_ratio_d0_d3"][1]) < 1e-3
              and x8[0]["blocks_kept_upper"] == exp["x8_first_row"][0] and abs(x8[0]["max_band_shift_cm"] - exp["x8_first_row"][1]) < 0.05)
        print(f"SELF-TEST {'PASSED' if ok else 'FAILED'}: X10 {got10} (expected {exp['x10_n_needed']}), X11 {got11} (expected {exp['x11_products']}), X9 ratios {r0:.4f}/{r3:.4f}, X8 first row {x8[0]['blocks_kept_upper']}/{x8[0]['max_band_shift_cm']:.2f}")
        if not ok: sys.exit(1)


if __name__ == "__main__":
    main()
