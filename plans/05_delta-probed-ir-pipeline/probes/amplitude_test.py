#!/usr/bin/env python3
"""The amplitude test, pre-registered in FINDING_2026-09-16_Stage_C_Off_Diagonal_Recovery.md.

Stage C found the off-diagonal recovery blocked at naphthalene: the couplings (7.00 uE_h) are the size
of the quartic contamination of a quadratic model at q_s = 1.0 (6.74 uE_h). The contamination falls as
q^4 and the signal as q^2, so halving the amplitude should improve the ratio fourfold.

PRE-REGISTERED PREDICTION (16 Sep 15:45, before any half-amplitude energy existed):
    rho_off ~ 0.24 +- 0.1   contamination-dominated -> the energies route survives
    rho_off >= 0.8          noise-dominated         -> no amplitude window at naphthalene
Stage B2 (16 Sep 22:19) measured this arm's noise floor at 0.0059 uE_h against a half-amplitude
off-diagonal signal near 1.75 uE_h, so for THIS arm the second branch is already implausible. The
coupled-cluster arm's own noise is a separate question this run does not touch.

  --stage run       the 616 off-diagonal patterns at q = 0.5 (resumable, own cache file)
  --stage analyse   rho_off at q = 0.5 beside the q = 1.0 value, diagonal anchored from the single block
"""
import argparse, json, os, time
import numpy as np
import dryrun_dft_delta_recovery as dr

HALF = 0.5
CACHE = "stageB_half_responses.json"


def half_patterns(deck):
    """The off-diagonal block at half amplitude: same patterns, same hold-out split, a -> a/2."""
    out = []
    for p in deck["patterns"]:
        if p["kind"] in ("two-mode", "multi"):
            q = dict(p)
            q["a"] = (np.asarray(p["a"]) * HALF).tolist()
            q["amp"] = p["amp"] * HALF
            q["kind"] = p["kind"] + "-half"
            out.append(q)
    return out


def run(psi4, a, deck, out, limit=None):
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    symbols = a["symbols"]
    path = os.path.join(out, CACHE)
    cache = json.load(open(path)) if os.path.exists(path) else {}
    pats = half_patterns(deck)
    if limit:
        pats = pats[:limit]
    total = len(pats)
    t0_all, n_done = time.time(), 0
    for p in pats:
        key = str(p["index"])
        if key in cache:
            continue
        rec = {}
        for sign in ("+", "-"):
            disp = dr.pattern_to_cartesian(p["a"], L, omega, Minv).reshape(-1, 3)
            x = coords0 + (1.0 if sign == "+" else -1.0) * disp
            rec[sign] = {}
            for arm, fn in dr.FUNCTIONALS.items():
                m = dr.make_molecule(psi4, symbols, x)
                t0 = time.time()
                e, g = dr.dft_energy_gradient(psi4, m, fn)
                rec[sign][arm] = {"E": e, "g": g.tolist(), "wall_s": time.time() - t0}
        cache[key] = rec
        n_done += 1
        if n_done % 5 == 0 or n_done == total:
            json.dump(cache, open(path, "w"))
            el = time.time() - t0_all
            done = sum(1 for q in pats if str(q["index"]) in cache)
            dr.log("amplitude test: %d/%d patterns, %.1f min, %.1f s per pattern"
                   % (done, total, el / 60, el / max(n_done, 1)))
    json.dump(cache, open(path, "w"))
    dr.log("amplitude test: responses done")


