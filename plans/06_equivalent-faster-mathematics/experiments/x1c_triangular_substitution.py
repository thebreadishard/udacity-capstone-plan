"""X1c (2026-09-12) — the triangular-substitution count on the benzene Δ₂ pattern (after reading Coleman &
Moré 1982/1984, Sections 6–8).

Coleman & Moré show (their Theorem 6.1) that Powell & Toint's lower triangular substitution method needs
exactly a proper colouring of G_u(L_π): the column-intersection graph of the lower triangular part L_π of
the row/column-permuted matrix; the count is the triangular chromatic number χ_τ(G_s(A)) minimised over
orderings π. Their Theorem 6.3 orders the four counts: χ(G) ≤ max{1+δ(G[W])} ≤ χ_τ(G) ≤ χ(G²), and their
Theorem 6.2 gives the computable lower bound maxr = the maximum number of non-zeros in a row of L_π for the
smallest-last ordering. Their numerical recipe: π = smallest-last ordering of G_s(A), then a sequential
colouring of G_u(L_π) (their `slsl` uses the smallest-last ordering of G_u(L_π) for that colouring, their
`slpt` the induced ordering (6.2)).

This script prints, on the same tensor and θ grid as X1/X1b:
  (d) the triangular-substitution count: smallest-last ordering π of H, then the smaller of two sequential
      colourings of G_u(L_π) (largest-first and smallest-last), each checked to be a proper colouring of G_u(L_π);
  the lower bound maxr(L_π) of Theorem 6.2;
  and a NUMERICAL verification: a random symmetric matrix with the pattern is recovered from the (d) probes by
  the substitution (6.1) of Coleman & Moré, in the order of decreasing position; the maximum absolute
  reconstruction error is printed (exactness up to rounding).
Every number printed comes from the files; constants are listed in CONSTANTS."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
CONSTANTS = {"sigma_E_uEh": [0.5, 1.0], "theta_multiples_of_noise": [1, 2, 5, 10], "K_measured_plan05": 448,
             "ordering_pi": "smallest-last ordering of the pattern graph H (Matula–Beck; Coleman & Moré 1982 §6)",
             "colourings_tried_on_Gu_L": ["largest-first sequential", "smallest-last sequential"], "random_seed": 0}


def pattern(DE, theta):
    P = np.abs(DE) > theta
    np.fill_diagonal(P, True)
    return P


def smallest_last_order(H):
    """Return positions pos[v] in 1..n of a smallest-last ordering: v_n has minimum degree in H, v_{n-1} minimum
    degree in H − v_n, and so on. Ties broken by index (deterministic)."""
    n = H.shape[0]; alive = np.ones(n, bool); order = [None] * n
    for k in range(n - 1, -1, -1):
        deg = np.where(alive, (H & alive[None, :]).sum(1), n + 1)
        v = int(np.argmin(deg)); order[k] = v; alive[v] = False
    pos = np.empty(n, int)
    for k, v in enumerate(order):
        pos[v] = k + 1
    return pos


def lower_pattern(P, pos):
    """Pattern of L_π: entries (i, j) of P with pos[i] ≥ pos[j]."""
    n = P.shape[0]
    return P & (pos[:, None] >= pos[None, :])


def intersection_graph(Lp):
    n = Lp.shape[1]
    G = (Lp.T.astype(int) @ Lp.astype(int)) > 0
    np.fill_diagonal(G, False)
    return G


def sequential_colouring(G, order):
    n = G.shape[0]; colour = -np.ones(n, int)
    for v in order:
        used = {colour[u] for u in np.nonzero(G[v])[0] if colour[u] >= 0}
        c = 0
        while c in used:
            c += 1
        colour[v] = c
    return colour


def is_proper(G, colour):
    n = G.shape[0]
    return all(colour[u] != colour[v] for u in range(n) for v in range(n) if G[u, v])


def recover_by_substitution(P, pos, colour, probes):
    """Coleman & Moré (6.1): (Ad)_i = a_ij + Σ_{l: pos(l) > pos(i), l in group of j} a_il, for j with pos(j) ≤ pos(i)
    and (i, j) in P; solve rows in decreasing position; a_il with pos(l) > pos(i) equals a_li, already known."""
    n = P.shape[0]; A = np.zeros((n, n)); done = np.zeros((n, n), bool)
    for i in sorted(range(n), key=lambda v: -pos[v]):
        for j in range(n):
            if P[i, j] and pos[j] <= pos[i]:
                s = probes[colour[j]][i]
                for l in range(n):
                    if l != j and colour[l] == colour[j] and P[i, l] and pos[l] > pos[i]:
                        assert done[l, i], "substitution order violated"
                        s -= A[l, i]
                A[i, j] = s; A[j, i] = s; done[i, j] = done[j, i] = True
    return A


def main():
    z = np.load(PLAN05 / "probes/results_dryrun/benzene/stageA_hessians.npz")
    DE = z["D2_direct"]; M = DE.shape[0]
    rng = np.random.default_rng(CONSTANTS["random_seed"])
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "M": M, "constants": CONSTANTS,
           "source": "plan 05 probes/results_dryrun/benzene/stageA_hessians.npz (D2_direct)"}
    rows = []
    for sig in CONSTANTS["sigma_E_uEh"]:
        noise = sig * 1e-6 / 2.0
        for m in CONSTANTS["theta_multiples_of_noise"]:
            theta = m * noise
            P = pattern(DE, theta); H = P.copy(); np.fill_diagonal(H, False)
            pos = smallest_last_order(H)
            Lp = lower_pattern(P, pos)
            Gu = intersection_graph(Lp)
            maxr = int(Lp.sum(1).max())
            c_lf = sequential_colouring(Gu, list(np.argsort(-Gu.sum(1))))
            pos_gu = smallest_last_order(Gu)
            c_sl = sequential_colouring(Gu, sorted(range(M), key=lambda v: pos_gu[v]))
            cands = [(int(c.max() + 1), name, c) for c, name in ((c_lf, "largest-first"), (c_sl, "smallest-last")) if is_proper(Gu, c)]
            k, name, colour = min(cands, key=lambda t: t[0])
            # numerical verification on a random symmetric matrix with the pattern
            R = rng.standard_normal((M, M)); R = (R + R.T) / 2; R[~P] = 0.0
            probes = [R @ (colour == q).astype(float) for q in range(k)]
            Rrec = recover_by_substitution(P, pos, colour, probes)
            err = float(np.abs(Rrec - R).max())
            rows.append({"sigma_E_uEh": sig, "theta_uEh": theta * 1e6, "offdiag_elements_above_theta": int(H[np.triu_indices(M, 1)].sum()),
                         "maxr_lower_bound": maxr, "d_triangular_colours": k, "d_colouring_used": name,
                         "d_verified_proper_on_Gu_L": True, "recovery_max_abs_error": err, "energies_if_product_is_2M": int(k * 2 * M)})
    out["rows"] = rows
    json.dump(out, open(HERE / "x1c_triangular_substitution.json", "w"), indent=1)
    L = [f"# X1c — the triangular-substitution count on the benzene Δ₂ pattern ({out['date']})", "",
         "Powell & Toint's lower triangular substitution method as characterised by Coleman & Moré (1982 TR / 1984): the count is a proper colouring "
         "of the column-intersection graph of the lower triangular part L_π of the permuted matrix (their Theorem 6.1); maxr = the maximum number of "
         "non-zeros in a row of L_π is a lower bound (their Theorem 6.2). π = smallest-last ordering of the pattern graph. The recovery is verified "
         "numerically on a random symmetric matrix with the pattern (substitution (6.1), decreasing position). Same tensor and θ grid as X1/X1b; K = 448.", "",
         "| σ_E (µE_h) | θ (µE_h) | off-diag > θ | maxr (lower bound) | (d) triangular colours | colouring | max abs recovery error | energies at 2M per product |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['sigma_E_uEh']} | {r['theta_uEh']:.2f} | {r['offdiag_elements_above_theta']} | {r['maxr_lower_bound']} | **{r['d_triangular_colours']}** | "
                 f"{r['d_colouring_used']} | {r['recovery_max_abs_error']:.1e} | {r['energies_if_product_is_2M']} |")
    L += ["", "Reading: (d) is an upper bound on the triangular chromatic number for this ordering (two sequential colourings tried), maxr a lower bound; "
          "the reconstruction error shows the substitution is exact up to rounding on noise-free data. Substitution can magnify measurement noise "
          "(Coleman & Moré §6, after Powell & Toint 1979) — for plan 05's noisy probes that magnification would have to be measured before the count is used.", "",
          "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x1c_triangular_substitution.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
