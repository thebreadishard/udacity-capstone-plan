"""S2's search (amendment 2 §3 as corrected, 18 Oct 2026): model class × features, nested leave-one-scaffold-out, per family.

    python s2_search.py <s2_root> --selection <selection.json> [--extra ID=DIR ...] --gvpt2-dir <dir> --scope all|no-large-amplitude --out <dir>

Configurations: three feature sets (F1 as registered: family, ω/1000, h, o; F2 = F1 + local environment; F3 = F2 + resonance proximity
from ω, `probes/s2_features.py`) × three model classes (ridge in route (b)'s form; RBF kernel ridge; a one-hidden-layer network of 32
units with early stopping on a scaffold-held-out validation split, decision 51) with their small hyper-parameter grids.

Nested read: for every outer held-out scaffold, each configuration is scored by an inner leave-one-scaffold-out on the outer training
scaffolds only; per family the configuration with the lowest inner rms on that family is refitted on all outer training scaffolds and
predicts the held-out scaffold's modes of that family. The pooled outer rms per family is the search's score (line 2: ≤ 3.0 cm⁻¹). For
information only, the plain leave-one-scaffold-out rms of every configuration (choosing the best of these would flatter it).
"""
import argparse
import json
import os
import sys
import warnings
from dataclasses import dataclass

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s2_read import FAMILIES, LINE_LICENSE, RIDGE, SCOPES, WINDOW, load_selection, options_from_args, rms, write_atomic  # noqa: E402

FEATURE_SETS = ("F1", "F2", "F3")
XTB_FEATURES = "FX"                    # S2 amendment 4: F1 + Δ_xtb of the matched GFN2-xTB mode
KRR_ALPHA = (1e-2, 1e-1, 1.0)
KRR_GAMMA = (0.3, 1.0, 3.0)            # divided by the number of input columns (standardised inputs)
MLP_ALPHA = (1e-4, 1e-2)
MLP_HIDDEN = 32
MLP_MAX_EPOCHS = 3000
MLP_PATIENCE = 50
MLP_BATCH = 32
MLP_RATE = 1e-2
CAP_SHARE = 0.9                        # decision 51: a best epoch above this share of the cap means re-run
MLP_VAL_SHARE = 0.15                   # share of the training scaffolds held out for early stopping (at least one)
SEED = 0


@dataclass(frozen=True)
class Config:
    model: str           # 'ridge' | 'krr' | 'mlp'
    features: str        # 'F1' | 'F2' | 'F3'
    alpha: float = RIDGE
    gamma: float = 0.0

    @property
    def name(self) -> str:
        extra = f" α={self.alpha:g}" + (f" γ={self.gamma:g}" if self.model == "krr" else "")
        return f"{self.model}-{self.features}{extra if self.model != 'ridge' else ''}"


def configs() -> list[Config]:
    out = [Config("ridge", f) for f in FEATURE_SETS]
    out += [Config("krr", f, a, g) for f in FEATURE_SETS for a in KRR_ALPHA for g in KRR_GAMMA]
    out += [Config("mlp", f, a) for f in FEATURE_SETS for a in MLP_ALPHA]
    return out


def window_table(mols):
    """All window modes of a list of molecules: label, family, ω, h, o, then local (· × 9), prox (· × 2) and Δ_xtb where every molecule
    carries them."""
    keys = ("delta", "family", "omega", "h", "o", *(k for k in ("local", "prox", "xtb") if mols and all(k in m for m in mols)))
    out = {k: np.concatenate([m[k] for m in mols]) for k in keys}
    w = (out["omega"] >= WINDOW[0]) & (out["omega"] <= WINDOW[1])
    return {k: v[w] for k, v in out.items()}


def inputs(t, features):
    """The input columns of a feature set: family one-hot, ω/1000, h, o, then local (F2, F3) and proximity (F3)."""
    cols = [np.stack([(t["family"] == f).astype(float) for f in FAMILIES], axis=1), t["omega"][:, None] / 1000.0, t["h"][:, None], t["o"][:, None]]
    if features in ("F2", "F3"):
        cols.append(t["local"])
    if features == "F3":
        cols.append(t["prox"])
    if features == XTB_FEATURES:
        cols.append(t["xtb"][:, None])
    return np.hstack(cols)


