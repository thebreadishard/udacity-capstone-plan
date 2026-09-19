"""E-series — can a separately trained network learn what is transferable between PAHs? (19 September 2026)

Pre-registration: GoalGathering/notes/PreRegistration_2026-09-19_E_Series_Learned_Mode_Embeddings.md.
E0  ridge on the first-pass tokens (variance vs bias).
E1  self-supervised mode embedding: atom-set encoder trained contrastively (InfoNCE, two augmented views of the same
    mode), no target seen; frozen embedding probed with ridge; probe curve at 5/10/20/30 molecules.
E1b the same encoder trained supervised on the proxy target of the training molecules; embedding probed likewise.
E2  molecule-level tokens (ring count, longest fused-ring run, heavy atoms, heteroatoms) appended; ridge + Transformer.
Same molecules, same hash split, same target as learning_curve_layerA.py. One thread, lowest priority.

Usage: python embedding_experiments_E.py <corpus/molecules dir> <out prefix> [--steps 1500] [--threads 1]
"""
import argparse
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as Fn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from learning_curve_layerA import AMU2AU, FAMILIES, SEEDS, molecule_features, normal_modes, predict, rms, train  # noqa: E402
from learning_curve_layerA_v2_descriptors import BOHR, bond_graph, rings  # noqa: E402

ELEMENTS = ["C", "H", "N", "O", "S"]
NMAX = 28
SIZES = [5, 10, 20, 30]


# ----------------------------------------------------------------------------------------------- data
def principal_frame(coords_A, masses):
    com = (coords_A * masses[:, None]).sum(0) / masses.sum(); x = coords_A - com
    I = sum(m * (np.dot(r, r) * np.eye(3) - np.outer(r, r)) for r, m in zip(x, masses))
    w, R = np.linalg.eigh(I)                     # ascending: z (last) = largest moment = normal of a planar molecule
    return x @ R, R


def atom_sets(mol_dir, base):
    """Per mode: (NMAX, 13) atom tokens [onehot5, x/5, y/5, z/5, dx, dy, dz, |d|, participation] and a mask."""
    g = json.load(open(mol_dir / "geometry.json"))
    symbols = g["symbols"]; masses = np.asarray(g["masses_amu"]); coords = np.asarray(g["coords_bohr"]) * BOHR
    lo = np.load(mol_dir / "hessian_b3lyp.npz")
    _, _, V, _ = normal_modes(lo["H_projected"], masses)
    xf, R = principal_frame(coords, masses)
    N, M = len(symbols), V.shape[1]
    onehot = np.array([[1.0 if s == e else 0.0 for e in ELEMENTS] for s in symbols])
    X = np.zeros((M, NMAX, 13), np.float32); mask = np.ones((M, NMAX), bool)
    for i in range(M):
        d = (V[:, i].reshape(N, 3) @ R)          # rotate displacement into the frame
        d = d / (np.linalg.norm(d) + 1e-12)
        amp = np.linalg.norm(d, axis=1); part = amp ** 2
        X[i, :N] = np.concatenate([onehot, xf / 5.0, d, amp[:, None], part[:, None]], 1)
        mask[i, :N] = False
    return X, mask


def molecule_level_tokens(mol_dir):
    g = json.load(open(mol_dir / "geometry.json")); symbols = g["symbols"]
    adj = bond_graph(symbols, g["coords_bohr"]); R = rings(adj)
    # fusion graph: rings sharing >= 2 atoms; longest simple path in it = longest fused run
    n = len(R); fadj = [set() for _ in range(n)]
    for a in range(n):
        for b in range(a + 1, n):
            if len(R[a] & R[b]) >= 2: fadj[a].add(b); fadj[b].add(a)
    best = 1 if n else 0
    def dfs(v, seen):
        nonlocal best
        best = max(best, len(seen))
        for w in fadj[v]:
            if w not in seen: dfs(w, seen | {w})
    for v in range(n): dfs(v, {v})
    heavy = sum(1 for s in symbols if s != "H"); hetero = sum(1 for s in symbols if s not in ("C", "H"))
    return np.array([n / 5.0, best / 5.0, heavy / 30.0, hetero / 3.0], np.float32)


