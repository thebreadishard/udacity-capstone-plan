"""E7 / rung B re-read with second-route Hessians (23 September 2026, post-hoc): molecules that have hessian_<tag>_analytic.npz (pyscf analytic,
same geometry) are loaded from those files instead of the psi4 finite-difference ones; everything else as e7_rungB_pairs.py (GBT, deterministic,
plus the MLP seed 0). Prints per-molecule read-outs of hold-out (a) and the aggregates of (a) and (b) at the full pool, before and after the
substitution, so the effect of the corrected targets is isolated.
Usage: python e7_rungB_reread_analytic.py <corpus/molecules dir> <out prefix> [--threads 16] [--epochs 60]"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_rungB_pairs as RB  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from learning_curve_layerA import AMU2AU, HARTREE2CM, normal_modes  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor  # noqa: E402

RING = "ring-ip"


def substitute(m, d):
    """Replace the psi4 FD Hessians of molecule m by the analytic ones in dir d (both functionals required); recompute everything derived."""
    lo = np.load(d / "hessian_b3lyp_analytic.npz")["H_projected"]; hi = np.load(d / "hessian_wb97x_analytic.npz")["H_projected"]
    masses = m["masses"]; w, f, V, _ = normal_modes(lo, masses)
    mm = np.repeat(masses * AMU2AU, 3); dH = hi - lo
    Km = V.T @ (dH / np.sqrt(np.outer(mm, mm))) @ V; om = np.sqrt(np.abs(w))
    K = (Km / (2 * np.sqrt(np.outer(om, om))) * HARTREE2CM).astype(np.float32)
    Fl, _ = T2.to_internal(lo, m["B"]); Fh, _ = T2.to_internal(hi, m["B"])
    # families and tokens are kept from the corpus loader (same geometry; the mode order may differ slightly — the family label follows the
    # frequency and shares, which the analytic Hessian changes by < 1 cm⁻¹ for a sound molecule and by the artefact for benzene)
    m.update(V=V, w=w, freq=f, K=K, target=np.diag(K).astype(np.float32), F_low=Fl, F_high=Fh, H_low=lo, dH_true=dH, substituted=True)
    fam = m["family"]
    if len(fam) != len(f):
        raise RuntimeError(f"{d.name}: mode count changed ({len(fam)} vs {len(f)})")
    return m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("molecules"); ap.add_argument("out_prefix"); ap.add_argument("--threads", type=int, default=16); ap.add_argument("--epochs", type=int, default=60)
    a = ap.parse_args(); torch.set_num_threads(a.threads); t0 = time.time()
    mdir = Path(a.molecules)
    names = {r["id"]: r["name"] for r in csv.DictReader(open(mdir.parent / "manifest.csv", newline="", encoding="utf-8"))}
    mols = T2.load(a.molecules); test_a, test_b, cores, pool = E6.splits(mols)
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    test_a = [i for i in test_a if i in mols]; test_b = [i for i in test_b if i in mols]; pool = [i for i in pool if i in mols]
    subs = [i for i in mols if (mdir / i / "hessian_b3lyp_analytic.npz").exists() and (mdir / i / "hessian_wb97x_analytic.npz").exists()]
    print(f"{len(mols)} molecules; analytic second route available for {len(subs)}: " + ", ".join(f"{i}={names.get(i, '?')}" for i in subs), flush=True)
    for i, m in mols.items():
        g = json.load(open(mdir / i / "geometry.json"))
        pairs, X, c, B = RB.molecule_pairs(g["symbols"], np.asarray(g["coords_bohr"]), m["F_low"])
        m.update(pairs=pairs, X=X, pc=c, geom=g)

    def build_targets(mols):
        for i, m in mols.items():
            Bp = np.linalg.pinv(m["B"]); dFmn = Bp.T @ m["dH_true"] @ Bp
            m["y"] = np.array([dFmn[i_, j_] for i_, j_ in m["pairs"]])
            # F_low enters the pair features (columns with F_low,kk and F_low,ij); rebuild them for substituted molecules
            if m.get("substituted"):
                pairs, X, c, _ = RB.molecule_pairs(m["geom"]["symbols"], np.asarray(m["geom"]["coords_bohr"]), m["F_low"]); m.update(pairs=pairs, X=X, pc=c)
                Bp = np.linalg.pinv(m["B"]); dFmn = Bp.T @ m["dH_true"] @ Bp; m["y"] = np.array([dFmn[i_, j_] for i_, j_ in m["pairs"]])

    def run(label, mols):
        build_targets(mols); tr = pool
        X = np.concatenate([mols[i]["X"] for i in tr]); y = np.concatenate([mols[i]["y"] for i in tr]); c = np.concatenate([mols[i]["pc"] for i in tr])
        gbt = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.08, max_leaf_nodes=63, random_state=0).fit(X, y)
        mu = X.mean(0); sd = X.std(0) + 1e-6
        tscale = np.array([max(float(np.std(y[c == k])), 1e-6) if (c == k).any() else 1.0 for k in range(len(RB.PAIR_CLASS))], np.float32)
        mlp = RB.train_mlp(X, y, c, 0, a.epochs, mu, sd, tscale)
        out = {"per_molecule_a": {}}
        print(f"\n=== {label}", flush=True)
        for i in test_a:
            dF = RB.assemble(mols[i], mols[i]["pairs"], gbt.predict(mols[i]["X"]))
            x = RB.readouts(mols, [i], tr, lambda j, dF=dF: dF)
            out["per_molecule_a"][i] = {"name": names.get(i, "?"), "coupling_ratio": x["coupling_ratio"], "ring_diag": x["diag_rms"][RING], "corrected_freq_rms": x["corrected_freq_rms"],
                                        "corrected_freq_rms_zero": x["corrected_freq_rms_zero_rule"], "dH_residual_ratio": x["dH_residual_ratio"], "substituted": bool(mols[i].get("substituted"))}
            print(f"  {names.get(i, '?'):20s}{' *' if mols[i].get('substituted') else '  '} ratio {x['coupling_ratio']:.2f} | ring diag {x['diag_rms'][RING]:6.2f} | corrected ω {x['corrected_freq_rms']:5.2f} (zero {x['corrected_freq_rms_zero_rule']:5.2f}) | ΔH residual {x['dH_residual_ratio']:.2f}", flush=True)
        for h, ids in (("a", test_a), ("b", test_b)):
            for mname, pred in (("gbt", lambda j: RB.assemble(mols[j], mols[j]["pairs"], gbt.predict(mols[j]["X"]))),
                                ("mlp", lambda j: RB.assemble(mols[j], mols[j]["pairs"], RB.predict_mlp(mlp, mols[j]["X"], mols[j]["pc"], mu, sd, tscale)))):
                x = RB.readouts(mols, ids, tr, pred); out[f"{h}_{mname}"] = x
                print(f"  ALL ({h}) {mname}: ratio {x['coupling_ratio']:.2f} | ring diag {x['diag_rms'][RING]:.2f} | corrected ω {x['corrected_freq_rms']:.2f} (zero {x['corrected_freq_rms_zero_rule']:.2f}) | overlap {x['duschinsky_overlap_median']:.3f} | residual {x['dH_residual_ratio']:.2f}", flush=True)
        return out

    res = {"substituted": subs, "before": run("before substitution (corpus FD Hessians everywhere)", mols)}
    for i in subs:
        substitute(mols[i], mdir / i)
    res["after"] = run("after substitution (analytic Hessians for the molecules above)", mols)
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = ["# E7 / rung B re-read with second-route Hessians (post-hoc, 23 September 2026)", "", f"Analytic Hessians substituted for: " + ", ".join(f"{names.get(i, '?')} ({i})" for i in subs), "",
          "| molecule of hold-out (a) | ratio before | ratio after | ring diag before / after | corrected ω before / after (zero) | ΔH residual before / after |", "|---|---|---|---|---|---|"]
    for i in test_a:
        b_, a_ = res["before"]["per_molecule_a"][i], res["after"]["per_molecule_a"][i]
        md.append(f"| {b_['name']}{' *' if a_['substituted'] else ''} | {b_['coupling_ratio']:.2f} | **{a_['coupling_ratio']:.2f}** | {b_['ring_diag']:.1f} / {a_['ring_diag']:.1f} | {b_['corrected_freq_rms']:.1f} / {a_['corrected_freq_rms']:.1f} ({a_['corrected_freq_rms_zero']:.1f}) | {b_['dH_residual_ratio']:.2f} / {a_['dH_residual_ratio']:.2f} |")
    md += ["", "| aggregate | before | after |", "|---|---|---|"]
    for k in ("a_gbt", "a_mlp", "b_gbt", "b_mlp"):
        b_, a_ = res["before"][k], res["after"][k]
        md.append(f"| ({k[0]}) {k[2:].upper()}: ratio / ring diag / corrected ω | {b_['coupling_ratio']:.2f} / {b_['diag_rms'][RING]:.1f} / {b_['corrected_freq_rms']:.1f} | **{a_['coupling_ratio']:.2f}** / {a_['diag_rms'][RING]:.1f} / {a_['corrected_freq_rms']:.1f} |")
    md += ["", "\\* = analytic second-route Hessians substituted.", f"Total {res['seconds']} s."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n"); print("wrote", a.out_prefix, flush=True)


if __name__ == "__main__":
    main()
