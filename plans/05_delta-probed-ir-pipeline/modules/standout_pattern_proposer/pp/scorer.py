"""P1 — the mode-pair scorer of the pre-registration (26 September 2026): predicts |Δ_ij| for every mode pair of a new molecule from what the deck may
see (nothing from the molecule's own Δ₂), and hands the score matrix to `core.order_by_scores`.

Features per mode pair (i, j), all from the B3LYP side:
  ω_i, ω_j (scaled /1000), |ω_i − ω_j|/1000, in-band flag (≤ 200 cm⁻¹), atom-participation overlap Σ_a A_ai A_aj (the non-local channel: two modes
  that move the same atoms couple whatever their frequencies), participation overlap restricted to heavy atoms and to hydrogens, the element shares of
  each mode (C, H, N, O + other), each mode's localisation (inverse participation ratio) and, from the low-level Hessian, the mode-basis F_low pair
  scalar |L_iᵀ F_low,mw L_j| / √(ω_i ω_j) (zero for exact B3LYP modes up to projection noise — kept because the deck sees it).
Target: log10(|Δ_ij| + 1e-8). Model: an MLP (2 × 128, SiLU, AdamW, early stopping on the validation split), seeds 0–2. Own torch code.

    python -m pp.scorer fit  <export_dir> <out_prefix> [--seed 0]      # trains on split "train", selects on "val", writes weights + a json log
The evaluation harness (`run_simulation.py`) loads the weights and scores the evaluation molecules; the scorer never sees them."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pp import core as C  # noqa: E402

ELEM = ("C", "H", "N", "O")
BAND_CM = 200.0


def pair_features(exp: dict) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int]]]:
    """(n_pairs, d) features, log10|Δ_ij| targets and the (i, j) list for i < j."""
    M, f, A, sym = exp["M"], np.asarray(exp["freq_cm"], float), np.asarray(exp["participation"], float), exp["symbols"]
    heavy = np.array([s != "H" for s in sym])
    shares = np.stack([A[np.array([s == e for s in sym])].sum(0) if any(s == e for s in sym) else np.zeros(M) for e in ELEM], 1)   # (M, 4)
    other = np.clip(1.0 - shares.sum(1), 0.0, 1.0)
    ipr = 1.0 / ((A ** 2).sum(0) * len(sym))
    X, y, pairs = [], [], []
    D2 = exp["D2"]
    for i in range(M):
        for j in range(i + 1, M):
            ov = float(A[:, i] @ A[:, j])
            ovh = float(A[heavy, i] @ A[heavy, j])
            ovH = float(A[~heavy, i] @ A[~heavy, j])
            X.append([f[i] / 1000, f[j] / 1000, abs(f[i] - f[j]) / 1000, float(abs(f[i] - f[j]) <= BAND_CM), ov, ovh, ovH,
                      *shares[i], other[i], *shares[j], other[j], ipr[i], ipr[j], min(f[i], f[j]) / 1000, max(f[i], f[j]) / 1000])
            y.append(np.log10(abs(D2[i, j]) + 1e-8))
            pairs.append((i, j))
    return np.array(X, np.float32), np.array(y, np.float32), pairs


def scores_matrix(exp: dict, pred_log10: np.ndarray, pairs) -> np.ndarray:
    S = np.zeros((exp["M"], exp["M"]))
    for (i, j), v in zip(pairs, pred_log10, strict=True):
        S[i, j] = S[j, i] = 10.0 ** v
    return S


class Scorer:
    def __init__(self, width: int = 128, seed: int = 0):
        import torch
        import torch.nn as nn
        torch.manual_seed(seed)
        self.torch, self.seed = torch, seed
        self.net = nn.Sequential(nn.Linear(21, width), nn.SiLU(), nn.Linear(width, width), nn.SiLU(), nn.Linear(width, 1))
        self.mu = self.sd = None

    def fit(self, X, y, Xv, yv, epochs: int = 200, patience: int = 10, lr: float = 1e-3, log=print) -> dict:
        torch = self.torch
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-6
        Xt, yt = torch.tensor((X - self.mu) / self.sd), torch.tensor(y)[:, None]
        Xvt, yvt = torch.tensor((Xv - self.mu) / self.sd), torch.tensor(yv)[:, None]
        opt = torch.optim.AdamW(self.net.parameters(), lr=lr, weight_decay=1e-4)
        best, bad, hist, state = np.inf, 0, [], None
        g = torch.Generator().manual_seed(self.seed)
        for _ep in range(epochs):
            self.net.train()
            perm = torch.randperm(len(Xt), generator=g)
            for k in range(0, len(Xt), 4096):
                idx = perm[k:k + 4096]
                opt.zero_grad()
                loss = ((self.net(Xt[idx]) - yt[idx]) ** 2).mean()
                loss.backward()
                opt.step()
            self.net.eval()
            with torch.no_grad():
                vl = float(((self.net(Xvt) - yvt) ** 2).mean())
            hist.append(vl)
            if vl < best - 1e-4:
                best, bad, state = vl, 0, {k: v.clone() for k, v in self.net.state_dict().items()}
            else:
                bad += 1
            if bad >= patience:
                break
        self.net.load_state_dict(state)
        log(f"scorer seed {self.seed}: {len(hist)} epochs, best val MSE(log10) {best:.4f}")
        return dict(epochs=len(hist), best_val_mse=best, history=hist)

    def predict(self, X) -> np.ndarray:
        torch = self.torch
        self.net.eval()
        with torch.no_grad():
            return self.net(torch.tensor((X - self.mu) / self.sd)).numpy()[:, 0]

    def save(self, prefix: Path) -> None:
        self.torch.save(self.net.state_dict(), str(prefix) + f"_seed{self.seed}.pt")
        np.savez(str(prefix) + f"_seed{self.seed}_norm.npz", mu=self.mu, sd=self.sd)

    @classmethod
    def load(cls, prefix: Path, seed: int) -> Scorer:
        s = cls(seed=seed)
        s.net.load_state_dict(s.torch.load(str(prefix) + f"_seed{seed}.pt"))
        z = np.load(str(prefix) + f"_seed{seed}_norm.npz")
        s.mu, s.sd = z["mu"], z["sd"]
        return s


def fit_from_exports(export_dir: Path, out_prefix: Path, seed: int = 0, log=print) -> dict:
    """Train on the exports whose split is 'train', select on 'val'; the evaluation molecules are never loaded here."""
    Xs, ys, Xv, yv, used = [], [], [], [], {"train": [], "val": []}
    for p in sorted(Path(export_dir).glob("*.npz")):
        mid = p.stem
        layer = "A" if mid.startswith("A_") else ("A2" if mid.startswith("A2_") else "B")
        split = C.split_of(mid, layer)
        if split not in ("train", "val"):
            continue
        e = C.load_export(p)
        X, y, _ = pair_features(e)
        (Xs if split == "train" else Xv).append(X)
        (ys if split == "train" else yv).append(y)
        used[split].append(mid)
    X, y, Xv, yv = np.concatenate(Xs), np.concatenate(ys), np.concatenate(Xv), np.concatenate(yv)
    s = Scorer(seed=seed)
    info = s.fit(X, y, Xv, yv, log=log)
    s.save(out_prefix)
    info.update(n_train_pairs=int(len(X)), n_val_pairs=int(len(Xv)), molecules=used, seed=seed)
    json.dump(info, open(str(out_prefix) + f"_seed{seed}.json", "w"), indent=1)
    return info


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["fit"])
    ap.add_argument("export_dir")
    ap.add_argument("out_prefix")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    fit_from_exports(Path(a.export_dir), Path(a.out_prefix), a.seed)