# ----------------------------------------------------------------------------------------------- models
class AtomSetEncoder(nn.Module):
    def __init__(self, d_in=13, d=64, n_heads=4, n_layers=2, d_emb=32):
        super().__init__()
        self.embed = nn.Sequential(nn.Linear(d_in, d), nn.GELU(), nn.Linear(d, d), nn.LayerNorm(d))
        layer = nn.TransformerEncoderLayer(d_model=d, nhead=n_heads, dim_feedforward=2 * d, dropout=0.0, batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, num_layers=n_layers, enable_nested_tensor=False)
        self.query = nn.Parameter(torch.randn(1, 1, d) / math.sqrt(d))
        self.pool = nn.MultiheadAttention(d, n_heads, batch_first=True)
        self.proj = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Linear(d, d_emb))   # contrastive head
        self.head = nn.Linear(d, 1)                                                     # supervised head (E1b)

    def forward(self, x, mask):
        h = self.enc(self.embed(x), src_key_padding_mask=mask)
        q = self.query.expand(x.shape[0], -1, -1)
        z, _ = self.pool(q, h, h, key_padding_mask=mask)
        return z.squeeze(1)                                                            # (B, d) the embedding


def augment(x, mask, rng):
    """In-plane rotation, random reflections, coordinate noise, atom dropout — applied to a batch (B, NMAX, 13)."""
    x = x.clone(); B = x.shape[0]
    th = torch.tensor(rng.uniform(0, 2 * np.pi, B), dtype=torch.float32)
    c, s = torch.cos(th), torch.sin(th)
    for sl in (slice(5, 8), slice(8, 11)):          # positions and displacements share the rotation
        px, py = x[:, :, sl.start].clone(), x[:, :, sl.start + 1].clone()
        x[:, :, sl.start] = c[:, None] * px - s[:, None] * py
        x[:, :, sl.start + 1] = s[:, None] * px + c[:, None] * py
    refl_x = torch.tensor(rng.integers(0, 2, B) * 2 - 1, dtype=torch.float32)[:, None]
    refl_z = torch.tensor(rng.integers(0, 2, B) * 2 - 1, dtype=torch.float32)[:, None]
    x[:, :, 5] *= refl_x; x[:, :, 8] *= refl_x; x[:, :, 7] *= refl_z; x[:, :, 10] *= refl_z
    x[:, :, 5:8] += torch.tensor(rng.normal(0, 0.004, (B, NMAX, 3)), dtype=torch.float32) * (~mask)[..., None]
    drop = torch.tensor(rng.uniform(0, 1, (B, NMAX)) < 0.15) & (~mask)
    keep_any = (~(mask | drop)).sum(1) > 0
    mask2 = mask | (drop & keep_any[:, None])
    return x, mask2


def train_contrastive(X, mask, steps, seed, batch=256, tau=0.1):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    enc = AtomSetEncoder(); opt = torch.optim.AdamW(enc.parameters(), lr=1e-3, weight_decay=1e-4)
    Xt, Mt = torch.tensor(X), torch.tensor(mask); n = Xt.shape[0]
    for step in range(steps):
        idx = torch.tensor(rng.choice(n, size=min(batch, n), replace=False))
        xa, ma = augment(Xt[idx], Mt[idx], rng); xb, mb = augment(Xt[idx], Mt[idx], rng)
        za = Fn.normalize(enc.proj(enc(xa, ma)), dim=1); zb = Fn.normalize(enc.proj(enc(xb, mb)), dim=1)
        logits = za @ zb.T / tau
        labels = torch.arange(len(idx))
        loss = 0.5 * (Fn.cross_entropy(logits, labels) + Fn.cross_entropy(logits.T, labels))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0 or step == steps - 1:
            print(f"    contrastive seed {seed} step {step} loss {loss.item():.3f}", flush=True)
    enc.eval(); return enc