def analyse(a, deck, out):
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    omega, D2_direct = z["omega_au"], z["D2_direct"]
    M = a["M"]
    freq = np.array(a["freq_low_cm"])
    families = a["families"]
    pairs, _ = dr.sym_index(M)
    full = json.load(open(os.path.join(out, "stageB_responses.json")))
    hpath = os.path.join(out, CACHE)
    half = json.load(open(hpath)) if os.path.exists(hpath) else {}
    dE0 = full["ref"]["high"]["E"] - full["ref"]["low"]["E"]

    def Rs(cache, idx):
        r = cache[str(idx)]
        ep = r["+"]["high"]["E"] - r["+"]["low"]["E"]
        em = r["-"]["high"]["E"] - r["-"]["low"]["E"]
        return 0.5 * (ep + em) - dE0

    singles = [p for p in deck["patterns"] if p["kind"] == "single"]
    q2s = {p["modes"][0]: p for p in deck["patterns"] if p["kind"] == "q2"}
    c0_list = []
    for p in singles:
        i = p["modes"][0]
        r1, r2 = Rs(full, p["index"]), Rs(full, q2s[i]["index"])
        dii = 2 * (r2 - r1) / (dr.Q_2 ** 2 - dr.Q_S ** 2)
        c0_list.append(r1 - 0.5 * dii * dr.Q_S ** 2)
    c0 = float(np.mean(c0_list))
    d2q = np.zeros(M)
    d4 = np.zeros(M)
    Aq = np.array([[0.5 * dr.Q_S ** 2, dr.Q_S ** 4 / 24], [0.5 * dr.Q_2 ** 2, dr.Q_2 ** 4 / 24]])
    for p in singles:
        i = p["modes"][0]
        rhs = np.array([Rs(full, p["index"]) - c0, Rs(full, q2s[i]["index"]) - c0])
        d2q[i], d4[i] = np.linalg.solve(Aq, rhs)

    res = {}
    blocks = [("q=1.0", [p for p in deck["patterns"] if p["kind"] in ("two-mode", "multi")], full),
              ("q=0.5", half_patterns(deck), half)]
    for tag, pats, cache in blocks:
        pats = [p for p in pats if str(p["index"]) in cache]
        if not pats:
            print("%s: no responses yet" % tag)
            continue
        A = np.array([dr.design_row_E(p["a"], pairs) for p in pats])
        b = np.array([Rs(cache, p["index"]) - c0 for p in pats])
        hold = np.array([p["holdout"] for p in pats])
        if hold.sum() == 0 or (~hold).sum() == 0:
            print("%s: %d patterns, not enough for a hold-out yet" % (tag, len(pats)))
            continue
        quart = np.array([np.sum(d4 * np.asarray(p["a"]) ** 4) / 24.0 for p in pats])
        d_diag = np.array([d2q[i] if i == j else 0.0 for (i, j) in pairs])
        b_off = b - quart - A @ d_diag
        off = np.array([i != j for (i, j) in pairs])
        wts = dr.band_weights(pairs, freq, 25.0, 1e-7 * np.max(np.abs(A[~hold])))
        d = np.zeros(len(pairs))
        d[off] = dr.fista_lasso(A[~hold][:, off], b_off[~hold], wts[off])
        rms_off = float(np.sqrt(np.mean(b_off[hold] ** 2)))
        rho_off = float(np.sqrt(np.mean((A[hold][:, off] @ d[off] - b_off[hold]) ** 2)) / (rms_off + 1e-30))
        fam = dr.family_rms_freq_error(dr.unpack(d + d_diag, pairs, M), D2_direct, omega, families)
        worst = max(v["rms_full_rediag_cm"] for v in fam.values())
        res[tag] = dict(n_patterns=len(pats), rms_off_uEh=rms_off * 1e6, rho_off=rho_off,
                        worst_family_cm=worst, family=fam)
        print("%s: %d patterns, off-diagonal RMS %8.3f uE_h, rho_off = %.3f, worst family %.3f cm-1"
              % (tag, len(pats), rms_off * 1e6, rho_off, worst))
    if "q=0.5" in res:
        r = res["q=0.5"]["rho_off"]
        if r <= 0.34:
            verdict = "PASS: contamination-dominated, as predicted"
        elif r >= 0.8:
            verdict = "FAIL: no amplitude window at naphthalene"
        else:
            verdict = "BETWEEN the pre-registered branches"
        print("")
        print("Pre-registered: 0.24 +- 0.1 contamination-dominated; >= 0.8 noise-dominated.")
        print("Measured rho_off(q=0.5) = %.3f  ->  %s" % (r, verdict))
        res["verdict"] = verdict
        res["prediction"] = {"contamination_branch": [0.14, 0.34], "noise_branch_at_or_above": 0.8}
    json.dump(res, open(os.path.join(out, "amplitude_test.json"), "w"), indent=1)
    print("written: " + os.path.join(out, "amplitude_test.json"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", default="naphthalene")
    ap.add_argument("--dir", default=None)
    ap.add_argument("--stage", default="run", choices=["run", "analyse"])
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--psi4-memory", default="3 GB", dest="psi4_memory")
    ap.add_argument("--limit", type=int, default=None, help="smoke test: only this many patterns")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = args.dir or os.path.join(here, "results_dryrun", args.molecule + "_sym")
    a = json.load(open(os.path.join(out, "stageA.json")))
    deck = json.load(open(os.path.join(out, "deck.json")))
    if args.stage == "run":
        psi4 = dr.psi4_setup(args.threads, os.path.join(out, "psi4_half.out"), args.psi4_memory)
        run(psi4, a, deck, out, args.limit)
    else:
        analyse(a, deck, out)


if __name__ == "__main__":
    main()
