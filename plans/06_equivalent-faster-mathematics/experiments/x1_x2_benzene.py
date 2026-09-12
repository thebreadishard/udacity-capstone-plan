#!/usr/bin/env python
"""Plan 06, experiments X1 (direction S5) and X2 (direction S4) on the benzene dry-run tensor of plan 05
(probes/results_dryrun/benzene/stageA_hessians.npz: D2_direct_Q = L^T (F_high - F_low) L in the low-level mode basis,
a.u. of omega^2; D2_direct the same in E_h per dimensionless q^2; omega_au the low-level harmonic frequencies).
No CC compute; minutes.  Run:  python x1_x2_benzene.py

X2 — which elements of Delta_2 move a band position?  Exact harmonic positions from Omega^2 = diag(omega^2) + D2Q.
  (a) drop-one: set one off-diagonal pair (i,j) to zero, print the largest change of any frequency; count pairs > 0.5 cm-1.
  (b) noise-level: perturb one element by plan 05's per-element measurement uncertainty (sigma_E/2 per dimensionless q^2,
      sigma_E = 0.5 and 1.0 uE_h from the dry-run noise column) and count elements whose perturbation moves any band > 0.5.
X1 — how many exact queries would recover Delta_2?  Numerical rank at the noise level; greedy colouring number of the
  sparsity pattern |D2_direct| > theta (theta = noise multiples) -> Hessian-vector products needed for exact recovery
  (Powell-Toint / Coleman-More type schemes); low-rank r + p products; against plan 05's measured K = 448 energies.
Every number printed comes from the files; constants are listed in CONSTANTS."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
HARTREE_TO_CM = 219474.63
CONSTANTS = {"band_threshold_cm": 0.5, "sigma_E_uEh": [0.5, 1.0], "element_uncertainty_rule": "delta(D2_direct_ij) = sigma_E / 2 (four-point pattern at q_s = 1)",
             "theta_multiples_of_noise": [1, 2, 5, 10], "K_measured_plan05": 448, "oversampling_p": 5}


def freqs_cm(W2):
    w2 = np.linalg.eigvalsh(W2)
    return np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM


def greedy_colouring(adj):
    """Largest-first greedy vertex colouring of an undirected graph (adjacency boolean matrix); returns colour count.
    A proper colouring of the *intersection graph of columns* is what Curtis-Powell-Reid need; for a symmetric matrix the
    Powell-Toint bound is at most this (symmetry can only reduce it). Upper bound, printed as such."""
    n = adj.shape[0]; order = np.argsort(-adj.sum(1)); colour = -np.ones(n, int)
    for v in order:
        used = {colour[u] for u in np.nonzero(adj[v])[0] if colour[u] >= 0}
        c = 0
        while c in used: c += 1
        colour[v] = c
    return int(colour.max() + 1)


def main():
    z = np.load(PLAN05 / "probes/results_dryrun/benzene/stageA_hessians.npz"); a = json.load(open(PLAN05 / "probes/results_dryrun/benzene/stageA.json"))
    DQ, DE, w = z["D2_direct_Q"], z["D2_direct"], z["omega_au"]; M = len(w)
    s = np.sqrt(np.abs(np.diag(DE) / np.diag(DQ)))          # scale dimensionless q -> mass-weighted, per mode (from the files)
    W2 = np.diag(w ** 2) + DQ
    f0 = freqs_cm(W2); f_low = w * HARTREE_TO_CM
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "M": M, "constants": CONSTANTS, "functionals": a["functionals"], "basis": a["basis"]}
    # ---- X2 (a): drop-one off-diagonal pair
    iu = np.triu_indices(M, 1); effects = []
    for i, j in zip(*iu):
        W = W2.copy(); W[i, j] = W[j, i] = 0.0
        effects.append(np.abs(freqs_cm(W) - f0).max())
    effects = np.array(effects); thr = CONSTANTS["band_threshold_cm"]
    diag_shift = f0 - f_low
    out["x2_drop_one"] = {"n_offdiag_pairs": int(len(effects)), "pairs_moving_any_band_gt_thr": int((effects > thr).sum()), "pairs_gt_0.1": int((effects > 0.1).sum()),
                          "max_effect_cm": float(effects.max()), "median_effect_cm": float(np.median(effects)), "all_offdiag_dropped_max_shift_cm": float(np.abs(freqs_cm(np.diag(np.diag(W2))) - f0).max()),
                          "diagonal_only_shift_range_cm": [float(diag_shift.min()), float(diag_shift.max())]}
    top = np.argsort(-effects)[:8]
    out["x2_drop_one"]["largest_pairs"] = [{"i": int(iu[0][k]), "j": int(iu[1][k]), "omega_i_cm": round(float(f_low[iu[0][k]]), 1), "omega_j_cm": round(float(f_low[iu[1][k]]), 1), "effect_cm": round(float(effects[k]), 3)} for k in top]
    # ---- X2 (b): noise-level perturbation per element (diagonal and off-diagonal)
    xb = {}
    for sig in CONSTANTS["sigma_E_uEh"]:
        dE = sig * 1e-6 / 2.0                                  # E_h per q^2
        cnt_off = 0; cnt_diag = 0; maxeff = 0.0
        for i in range(M):
            for j in range(i, M):
                d = dE / (s[i] * s[j])                          # to a.u. of omega^2
                W = W2.copy(); W[i, j] += d
                if i != j: W[j, i] += d
                e = np.abs(freqs_cm(W) - f0).max(); maxeff = max(maxeff, e)
                if e > thr: (cnt_diag if i == j else cnt_off)
                if e > thr:
                    if i == j: cnt_diag += 1
                    else: cnt_off += 1
        xb[f"sigma_E_{sig}_uEh"] = {"diagonal_elements_moving_gt_thr": cnt_diag, "offdiag_elements_moving_gt_thr": cnt_off, "max_effect_cm": float(maxeff)}
    out["x2_noise_level"] = xb
    # ---- X1: rank and colouring
    sv = np.linalg.svd(DE, compute_uv=False)
    x1 = {"singular_values_uEh_top10": [round(float(v) * 1e6, 3) for v in sv[:10]], "n_elements_offdiag_abs_gt_1uEh": int((np.abs(DE - np.diag(np.diag(DE)))[iu] > 1e-6).sum())}
    for sig in CONSTANTS["sigma_E_uEh"]:
        noise = sig * 1e-6 / 2.0
        x1[f"rank_at_noise_{sig}_uEh"] = int((sv > noise * np.sqrt(M)).sum())
        rows = {}
        for m in CONSTANTS["theta_multiples_of_noise"]:
            theta = m * noise
            adj = (np.abs(DE) > theta); np.fill_diagonal(adj, False)
            ncol = greedy_colouring(adj) if adj.any() else 1
            n_nonzero_off = int(adj[iu].sum())
            r = int((sv > theta * np.sqrt(M)).sum())
            rows[f"theta_{m}x"] = {"theta_uEh": theta * 1e6, "offdiag_elements_above_theta": n_nonzero_off, "colouring_upper_bound": ncol,
                                    "gradients_for_exact_sparse_recovery": ncol, "energies_if_each_gradient_is_2M_energies": ncol * 2 * M,
                                    "rank_r": r, "low_rank_products_r_plus_p": r + CONSTANTS["oversampling_p"]}
        x1[f"schemes_at_noise_{sig}_uEh"] = rows
    x1["plan05_measured_K_energies"] = CONSTANTS["K_measured_plan05"]; x1["dense_symmetric_lower_bound_energies_mode_E"] = M * (M + 1) // 2 * 2
    out["x1"] = x1
    json.dump(out, open(HERE / "x1_x2_benzene.json", "w"), indent=1)
    d = out["x2_drop_one"]
    L = [f"# X1 / X2 on the benzene dry-run tensor ({a['functionals']['low']} -> {a['functionals']['high']}, {a['basis']}, M = {M}) — {out['date']}", "",
         "## X2 — which elements of Δ₂ move a band position (exact harmonic positions from diag(ω²) + Δ₂)", "",
         f"- Diagonal alone shifts bands by {d['diagonal_only_shift_range_cm'][0]:+.1f} to {d['diagonal_only_shift_range_cm'][1]:+.1f} cm⁻¹; dropping **all** off-diagonal elements changes the largest band by {d['all_offdiag_dropped_max_shift_cm']:.2f} cm⁻¹.",
         f"- Drop-one: of {d['n_offdiag_pairs']} off-diagonal pairs, **{d['pairs_moving_any_band_gt_thr']} move any band by more than {thr} cm⁻¹** ({d['pairs_gt_0.1']} by more than 0.1); largest single effect {d['max_effect_cm']:.2f} cm⁻¹, median {d['median_effect_cm']:.4f}.",
         "- Largest pairs: " + "; ".join(f"({p['i']},{p['j']}) ω {p['omega_i_cm']}/{p['omega_j_cm']} → {p['effect_cm']}" for p in d["largest_pairs"]) + ".",
         "- Noise-level perturbation (one element by σ_E/2 per q²): " + "; ".join(f"σ_E = {k.split('_')[2]} µE_h: {v['diagonal_elements_moving_gt_thr']} diagonal and {v['offdiag_elements_moving_gt_thr']} off-diagonal elements move a band > {thr} cm⁻¹ (max {v['max_effect_cm']:.2f})" for k, v in xb.items()) + ".", "",
         "## X1 — exact-query schemes against plan 05's K = 448 energies", "",
         f"- Singular values (µE_h, top 10): {x1['singular_values_uEh_top10']}; off-diagonal elements above 1 µE_h: {x1['n_elements_offdiag_abs_gt_1uEh']} of {len(iu[0])}.",
         f"- Dense symmetric lower bound in mode E: {x1['dense_symmetric_lower_bound_energies_mode_E']} energies (M(M+1)/2 unknowns, ± pairs); plan 05 measured {CONSTANTS['K_measured_plan05']}.", "",
         "| noise σ_E (µE_h) | θ | off-diag elements > θ | colouring bound (gradients for exact sparse recovery) | as energies (2M each) | rank r at θ | low-rank products r + p |", "|---|---|---|---|---|---|---|"]
    for sig in CONSTANTS["sigma_E_uEh"]:
        for k, v in x1[f"schemes_at_noise_{sig}_uEh"].items():
            L.append(f"| {sig} | {v['theta_uEh']:.2f} | {v['offdiag_elements_above_theta']} | {v['colouring_upper_bound']} | {v['energies_if_each_gradient_is_2M_energies']} | {v['rank_r']} | {v['low_rank_products_r_plus_p']} |")
    L += ["", "Reading rules: a 'gradient' here is one exact Hessian–vector product (a pair of analytic gradients at ±d); plan 05's engine has no local-CC analytic gradient, and a canonical one cost ≈ 50 energies at DZ, so the 'as energies' column is the honest comparison unless gradients become available. The colouring number is a greedy upper bound. Nothing here is a plan-05 decision; it is the first test of directions S4 and S5.",
          "", f"Printed by `{HERE.name}/x1_x2_benzene.py`; inputs sealed in plan 05's dry run (2026-09-05)."]
    (HERE / "x1_x2_benzene.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
