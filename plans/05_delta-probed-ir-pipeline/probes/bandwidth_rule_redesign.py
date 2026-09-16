#!/usr/bin/env python3
"""Redesign of the band-width rule (desk work, 16 September 2026; no new energies).

The rule in `dryrun_dft_delta_recovery.py` picks the smallest candidate width whose worst-family
frequency RMS **against the direct Δ₂** clears τ₇ = 5 cm⁻¹. Two faults: it reads a quantity a real
molecule does not have, and "smallest that clears a tolerance" stops at the first acceptable answer
(w = 25, 3.37 cm⁻¹) instead of the best available one (w = 400, 0.82 cm⁻¹).

The replacement uses only fitted quantities:

  sigma(w)  how far the answer moves when a fifth of the training data is dropped (5-fold),
            measured in cm⁻¹ as the worst-family frequency RMS against the full-data fit at the
            same w. This is the noise the data itself carries.
  drift(w)  how far the answer at width w sits from the answer at the widest width tried,
            same units, same worst-family aggregation. This is what the truncation costs.

  RULE: choose the smallest w with drift(w) <= sigma(w) — the narrowest band whose answer the data
        cannot distinguish from the widest one. If only w_max qualifies, the ladder is too short and
        the run says so rather than selecting silently.

Run: OMP_NUM_THREADS=2 python bandwidth_rule_redesign.py --dir results_dryrun/naphthalene_sym
"""
import argparse, json, os, sys
import numpy as np
import dryrun_dft_delta_recovery as dr

LADDER = [25.0, 50.0, 100.0, 200.0, 400.0, 800.0, 1600.0, 3200.0]
LAM_GRID = [1e-7, 1e-6, 1e-5, 1e-4]
NFOLD = 5


def load(out):
    a = json.load(open(os.path.join(out, "stageA.json")))
    deck = json.load(open(os.path.join(out, "deck.json")))
    cache = json.load(open(os.path.join(out, "stageB_responses.json")))
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    return a, deck, cache, z


def build(a, deck, cache, z):
    """Exactly stage C's mode-E design: same c₀, same rows, same hold-out flags."""
    L, omega, Minv = z["L"], z["omega_au"], z["Minv"]
    M = a["M"]
    pairs, _ = dr.sym_index(M)
    ref = cache["ref"]
    dE0 = ref["high"]["E"] - ref["low"]["E"]

    def resp_S(p):
        rec = cache[str(p["index"])]
        e_plus = rec["+"]["high"]["E"] - rec["+"]["low"]["E"]
        e_minus = rec["-"]["high"]["E"] - rec["-"]["low"]["E"]
        return 0.5 * (e_plus + e_minus) - dE0

    singles = [p for p in deck["patterns"] if p["kind"] == "single"]
    q2s = {p["modes"][0]: p for p in deck["patterns"] if p["kind"] == "q2"}
    offs = [p for p in deck["patterns"] if p["kind"] in ("two-mode", "multi")]
    ordered = sorted(singles + offs, key=lambda p: p["index"])

    c0_list = []
    for p in singles:
        i = p["modes"][0]
        Rs1, Rs2 = resp_S(p), resp_S(q2s[i])
        dii = 2 * (Rs2 - Rs1) / (dr.Q_2 ** 2 - dr.Q_S ** 2)
        c0_list.append(Rs1 - 0.5 * dii * dr.Q_S ** 2)
    c0 = float(np.mean(c0_list))

    A_all = np.array([dr.design_row_E(p["a"], pairs) for p in ordered])
    b_all = np.array([resp_S(p) - c0 for p in ordered])
    hold = np.array([p["holdout"] for p in ordered])
    return dict(A_tr=A_all[~hold], b_tr=b_all[~hold], A_ho=A_all[hold], b_ho=b_all[hold],
                pairs=pairs, M=M, omega=omega, freq=np.array(a["freq_low_cm"]),
                families=a["families"], D2_direct=z["D2_direct"])


def worst_family(D2_a, D2_b, omega, families):
    fam = dr.family_rms_freq_error(D2_a, D2_b, omega, families)
    return max(v["rms_full_rediag_cm"] for v in fam.values())


