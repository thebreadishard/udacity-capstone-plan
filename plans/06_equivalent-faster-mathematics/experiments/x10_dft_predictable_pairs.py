"""X10 (2026-09-12, evening) — can the off-diagonal elements that matter be predicted from DFT alone? (direction S4, "reduce the target")

X2 found that of 435 off-diagonal Δ₂ elements at benzene only 6 move any band by more than 0.5 cm⁻¹, and that all of them join two
modes of the same irreducible representation. Plan 05's symmetry prior already restricts the deck to same-irrep pairs (57 at benzene,
stageC_symmetry_prior.json 'n_allowed_off'). The next saving would be to measure only the same-irrep pairs a DFT-computable rule ranks
highest. Second-order perturbation theory says the effect of an off-diagonal element Δ_ij on the band positions is ≈ Δ_ij² / |ω_i² − ω_j²|
(in ω² units), so the DFT-only part of that predictor is the resonance denominator 1/|ω_i² − ω_j²|.

This script ranks the allowed pairs by three predictors and, for each, asks how many top-ranked pairs must be kept (all other off-diagonal
elements zeroed, diagonal kept) for every harmonic band to stay within 0.5 cm⁻¹ of the full-Δ₂ positions (X2's exact rule):
  (P1) DFT-only: 1/|ω_i² − ω_j²| among same-irrep pairs;
  (P2) oracle magnitude: |Δ_ij| (what a perfect prior for the element sizes would give — an upper bound for any learned prior);
  (P3) oracle effect: X2's measured drop-one effect (the best possible ordering).
Printed: n needed at 0.5 and at 0.1 cm⁻¹ for each predictor; the implied energies (2 per diagonal mode + 2 per kept pair in mode E's
symmetric pattern, the convention of the dry run's K = 2M + K_off) against K = 448; rank correlation between P1 and P3; the top-10 lists.
Losing condition for the DFT-only rule (pre-stated): n(P1) at 0.5 cm⁻¹ exceeds half the allowed pairs. Every number from the files."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
HARTREE_TO_CM = 219474.63
CONSTANTS = {"tolerances_cm": [0.5, 0.1], "K_measured_plan05": 448, "energies_per_diag_mode": 2, "energies_per_off_pair": 2}


def freqs_cm(W2):
    w2 = np.linalg.eigvalsh((W2 + W2.T) / 2)
    return np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main():
    z = np.load(PLAN05 / "probes/results_dryrun/benzene/stageA_hessians.npz")
    a = json.load(open(PLAN05 / "probes/results_dryrun/benzene/stageA.json"))
    sp = json.load(open(PLAN05 / "probes/results_dryrun/benzene/stageC_symmetry_prior.json"))
    DQ, w = z["D2_direct_Q"], z["omega_au"]; M = len(w)
    labels = [set(l) for l in sp["labels"]]
    grp = {}
    for gi, g in enumerate(sp["groups"]):
        for m in g:
            grp[m] = gi
    W2 = np.diag(w ** 2) + DQ; f0 = freqs_cm(W2)
    allowed_all = [(i, j) for i in range(M) for j in range(i + 1, M) if labels[i] & labels[j]]
    def is_partner(i, j):  # the two components of one degenerate E level: no independent element; an accidental near-degeneracy (e.g. A1g/B1u at 1020 cm-1) is kept
        return grp[i] == grp[j] and len(labels[i]) == 1 and next(iter(labels[i])).startswith("E")
    partner = [(i, j) for i, j in allowed_all if is_partner(i, j)]
    allowed = [(i, j) for i, j in allowed_all if not is_partner(i, j)]
    forbidden = [(i, j) for i in range(M) for j in range(i + 1, M) if not (labels[i] & labels[j])]
    # baseline: diagonal + all allowed pairs (plan 05's symmetry prior), forbidden zeroed
    def shift_keep(pairs):
        W = np.diag(np.diag(W2))
        for i, j in pairs:
            W[i, j] = W[j, i] = W2[i, j]
        return float(np.abs(freqs_cm(W) - f0).max())
    base_allowed = shift_keep(allowed)
    # predictors
    den = np.array([1.0 / abs(w[i] ** 2 - w[j] ** 2) for i, j in allowed])
    mag = np.array([abs(DQ[i, j]) for i, j in allowed])
    eff = []
    for i, j in allowed:
        W = W2.copy(); W[i, j] = W[j, i] = 0.0
        eff.append(float(np.abs(freqs_cm(W) - f0).max()))
    eff = np.array(eff)
    preds = {"P1 DFT-only 1/|w_i^2-w_j^2|": den, "P2 oracle |Delta_ij|": mag, "P3 oracle drop-one effect": eff}
    res = {}
    for name, p in preds.items():
        order = np.argsort(-p)
        curve = []
        for k in range(0, len(allowed) + 1):
            curve.append(shift_keep([allowed[t] for t in order[:k]]))
        curve = np.array(curve)
        need = {}
        for tol in CONSTANTS["tolerances_cm"]:
            ok = np.nonzero(curve <= tol)[0]
            need[str(tol)] = int(ok[0]) if len(ok) else None
        res[name] = {"n_needed": need, "curve_first_20": curve[:21].tolist(), "top10": [(allowed[t], float(p[t]), float(eff[t]), round(float(w[allowed[t][0]] * HARTREE_TO_CM), 1), round(float(w[allowed[t][1]] * HARTREE_TO_CM), 1)) for t in order[:10]]}
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "M": M, "n_allowed_pairs": len(allowed), "n_forbidden_pairs": len(forbidden),
           "n_degenerate_partner_pairs_excluded": len(partner), "max_shift_dropping_partner_pairs_cm": shift_keep(allowed),
           "plan05_prior": {k: sp.get(k) for k in ("n_allowed_off", "n_allowed_in_deck", "n_degenerate_partner_pairs", "K_off_at_rho_off_0.3_energies")},
           "max_shift_dropping_all_forbidden_keeping_allowed_cm": base_allowed, "max_shift_dropping_all_offdiag_cm": shift_keep([]),
           "spearman_P1_vs_P3": spearman(den, eff), "spearman_P2_vs_P3": spearman(mag, eff), "predictors": res}
    json.dump(out, open(HERE / "x10_dft_predictable_pairs.json", "w"), indent=1)
    E = lambda n: CONSTANTS["energies_per_diag_mode"] * M + CONSTANTS["energies_per_off_pair"] * n
    L = [f"# X10 — which off-diagonal pairs must be measured, and can DFT alone say which (benzene, {out['date']})", "",
         f"Same-irrep pairs: {len(allowed_all)} of 435, of which {len(partner)} join the two components of one degenerate level (no independent element; plan 05's prior file counts "
         f"{sp.get('n_degenerate_partner_pairs')} such pairs and {sp.get('n_allowed_in_deck')} allowed pairs in the deck) — ranked here: the remaining **{len(allowed)}**; forbidden: {len(forbidden)}. "
         f"Keeping the diagonal and all {len(allowed)} ranked pairs, zeroing everything else: max band shift {base_allowed:.3f} cm⁻¹ (the symmetry prior is exact to that level). "
         f"Dropping every off-diagonal element: {out['max_shift_dropping_all_offdiag_cm']:.2f} cm⁻¹.", "",
         f"Rank correlation (Spearman) of the DFT-only denominator with the measured drop-one effect over the allowed pairs: **{out['spearman_P1_vs_P3']:.3f}**; of the oracle magnitude: {out['spearman_P2_vs_P3']:.3f}.", "",
         "| predictor | pairs needed for ≤ 0.5 cm⁻¹ | energies (2M + 2n) | pairs needed for ≤ 0.1 cm⁻¹ | energies |", "|---|---|---|---|---|"]
    for name, r in res.items():
        n5, n1 = r["n_needed"]["0.5"], r["n_needed"]["0.1"]
        L.append(f"| {name} | **{n5}** | {E(n5) if n5 is not None else '—'} | {n1} | {E(n1) if n1 is not None else '—'} |")
    L += ["", f"Against plan 05's measured deck K = {CONSTANTS['K_measured_plan05']} (2M = {2*M} diagonal energies plus K_off under the stopping rule). "
          "The energies column is the naive symmetric-pattern count and ignores that the dry run's deck also buys its noise column and stopping test; it is a lower bound on any real deck.", ""]
    for name, r in res.items():
        L += [f"Top 10 by {name} — (i, j), predictor value, measured effect (cm⁻¹), ω_i, ω_j (cm⁻¹):", ""]
        L += [f"- {t[0]} · {t[1]:.3e} · effect {t[2]:.3f} · {t[3]} / {t[4]}" for t in r["top10"]]
        L.append("")
    L += ["Reading: P3 is the best any ordering can do; P2 is what a perfect element-size prior (Module 05's target) would do; P1 is what DFT knows for free. "
          "Losing condition for the DFT-only rule (pre-stated): n(P1) at 0.5 cm⁻¹ above half the allowed pairs. One molecule, one stand-in functional pair; a rule, if any, is proposed for naphthalene, not adopted.", "",
          "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x10_dft_predictable_pairs.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
