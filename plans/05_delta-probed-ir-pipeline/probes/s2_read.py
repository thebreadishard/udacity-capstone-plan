"""S2's registered read (14 Oct 2026; `GoalGathering/notes/PreRegistration_2026-10-14_S2_Anharmonic_Shift.md` with amendment 1): can the
per-mode anharmonic shift Δ_anh = ν − ω be predicted from the mode's own description (route b) better than by one constant per family
(route c), and well enough (≤ 3.0 cm⁻¹) for the spectral shape?

    python s2_read.py <s2_root> --selection <selection.json> [--setting G] [--extra ID=DIR ...] --out <dir>

<s2_root>/<id>/<setting>/ holds a molecule's reference Hessian (ref.json) and dpir.qff report (qff_report.npz), as probes/s2_batch.sh
leaves them; --extra adds a molecule computed elsewhere (benzene: S1's G directory). A molecule without a report (STOPPED, FAILED) or with
a NOISY marker is excluded and named (the registration's noise rule).

Per mode: ω and Δ_anh (dpir.qff's symmetry-averaged ν, each normal mode one row), the corpus family (`e8_cc_locality.families`), and the
features of route (b) — the hydrogen share h and the out-of-plane share o of the mass-weighted mode (`e8_cc_locality.mode_shares`, the
family rule's own numbers; o without the rule's planarity gate, so a methylated molecule keeps its feature).
- (c) family constants: the mean Δ_anh of the training modes of the family.
- (b) Δ_anh = a_f + b_f · ω/1000 + c · h + d · o, least squares with a ridge of 1e-3 on all ten coefficients, features as given.
Development note (14 Oct 2026, before any S2 report was read): both routes are fitted on the training molecules' modes inside the window
(550–2,000 cm⁻¹), the modes they are scored on; below 550 cm⁻¹ are the torsions and methyl rotors whose VPT2 shifts are not this read's
object. A held-out mode whose family has no training mode (possible only in a small subset) is predicted by the training window mean in
both routes, and counted.

Read: leave one scaffold out, pooled rms over all held-out window modes; amendment 1's learning curve — for each held-out scaffold, k ∈ {4,
6, 8, 10} of its training scaffolds in 20 random subsets per k (numpy default_rng(0); draws in the order k, subset, held-out scaffold; the
same subsets for both routes) and 'all'; per k the mean of the pooled rms over the subsets and its standard error. Verdicts as amendment 1.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.optimize import curve_fit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from e8_cc_locality import families, mode_shares  # noqa: E402

FAMILIES = ("CH-stretch", "CH-oop", "ring-ip", "other")
WINDOW = (550.0, 2000.0)
KS = (4, 6, 8, 10)
N_SUBSETS = 20
RIDGE = 1e-3
LINE_LICENSE = 3.0          # cm⁻¹, line 2
LINE_RATIO = 0.8            # line 1: (b) ≤ 0.8 × (c)


def load_molecule(setting_dir):
    """The per-mode table of one molecule from its setting directory; None (with the reason) if it is excluded."""
    from s1_anharmonic_level import harmonic_modes

    from dpir.qff import MASS
    if os.path.exists(os.path.join(setting_dir, "NOISY")):
        return None, "NOISY (noise rule)"
    rep = os.path.join(setting_dir, "qff_report.npz")
    if not os.path.exists(rep):
        return None, "no qff_report.npz (STOPPED or FAILED)"
    ref = os.path.join(setting_dir, "ref.json")
    omega, q = harmonic_modes(ref)
    z = np.load(rep)
    if len(z["omega_cm"]) != len(omega) or not np.allclose(z["omega_cm"], omega, atol=1e-3):
        raise SystemExit(f"{setting_dir}: the report's ω does not match its own ref.json (max diff "
                         f"{np.abs(np.asarray(z['omega_cm']) - omega).max() if len(z['omega_cm']) == len(omega) else 'shape'})")
    r = json.load(open(ref, encoding="utf-8"))
    sym = r["molecule"]["symbols"]
    x = np.array(r["molecule"]["geometry"], float).reshape(-1, 3)
    m = np.array([MASS[s] for s in sym])
    h, o, planar = mode_shares(q, sym, m, x)
    return {"omega": omega, "delta": np.asarray(z["nu_sym"]) - np.asarray(z["omega_cm"]), "family": families(omega, q, sym, m, x),
            "h": h, "o": o, "planar": bool(planar)}, ""


def design(omega, fam, h, o):
    """Route (b)'s design matrix: one-hot family intercepts, one-hot family slopes on ω/1000, h, o (features as given)."""
    X = np.zeros((len(omega), 2 * len(FAMILIES) + 2))
    for j, f in enumerate(FAMILIES):
        sel = fam == f
        X[sel, j] = 1.0
        X[sel, len(FAMILIES) + j] = omega[sel] / 1000.0
    X[:, -2], X[:, -1] = h, o
    return X