def ridge_design(t, features):
    """Route (b)'s form: per-family intercepts and ω slopes, the other columns shared across families; with FX (amendment 4's x1) h and o
    shared and Δ_xtb with a slope per family."""
    n_fam = len(FAMILIES)
    width = 3 * n_fam if features == XTB_FEATURES else 2 * n_fam
    base = np.zeros((len(t["omega"]), width))
    for j, f in enumerate(FAMILIES):
        sel = t["family"] == f
        base[sel, j] = 1.0
        base[sel, n_fam + j] = t["omega"][sel] / 1000.0
        if features == XTB_FEATURES:
            base[sel, 2 * n_fam + j] = t["xtb"][sel]
    shared = inputs(t, "F1" if features == XTB_FEATURES else features)[:, n_fam + 1:]
    return np.hstack([base, shared])


def split_validation(train_scaffold_ids, rng):
    """Scaffold ids held out for early stopping: MLP_VAL_SHARE of them, at least one."""
    ids = sorted(set(train_scaffold_ids))
    n_val = max(1, round(MLP_VAL_SHARE * len(ids)))
    return set(rng.choice(ids, size=n_val, replace=False).tolist())


def fit_predict(cfg, train, test, train_scaffolds):
    """One configuration fitted on `train` (window table) and evaluated on `test`; returns (predictions, best epoch or None)."""
    if cfg.model == "ridge":
        X, Xt = ridge_design(train, cfg.features), ridge_design(test, cfg.features)
        beta = np.linalg.solve(X.T @ X + cfg.alpha * np.eye(X.shape[1]), X.T @ train["delta"])
        return Xt @ beta, None
    X, Xt = inputs(train, cfg.features), inputs(test, cfg.features)
    mu, sd = X.mean(axis=0), X.std(axis=0)
    sd[sd == 0] = 1.0
    X, Xt = (X - mu) / sd, (Xt - mu) / sd
    ym, ys = train["delta"].mean(), train["delta"].std() or 1.0
    y = (train["delta"] - ym) / ys
    if cfg.model == "krr":
        from sklearn.kernel_ridge import KernelRidge
        m = KernelRidge(kernel="rbf", alpha=cfg.alpha, gamma=cfg.gamma / X.shape[1]).fit(X, y)
        return m.predict(Xt) * ys + ym, None
    pred, epoch = mlp_fit_predict(cfg, X, y, Xt, train_scaffolds)
    return pred * ys + ym, epoch


def mlp_fit_predict(cfg, X, y, Xt, train_scaffolds):
    """One-hidden-layer network on standardised data, early stopping on held-out training scaffolds (decision 51): patience
    MLP_PATIENCE, the best epoch's weights kept; returns standardised predictions and the best epoch."""
    from sklearn.neural_network import MLPRegressor
    rng = np.random.default_rng(SEED)
    val_ids = split_validation(train_scaffolds, rng)
    val = np.isin(train_scaffolds, list(val_ids))
    m = MLPRegressor(hidden_layer_sizes=(MLP_HIDDEN,), alpha=cfg.alpha, learning_rate_init=MLP_RATE, batch_size=MLP_BATCH, random_state=SEED)
    best, best_epoch, best_state, since = np.inf, 0, None, 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for epoch in range(1, MLP_MAX_EPOCHS + 1):
            m.partial_fit(X[~val], y[~val])
            loss = float(np.mean((m.predict(X[val]) - y[val]) ** 2))
            if loss < best:
                best, best_epoch, since = loss, epoch, 0
                best_state = ([c.copy() for c in m.coefs_], [b.copy() for b in m.intercepts_])
            else:
                since += 1
                if since >= MLP_PATIENCE:
                    break
    m.coefs_, m.intercepts_ = best_state
    return m.predict(Xt), best_epoch


def fit_on(cfg, by_scaf, train_scafs, test_scaf):
    """One configuration fitted on the window modes of `train_scafs`, evaluated on `test_scaf`'s: labels, families, predictions, epoch."""
    train_mols = [(t, m) for t in train_scafs for m in by_scaf[t]]
    train = window_table([m for _t, m in train_mols])
    train_scaf = np.concatenate([[t] * int(window_table([m])["omega"].size) for t, m in train_mols])
    test = window_table(by_scaf[test_scaf])
    pred, epoch = fit_predict(cfg, train, test, train_scaf)
    return {"truth": test["delta"], "family": test["family"], "pred": pred, "epoch": epoch}


def loso_predictions(cfg, by_scaf, scaffolds):
    """Leave-one-scaffold-out over `scaffolds`: per held-out scaffold with window modes, fit_on's result."""
    return {s: fit_on(cfg, by_scaf, [t for t in scaffolds if t != s], s) for s in scaffolds if window_table(by_scaf[s])["omega"].size}


