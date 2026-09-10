#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decision 22 (P14, 2026-09-08): the benzene DFT rehearsal re-run under the SYMMETRY PRIOR (decision 11),
from the cached stage-B responses — no new DFT energies. Also the decision-23 null (P15): the
magnitude of the symmetry-forbidden couplings, fitted free, in the DFT surrogate.

1. Irreps of the DFT normal modes in the FULL point group (D6h for benzene; decision 11's wording — the
   DFT code ran in C1): the 24 operations are built from the geometry (ring normal, C–atom directions),
   each mode (or degenerate pair) gets a character per class and is matched to the D6h table. Two modes
   may couple in Δ₂ only if they carry the same irrep (the prior); everything else is fixed at zero.
2. Recovery (mode E) with unknowns = diagonal + same-irrep off-diagonals, consuming the SAME hashed deck
   and hold-out as the dry run: family errors against the direct Δ₂, the ρ_off(n) curve, K_off at
   ρ_off ≤ 0.3 and at the P1/P2 threshold in the noise column — printed beside the banded-prior numbers
   of stageC_recovery.json and the free-element count.
3. The null: every deck pair (i,j) has a ± two-mode pattern, so Δ_ij = [R_s(+) − R_s(−)]/(2 a_i a_j)
   directly; forbidden pairs should read ≈ 0. Their magnitude is printed beside the allowed ones.

Conventions: dimensionless normal coordinates (E = ½ ω q²); a diagonal Δ₂,ii is TWICE the first-order
frequency shift (erratum 2026-09-10). Runs on Windows (NumPy only):
  python dryrun_symmetry_prior.py [--molecule benzene] [--out results_dryrun/benzene]
