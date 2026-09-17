#!/usr/bin/env python3
"""Like-for-like control for the amplitude test.

The q = 0.5 block is only partly computed, so its rho_off is fitted on fewer patterns than the
q = 1.0 block. Fewer training rows inflate a held-out residual on their own. This restricts the
q = 1.0 block to EXACTLY the pattern indices the half-amplitude cache holds, so the two numbers
differ only in amplitude.
"""
import json, os, sys
import numpy as np
import dryrun_dft_delta_recovery as dr
import amplitude_test as at

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_dryrun", "naphthalene_sym")
z = np.load(os.path.join(out, "stageA_hessians.npz"))
omega, D2_direct = z["omega_au"], z["D2_direct"]
a = json.load(open(os.path.join(out, "stageA.json")))
deck = json.load(open(os.path.join(out, "deck.json")))
M = a["M"]; freq = np.array(a["freq_low_cm"]); families = a["families"]
pairs, _ = dr.sym_index(M)
full = json.load(open(os.path.join(out, "stageB_responses.json")))
half = json.load(open(os.path.join(out, at.CACHE)))
dE0 = full["ref"]["high"]["E"] - full["ref"]["low"]["E"]


def Rs(cache, idx):
    r = cache[str(idx)]
    return 0.5 * ((r["+"]["high"]["E"] - r["+"]["low"]["E"]) + (r["-"]["high"]["E"] - r["-"]["low"]["E"])) - dE0


singles = [p for p in deck["patterns"] if p["kind"] == "single"]
q2s = {p["modes"][0]: p for p in deck["patterns"] if p["kind"] == "q2"}
c0 = float(np.mean([Rs(full, p["index"]) - 0.5 * (2 * (Rs(full, q2s[p["modes"][0]]["index"]) - Rs(full, p["index"]))
                                                 / (dr.Q_2 ** 2 - dr.Q_S ** 2)) * dr.Q_S ** 2 for p in singles]))
d2q = np.zeros(M); d4 = np.zeros(M)
Aq = np.array([[0.5 * dr.Q_S ** 2, dr.Q_S ** 4 / 24], [0.5 * dr.Q_2 ** 2, dr.Q_2 ** 4 / 24]])
for p in singles:
    i = p["modes"][0]
    d2q[i], d4[i] = np.linalg.solve(Aq, np.array([Rs(full, p["index"]) - c0, Rs(full, q2s[i]["index"]) - c0]))

W = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0
print("band width %.0f cm-1" % W)
have = set(half.keys())
print("matched control: %d pattern indices present in both blocks\n" % len(have))
print("%-8s %9s %12s %10s %12s" % ("block", "patterns", "off RMS uEh", "rho_off", "worst fam"))
res = {}
for tag, pats, cache in (("q=1.0", [p for p in deck["patterns"] if p["kind"] in ("two-mode", "multi")], full),
                         ("q=0.5", at.half_patterns(deck), half)):
    pats = [p for p in pats if str(p["index"]) in have]
    A = np.array([dr.design_row_E(p["a"], pairs) for p in pats])
    b = np.array([Rs(cache, p["index"]) - c0 for p in pats])
    hold = np.array([p["holdout"] for p in pats])
    quart = np.array([np.sum(d4 * np.asarray(p["a"]) ** 4) / 24.0 for p in pats])
    d_diag = np.array([d2q[i] if i == j else 0.0 for (i, j) in pairs])
    b_off = b - quart - A @ d_diag
    off = np.array([i != j for (i, j) in pairs])
    wts = dr.band_weights(pairs, freq, W, 1e-7 * np.max(np.abs(A[~hold])))
    d = np.zeros(len(pairs))
    d[off] = dr.fista_lasso(A[~hold][:, off], b_off[~hold], wts[off])
    rms = float(np.sqrt(np.mean(b_off[hold] ** 2)))
    rho = float(np.sqrt(np.mean((A[hold][:, off] @ d[off] - b_off[hold]) ** 2)) / (rms + 1e-30))
    fam = dr.family_rms_freq_error(dr.unpack(d + d_diag, pairs, M), D2_direct, omega, families)
    worst = max(v["rms_full_rediag_cm"] for v in fam.values())
    res[tag] = dict(n=len(pats), rms_uEh=rms * 1e6, rho_off=rho, worst_cm=worst,
                    n_train=int((~hold).sum()), n_hold=int(hold.sum()))
    print("%-8s %9d %12.3f %10.3f %12.3f" % (tag, len(pats), rms * 1e6, rho, worst))

r1, rh = res["q=1.0"], res["q=0.5"]
print("\ntrain/hold split (identical by construction): %d / %d" % (r1["n_train"], r1["n_hold"]))
print("signal fell by %.2fx (q^2 predicts 4.00x)" % (r1["rms_uEh"] / rh["rms_uEh"]))
print("rho_off improved by %.2fx (a fourfold ratio gain predicts ~4x)" % (r1["rho_off"] / rh["rho_off"]))
json.dump(res, open(os.path.join(out, ("amplitude_test_matched_control_w%d.json" % int(W))), "w"), indent=1)
print("written: amplitude_test_matched_control.json")