def fit_predict(train, test):
    """Both routes fitted on `train`, evaluated on `test` (dicts of per-mode arrays). Returns (pred_b, pred_c, n_unseen)."""
    Xtr = design(train["omega"], train["family"], train["h"], train["o"])
    beta = np.linalg.solve(Xtr.T @ Xtr + RIDGE * np.eye(Xtr.shape[1]), Xtr.T @ train["delta"])
    pb = design(test["omega"], test["family"], test["h"], test["o"]) @ beta
    mean = train["delta"].mean()
    pc = np.full(len(test["omega"]), mean)
    seen = np.isin(test["family"], np.unique(train["family"]))
    for f in np.unique(train["family"]):
        pc[test["family"] == f] = train["delta"][train["family"] == f].mean()
    pb[~seen] = mean
    return pb, pc, int((~seen).sum())


def concat(mols):
    """The window modes of a list of molecules, stacked."""
    keys = ("omega", "delta", "family", "h", "o")
    out = {k: np.concatenate([m[k] for m in mols]) for k in keys}
    w = (out["omega"] >= WINDOW[0]) & (out["omega"] <= WINDOW[1])
    return {k: v[w] for k, v in out.items()}


def loso(mols_by_scaffold, k=None, rng=None):
    """One leave-one-scaffold-out pass; with k, each held-out scaffold trains on k of its training scaffolds drawn from rng.
    Returns pooled arrays (truth, pred_b, pred_c, family) over all held-out window modes and the unseen-family count."""
    scafs = sorted(mols_by_scaffold)
    truth, pb, pc, fam, unseen = [], [], [], [], 0
    for s in scafs:
        others = [t for t in scafs if t != s]
        if k is not None:
            others = list(rng.choice(others, size=min(k, len(others)), replace=False))
        train = concat([m for t in others for m in mols_by_scaffold[t]])
        test = concat(mols_by_scaffold[s])
        if len(test["omega"]) == 0:
            continue
        b, c, u = fit_predict(train, test)
        truth.append(test["delta"]); pb.append(b); pc.append(c); fam.append(test["family"]); unseen += u
    return np.concatenate(truth), np.concatenate(pb), np.concatenate(pc), np.concatenate(fam), unseen


def rms(a):
    return float(np.sqrt(np.mean(np.square(a)))) if len(a) else float("nan")


def curve(mols_by_scaffold, ks=KS, n_subsets=N_SUBSETS, seed=0):
    """Amendment 1's learning curve: per k, the pooled rms of (b) and (c) as mean ± SE over the subsets; 'all' once."""
    rng = np.random.default_rng(seed)
    rows = {}
    for k in ks:
        rb, rc, un = [], [], 0
        for _ in range(n_subsets):
            t, b, c, _f, u = loso(mols_by_scaffold, k, rng)
            rb.append(rms(b - t)); rc.append(rms(c - t)); un += u
        rows[str(k)] = {"b": float(np.mean(rb)), "b_se": float(np.std(rb, ddof=1) / np.sqrt(n_subsets)),
                        "c": float(np.mean(rc)), "c_se": float(np.std(rc, ddof=1) / np.sqrt(n_subsets)), "unseen_family_modes": un}
    t, b, c, f, un = loso(mols_by_scaffold)
    fam_rows = {fa: {"n": int((f == fa).sum()), "b": rms((b - t)[f == fa]), "c": rms((c - t)[f == fa])} for fa in FAMILIES}
    rows["all"] = {"b": rms(b - t), "b_se": 0.0, "c": rms(c - t), "c_se": 0.0, "unseen_family_modes": un, "n_modes": int(len(t)),
                   "per_family": fam_rows, "k": len(mols_by_scaffold) - 1}
    return rows


def still_learning(rows, route):
    """Amendment 1: rms at 'all' below rms at k = 6 by more than twice the combined SE, and the last step (k = 10 → all) still downward."""
    a, six, ten = rows["all"], rows["6"], rows["10"]
    return bool(a[route] < six[route] - 2 * np.hypot(six[f"{route}_se"], a[f"{route}_se"]) and a[route] < ten[route])


def extrapolate(rows, route, target=LINE_LICENSE):
    """Fit rms(k) = a + b·k^(−c) to the curve; the number of training scaffolds at which it reaches the target (None if the asymptote a
    is at or above it, or the fit fails)."""
    ks = np.array([int(k) for k in rows if k != "all"] + [rows["all"]["k"]], float)
    ys = np.array([rows[k][route] for k in rows if k != "all"] + [rows["all"][route]])
    try:
        (a, b, c), _ = curve_fit(lambda k, a, b, c: a + b * k ** (-c), ks, ys, p0=(ys.min() * 0.8, ys.max(), 0.5),
                                 bounds=([0, 0, 0.01], [np.inf, np.inf, 5]), maxfev=20000)
    except RuntimeError:
        return {"fit": None, "scaffolds_needed": None}
    need = float((b / (target - a)) ** (1 / c)) if a < target else None
    return {"fit": {"a": float(a), "b": float(b), "c": float(c)}, "scaffolds_needed": need}