def train_supervised(X, mask, y, steps, seed, batch=256, scale=50.0):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    enc = AtomSetEncoder(); opt = torch.optim.AdamW(enc.parameters(), lr=1e-3, weight_decay=1e-4)
    Xt, Mt, yt = torch.tensor(X), torch.tensor(mask), torch.tensor(y / scale, dtype=torch.float32); n = Xt.shape[0]
    for step in range(steps):
        idx = torch.tensor(rng.choice(n, size=min(batch, n), replace=False))
        xa, ma = augment(Xt[idx], Mt[idx], rng)
        pred = enc.head(enc(xa, ma)).squeeze(-1)
        loss = Fn.mse_loss(pred, yt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0 or step == steps - 1:
            print(f"    supervised seed {seed} step {step} loss {loss.item():.4f}", flush=True)
    enc.eval(); return enc, scale


def embed(enc, X, mask):
    with torch.no_grad():
        out = [enc(torch.tensor(X[i:i + 512]), torch.tensor(mask[i:i + 512])).numpy() for i in range(0, len(X), 512)]
    return np.concatenate(out, 0)


# ----------------------------------------------------------------------------------------------- ridge probe
def ridge_fit_predict(Xtr, ytr, Xte, groups_tr, lams=(0.01, 0.1, 1.0, 10.0, 100.0)):
    """Standardised ridge; λ chosen by held-out molecules inside the training set (last 25 % in the given order)."""
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-8
    A, B = (Xtr - mu) / sd, (Xte - mu) / sd
    ug = list(dict.fromkeys(groups_tr)); nval = max(1, len(ug) // 4); val_g = set(ug[-nval:])
    va = np.array([g in val_g for g in groups_tr])
    def fit(Xa, ya, lam):
        Xa1 = np.concatenate([Xa, np.ones((len(Xa), 1))], 1)
        return np.linalg.solve(Xa1.T @ Xa1 + lam * np.eye(Xa1.shape[1]), Xa1.T @ ya)
    best = None
    if va.sum() and (~va).sum():
        for lam in lams:
            w = fit(A[~va], ytr[~va], lam); e = rms(np.concatenate([A[va], np.ones((va.sum(), 1))], 1) @ w - ytr[va])
            if best is None or e < best[0]: best = (e, lam)
    lam = best[1] if best else 1.0
    w = fit(A, ytr, lam)
    return np.concatenate([B, np.ones((len(B), 1))], 1) @ w, lam


def probe(feat, mols, train_ids, test_ids, label):
    """feat: dict id -> (M, d) features; returns per-family held-out RMS of a ridge probe trained on train_ids."""
    Xtr = np.concatenate([feat[i] for i in train_ids]); ytr = np.concatenate([mols[i]["target"] for i in train_ids])
    gtr = sum([[i] * len(mols[i]["target"]) for i in train_ids], [])
    Xte = np.concatenate([feat[i] for i in test_ids]); yte = np.concatenate([mols[i]["target"] for i in test_ids])
    fte = np.concatenate([np.array(mols[i]["family"]) for i in test_ids])
    pred, lam = ridge_fit_predict(Xtr, ytr, Xte, gtr)
    out = {F: rms((pred - yte)[fte == F]) for F in FAMILIES}; out["all"] = rms(pred - yte); out["lambda"] = lam
    print(f"  {label:44s} " + " ".join(f"{F} {out[F]:6.2f} |" for F in FAMILIES) + f" λ={lam}", flush=True)
    return out


# ----------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--steps", type=int, default=1500); ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--test-frac", type=float, default=0.25)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    mdir = Path(a.molecules)
    mols, sets, mtok = {}, {}, {}
    for d in sorted(p for p in mdir.iterdir() if (p / "hessian_wb97x.npz").exists() and (p / "hessian_b3lyp.npz").exists()):
        try:
            base = molecule_features(d); mols[d.name] = base
            sets[d.name] = atom_sets(d, base); mtok[d.name] = molecule_level_tokens(d)
        except Exception as e:
            print("skip", d.name, repr(e))
    ids = sorted(mols, key=lambda i: hashlib.sha1(i.encode()).hexdigest())
    n_test = max(1, math.ceil(a.test_frac * len(ids))); test_ids, pool = ids[:n_test], ids[n_test:]
    sizes = [n for n in SIZES if n <= len(pool)] or [len(pool)]
    print(f"{len(ids)} molecules, {n_test} held out, pool {len(pool)}; modes {sum(len(m['target']) for m in mols.values())}", flush=True)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_molecules": len(ids), "n_test": n_test, "sizes": sizes, "steps": a.steps}
    tok1 = {i: mols[i]["tokens"] for i in ids}

    print("E0 ridge on first-pass tokens", flush=True)
    res["E0"] = {str(n): probe(tok1, mols, pool[:n], test_ids, f"E0 ridge tokens n={n}") for n in sizes}

    print("E2 molecule-level tokens", flush=True)
    tok2 = {i: np.concatenate([mols[i]["tokens"], np.repeat(mtok[i][None], len(mols[i]["target"]), 0)], 1) for i in ids}
    res["E2"] = {"ridge": {str(n): probe(tok2, mols, pool[:n], test_ids, f"E2 ridge tokens+mol n={n}") for n in sizes}}
    tr30 = [dict(mols[i], tokens=tok2[i]) for i in pool[:sizes[-1]]]; te = [dict(mols[i], tokens=tok2[i]) for i in test_ids]
    per_seed = []
    for s in SEEDS:
        model, scale = train(tr30, s, 600); preds = predict(model, scale, te)
        err = {F: np.concatenate([(p - m["target"])[np.array(m["family"]) == F] for p, m in zip(preds, te)]) for F in FAMILIES}
        per_seed.append({F: rms(err[F]) for F in FAMILIES})
    res["E2"]["transformer_n30"] = {F: float(np.mean([p[F] for p in per_seed])) for F in FAMILIES}
    print("  E2 transformer n=30 (mean of seeds): " + " ".join(f"{F} {res['E2']['transformer_n30'][F]:6.2f} |" for F in FAMILIES), flush=True)

    X_all = np.concatenate([sets[i][0] for i in ids]); M_all = np.concatenate([sets[i][1] for i in ids])
    offsets = np.cumsum([0] + [len(mols[i]["target"]) for i in ids])
    def split_feat(E):
        return {i: E[offsets[k]:offsets[k + 1]] for k, i in enumerate(ids)}

    print("E1 self-supervised contrastive embedding (no target seen)", flush=True)
    res["E1"] = {}
    for s in SEEDS:
        enc = train_contrastive(X_all, M_all, a.steps, s)
        feat = split_feat(embed(enc, X_all, M_all))
        res["E1"][f"seed{s}"] = {str(n): probe(feat, mols, pool[:n], test_ids, f"E1 contrastive emb seed {s} n={n}") for n in sizes}
        featc = {i: np.concatenate([feat[i], tok1[i]], 1) for i in ids}
        res["E1"][f"seed{s}_plus_tokens"] = probe(featc, mols, pool[:sizes[-1]], test_ids, f"E1 emb+tokens seed {s} n={sizes[-1]}")
    res["E1"]["mean_n30"] = {F: float(np.mean([res["E1"][f"seed{s}"][str(sizes[-1])][F] for s in SEEDS])) for F in FAMILIES}

    print("E1b supervised atom-set encoder on the training molecules", flush=True)
    tr_idx = [k for k, i in enumerate(ids) if i in set(pool[:sizes[-1]])]
    sel = np.concatenate([np.arange(offsets[k], offsets[k + 1]) for k in tr_idx])
    y_tr = np.concatenate([mols[ids[k]]["target"] for k in tr_idx])
    res["E1b"] = {}
    for s in SEEDS:
        enc, scale = train_supervised(X_all[sel], M_all[sel], y_tr, a.steps, s)
        with torch.no_grad():
            direct = {i: (enc.head(enc(torch.tensor(sets[i][0]), torch.tensor(sets[i][1]))).squeeze(-1).numpy() * scale) for i in ids}
        yte = np.concatenate([mols[i]["target"] for i in test_ids]); fte = np.concatenate([np.array(mols[i]["family"]) for i in test_ids])
        pd_ = np.concatenate([direct[i] for i in test_ids])
        res["E1b"][f"seed{s}_direct"] = {F: rms((pd_ - yte)[fte == F]) for F in FAMILIES}
        print(f"  E1b direct seed {s}: " + " ".join(f"{F} {res['E1b'][f'seed{s}_direct'][F]:6.2f} |" for F in FAMILIES), flush=True)
        feat = split_feat(embed(enc, X_all, M_all))
        res["E1b"][f"seed{s}_probe"] = probe(feat, mols, pool[:sizes[-1]], test_ids, f"E1b emb probe seed {s} n={sizes[-1]}")
    res["E1b"]["mean_direct"] = {F: float(np.mean([res["E1b"][f"seed{s}_direct"][F] for s in SEEDS])) for F in FAMILIES}

    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E-series — learned mode embeddings ({res['date']}); held-out RMS in cm⁻¹, same 12 molecules as the learning curves", "",
          "| experiment (n_train = 30) | " + " | ".join(FAMILIES) + " |", "|---|" + "---|" * len(FAMILIES)]
    md.append("| E0 ridge, first-pass tokens | " + " | ".join(f"{res['E0'][str(sizes[-1])][F]:.2f}" for F in FAMILIES) + " |")
    md.append("| E2 ridge, + molecule tokens | " + " | ".join(f"{res['E2']['ridge'][str(sizes[-1])][F]:.2f}" for F in FAMILIES) + " |")
    md.append("| E2 Transformer, + molecule tokens | " + " | ".join(f"{res['E2']['transformer_n30'][F]:.2f}" for F in FAMILIES) + " |")
    md.append("| E1 contrastive embedding + ridge (mean of seeds) | " + " | ".join(f"{res['E1']['mean_n30'][F]:.2f}" for F in FAMILIES) + " |")
    md.append("| E1b supervised encoder, direct (mean of seeds) | " + " | ".join(f"{res['E1b']['mean_direct'][F]:.2f}" for F in FAMILIES) + " |")
    md += ["", "E1 probe curve (seed 0): " + "; ".join(f"n={n}: ring-ip {res['E1']['seed0'][str(n)]['ring-ip']:.2f}" for n in sizes),
           "Reference (first pass, Transformer, n=30): C–H stretch 1.78, C–H oop 4.31, ring-ip 12.41, other 26.6; family-median rule ring-ip 18.5; zero rule 21.9."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md", flush=True)


if __name__ == "__main__":
    main()