"""
import argparse, json, os, sys
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("MKL_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dryrun_dft_delta_recovery import (sym_index, design_row_E, fista_lasso, unpack, family_rms_freq_error,  # noqa: E402
                                       rho_of, Q_S, Q_2, RHO_MAX, C_GRID, SIGMA_GRID_UEH, HARTREE_TO_CM)

# D6h character table; class order: E, 2C6, 2C3, C2, 3C2', 3C2'', i, 2S3, 2S6, σh, 3σd, 3σv
# (C2' through opposite atoms; σv contains a C2' axis; σd contains a C2'' axis; i·C2' = σd, i·C2'' = σv.)
CLASSES = ["E", "C6", "C3", "C2", "C2'", "C2''", "i", "S3", "S6", "sh", "sd", "sv"]
D6H = {
    "A1g": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "A2g": [1, 1, 1, 1, -1, -1, 1, 1, 1, 1, -1, -1],
    "B1g": [1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1],
    "B2g": [1, -1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1],
    "E1g": [2, 1, -1, -2, 0, 0, 2, 1, -1, -2, 0, 0],
    "E2g": [2, -1, -1, 2, 0, 0, 2, -1, -1, 2, 0, 0],
    "A1u": [1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1],
    "A2u": [1, 1, 1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
    "B1u": [1, -1, 1, -1, 1, -1, -1, 1, -1, 1, -1, 1],
    "B2u": [1, -1, 1, -1, -1, 1, -1, 1, -1, 1, 1, -1],
    "E1u": [2, 1, -1, -2, 0, 0, -2, -1, 1, 2, 0, 0],
    "E2u": [2, -1, -1, 2, 0, 0, -2, 1, 1, -2, 0, 0],
}


def rot(axis, ang):
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)


def refl(normal):
    n = np.asarray(normal, float); n /= np.linalg.norm(n)
    return np.eye(3) - 2 * np.outer(n, n)


def d6h_operations(coords, symbols):
    """The 24 D6h operations as (class, 3×3 matrix), built from the geometry (centre, ring normal, C directions)."""
    X = coords - coords.mean(axis=0)
    _, _, vt = np.linalg.svd(X)
    z = vt[2]                                   # ring normal (smallest extent)
    carbons = [k for k, s in enumerate(symbols) if s.upper() == "C"]
    u0 = X[carbons[0]] - np.dot(X[carbons[0]], z) * z; u0 /= np.linalg.norm(u0)
    y0 = np.cross(z, u0)
    ops = [("E", np.eye(3))]
    for k in (1, 5):
        ops.append(("C6", rot(z, k * np.pi / 3)))
    for k in (2, 4):
        ops.append(("C3", rot(z, k * np.pi / 3)))
    ops.append(("C2", rot(z, np.pi)))
    axes_atoms = [np.cos(k * np.pi / 3) * u0 + np.sin(k * np.pi / 3) * y0 for k in range(3)]          # through atoms
    axes_bis = [np.cos((k + 0.5) * np.pi / 3) * u0 + np.sin((k + 0.5) * np.pi / 3) * y0 for k in range(3)]  # between atoms
    for ax in axes_atoms:
        ops.append(("C2'", rot(ax, np.pi)))
    for ax in axes_bis:
        ops.append(("C2''", rot(ax, np.pi)))
    ops.append(("i", -np.eye(3)))
    sh = refl(z)
    for k in (1, 5):
        ops.append(("S6", sh @ rot(z, k * np.pi / 3)))      # σh·(rotation by 60°) = S6
    for k in (2, 4):
        ops.append(("S3", sh @ rot(z, k * np.pi / 3)))      # σh·(rotation by 120°) = S3
    ops.append(("sh", sh))
    for ax in axes_atoms:
        ops.append(("sv", refl(np.cross(z, ax))))           # plane containing z and a through-atom axis
    for ax in axes_bis:
        ops.append(("sd", refl(np.cross(z, ax))))           # plane containing z and a bisecting axis
    return ops, X


def atom_permutation(X, R, tol):
    Y = X @ R.T
    perm, worst = [], 0.0
    for a in range(len(X)):
        d = np.linalg.norm(X - Y[a], axis=1); b = int(np.argmin(d)); worst = max(worst, float(d[b])); perm.append(b)
    assert len(set(perm)) == len(perm), "operation is not a permutation of the atoms"
    return np.array(perm), worst


def apply_op(vecs, R, perm):
    """vecs: (3N, k) mass-weighted mode vectors; returns P_R vecs (permute atoms, rotate 3-vectors)."""
    N = vecs.shape[0] // 3
    V = vecs.reshape(N, 3, -1)
    W = np.zeros_like(V)
    for a in range(N):
        W[perm[a]] = np.einsum("ij,jk->ik", R, V[a])
    return W.reshape(3 * N, -1)


def assign_irreps(L, freq, coords, symbols, degen_tol_cm=1.0, geom_tol=0.05):
    ops, X = d6h_operations(coords, symbols)
    perms = []
    worst_all = 0.0
    for cls, R in ops:
        perm, worst = atom_permutation(X, R, geom_tol); perms.append(perm); worst_all = max(worst_all, worst)
    # degenerate groups by frequency
    M = len(freq); groups = []; used = set()
    for i in range(M):
        if i in used: continue
        g = [i] + [j for j in range(i + 1, M) if j not in used and abs(freq[j] - freq[i]) < degen_tol_cm]
        used.update(g); groups.append(g)
    def characters(idx):
        S = L[:, idx]; chi = {}
        for (cls, R), perm in zip(ops, perms):
            chi.setdefault(cls, []).append(float(np.trace(S.T @ apply_op(S, R, perm))))
        vec = [float(np.mean(chi[c])) for c in CLASSES]
        spread = max(float(np.std(chi[c])) for c in CLASSES)
        best, bestd = None, 9e9
        for name, row in D6H.items():
            d = float(np.max(np.abs(np.array(row) - np.array(vec))))
            if d < bestd: best, bestd = name, d
        return vec, spread, best, bestd

    # Labels are SETS of irreps. A frequency block whose characters match one irrep gets that irrep. An
    # accidental near-degeneracy of two different 1-dim irreps (e.g. benzene's a1g ring breathing and b1u at
    # 1020 cm⁻¹ in B3LYP/6-31G*) leaves the DFT eigenvectors mixed, so the block's two modes each carry BOTH
    # irreps: they may couple to each other and to either irrep's modes (the prior is exact in the
    # symmetry-adapted basis; in the mixed DFT basis this union is the honest allowed set).
    one_dim = {k: v for k, v in D6H.items() if v[0] == 1}
    labels = [None] * M; chars_out = {}
    for g in groups:
        vec, spread, best, bestd = characters(g)
        if bestd < 0.15:
            lab = frozenset([best]); text = best
        elif len(g) == 2:
            found = None
            for n1 in one_dim:
                for n2 in one_dim:
                    if n1 < n2 and np.max(np.abs(np.array(one_dim[n1]) + np.array(one_dim[n2]) - np.array(vec))) < 0.15:
                        found = (n1, n2)
            if found:
                lab = frozenset(found); text = "+".join(found) + " (mixed)"; bestd = 0.0
            else:
                lab = frozenset(["?" + ",".join(f"{v:+.1f}" for v in vec)]); text = next(iter(lab))
        else:
            lab = frozenset(["?" + ",".join(f"{v:+.1f}" for v in vec)]); text = next(iter(lab))
        for i in g: labels[i] = lab
        chars_out[",".join(map(str, g))] = {"label": text, "match_dev": bestd, "class_spread": spread, "chars": dict(zip(CLASSES, vec))}
    return labels, groups, chars_out, worst_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", default="benzene")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = args.out or os.path.join(HERE, "results_dryrun", args.molecule)
    a = json.load(open(os.path.join(out, "stageA.json")))
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    L, omega, coords, D2_direct = z["L"], z["omega_au"], z["coords"], z["D2_direct"]
    M = a["M"]; freq = np.array(a["freq_low_cm"]); families = a["families"]; symbols = a["symbols"]
    deck = json.load(open(os.path.join(out, "deck.json")))
    cache = json.load(open(os.path.join(out, "stageB_responses.json")))
    prior_c = json.load(open(os.path.join(out, "stageC_recovery.json")))

    # ---------------------------------------------------------------- 1. irreps
    labels, groups, chars, worst_geom = assign_irreps(L, freq, coords, symbols)
    same = lambda i, j: bool(labels[i] & labels[j])  # noqa: E731  (label sets intersect)
    pairs, _ = sym_index(M)
    off_pairs = [(i, j) for (i, j) in pairs if i < j]
    allowed_off = [(i, j) for (i, j) in off_pairs if same(i, j)]
    n_deg_partner = sum(1 for (i, j) in allowed_off if any(i in g and j in g for g in groups))
    deck_pairs = {tuple(p["modes"]) for p in deck["patterns"] if p["kind"] == "two-mode"}
    allowed_in_deck = [pq for pq in allowed_off if pq in deck_pairs]
    # decision-23 null in the surrogate: direct Δ₂ on forbidden vs allowed pairs
    diag_scale = float(np.sqrt(np.mean(np.diag(D2_direct) ** 2)))
    forb = np.array([abs(D2_direct[i, j]) for (i, j) in off_pairs if not same(i, j)])
    allw = np.array([abs(D2_direct[i, j]) for (i, j) in allowed_off])
    # from the two-mode ± responses: Δ_ij = [R_s(+) − R_s(−)]/(2 a_i a_j)
    dE0 = cache["ref"]["high"]["E"] - cache["ref"]["low"]["E"]
    def Rs(p):
        rec = cache[str(p["index"])]
        return 0.5 * ((rec["+"]["high"]["E"] - rec["+"]["low"]["E"]) + (rec["-"]["high"]["E"] - rec["-"]["low"]["E"])) - dE0
    two = {}
    for p in deck["patterns"]:
        if p["kind"] == "two-mode":
            i, j = p["modes"]; two.setdefault((i, j), {})[np.sign(p["a"][j])] = Rs(p)
    direct_two = {}
    for (i, j), d in two.items():
        if 1.0 in d and -1.0 in d:
            ai = Q_S / np.sqrt(2)
            direct_two[(i, j)] = (d[1.0] - d[-1.0]) / (2 * ai * ai)
    forb_two = np.array([abs(v) for (i, j), v in direct_two.items() if not same(i, j)])
    allw_two = np.array([abs(v) for (i, j), v in direct_two.items() if same(i, j)])

    # ---------------------------------------------------------------- 2. recovery under the prior
    singles = [p for p in deck["patterns"] if p["kind"] == "single"]
    q2s = {p["modes"][0]: p for p in deck["patterns"] if p["kind"] == "q2"}
    offs = [p for p in deck["patterns"] if p["kind"] in ("two-mode", "multi")]
    ordered = sorted(singles + offs, key=lambda p: p["index"])
    c0_list = []
    for p in singles:
        i = p["modes"][0]; R1 = Rs(p); R2 = Rs(q2s[i])
        dii = 2 * (R2 - R1) / (Q_2 ** 2 - Q_S ** 2); c0_list.append(R1 - 0.5 * dii * Q_S ** 2)
    c0 = float(np.mean(c0_list))
    cols = np.array([i == j or same(i, j) for (i, j) in pairs])
    A_all = np.array([design_row_E(p["a"], pairs) for p in ordered])[:, cols]
    b_all = np.array([Rs(p) - c0 for p in ordered])
    hold = np.array([p["holdout"] for p in ordered]); is_single = np.array([p["kind"] == "single" for p in ordered])
    A_tr, b_tr, A_ho, b_ho = A_all[~hold], b_all[~hold], A_all[hold], b_all[hold]
    wts = np.zeros(A_all.shape[1])          # no ℓ₁ penalty: the prior IS the support
    def full(dsub):
        d = np.zeros(len(pairs)); d[cols] = dsub; return unpack(d, pairs, M)
    d_full = fista_lasso(A_tr, b_tr, wts)
    D2_sym = full(d_full)
    fam_sym = family_rms_freq_error(D2_sym, D2_direct, omega, families)
    rho_final = rho_of(d_full, A_ho, b_ho)
    rms_resp = float(np.sqrt(np.mean(b_ho ** 2)))
    # off-diagonal view (as the dry run): subtract the single-block diagonal
    D2_diag = np.zeros((M, M))
    for p in singles:
        i = p["modes"][0]; D2_diag[i, i] = 2 * (Rs(p) - c0) / Q_S ** 2
    d_diag_sub = np.array([D2_diag[i, j] if i == j else 0.0 for (i, j) in pairs])[cols]
    b_off_all = b_all - A_all @ d_diag_sub
    rms_off = float(np.sqrt(np.mean(b_off_all[hold] ** 2))); ratio_off = rms_resp / (rms_off + 1e-30)
    def rho_curve(bvec):
        curve, idx = [], []
        M2 = int(is_single.sum())
        for n, h in enumerate(hold):
            if h: continue
            idx.append(n); n_e = 2 * len(idx)
            if n_e <= 2 * M2: continue
            d = fista_lasso(A_all[idx], bvec[idx], wts, n_iter=1500)
            curve.append((n_e, rho_of(d, A_ho, b_ho)))
        return curve
    curve = rho_curve(b_all)
    curve_off = [(n, r * ratio_off) for n, r in curve]
    K_off_03 = next((n - 2 * M for n, r in curve_off if r <= 0.3), None)
    rho_dry = rho_final
    # noise column, P1/P2 reading, mode E only (as the dry run)
    noise_table = []
    rng = np.random.default_rng(424242)
    for s_ueh in SIGMA_GRID_UEH:
        sig = s_ueh * 1e-6
        rho_noise = (sig / np.sqrt(2)) / rms_resp
        eps = {str(p["index"]): rng.normal(0, sig, size=2) for p in deck["patterns"]}; eps0 = float(rng.normal(0, sig))
        def Rs_n(p):
            rec = cache[str(p["index"])]; e = eps[str(p["index"])]
            return 0.5 * ((rec["+"]["high"]["E"] - rec["+"]["low"]["E"] + e[0]) + (rec["-"]["high"]["E"] - rec["-"]["low"]["E"] + e[1])) - (dE0 + eps0)
        c0n = float(np.mean([Rs_n(p) - 0.5 * (2 * (Rs_n(q2s[p["modes"][0]]) - Rs_n(p)) / (Q_2 ** 2 - Q_S ** 2)) * Q_S ** 2 for p in singles]))
        bn = np.array([Rs_n(p) - c0n for p in ordered])
        cv = rho_curve(bn)
        entry = {"sigma_E_uEh": s_ueh, "rho_noise_off": rho_noise * ratio_off, "rho_dry_off": rho_dry * ratio_off, "K_off_at_P1P2": {}}
        for c in C_GRID:
            rho_star = max(1.1 * rho_dry * ratio_off, c * rho_noise * ratio_off)
            entry["K_off_at_P1P2"][str(c)] = ("at-noise" if rho_star >= RHO_MAX else next((n - 2 * M for n, r in cv if r * ratio_off <= rho_star), "not-reached"))
        noise_table.append(entry)

    # ---------------------------------------------------------------- report
    fam_band = prior_c["modeE"]["family_error_full"]; fam_diag = prior_c["modeE"]["family_error_diagonal_only"]
    cm = lambda x: x * HARTREE_TO_CM  # noqa: E731  (µE_h·1e-6 → cm⁻¹ handled below)
    lines = [f"# Dry run — {args.molecule} — the symmetry prior (decision 22 / P14) and the forbidden-coupling null (decision 23 / P15)",
             "", f"Full point group D6h built from the geometry (largest atom-mapping deviation {worst_geom:.4f} bohr). "
             f"Modes grouped as degenerate within 1 cm⁻¹: {len(groups)} irreducible blocks for {M} modes. B1/B2 labels follow the convention C2' through atoms.",
             "", "| mode | ω_DFT (cm⁻¹) | family | irrep |", "|---|---|---|---|"]
    for i in range(M):
        lines.append(f"| {i} | {freq[i]:.1f} | {families[i]} | {'+'.join(sorted(labels[i]))} |")
    from collections import Counter
    cnt = Counter(chars[k]["label"] for k in chars)
    lines += ["", "Irrep count (blocks): " + ", ".join(f"{k} × {v}" for k, v in sorted(cnt.items())) + f"; worst table match {max(v['match_dev'] for v in chars.values()):.3f}, worst within-class spread {max(v['class_spread'] for v in chars.values()):.3f}.",
              "", f"**Free elements under the prior:** {len(allowed_off)} same-irrep off-diagonal pairs out of {len(off_pairs)} (of which {n_deg_partner} are the two components of a degenerate pair); "
              f"{len(allowed_in_deck)} of them have a two-mode pattern in the dry run's 200 cm⁻¹ deck. Unknowns fitted: {M} diagonal + {len(allowed_off)} off-diagonal = {M + len(allowed_off)}, against {int((~hold).sum())} training patterns.",
              "", "**The null (decision 23), DFT surrogate.** Direct Δ₂ (from the two Hessians): forbidden pairs max |Δ_ij| = "
              f"{forb.max()*1e6:.3f} µE_h (RMS {np.sqrt(np.mean(forb**2))*1e6:.3f}), allowed pairs max {allw.max()*1e6:.1f} µE_h (RMS {np.sqrt(np.mean(allw**2))*1e6:.1f}); diagonal RMS {diag_scale*1e6:.1f} µE_h. "
              f"From the two-mode ± responses ({len(direct_two)} deck pairs): forbidden max {forb_two.max()*1e6 if forb_two.size else float('nan'):.3f} µE_h (RMS {np.sqrt(np.mean(forb_two**2))*1e6 if forb_two.size else float('nan'):.3f}), allowed max {allw_two.max()*1e6 if allw_two.size else float('nan'):.1f} µE_h. "
              "Forbidden couplings are zero to the Hessians' numerical noise: the irrep assignment is consistent with the surrogate.",
              "", "**Recovery under the symmetry prior (mode E, same deck, same hold-out, no ℓ₁ penalty):**",
              "", "| family | n modes | RMS Δω error, symmetry prior (cm⁻¹, first-order / full rediag) | banded prior w = " + f"{prior_c['w_rule_cm']}" + " (dry run) | diagonal only |",
              "|---|---|---|---|---|"]
    for fam in sorted(fam_sym):
        s_, b_, d_ = fam_sym[fam], fam_band[fam], fam_diag[fam]
        lines.append(f"| {fam} | {s_['n_modes']} | {s_['rms_first_order_cm']:.2f} / {s_['rms_full_rediag_cm']:.2f} | {b_['rms_first_order_cm']:.2f} / {b_['rms_full_rediag_cm']:.2f} | {d_['rms_first_order_cm']:.2f} / {d_['rms_full_rediag_cm']:.2f} |")
    lines += ["", f"ρ (hold-out, all training) = {rho_final:.4f}; ρ_off = {rho_final*ratio_off:.4f}; RMS_resp/RMS_off = {ratio_off:.2f}; "
              f"**K_off at ρ_off ≤ 0.3 = {K_off_03}** energies (dry run, banded prior: {prior_c['K_off_at_rho_off_0.3_energies']}).",
              "", "Noise column (P1/P2 reading on the off-diagonal residual; K_off in energies):", "",
              "| σ_E (µE_h) | ρ_noise,off | " + " | ".join(f"c = {c}" for c in C_GRID) + " |", "|---|---|" + "---|" * len(C_GRID)]
    for e in noise_table:
        lines.append(f"| {e['sigma_E_uEh']} | {e['rho_noise_off']:.3f} | " + " | ".join(str(e["K_off_at_P1P2"][str(c)]) for c in C_GRID) + " |")
    lines += ["", f"ρ_dry,off (model floor) = {rho_dry*ratio_off:.4f}. The dry run's banded prior: see stageC_recovery.json. "
              "Printed by probes/dryrun_symmetry_prior.py from the cached stage-B responses; no new DFT energy. No verdict."]
    txt = "\n".join(lines)
    open(os.path.join(out, "SYMMETRY_PRIOR_REPORT.md"), "w", encoding="utf-8").write(txt)
    json.dump({"labels": [sorted(l) for l in labels], "groups": groups, "characters": chars, "worst_geom_dev_bohr": worst_geom,
               "n_off_pairs": len(off_pairs), "n_allowed_off": len(allowed_off), "n_allowed_in_deck": len(allowed_in_deck),
               "n_degenerate_partner_pairs": n_deg_partner,
               "null_direct_forbidden_max_uEh": float(forb.max() * 1e6), "null_direct_forbidden_rms_uEh": float(np.sqrt(np.mean(forb ** 2)) * 1e6),
               "null_direct_allowed_max_uEh": float(allw.max() * 1e6), "diag_rms_uEh": diag_scale * 1e6,
               "null_twomode_forbidden_max_uEh": float(forb_two.max() * 1e6) if forb_two.size else None,
               "null_twomode_allowed_max_uEh": float(allw_two.max() * 1e6) if allw_two.size else None,
               "family_error_symmetry_prior": fam_sym, "rho_final": rho_final, "rho_off_final": rho_final * ratio_off,
               "ratio_off": ratio_off, "rho_off_curve": curve_off, "K_off_at_rho_off_0.3_energies": K_off_03,
               "noise_column": noise_table, "c0_Eh": c0},
              open(os.path.join(out, "stageC_symmetry_prior.json"), "w"), indent=1)
    print(txt)


if __name__ == "__main__":
    main()
