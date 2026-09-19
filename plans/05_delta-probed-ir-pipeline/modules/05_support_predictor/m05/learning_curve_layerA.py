"""Learning curve on the DFT-DFT proxy corpus (layer A), per band family — 19 September 2026.

Target per DFT mode i of the low level (B3LYP/6-31G*): the first-order band shift the high level (ωB97X, same
geometry) would give,  δν_i = (L_iᵀ H_high L_i − ω_i²) / (2 ω_i)  in cm⁻¹  — the proxy for pipeline B's
Δ₂,ii/(2ω_i) (RECIPE.md, P26 amendment). Tokens per mode: ω/1000, family one-hot (4), C/H/N/O participation
shares, localisation index, out-of-plane share. Model: the recipe's Transformer (2 layers, 4 heads, width 64)
with a regression head; AdamW 1e-3; seeds 0, 1, 2.

Protocol (fixed in Desk_2026-09-18_Network_Architecture_and_Label_Count.md §5): split by MOLECULE; a fixed
held-out set chosen by hash; training sets of 5, 10, 20, 30 molecules (as available) drawn in hash order;
per family the held-out RMS of the model, of the zero rule, and of the family-median rule (median of the
training targets in that family); the power-law slope of log RMS vs log n per family. Reported in cm⁻¹.

Usage: python learning_curve_layerA.py <corpus/molecules dir> <out prefix> [--test-frac 0.25] [--epochs 150]
CPU only; a few minutes for 39 molecules × 3 seeds × 4 sizes.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705
FAMILIES = ["CH-stretch", "CH-oop", "ring-ip", "other"]
SIZES = [5, 10, 20, 30]
SEEDS = [0, 1, 2]


def normal_modes(H, masses_amu):
    m = np.repeat(np.asarray(masses_amu) * AMU2AU, 3)
    Hm = H / np.sqrt(np.outer(m, m))
    w, V = np.linalg.eigh(Hm)
    freq = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    keep = np.sort(np.argsort(np.abs(freq))[6:])
    return w[keep], freq[keep], V[:, keep], Hm


def molecule_features(mol_dir):
    g = json.load(open(mol_dir / "geometry.json"))
    lo = np.load(mol_dir / "hessian_b3lyp.npz"); hi = np.load(mol_dir / "hessian_wb97x.npz")
    masses = np.asarray(g["masses_amu"]); symbols = g["symbols"]; coords = np.asarray(g["coords_bohr"])
    w, freq, V, _ = normal_modes(lo["H_projected"], masses)
    m = np.repeat(masses * AMU2AU, 3)
    Hhi_mw = hi["H_projected"] / np.sqrt(np.outer(m, m))
    k_hi = np.einsum("ij,ij->j", V, Hhi_mw @ V)                 # curvature of the high level along each low mode
    omega = np.sqrt(np.abs(w))
    target = (k_hi - w) / (2 * omega) * HARTREE2CM              # first-order shift, cm⁻¹
    # atom shares (mass-weighted squared amplitude per atom sums to 1)
    A = (V.reshape(len(symbols), 3, -1) ** 2).sum(1)           # (N, M)
    sym = np.array(symbols)
    shares = np.stack([A[sym == s].sum(0) if (sym == s).any() else np.zeros(V.shape[1]) for s in ("C", "H", "N", "O")], 1)
    ipr = 1.0 / (A ** 2).sum(0) / len(symbols)                  # localisation: 1 = fully delocalised, small = local
    # out-of-plane share: component along the molecular normal (smallest principal axis), meaningful for near-planar
    com = (coords * masses[:, None]).sum(0) / masses.sum(); x = coords - com
    I = sum(mm * (np.dot(r, r) * np.eye(3) - np.outer(r, r)) for r, mm in zip(x, masses))
    ev, R = np.linalg.eigh(I); nrm = R[:, np.argmax(ev)]        # largest moment ⇒ normal of a planar molecule
    planarity = float(np.abs(x @ nrm).max())
    Vn = (V.reshape(len(symbols), 3, -1) * nrm[None, :, None]).sum(1)   # (N, M)
    oop = (Vn ** 2).sum(0) if planarity < 0.5 else np.zeros(V.shape[1])
    fam = []
    for i in range(V.shape[1]):
        f = freq[i]
        if f > 2800 and shares[i, 1] > 0.5: fam.append("CH-stretch")
        elif 600 < f < 1050 and oop[i] > 0.6 and shares[i, 1] > 0.3: fam.append("CH-oop")
        elif 950 < f < 1750 and oop[i] < 0.3: fam.append("ring-ip")
        else: fam.append("other")
    onehot = np.array([[1.0 if fam[i] == F else 0.0 for F in FAMILIES] for i in range(len(fam))])
    tokens = np.concatenate([freq[:, None] / 1000.0, onehot, shares, ipr[:, None], oop[:, None]], 1).astype(np.float32)
    return dict(id=mol_dir.name, tokens=tokens, target=target.astype(np.float32), family=fam, freq=freq)


class RegTransformer(nn.Module):
    def __init__(self, d_in, d_model=64, n_heads=4, n_layers=2, dropout=0.1):
        super().__init__()
        self.embed = nn.Sequential(nn.Linear(d_in, d_model), nn.GELU(), nn.LayerNorm(d_model))
        layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=n_heads, dim_feedforward=4 * d_model, dropout=dropout,
                                           batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers, enable_nested_tensor=False)
        self.head = nn.Sequential(nn.Linear(d_model, d_model), nn.GELU(), nn.Linear(d_model, 1))

    def forward(self, tokens, pad_mask):
        h = self.encoder(self.embed(tokens), src_key_padding_mask=pad_mask)
        return self.head(h).squeeze(-1)


def pad(mols):
    M = max(len(m["target"]) for m in mols); d = mols[0]["tokens"].shape[1]
    X = np.zeros((len(mols), M, d), np.float32); Y = np.zeros((len(mols), M), np.float32); mask = np.ones((len(mols), M), bool)
    for b, m in enumerate(mols):
        n = len(m["target"]); X[b, :n] = m["tokens"]; Y[b, :n] = m["target"]; mask[b, :n] = False
    return torch.tensor(X), torch.tensor(Y), torch.tensor(mask)


def train(train_mols, seed, epochs, scale=50.0):
    torch.manual_seed(seed); np.random.seed(seed)
    X, Y, mask = pad(train_mols)
    model = RegTransformer(X.shape[-1])
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    for ep in range(epochs):
        model.train(); opt.zero_grad()
        pred = model(X, mask)
        loss = (((pred - Y / scale) ** 2) * (~mask)).sum() / (~mask).sum()
        loss.backward(); opt.step()
    model.eval()
    return model, scale


def predict(model, scale, mols):
    X, Y, mask = pad(mols)
    with torch.no_grad():
        P = model(X, mask).numpy() * scale
    out = []
    for b, m in enumerate(mols):
        out.append(P[b, :len(m["target"])])
    return out


def rms(x):
    x = np.asarray(x, float); return float(np.sqrt(np.mean(x ** 2))) if x.size else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--test-frac", type=float, default=0.25); ap.add_argument("--epochs", type=int, default=150)
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    mdir = Path(a.molecules)
    mols = []
    for d in sorted(p for p in mdir.iterdir() if (p / "hessian_wb97x.npz").exists() and (p / "hessian_b3lyp.npz").exists()):
        try:
            mols.append(molecule_features(d))
        except Exception as e:
            print("skip", d.name, repr(e))
    # hash order, fixed once: test set = first ceil(test_frac × n) in hash order; training pools = next n_train
    mols.sort(key=lambda m: hashlib.sha1(m["id"].encode()).hexdigest())
    n_test = max(1, math.ceil(a.test_frac * len(mols)))
    test, pool = mols[:n_test], mols[n_test:]
    print(f"{len(mols)} molecules: {len(test)} held out, {len(pool)} in the training pool; modes per family (all):",
          {F: sum(m["family"].count(F) for m in mols) for F in FAMILIES})
    sizes = [n for n in SIZES if n <= len(pool)] or [len(pool)]
    y_test = {F: np.concatenate([m["target"][np.array(m["family"]) == F] for m in test]) for F in FAMILIES}
    results = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_molecules": len(mols), "n_test": len(test),
               "test_ids": [m["id"] for m in test], "sizes": sizes, "seeds": SEEDS, "epochs": a.epochs,
               "modes_test_per_family": {F: int(len(y_test[F])) for F in FAMILIES},
               "zero_rule_rms": {F: rms(y_test[F]) for F in FAMILIES}, "curve": {}}
    for n in sizes:
        tr = pool[:n]
        med = {}
        for F in FAMILIES:
            vals = np.concatenate([m["target"][np.array(m["family"]) == F] for m in tr])
            med[F] = float(np.median(vals)) if vals.size else 0.0
        med_rms = {F: rms(y_test[F] - med[F]) for F in FAMILIES}
        per_seed = []
        for s in SEEDS:
            model, scale = train(tr, s, a.epochs)
            preds = predict(model, scale, test)
            err = {F: np.concatenate([(p - m["target"])[np.array(m["family"]) == F] for p, m in zip(preds, test)]) for F in FAMILIES}
            tr_preds = predict(model, scale, tr)
            tr_err = np.concatenate([p - m["target"] for p, m in zip(tr_preds, tr)])
            per_seed.append({"seed": s, "rms": {F: rms(err[F]) for F in FAMILIES}, "rms_all": rms(np.concatenate(list(err.values()))),
                             "train_rms_all": rms(tr_err)})
        mean_rms = {F: float(np.mean([p["rms"][F] for p in per_seed])) for F in FAMILIES}
        results["curve"][str(n)] = {"n_train": n, "family_median": med, "family_median_rms": med_rms, "model_rms_mean": mean_rms,
                                    "model_rms_all_mean": float(np.mean([p["rms_all"] for p in per_seed])),
                                    "train_rms_all_mean": float(np.mean([p["train_rms_all"] for p in per_seed])), "per_seed": per_seed}
        print(f"n={n:2d} " + " ".join(f"{F}: model {mean_rms[F]:6.2f} median {med_rms[F]:6.2f} zero {results['zero_rule_rms'][F]:6.2f} |"
                                     for F in FAMILIES) + f" train {results['curve'][str(n)]['train_rms_all_mean']:.2f}")
    # power-law slope per family over the sizes that have ≥ 2 points
    slopes = {}
    if len(sizes) >= 2:
        ln = np.log(sizes)
        for F in FAMILIES:
            y = np.array([results["curve"][str(n)]["model_rms_mean"][F] for n in sizes])
            if np.all(np.isfinite(y)) and np.all(y > 0):
                slopes[F] = float(np.polyfit(ln, np.log(y), 1)[0])
    results["power_law_slope"] = slopes
    json.dump(results, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# Learning curve, layer A proxy (ωB97X − B3LYP first-order shifts) — {results['date']}", "",
          f"{len(mols)} molecules; {len(test)} held out (hash order); seeds {SEEDS}; {a.epochs} epochs; RMS in cm⁻¹ on held-out modes.", "",
          "| n_train | " + " | ".join(f"{F} model / median / zero" for F in FAMILIES) + " | all (model) | train |", "|---|" + "---|" * (len(FAMILIES) + 2)]
    for n in sizes:
        c = results["curve"][str(n)]
        md.append(f"| {n} | " + " | ".join(f"{c['model_rms_mean'][F]:.2f} / {c['family_median_rms'][F]:.2f} / {results['zero_rule_rms'][F]:.2f}" for F in FAMILIES)
                  + f" | {c['model_rms_all_mean']:.2f} | {c['train_rms_all_mean']:.2f} |")
    md += ["", "Power-law slope of log RMS vs log n per family: " + ", ".join(f"{F} {s:+.2f}" for F, s in slopes.items()),
           "", "Held-out modes per family: " + ", ".join(f"{F} {results['modes_test_per_family'][F]}" for F in FAMILIES)]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md")


if __name__ == "__main__":
    main()
