"""X1b (2026-09-12) — which graph did X1 colour, and what do the three recovery schemes really cost?

X1's `greedy_colouring(adj)` coloured the *pattern graph* H itself (columns adjacent when the element
|Δ₂,ij| > θ), and called the result an upper bound on the Curtis–Powell–Reid (CPR) count. That is not what
CPR needs: CPR needs a proper colouring of the *column-intersection graph* H_cpr (two columns adjacent
when some row holds both). A proper colouring of H is necessary but in general not sufficient for either
the CPR scheme or the symmetric direct scheme. This script prints, on the same benzene Δ₂ tensor and the
same θ grid as X1:

  (a) X1's number: greedy proper colouring of H (reproduced);
  (b) the CPR-valid count: greedy proper colouring of H_cpr, verified by the two-sided readability check;
  (c) the symmetric-direct count: a greedy colouring that keeps every pattern entry readable from at
      least one side (the definition in the T1b note), verified by the exact one-sided readability check;
  and, for X1's colouring (a), the number of pattern entries that are NOT readable — the measure of how
  much X1's count under-stated the cost.

Definitions (T1b note, §2): with pattern P (H plus the diagonal) and colouring c,
  readable_col(i, j) := no column j' ≠ j with (i, j') ∈ P has c(j') = c(j)      [read A_ij from probe c(j) at row i]
  readable_row(i, j) := readable_col(j, i)                                        [read A_ji = A_ij from probe c(i) at row j]
  CPR-valid  : readable_col(i, j) for every (i, j) ∈ P
  symm-valid : readable_col(i, j) or readable_row(i, j) for every (i, j) ∈ P
Every number printed comes from the files; constants are listed in CONSTANTS."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
CONSTANTS = {"sigma_E_uEh": [0.5, 1.0], "element_uncertainty_rule": "delta(D2_direct_ij) = sigma_E / 2 (as X1)",
             "theta_multiples_of_noise": [1, 2, 5, 10], "K_measured_plan05": 448, "greedy_order": "largest degree first (as X1)"}


def pattern(DE, theta):
    P = np.abs(DE) > theta
    np.fill_diagonal(P, True)          # the diagonal is always in the pattern (always probed)
    return P


def readable_col(P, c, i, j):
    """A_ij readable from the probe of colour c[j] at row i: no other column of that colour in row i."""
    return not any(P[i, jp] and jp != j and c[jp] == c[j] for jp in range(P.shape[0]))


def cpr_valid(P, c):
    n = P.shape[0]
    return all(readable_col(P, c, i, j) for i in range(n) for j in range(n) if P[i, j])


def symm_valid(P, c):
    n = P.shape[0]
    return all(readable_col(P, c, i, j) or readable_col(P, c, j, i) for i in range(n) for j in range(n) if P[i, j])


def unreadable_entries(P, c):
    n = P.shape[0]
    return int(sum(1 for i in range(n) for j in range(n) if P[i, j] and not (readable_col(P, c, i, j) or readable_col(P, c, j, i))))


def greedy_proper(adj):
    """X1's greedy: largest-first, smallest colour not used by a coloured neighbour."""
    n = adj.shape[0]; order = np.argsort(-adj.sum(1)); colour = -np.ones(n, int)
    for v in order:
        used = {colour[u] for u in np.nonzero(adj[v])[0] if colour[u] >= 0}
        c = 0
        while c in used:
            c += 1
        colour[v] = c
    return colour


def greedy_symmetric(P):
    """Greedy one-sided scheme: largest-first; give v the smallest colour that keeps every entry between
    already-coloured vertices readable from at least one side (checked on the coloured subgraph). The
    result is verified afterwards by `symm_valid` on the whole pattern; only a verified colouring counts."""
    n = P.shape[0]; H = P.copy(); np.fill_diagonal(H, False)
    order = np.argsort(-H.sum(1)); colour = -np.ones(n, int)
    for v in order:
        c = 0
        while True:
            colour[v] = c
            done = [u for u in range(n) if colour[u] >= 0]
            sub = np.ix_(done, done)
            ok = symm_valid(P[sub], colour[done])
            if ok:
                break
            c += 1
    return colour