def fit(A, b, d, w, lam):
    wts = dr.band_weights(d["pairs"], d["freq"], w, lam * np.max(np.abs(d["A_tr"])))
    return dr.unpack(dr.fista_lasso(A, b, wts), d["pairs"], d["M"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--seed", type=int, default=20260916)
    ap.add_argument("--fixed-lam", type=float, default=None, dest="fixed_lam",
                    help="hold lambda at this value for every width, isolating the width effect from the lambda choice")
    args = ap.parse_args()
    out = args.dir if os.path.isabs(args.dir) else os.path.join(os.path.dirname(os.path.abspath(__file__)), args.dir)
    a, deck, cache, z = load(out)
    d = build(a, deck, cache, z)
    n = len(d["b_tr"])
    rng = np.random.default_rng(args.seed)
    folds = rng.permutation(n) % NFOLD
    print(f"{n} training rows, {len(d['pairs'])} unknowns, ladder {LADDER}\n")

    full, lam_of = {}, {}
    for w in LADDER:                       # λ per width by hold-out ρ, as before
        best = (np.inf, None, None)
        for lam in ([args.fixed_lam] if args.fixed_lam else LAM_GRID):
            D = fit(d["A_tr"], d["b_tr"], d, w, lam)
            flat = np.array([D[i, j] for (i, j) in d["pairs"]])
            r = dr.rho_of(flat, d["A_ho"], d["b_ho"])
            if r < best[0]:
                best = (r, lam, D)
        full[w], lam_of[w] = best[2], best[1]
        print(f"  w={w:6.0f}  lambda={best[1]:.0e}  rho_holdout={best[0]:.4f}")

    w_max = LADDER[-1]
    print(f"\n{'w':>6} {'sigma (cm-1)':>13} {'drift vs w_max':>15} {'drift<=sigma':>13} "
          f"{'| true err':>11}  (the last column is the rehearsal's answer key, not an input to the rule)")
    rows, chosen = [], None
    for w in LADDER:
        devs = []
        for k in range(NFOLD):
            m = folds != k
            Dk = fit(d["A_tr"][m], d["b_tr"][m], d, w, lam_of[w])
            devs.append(worst_family(Dk, full[w], d["omega"], d["families"]))
        sigma = float(np.sqrt(np.mean(np.square(devs))))
        drift = worst_family(full[w], full[w_max], d["omega"], d["families"])
        true_err = worst_family(full[w], d["D2_direct"], d["omega"], d["families"])
        ok = drift <= sigma
        if ok and chosen is None:
            chosen = w
        rows.append(dict(w_cm=w, sigma_cm=sigma, drift_cm=drift, passes=bool(ok),
                         true_worst_family_cm=true_err, lam=lam_of[w]))
        print(f"{w:6.0f} {sigma:13.3f} {drift:15.3f} {str(ok):>13} {true_err:11.3f}")

    print()
    # What a truth-free diagnostic can and cannot say. It can detect that two widths DISAGREE by
    # more than the data's own noise. It cannot say which of them is RIGHT — that is precisely what
    # the old rule used the direct Δ₂ for. Both numbers are printed so the distinction stays visible.
    spread = max(r["drift_cm"] for r in rows) - min(r["drift_cm"] for r in rows)
    sigma_med = float(np.median([r["sigma_cm"] for r in rows]))
    disagree = [r["w_cm"] for r in rows if r["drift_cm"] > r["sigma_cm"]]
    discriminating = bool(disagree)
    print(f"DIAGNOSTIC: median fold-to-fold noise {sigma_med:.3f} cm-1; drift spread {spread:.3f} cm-1.")
    if disagree:
        print(f"            Widths whose answer differs from w_max by more than their own noise: "
              f"{', '.join(f'{w:.0f}' for w in disagree)} — the data can see that these DISAGREE with the")
        print("            widest fit, but nothing here says which is closer to the truth. No truth-free")
        print("            score can rank widths; that is what the old rule needed the direct Delta_2 for.")
    else:
        print("            No width differs from the widest by more than its own noise: the data cannot")
        print("            separate the ladder at all, and any choice below is parsimony, not evidence.")
    worst_true = max(r["true_worst_family_cm"] for r in rows)
    best_true = min(r["true_worst_family_cm"] for r in rows)
    print(f"            Rehearsal answer key, for scale: the whole ladder spans {best_true:.2f}-{worst_true:.2f} cm-1")
    print(f"            of true worst-family error. The project needs 0.5. No width on this ladder reaches it.")
    if chosen is None:
        print("RULE: no width qualifies — the ladder is too short; extend it and rerun.")
    elif chosen == w_max:
        print(f"RULE: only w_max = {w_max:.0f} qualifies — the ladder is too short to show a plateau; "
              f"extend it and rerun before trusting the choice.")
    else:
        print(f"RULE selects w = {chosen:.0f} cm-1 (lambda {lam_of[chosen]:.0e}).")
    old = min((r for r in rows), key=lambda r: r["w_cm"])
    print(f"OLD rule selected w = 25 (smallest clearing tau7 = 5.0 against the direct Delta_2): "
          f"true worst family {old['true_worst_family_cm']:.3f} cm-1")
    if chosen is not None:
        c = next(r for r in rows if r["w_cm"] == chosen)
        print(f"NEW rule's width: true worst family {c['true_worst_family_cm']:.3f} cm-1 "
              f"-- and it never read the direct Delta_2 to get there.")
    json.dump(dict(ladder=LADDER, nfold=NFOLD, seed=args.seed, rows=rows, selected=chosen,
                   sigma_median_cm=sigma_med, drift_spread_cm=spread, discriminating=bool(discriminating)),
              open(os.path.join(out, "bandwidth_rule_redesign.json"), "w"), indent=1)
    print(f"\nwritten: {os.path.join(out, 'bandwidth_rule_redesign.json')}")


if __name__ == "__main__":
    main()
