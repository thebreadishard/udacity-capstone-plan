"""P2 — the learned-representation scorer (pre-registration amendment of 26 September 2026, 10:5x): nothing about a molecule is prescribed beyond the
physics of rotation, reflection and permutation. The rung-C body (`m05/rungC_equivariant.py`, `DeltaHessianModel.encode`) turns atomic numbers,
coordinates and the registered pair scalars of the low-level Hessian into per-atom features s_a; a mode's embedding is the participation-weighted sum
e_i = Σ_a A_ai s_a passed through a linear layer together with ω_i/1000; the pair head reads (e_i + e_j, e_i ⊙ e_j, |ω_i − ω_j|/1000) → log10|Δ_ij|.
No hand-made overlap or element features enter: if atom sharing matters, the network must find it in s.

Training: one molecule per step (all its pairs), MSE on log10|Δ_ij|, AdamW 1e-3, early stopping on the validation split (patience 8, max 120 epochs),
seeds 0–2; the evaluation molecules are never loaded. Own torch code; CPU; the body has 171 k parameters, the heads a few thousand.

    python -m pp.embed_scorer fit <export_dir> <out_prefix> [--seed 0] [--threads 2]"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "modules" / "05_support_predictor" / "m05"))
from pp import core as C  # noqa: E402

Z_OF = {"H": 1, "C": 6, "N": 7, "O": 8, "F": 9, "S": 16, "CL": 17, "BR": 35}


def molecule_tensors(e: dict, torch):
    """What P2 may see of a molecule (all low-level) plus the pair targets."""
    Z = torch.tensor([Z_OF[s] for s in e["symbols"]], dtype=torch.long)
    pos = torch.tensor(np.asarray(e["pos"]), dtype=torch.float32)
    H = torch.tensor(np.asarray(e["H_low"]), dtype=torch.float32)
    A = torch.tensor(np.asarray(e["participation"]), dtype=torch.float32)          # (N, M)
    f = torch.tensor(np.asarray(e["freq_cm"]) / 1000.0, dtype=torch.float32)
    M = e["M"]
    iu = torch.triu_indices(M, M, offset=1)
    y = torch.tensor(np.log10(np.abs(np.asarray(e["D2"]))[iu[0].numpy(), iu[1].numpy()] + 1e-8), dtype=torch.float32)
    return dict(Z=Z, pos=pos, H=H, A=A, f=f, iu=iu, y=y, M=M)


class EmbedScorer:
    def __init__(self, seed: int = 0, n_embed: int = 64, n_blocks: int = 3):
        import torch
        import torch.nn as nn
        from rungC_equivariant import N_S, DeltaHessianModel
        torch.manual_seed(seed)
        self.torch, self.seed, self.cfg = torch, seed, dict(n_embed=n_embed, n_blocks=n_blocks)
        self.body = DeltaHessianModel(n_blocks=n_blocks)                             # only .encode is used; the tensor head stays untouched
        self.mode_in = nn.Linear(N_S + 1, n_embed)
        self.head = nn.Sequential(nn.Linear(2 * n_embed + 1, 128), nn.SiLU(), nn.Linear(128, 128), nn.SiLU(), nn.Linear(128, 1))
        self.params = list(self.body.parameters()) + list(self.mode_in.parameters()) + list(self.head.parameters())

    def modules(self):
        return (self.body, self.mode_in, self.head)

    def predict_t(self, t):
        s, _v, _i, _j, _rbf, _rhat = self.body.encode(t["Z"], t["pos"], t["H"])   # (N, n_s)
        emb = t["A"].T @ s                                                           # (M, n_s): participation-weighted atom features per mode
        e = self.mode_in(self.torch.cat([emb, t["f"][:, None]], -1))               # (M, n_embed)
        i, j = t["iu"]
        x = self.torch.cat([e[i] + e[j], e[i] * e[j], (t["f"][i] - t["f"][j]).abs()[:, None]], -1)
        return self.head(x)[:, 0]

    def loss_fn(self, pred, y, loss: str = "mse"):
        """Registered stage-2 variants: 'mse' on log₁₀|Δ|; 'huber' (δ = 1 in log units); 'rank' = MSE + a pairwise logistic ranking term on 4,096 random
        pairs of pairs of the same molecule — the read-out is an ordering, so the loss should care about order, not only magnitude."""
        torch = self.torch
        if loss == "huber":
            return torch.nn.functional.huber_loss(pred, y, delta=1.0)
        mse = ((pred - y) ** 2).mean()
        if loss == "mse":
            return mse
        n = len(y)
        g = torch.Generator().manual_seed(int(n))
        a = torch.randint(0, n, (4096,), generator=g)
        b = torch.randint(0, n, (4096,), generator=g)
        sign = torch.sign(y[a] - y[b])
        keep = sign != 0
        rank = torch.nn.functional.softplus(-sign[keep] * (pred[a] - pred[b])[keep]).mean()
        return mse + rank

    def fit(self, train: list, val: list, epochs: int = 120, patience: int = 8, lr: float = 1e-3, log=print, loss: str = "mse") -> dict:
        torch = self.torch
        opt = torch.optim.AdamW(self.params, lr=lr, weight_decay=1e-4)
        g = np.random.default_rng(self.seed)
        best, bad, hist, state = np.inf, 0, [], None
        t0 = time.time()
        for ep in range(epochs):
            for m in self.modules():
                m.train()
            for k in g.permutation(len(train)):
                t = train[k]
                opt.zero_grad()
                loss_value = self.loss_fn(self.predict_t(t), t["y"], loss)
                loss_value.backward()
                torch.nn.utils.clip_grad_norm_(self.params, 5.0)
                opt.step()
            vl = self.evaluate(val)
            hist.append(vl)
            if vl < best - 1e-4:
                best, bad, state = vl, 0, [{k: v.detach().clone() for k, v in m.state_dict().items()} for m in self.modules()]
            else:
                bad += 1
            if ep % 5 == 0 or bad >= patience:
                log(f"embed seed {self.seed}: epoch {ep + 1} val MSE(log10) {vl:.4f} best {best:.4f} ({time.time() - t0:.0f} s)")
            if bad >= patience:
                break
        for m, sd in zip(self.modules(), state, strict=True):
            m.load_state_dict(sd)
        return dict(epochs=len(hist), best_val_mse=float(best), history=[float(h) for h in hist], seconds=round(time.time() - t0, 1))

    def evaluate(self, mols: list) -> float:
        torch = self.torch
        for m in self.modules():
            m.eval()
        with torch.no_grad():
            se, n = 0.0, 0
            for t in mols:
                p = self.predict_t(t)
                se += float(((p - t["y"]) ** 2).sum())
                n += len(t["y"])
        return se / max(n, 1)

    def predict(self, e: dict) -> np.ndarray:
        """log10|Δ_ij| for i < j in `triu_indices` order (the same order `scorer.pair_features` uses)."""
        torch = self.torch
        for m in self.modules():
            m.eval()
        t = molecule_tensors(e, torch)
        with torch.no_grad():
            return self.predict_t(t).numpy()

    def save(self, prefix: Path) -> None:
        self.torch.save(dict(cfg=self.cfg, states=[m.state_dict() for m in self.modules()]), str(prefix) + f"_seed{self.seed}.pt")

    @classmethod
    def load(cls, prefix: Path, seed: int) -> EmbedScorer:
        import torch
        obj = torch.load(str(prefix) + f"_seed{seed}.pt")
        cfg, states = (obj["cfg"], obj["states"]) if isinstance(obj, dict) else (dict(n_embed=64, n_blocks=3), obj)   # first-run files were a bare list
        s = cls(seed=seed, **cfg)
        for m, sd in zip(s.modules(), states, strict=True):
            m.load_state_dict(sd)
        return s


def fit_from_exports(export_dir: Path, out_prefix: Path, seed: int = 0, threads: int = 2, log=print, lr: float = 1e-3, n_embed: int = 64,
                     n_blocks: int = 3, patience: int = 8, epochs: int = 120, loss: str = "mse") -> dict:
    import torch
    torch.set_num_threads(threads)
    train, val, used = [], [], {"train": [], "val": []}
    for p in sorted(Path(export_dir).glob("*.npz")):
        mid = p.stem
        layer = "A" if mid.startswith("A_") else ("A2" if mid.startswith("A2_") else "B")
        split = C.split_of(mid, layer)
        if split not in ("train", "val"):
            continue
        t = molecule_tensors(C.load_export(p), torch)
        (train if split == "train" else val).append(t)
        used[split].append(mid)
    log(f"embed scorer seed {seed}: {len(train)} training molecules, {len(val)} validation, {threads} threads")
    s = EmbedScorer(seed=seed, n_embed=n_embed, n_blocks=n_blocks)
    info = s.fit(train, val, epochs=epochs, patience=patience, lr=lr, log=log, loss=loss)
    s.save(out_prefix)
    info.update(molecules=used, seed=seed, n_params=int(sum(p.numel() for p in s.params)),
                recipe=dict(lr=lr, n_embed=n_embed, n_blocks=n_blocks, patience=patience, epochs=epochs, loss=loss))
    json.dump(info, open(str(out_prefix) + f"_seed{seed}.json", "w"), indent=1)
    return info


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["fit"])
    ap.add_argument("export_dir")
    ap.add_argument("out_prefix")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--n-embed", type=int, default=64)
    ap.add_argument("--n-blocks", type=int, default=3)
    ap.add_argument("--patience", type=int, default=8)
    ap.add_argument("--epochs", type=int, default=120)
    ap.add_argument("--loss", choices=["mse", "huber", "rank"], default="mse")
    a = ap.parse_args()
    fit_from_exports(Path(a.export_dir), Path(a.out_prefix), a.seed, a.threads, lr=a.lr, n_embed=a.n_embed, n_blocks=a.n_blocks, patience=a.patience,
                     epochs=a.epochs, loss=a.loss)
