"""X14 (2026-09-13) — the gradient cost of plan 05's R1 deck on naphthalene's real symmetry pattern, without any correction tensor.

X13 gave naphthalene's 48 B3LYP modes with their D2h irreps and the 141 same-irrep pairs (= the R1 deck's 282 off-diagonal energies at 2 per
pair). The substitution count (Powell–Toint / Coleman–Moré, X1c's code) depends only on the *pattern*, so lever C of the cost ladder — how many
products, hence how many gradients, a correction at R1 would take — can be counted today on the true pattern instead of extrapolated from
benzene. Patterns counted (mode space, 48 × 48, diagonal always in):
  (a) the symmetry prior: diagonal + all 141 eligible pairs                       — what plan 05's deck measures at R1;
  (b) diagonal + the top 40 % of eligible pairs by the DFT-only denominator 1/|ω_i² − ω_j²|  — benzene's X10 ratio (19 of 47) transplanted, a bracket;
  (c) diagonal + the top 50 %                                                       — the licence boundary of draft P25;
  (d) dense                                                                         — the reference (k = M).
Printed per pattern: pairs, elements, maxr (lower bound), k (products), gradients 2k, and the crossover g* = 474 / (2k) — the gradient-to-energy
cost ratio below which the gradient route costs fewer energy-equivalents than plan 05's R1 deck of 474 energies (proposal §3.2). Also the naive
2M + 2n count of the pattern itself. Recovery verified numerically on a random symmetric matrix with each pattern. Every number from the files;
constants in CONSTANTS. This gives M2a its bar for naphthalene before M2a runs."""
import json
import sys
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from x1c_triangular_substitution import (smallest_last_order, lower_pattern, intersection_graph,  # noqa: E402
                                         sequential_colouring, is_proper, recover_by_substitution)

CONSTANTS = {"R1_deck_energies": 474, "R1_deck_source": "plan 05 proposal §3.2: 96 + 96 + 282", "fractions": [0.4, 0.5], "random_seed": 0,
             "input": "x13_naphthalene_mode_table.json (naphthalene: modes with irreps and frequencies)"}
HARTREE_TO_CM = 219474.63


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
    x13 = json.load(open(HERE / "x13_naphthalene_mode_table.json"))["results"]["naphthalene"]
    modes = x13["modes"]; M = len(modes)
    irr = [m["irrep"] for m in modes]; w = np.array([m["freq_cm"] for m in modes]) / HARTREE_TO_CM
    eligible = [(i, j) for i in range(M) for j in range(i + 1, M) if irr[i] == irr[j] and irr[i] != "?"]
    den = np.array([1.0 / abs(w[i] ** 2 - w[j] ** 2) for i, j in eligible]); order = np.argsort(-den)
    rng = np.random.default_rng(CONSTANTS["random_seed"]); rows = []
    def add(name, pairs):
        P = np.eye(M, dtype=bool)
        for i, j in pairs:
            P[i, j] = P[j, i] = True
        maxr, k, nm, err = count(P, rng); n = len(pairs)
        rows.append({"pattern": name, "pairs": n, "elements_upper": int(P[np.triu_indices(M)].sum()), "naive_energies_2M_plus_2n": 2 * M + 2 * n,
                     "maxr": maxr, "k": k, "gradients_2k": 2 * k, "colouring": nm, "g_star_vs_R1_deck": CONSTANTS["R1_deck_energies"] / (2 * k),
                     "g_star_vs_naive": (2 * M + 2 * n) / (2 * k), "recovery_max_abs_error": err})
        print(name, "pairs", n, "maxr", maxr, "k", k, "2k", 2 * k, "g*", round(CONSTANTS["R1_deck_energies"] / (2 * k), 1), flush=True)
    add("(a) symmetry prior: diagonal + all eligible pairs", eligible)
    for f in CONSTANTS["fractions"]:
        n = int(round(f * len(eligible))); add(f"({'b' if f == 0.4 else 'c'}) diagonal + top {int(f*100)} % of eligible pairs by 1/|ω_i²−ω_j²| ({n})", [eligible[t] for t in order[:n]])
    add("(d) dense", [(i, j) for i in range(M) for j in range(i + 1, M)])
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "M": M, "n_eligible": len(eligible), "rows": rows}
    json.dump(out, open(HERE / "x14_naphthalene_symmetry_pattern_products.json", "w"), indent=1)
    L = [f"# X14 — substitution products on naphthalene's real symmetry pattern (mode space, M = {M}; {out['date']})", "",
         f"Pattern from X13 (B3LYP modes, D2h irreps): {len(eligible)} eligible pairs of {M*(M-1)//2}. Counting code: X1c's; recovery verified numerically. "
         f"g* = {CONSTANTS['R1_deck_energies']} / (2k): the gradient-to-energy cost ratio below which 2k gradients cost fewer energy-equivalents than plan 05's R1 deck ({CONSTANTS['R1_deck_source']}).", "",
         "| pattern | pairs | elements | naive energies 2M + 2n | maxr | k (products) | gradients 2k | **g\\* vs R1 deck (474)** | g\\* vs naive | recovery error |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['pattern']} | {r['pairs']} | {r['elements_upper']} | {r['naive_energies_2M_plus_2n']} | {r['maxr']} | **{r['k']}** | {r['gradients_2k']} | **{r['g_star_vs_R1_deck']:.1f}** | {r['g_star_vs_naive']:.1f} | {r['recovery_max_abs_error']:.1e} |")
    L += ["", "Reading: row (a) is the bar M2a's g must clear for the gradient route to beat plan 05's own R1 deck at naphthalene with no prior beyond symmetry; "
          "rows (b)–(c) are brackets for what P25's rule could add if its benzene ratio carried over (a tensor question); row (d) is mode G's 2·M gradients. "
          "The pattern is the DFT one (B3LYP modes, plan 02's Hessian); the correction's own pattern at R1 is unknown until the BHHLYP half exists.", "",
          "Constants: " + json.dumps(CONSTANTS, ensure_ascii=False)]
    (HERE / "x14_naphthalene_symmetry_pattern_products.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
