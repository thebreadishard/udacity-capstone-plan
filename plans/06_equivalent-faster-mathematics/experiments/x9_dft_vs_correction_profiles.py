"""X9 (2026-09-12, evening) — does the correction decay faster than the DFT Hessian itself? (test of T3′ at benzene)

Conjecture T3′ (T3 proof-plan note §4): the long-range part of the CC and DFT Hessians is mean-field/electrostatic and cancels in
the difference, so Δ₂ should decay faster in bond-graph distance than either Hessian. X5 profiled Δ₂ alone. Here the mass-weighted
DFT Hessian H_low and the stand-in correction Δ = H_high − H_low (both from plan 05's sealed benzene dry-run npz; the reading
'mass_weighted_by_Minv' validated in X5 to 2e-15) are profiled side by side:
  (i) norm level: per bond-graph distance d = 0, 1, 2, 3 (and per Euclidean shell) the median 3×3 block norm of H_low and of Δ,
      and their ratio;
  (ii) band level (X2's rule, exact harmonic positions): for each d*, zero every block at graph distance ≥ d* in H_low alone, in Δ
      alone, and read the largest band shift — 'how much does each object depend on its far blocks, in cm⁻¹'.
Losing condition for T3′ at benzene (pre-stated): the ratio ‖Δ[A,B]‖/‖H_low[A,B]‖ does not fall with d, and the band-level far-block
dependence of Δ is not smaller than that of H_low. Every number printed comes from the files; constants in CONSTANTS."""
import json
from collections import deque
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
HARTREE_TO_CM = 219474.63
CONSTANTS = {"bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "n_zero_modes": 6, "distance_cuts_for_band_test": [1, 2, 3]}


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
    return G, D


def blocks(H, n):
    return np.array([[np.linalg.norm(H[3 * a:3 * a + 3, 3 * b:3 * b + 3]) for b in range(n)] for a in range(n)])


def freqs_cm(Hmw):
    w2 = np.linalg.eigvalsh((Hmw + Hmw.T) / 2)
    w2 = np.sort(w2)[CONSTANTS["n_zero_modes"]:] if False else w2[np.argsort(np.abs(w2))][CONSTANTS["n_zero_modes"]:]
    return np.sort(np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM)


def zero_far(H, G, dstar):
    P = np.kron(G < dstar, np.ones((3, 3), bool))
    return H * P


def main():
    z = np.load(PLAN05 / "probes/results_dryrun/benzene/stageA_hessians.npz")
    a = json.load(open(PLAN05 / "probes/results_dryrun/benzene/stageA.json"))
    sym = a["symbols"]; n = len(sym); X = z["coords"]; Minv = z["Minv"]
    Hlo = Minv[:, None] * z["H_low"] * Minv[None, :]
    Dl = Minv[:, None] * (z["H_high"] - z["H_low"]) * Minv[None, :]
    # sanity: frequencies of the mass-weighted low Hessian against the file's freq_low_cm
    f_low_file = np.sort(np.array(a["freq_low_cm"])); f_low = freqs_cm(Hlo)
    sanity = float(np.abs(f_low - f_low_file).max())
    G, D = graph_distance(sym, X)
    Bl, Bd = blocks(Hlo, n), blocks(Dl, n)
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "sanity_freq_low_max_abs_diff_cm": sanity}
    # (i) norm profiles by graph distance
    prof = []
    for d in sorted(set(G[np.triu_indices(n)].tolist())):
        idx = [(i, j) for i in range(n) for j in range(i, n) if G[i, j] == d]
        rl = np.median([Bl[i, j] for i, j in idx]); rd = np.median([Bd[i, j] for i, j in idx])
        prof.append({"graph_distance": int(d), "pairs": len(idx), "median_block_H_low": float(rl), "median_block_Delta": float(rd), "ratio_Delta_over_H_low": float(rd / rl),
                     "max_ratio": float(max(Bd[i, j] / Bl[i, j] for i, j in idx))})
    out["profile_by_graph_distance"] = prof
    # by pair type at each distance (C..C, C..H, H..H)
    typed = []
    for d in sorted(set(G[np.triu_indices(n)].tolist())):
        for t in ("CC", "CH", "HH"):
            idx = [(i, j) for i in range(n) for j in range(i, n) if G[i, j] == d and "".join(sorted(sym[i] + sym[j])) == t]
            if idx:
                typed.append({"graph_distance": int(d), "type": t, "pairs": len(idx), "median_H_low": float(np.median([Bl[i, j] for i, j in idx])),
                              "median_Delta": float(np.median([Bd[i, j] for i, j in idx])), "median_ratio": float(np.median([Bd[i, j] / Bl[i, j] for i, j in idx]))})
    out["profile_by_distance_and_type"] = typed
    # (ii) band-level far-block dependence
    f_full_low = freqs_cm(Hlo); f_full_tot = freqs_cm(Hlo + Dl)
    band = []
    for dstar in CONSTANTS["distance_cuts_for_band_test"]:
        s_low = float(np.abs(freqs_cm(zero_far(Hlo, G, dstar)) - f_full_low).max())
        s_del = float(np.abs(freqs_cm(Hlo + zero_far(Dl, G, dstar)) - f_full_tot).max())
        n_del_gt = int((np.abs(freqs_cm(Hlo + zero_far(Dl, G, dstar)) - f_full_tot) > 0.5).sum())
        band.append({"blocks_kept": f"graph distance < {dstar}", "max_band_shift_zeroing_far_blocks_of_H_low_cm": s_low,
                     "max_band_shift_zeroing_far_blocks_of_Delta_cm": s_del, "bands_gt_0.5_Delta": n_del_gt,
                     "ratio_Delta_over_H_low": s_del / s_low if s_low else None})
    out["band_level"] = band
    json.dump(out, open(HERE / "x9_dft_vs_correction_profiles.json", "w"), indent=1)
    L = [f"# X9 — the DFT Hessian and the correction side by side, by bond-graph distance (benzene, {out['date']})", "",
         f"Sanity: harmonic frequencies from the mass-weighted H_low against the dry run's own list, max |diff| {sanity:.2e} cm⁻¹. "
         "Blocks are 3×3 atom-pair blocks of the mass-weighted matrices (units E_h per mass-weighted bohr²; only ratios are read).", "",
         "## Norm level: median block norm per bond-graph distance", "",
         "| graph distance | pairs | median ‖H_low[A,B]‖ | median ‖Δ[A,B]‖ | median ratio Δ/H_low | max ratio |", "|---|---|---|---|---|---|"]
    for r in prof:
        L.append(f"| {r['graph_distance']} | {r['pairs']} | {r['median_block_H_low']:.3e} | {r['median_block_Delta']:.3e} | **{r['ratio_Delta_over_H_low']:.4f}** | {r['max_ratio']:.4f} |")
    L += ["", "By pair type:", "", "| graph distance | type | pairs | median H_low | median Δ | median ratio |", "|---|---|---|---|---|---|"]
    for r in typed:
        L.append(f"| {r['graph_distance']} | {r['type']} | {r['pairs']} | {r['median_H_low']:.3e} | {r['median_Delta']:.3e} | {r['median_ratio']:.4f} |")
    L += ["", "## Band level: zero every block at graph distance ≥ d*, largest band shift (exact harmonic positions)", "",
          "| blocks kept | H_low alone: max shift (cm⁻¹) | Δ alone: max shift (cm⁻¹) | bands > 0.5 (Δ) | ratio Δ/H_low |", "|---|---|---|---|---|"]
    for r in band:
        L.append(f"| {r['blocks_kept']} | {r['max_band_shift_zeroing_far_blocks_of_H_low_cm']:.2f} | {r['max_band_shift_zeroing_far_blocks_of_Delta_cm']:.2f} | {r['bands_gt_0.5_Delta']} | {r['ratio_Delta_over_H_low']:.4f} |")
    L += ["", "Reading: T3′ predicts the ratio column to fall with distance (the correction shorter-ranged than the Hessian) and the band-level far-block dependence of Δ "
          "to be a small fraction of H_low's. Losing condition at benzene: neither falls. Benzene's graph-distance range (≤ 3) is short; naphthalene (≤ 5) is the first "
          "informative case, as for X5/X8. Stand-in caveat: Δ here is BHHLYP − B3LYP, not CC − DFT.", "", "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x9_dft_vs_correction_profiles.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
