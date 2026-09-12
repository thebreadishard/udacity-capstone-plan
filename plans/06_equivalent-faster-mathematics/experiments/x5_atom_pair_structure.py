"""X5 (2026-09-12) — where does the correction live in real space? Atom-pair block structure and rank of Δ₂
in mass-weighted Cartesian coordinates (first data test of S1 locality in real space and of S2 low rank).

X1 found Δ₂ full-rank in the normal-mode basis (30 of 30). That says nothing about atom-pair locality: a
correction that lives on bonded pairs only is dense in mode space. Here the sealed benzene dry-run tensor
(B3LYP → BHHLYP, 6-31G*, the stand-in with the algebraic form of CC − DFT) is mapped back to mass-weighted
Cartesian coordinates and cut into 3×3 atom-pair blocks.

Transform: the dry run displaces x = x0 + Minv ⊙ (L q/√ω) (q dimensionless, L 36×30 orthonormal columns,
Minv = 1/√m per Cartesian coordinate), so with the mass-weighted displacement y = L q/√ω the curvature in q is
D_q = Jᵀ H_y J, J = L diag(1/√ω). On the vibrational subspace H_y = L diag(√ω) D_q diag(√ω) Lᵀ. Validation:
the same projection of the STORED full Hessian difference H_high − H_low (in the npz) must agree with the
probed D2_direct up to the probing error.

Printed: (i) validation residual; (ii) eigen/singular spectrum of ΔH_y and the Frobenius fraction in the top k;
(iii) per atom-pair block Frobenius norms grouped by pair type and by distance, the fraction of the total
carried by on-atom + bonded blocks, and how many blocks exceed the noise floor; (iv) the noise floor per block
from X2's per-element noise propagated through the same transform (200 draws).
Every number printed comes from the files; constants are listed in CONSTANTS."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
CONSTANTS = {"sigma_E_uEh": 0.5, "element_uncertainty_rule": "delta = sigma_E / 2 per q^2 element (X2)", "n_noise_draws": 200, "seed": 0,
             "bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "top_k": [1, 2, 3, 5, 10, 15, 20, 30]}


def blocks(H, natom):
    B = np.zeros((natom, natom))
    for a in range(natom):
        for b in range(natom):
            B[a, b] = np.linalg.norm(H[3 * a:3 * a + 3, 3 * b:3 * b + 3])
    return B


def main():
    z = np.load(PLAN05 / "probes/results_dryrun/benzene/stageA_hessians.npz")
    a = json.load(open(PLAN05 / "probes/results_dryrun/benzene/stageA.json"))
    L, w, DE, Minv, X = z["L"], z["omega_au"], z["D2_direct"], z["Minv"], z["coords"]
    Hlo, Hhi = z["H_low"], z["H_high"]
    sym = a["symbols"]; natom = len(sym); M = len(w)
    sw = np.sqrt(w)
    Hy = L @ (sw[:, None] * DE * sw[None, :]) @ L.T                    # probed correction, mass-weighted Cartesian
    # validation against the stored full difference, projected on the vibrational subspace (both in the npz's own units)
    Dfull = Hhi - Hlo
    Dfull_vib = L @ (L.T @ Dfull @ L) @ L.T
    # the npz Hessians may be plain Cartesian or mass-weighted: test both readings and report the one that matches
    Dmw = (Minv[:, None] * Dfull * Minv[None, :]); Dmw_vib = L @ (L.T @ Dmw @ L) @ L.T
    cand = {"as_stored": Dfull_vib, "mass_weighted_by_Minv": Dmw_vib}
    val = {k: {"rel_residual": float(np.linalg.norm(v - Hy) / np.linalg.norm(Hy)), "max_abs_diff": float(np.abs(v - Hy).max())} for k, v in cand.items()}
    best = min(val, key=lambda k: val[k]["rel_residual"])
    # spectrum
    ev = np.linalg.eigvalsh(Hy); sv = np.sort(np.abs(ev))[::-1]
    fro2 = float((sv ** 2).sum())
    topk = {k: float((sv[:k] ** 2).sum() / fro2) for k in CONSTANTS["top_k"]}
    # atom-pair blocks
    B = blocks(Hy, natom)
    D = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=2)
    def ptype(i, j):
        if i == j: return "on-atom"
        s = "".join(sorted(sym[i] + sym[j]))
        cut = CONSTANTS["bond_cutoff_bohr"]["CC"] if s == "CC" else (CONSTANTS["bond_cutoff_bohr"]["CH"] if s == "CH" else 0.0)
        return f"{s} bonded" if D[i, j] < cut else f"{s} non-bonded"
    groups = {}
    for i in range(natom):
        for j in range(i, natom):
            groups.setdefault(ptype(i, j), []).append((i, j, float(B[i, j]), float(D[i, j])))
    tot = float(sum(B[i, j] ** 2 * (1 if i == j else 2) for i in range(natom) for j in range(i, natom)))
    # noise floor per block: propagate X2 noise (per q^2 element, symmetric) through the same transform
    rng = np.random.default_rng(CONSTANTS["seed"]); delta = CONSTANTS["sigma_E_uEh"] * 1e-6 / 2.0
    Bn = []
    for _ in range(CONSTANTS["n_noise_draws"]):
        N = rng.normal(0.0, delta, (M, M)); N = np.triu(N) + np.triu(N, 1).T
        Bn.append(blocks(L @ (sw[:, None] * N * sw[None, :]) @ L.T, natom))
    Bn = np.array(Bn); floor = np.sqrt((Bn ** 2).mean(0))            # RMS block norm under noise alone
    above = int(sum(1 for i in range(natom) for j in range(i, natom) if B[i, j] > 3 * floor[i, j]))
    npairs = natom * (natom + 1) // 2
    summary = {}
    for g, lst in groups.items():
        e = sum(v ** 2 * (1 if i == j else 2) for i, j, v, d in lst)
        summary[g] = {"n_blocks": len(lst), "fraction_of_total_fro2": e / tot, "median_block_norm": float(np.median([v for *_, v, d in lst])),
                      "median_noise_floor": float(np.median([floor[i, j] for i, j, *_ in lst])),
                      "blocks_above_3x_floor": int(sum(1 for i, j, v, d in lst if v > 3 * floor[i, j]))}
    # distance profile (off-atom blocks): median block norm per distance shell
    shells = {}
    for i in range(natom):
        for j in range(i + 1, natom):
            shells.setdefault(round(D[i, j], 1), []).append(B[i, j])
    prof = [(d, len(v), float(np.median(v))) for d, v in sorted(shells.items())]
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "natom": natom, "M": M, "validation": val, "validation_best_reading": best,
           "spectrum_abs_eigs_top10": sv[:10].tolist(), "rank_numerical": int(np.linalg.matrix_rank(Hy)), "fro_fraction_top_k": topk,
           "pair_groups": summary, "blocks_above_3x_noise_floor": above, "n_blocks": npairs, "distance_profile": prof}
    json.dump(out, open(HERE / "x5_atom_pair_structure.json", "w"), indent=1)
    Lns = [f"# X5 — atom-pair structure of the benzene Δ₂ in mass-weighted Cartesian coordinates ({out['date']})", "",
           f"Validation of the transform against the stored full Hessian difference projected on the vibrational subspace: best reading "
           f"'{best}', relative residual {val[best]['rel_residual']:.3e} (the other reading: {val[[k for k in val if k != best][0]]['rel_residual']:.3e}). "
           "A residual at the probing-error level means the mapping is right; a residual of order 1 would mean the stored Hessians are in other units.", "",
           f"**Spectrum.** Numerical rank {out['rank_numerical']} of {M}; Frobenius fraction in the top k eigen-directions: " +
           ", ".join(f"k={k}: {v:.3f}" for k, v in topk.items()) + ".", "",
           "**Atom-pair blocks** (3×3 blocks of the 36×36 matrix; fraction of the total Frobenius norm²; noise floor = RMS block norm under X2's per-element noise, 200 draws):", "",
           "| pair type | blocks | fraction of ‖Δ‖²_F | median block norm | median noise floor | blocks > 3× floor |", "|---|---|---|---|---|---|"]
    for g in sorted(summary, key=lambda k: -summary[k]["fraction_of_total_fro2"]):
        s = summary[g]
        Lns.append(f"| {g} | {s['n_blocks']} | {s['fraction_of_total_fro2']:.3f} | {s['median_block_norm']:.3e} | {s['median_noise_floor']:.3e} | {s['blocks_above_3x_floor']} |")
    Lns += ["", f"Blocks above 3× the noise floor: {above} of {npairs}.", "", "Distance profile of the off-atom blocks (median block norm per distance shell, bohr):", "",
            "| distance | pairs | median block norm |", "|---|---|---|"] + [f"| {d:.1f} | {n} | {v:.3e} |" for d, n, v in prof]
    Lns += ["", "Reading aid: S1 (real-space locality) predicts the norm concentrated in on-atom and bonded blocks and decaying with distance; "
            "S2 (low rank) predicts a steep Frobenius fraction in few eigen-directions. Units are the npz's own (E_h per mass-weighted bohr²); only ratios are read.", "",
            "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x5_atom_pair_structure.md").write_text("\n".join(Lns), encoding="utf-8")
    print("\n".join(Lns).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