def family_rms(folds, family):
    t = np.concatenate([f["truth"][f["family"] == family] for f in folds.values()])
    p = np.concatenate([f["pred"][f["family"] == family] for f in folds.values()])
    return rms(p - t), len(t)


def nested(by_scaf, cfgs):
    """The nested read: per outer scaffold and family, the configuration chosen on the inner folds predicts the outer held-out modes."""
    scafs = sorted(by_scaf)
    chosen, outer = {fa: [] for fa in FAMILIES}, {fa: {"truth": [], "pred": []} for fa in FAMILIES}
    for s in scafs:
        inner_scafs = [t for t in scafs if t != s]
        inner = {c: loso_predictions(c, by_scaf, inner_scafs) for c in cfgs}
        test = window_table(by_scaf[s])
        for fa in FAMILIES:
            sel = test["family"] == fa
            if not sel.any():
                continue
            scored = [(family_rms(inner[c], fa)[0], c) for c in cfgs]
            best = min((x for x in scored if np.isfinite(x[0])), key=lambda x: x[0])[1]
            chosen[fa].append(best.name)
            pred = fit_on(best, by_scaf, inner_scafs, s)["pred"]
            outer[fa]["truth"].append(test["delta"][sel])
            outer[fa]["pred"].append(pred[sel])
    result = {}
    for fa in FAMILIES:
        if outer[fa]["truth"]:
            t, p = np.concatenate(outer[fa]["truth"]), np.concatenate(outer[fa]["pred"])
            result[fa] = {"n": len(t), "rms": rms(p - t), "licensed": bool(rms(p - t) <= LINE_LICENSE),
                          "chosen": {name: chosen[fa].count(name) for name in sorted(set(chosen[fa]))}}
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--selection", required=True)
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--gvpt2-dir", required=True)
    ap.add_argument("--scope", choices=SCOPES, default="no-large-amplitude")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    opts = options_from_args(a)
    by_scaf, used, _excluded = load_selection(a.root, a.selection, type(opts)(**{**opts.__dict__, "features": True}))
    cfgs = configs()
    landscape = {}
    for c in cfgs:
        folds = loso_predictions(c, by_scaf, sorted(by_scaf))
        epochs = [f["epoch"] for f in folds.values() if f["epoch"] is not None]
        landscape[c.name] = {fa: family_rms(folds, fa)[0] for fa in FAMILIES} | (
            {"best_epoch_max": max(epochs), "cap_hit": bool(max(epochs) > CAP_SHARE * MLP_MAX_EPOCHS)} if epochs else {})
        print(f"{c.name}: " + ", ".join(f"{fa} {v:.2f}" for fa, v in landscape[c.name].items() if fa in FAMILIES and np.isfinite(v)), flush=True)
    result = nested(by_scaf, cfgs)
    res = {"amendment": "2 §3 as corrected (proximity from ω only)", "labels": "GVPT2", "scope": a.scope, "molecules": len(used),
           "scaffolds": len(by_scaf), "line": LINE_LICENSE, "nested": result, "landscape_not_a_score": landscape}
    lines = [f"# S2 search — {len(used)} molecules, {len(by_scaf)} scaffolds, GVPT2 labels, scope {a.scope}", "",
             "## Nested score (line 2: ≤ 3.0 cm⁻¹ per family)", "", "| family | modes | nested rms | licensed | chosen per outer fold |",
             "|---|---|---|---|---|"]
    lines += [f"| {fa} | {v['n']} | {v['rms']:.2f} | {'yes' if v['licensed'] else 'no'} | "
              + "; ".join(f"{k} ×{n}" for k, n in v["chosen"].items()) + " |" for fa, v in result.items()]
    lines += ["", "## Landscape — plain leave-one-scaffold-out per configuration (information, not a score)", "",
              "| configuration | " + " | ".join(FAMILIES) + " | best epoch (max) |", "|---|" + "---|" * (len(FAMILIES) + 1)]
    lines += [f"| {name} | " + " | ".join(f"{v[fa]:.2f}" if np.isfinite(v[fa]) else "—" for fa in FAMILIES)
              + f" | {v.get('best_epoch_max', '')}{' CAP — re-run (decision 51)' if v.get('cap_hit') else ''} |"
              for name, v in landscape.items()]
    os.makedirs(a.out, exist_ok=True)
    write_atomic(os.path.join(a.out, "s2_search.json"), json.dumps(res, indent=1))
    write_atomic(os.path.join(a.out, "s2_search.md"), "\n".join(lines) + "\n")
    print("\n".join(lines[:6 + len(result)]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