def main():
    z = np.load(PLAN05 / "probes/results_dryrun/benzene/stageA_hessians.npz")
    DE = z["D2_direct"]; M = DE.shape[0]
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "M": M, "constants": CONSTANTS, "source": "plan 05 probes/results_dryrun/benzene/stageA_hessians.npz (D2_direct)"}
    rows = []
    for sig in CONSTANTS["sigma_E_uEh"]:
        noise = sig * 1e-6 / 2.0
        for m in CONSTANTS["theta_multiples_of_noise"]:
            theta = m * noise
            P = pattern(DE, theta)
            H = P.copy(); np.fill_diagonal(H, False)
            Hcpr = (P.T.astype(int) @ P.astype(int)) > 0     # j ~ j' iff some row holds both
            np.fill_diagonal(Hcpr, False)
            c_a = greedy_proper(H)
            c_b = greedy_proper(Hcpr)
            c_c = greedy_symmetric(P)
            row = {"sigma_E_uEh": sig, "theta_uEh": theta * 1e6, "offdiag_elements_above_theta": int(H[np.triu_indices(M, 1)].sum()),
                   "max_degree_H": int(H.sum(1).max()), "max_degree_Hcpr": int(Hcpr.sum(1).max()),
                   "a_X1_colours_of_H": int(c_a.max() + 1), "a_is_symm_valid": bool(symm_valid(P, c_a)), "a_is_cpr_valid": bool(cpr_valid(P, c_a)),
                   "a_unreadable_entries": unreadable_entries(P, c_a), "pattern_entries_total": int(P.sum()),
                   "b_CPR_colours_of_Hcpr": int(c_b.max() + 1), "b_verified_cpr_valid": bool(cpr_valid(P, c_b)),
                   "c_symmetric_colours": int(c_c.max() + 1), "c_verified_symm_valid": bool(symm_valid(P, c_c)),
                   "energies_if_product_is_2M": {"a": int((c_a.max() + 1) * 2 * M), "b": int((c_b.max() + 1) * 2 * M), "c": int((c_c.max() + 1) * 2 * M)}}
            rows.append(row)
    out["rows"] = rows
    json.dump(out, open(HERE / "x1b_symmetric_colouring.json", "w"), indent=1)
    L = [f"# X1b — the three colouring counts on the benzene Δ₂ tensor ({out['date']})", "",
         "Same tensor and θ grid as X1. (a) = X1's printed number (a proper colouring of the pattern graph H); (b) = the CPR-valid count "
         "(proper colouring of the column-intersection graph); (c) = the symmetric-direct count (one-sided readability, T1b note). "
         "'valid' columns are exact checks of the readability definitions on the whole pattern; only verified colourings count. K = 448 is plan 05's measured mode-E deck.", "",
         "| σ_E (µE_h) | θ (µE_h) | off-diag > θ | Δ(H) | Δ(H_cpr) | (a) X1 colours | (a) symm-valid? | (a) unreadable entries / total | (b) CPR colours | (b) verified | (c) symmetric colours | (c) verified | energies (a / b / c) at 2M per product |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        e = r["energies_if_product_is_2M"]
        L.append(f"| {r['sigma_E_uEh']} | {r['theta_uEh']:.2f} | {r['offdiag_elements_above_theta']} | {r['max_degree_H']} | {r['max_degree_Hcpr']} | {r['a_X1_colours_of_H']} | "
                 f"{'yes' if r['a_is_symm_valid'] else '**no**'} | {r['a_unreadable_entries']} / {r['pattern_entries_total']} | **{r['b_CPR_colours_of_Hcpr']}** | {'yes' if r['b_verified_cpr_valid'] else 'NO'} | "
                 f"**{r['c_symmetric_colours']}** | {'yes' if r['c_verified_symm_valid'] else 'NO'} | {e['a']} / {e['b']} / {e['c']} |")
    L += ["", "Reading: (a) is a lower bound for both schemes (a proper colouring of H is necessary for either); the honest CPR count is (b); the symmetric direct "
          "scheme (c) sits between them when the greedy finds a verified colouring. The greedy of (c) is a heuristic — a smaller symmetric colouring may exist; "
          "the T1b note discusses the exact characterisation, which is to be read from Coleman & Moré (1984) and Powell & Toint (1979), not recalled.", "",
          "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x1b_symmetric_colouring.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
