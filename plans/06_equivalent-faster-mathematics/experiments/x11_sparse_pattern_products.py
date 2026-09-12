"""X11 (2026-09-12, evening) — do the two savings stack? Substitution products on the X10-selected pattern (benzene, mode space).

The cost ladder left one arithmetic open: X10 shrinks the *pattern* (diagonal + the pairs a ranking selects for 0.5 cm⁻¹), S5 shrinks the
*measurements per pattern* (Powell–Toint substitution products, each two gradients). If the products are counted on the smaller pattern, how
many are needed? This script takes X10's three rankings (P1 DFT-only denominators, P2 oracle magnitude, P3 oracle effect), builds the
mode-space pattern 'diagonal + top-n pairs' with n = X10's count for 0.5 cm⁻¹ (read from x10's json), and counts with X1c's unchanged code:
maxr (Coleman & Moré lower bound), the triangular-substitution colours k, and the numerical recovery check. Also printed for reference: the
full symmetry-prior pattern (diagonal + all eligible pairs) and X1c's noise-threshold pattern at θ = 0.5 µE_h. Energies: elements by direct
measurement in the 2M + 2n convention; products as 2·g·k gradient-equivalents; the crossover g* = (2M + 2n)/(2k). Every number from files."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from x1c_triangular_substitution import (smallest_last_order, lower_pattern, intersection_graph,  # noqa: E402
                                         sequential_colouring, is_proper, recover_by_substitution)

PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
CONSTANTS = {"theta_reference_uEh": 0.5, "random_seed": 0}


def count(P, rng):
    M = P.shape[0]; H = P.copy(); np.fill_diagonal(H, False)
    pos = smallest_last_order(H); Lp = lower_pattern(P, pos); Gu = intersection_graph(Lp)
    maxr = int(Lp.sum(1).max())
    c_lf = sequential_colouring(Gu, list(np.argsort(-Gu.sum(1)))); pos_gu = smallest_last_order(Gu)
    c_sl = sequential_colouring(Gu, sorted(range(M), key=lambda v: pos_gu[v]))
    cands = [(int(c.max() + 1), nm, c) for c, nm in ((c_lf, "largest-first"), (c_sl, "smallest-last")) if is_proper(Gu, c)]
    k, nm, colour = min(cands, key=lambda t: t[0])
    R = rng.standard_normal((M, M)); R = (R + R.T) / 2; R[~P] = 0.0
    probes = [R @ (colour == q).astype(float) for q in range(k)]
    err = float(np.abs(recover_by_substitution(P, pos, colour, probes) - R).max())
    return maxr, k, nm, err


def main():
    z = np.load(PLAN05 / "probes/results_dryrun/benzene/stageA_hessians.npz")
    sp = json.load(open(PLAN05 / "probes/results_dryrun/benzene/stageC_symmetry_prior.json"))
    x10 = json.load(open(HERE / "x10_dft_predictable_pairs.json"))
    DQ, DE, w = z["D2_direct_Q"], z["D2_direct"], z["omega_au"]; M = len(w)
    labels = [set(l) for l in sp["labels"]]; grp = {m: gi for gi, g in enumerate(sp["groups"]) for m in g}
    def is_partner(i, j):
        return grp[i] == grp[j] and len(labels[i]) == 1 and next(iter(labels[i])).startswith("E")
    eligible = [(i, j) for i in range(M) for j in range(i + 1, M) if (labels[i] & labels[j]) and not is_partner(i, j)]
    # X2-style drop-one effect for P3, magnitude for P2, denominators for P1 (same definitions as X10)
    HARTREE_TO_CM = 219474.63
    def freqs(W2):
        w2 = np.linalg.eigvalsh((W2 + W2.T) / 2); return np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM
    W2 = np.diag(w ** 2) + DQ; f0 = freqs(W2)
    den = np.array([1.0 / abs(w[i] ** 2 - w[j] ** 2) for i, j in eligible]); mag = np.array([abs(DQ[i, j]) for i, j in eligible])
    eff = []
    for i, j in eligible:
        W = W2.copy(); W[i, j] = W[j, i] = 0.0; eff.append(float(np.abs(freqs(W) - f0).max()))
    eff = np.array(eff)
    rank = {"P1 DFT-only 1/|w_i^2-w_j^2|": den, "P2 oracle |Delta_ij|": mag, "P3 oracle drop-one effect": eff}
    rng = np.random.default_rng(CONSTANTS["random_seed"])
    rows = []
    def add(name, pairs):
        P = np.eye(M, dtype=bool)
        for i, j in pairs:
            P[i, j] = P[j, i] = True
        maxr, k, nm, err = count(P, rng)
        n = len(pairs); E = 2 * M + 2 * n
        rows.append({"pattern": name, "pairs": n, "elements_upper": int(P[np.triu_indices(M)].sum()), "energies_direct_2M_plus_2n": E, "maxr": maxr, "k": k,
                     "colouring": nm, "g_star": E / (2 * k), "recovery_max_abs_error": err})
    for name, p in rank.items():
        n = x10["predictors"][name]["n_needed"]["0.5"]
        order = np.argsort(-p)[:n]
        add(f"X10 {name}: diagonal + top-{n} pairs (0.5 cm⁻¹)", [eligible[t] for t in order])
    add(f"symmetry prior: diagonal + all {len(eligible)} eligible pairs", eligible)
    theta = CONSTANTS["theta_reference_uEh"] * 1e-6 / 2.0
    add(f"X1c noise pattern θ = {CONSTANTS['theta_reference_uEh']} µE_h (|Δ_ij| > θ)", [(i, j) for i in range(M) for j in range(i + 1, M) if abs(DE[i, j]) > theta])
    add("dense", [(i, j) for i in range(M) for j in range(i + 1, M)])
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "M": M, "rows": rows}
    json.dump(out, open(HERE / "x11_sparse_pattern_products.json", "w"), indent=1)
    L = [f"# X11 — substitution products on the X10-selected patterns (benzene, mode space, {out['date']})", "",
         "Counting code: X1c's. Pattern = diagonal + the listed pairs; k = triangular-substitution colours (two sequential colourings of G_u(L_π), the smaller proper one), "
         "maxr = Coleman & Moré's lower bound; recovery verified numerically. Energies: direct measurement 2M + 2n (naive convention, a lower bound on a real deck); "
         "products 2·g·k gradient-equivalents; g* = (2M + 2n)/(2k) is the gradient-to-energy cost ratio below which products win.", "",
         "| pattern | pairs | elements | direct energies (2M + 2n) | maxr | k (products) | g* | recovery error |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['pattern']} | {r['pairs']} | {r['elements_upper']} | {r['energies_direct_2M_plus_2n']} | {r['maxr']} | **{r['k']}** | {r['g_star']:.1f} | {r['recovery_max_abs_error']:.1e} |")
    L += ["", "Reading: if k falls with the pattern, the two savings stack (fewer products on a smaller pattern); if k stays near the diagonal's floor, "
          "the substitution count is already set by the diagonal + a few couplings and X10 adds nothing to S5's side — it then only helps the energies-only deck. "
          "One molecule, one stand-in; naphthalene repeats the count.", "", "Constants: " + json.dumps(CONSTANTS, ensure_ascii=False)]
    (HERE / "x11_sparse_pattern_products.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