def verdict(rows):
    """Amendment 1's verdicts at 'all'."""
    a = rows["all"]
    out = {"line1_b_le_0.8c": bool(a["b"] <= LINE_RATIO * a["c"]),
           "licensed": [r for r in ("b", "c") if a[r] <= LINE_LICENSE],
           "still_learning": {r: still_learning(rows, r) for r in ("b", "c")}}
    if out["licensed"]:
        out["reading"] = f"line 2 met by route(s) {', '.join(out['licensed'])}: licensed, to be confirmed on tetracene in S3"
    else:
        best = "b" if a["b"] <= a["c"] else "c"
        if out["still_learning"][best]:
            out["reading"] = f"line 2 missed, route {best} still learning: not failed — data-limited; next S2b, sized by the extrapolation"
            out["extrapolation"] = extrapolate(rows, best)
        else:
            out["reading"] = f"line 2 missed, route {best} flat: no negative conclusion yet — the search (model class × features) first"
    if not out["line1_b_le_0.8c"]:
        slope = {r: rows["6"][r] - a[r] for r in ("b", "c")}
        out["line1_reading"] = ("(b) misses line 1 but descends faster than (c): not stopped, repeated at S2b's size"
                                if slope["b"] > slope["c"] else "(b) misses line 1 and does not descend faster than (c): (b) stops")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--selection", required=True)
    ap.add_argument("--setting", default="G")
    ap.add_argument("--extra", nargs="*", default=[], help="ID=DIR: a molecule's setting directory computed elsewhere")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sel = json.load(open(a.selection, encoding="utf-8"))["selected"]
    extra = dict(e.split("=", 1) for e in a.extra)
    by_scaf, used, excluded = {}, [], {}
    for m in sel:
        d = extra.get(m["id"], os.path.join(a.root, m["id"], a.setting))
        rec, why = load_molecule(d) if os.path.isdir(d) else (None, f"no directory {d}")
        if rec is None:
            excluded[m["id"]] = why
            continue
        by_scaf.setdefault(m["scaffold"], []).append(rec)
        used.append({"id": m["id"], "scaffold": m["scaffold"], "planar": rec["planar"], "n_modes": len(rec["omega"]),
                     "n_window": int(((rec["omega"] >= WINDOW[0]) & (rec["omega"] <= WINDOW[1])).sum())})
    if len(by_scaf) < 2:
        raise SystemExit(f"{len(by_scaf)} scaffold(s) with a usable molecule: no leave-one-scaffold-out read")
    rows = curve(by_scaf)
    res = {"registration": "PreRegistration_2026-10-14_S2_Anharmonic_Shift.md (+ amendment 1)", "window": WINDOW, "ridge": RIDGE,
           "molecules": used, "excluded": excluded, "scaffolds": len(by_scaf), "curve": rows, "verdict": verdict(rows)}
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "s2_read.json"), "w", encoding="utf-8"), indent=1)
    lines = [f"# S2 read — {len(used)} molecules in {len(by_scaf)} scaffolds, excluded {len(excluded)}", "",
             "| k (training scaffolds) | (b) rms ± SE | (c) rms ± SE | unseen-family modes |", "|---|---|---|---|"]
    for k, r in rows.items():
        lines.append(f"| {k if k != 'all' else 'all (' + str(r['k']) + ')'} | {r['b']:.2f} ± {r['b_se']:.2f} | {r['c']:.2f} ± {r['c_se']:.2f} | "
                     f"{r['unseen_family_modes']} |")
    lines += ["", "| family | modes | (b) | (c) |", "|---|---|---|---|"]
    lines += [f"| {f} | {v['n']} | {v['b']:.2f} | {v['c']:.2f} |" for f, v in rows["all"]["per_family"].items()]
    if rows["all"]["k"] <= max(KS):
        lines += ["", f"*Only {rows['all']['k']} training scaffolds per held-out scaffold: the curve's k ≥ {rows['all']['k']} rows equal 'all', "
                  "and 'still learning' cannot be read as registered.*"]
    lines += ["", f"**{res['verdict']['reading']}**"] + ([res["verdict"]["line1_reading"]] if "line1_reading" in res["verdict"] else [])
    lines += [""] + [f"- excluded {i}: {w}" for i, w in excluded.items()]
    open(os.path.join(a.out, "s2_read.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
