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
    def __init__(self, seed: int = 0, n_embed: int = 64):
        import torch
        import torch.nn as nn
        from rungC_equivariant import N_S, DeltaHessianModel
        torch.manual_seed(seed)
        self.torch, self.seed = torch, seed
        self.body = DeltaHessianModel()                                              # only .encode is used; the tensor head stays untouched
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

    def fit(self, train: list, val: list, epochs: int = 120, patience: int = 8, lr: float = 1e-3, log=print) -> dict:
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
                loss = ((self.predict_t(t) - t["y"]) ** 2).mean()
                loss.backward()
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
        self.torch.save([m.state_dict() for m in self.modules()], str(prefix) + f"_seed{self.seed}.pt")

    @classmethod
    def load(cls, prefix: Path, seed: int) -> EmbedScorer:
        s = cls(seed=seed)
        for m, sd in zip(s.modules(), s.torch.load(str(prefix) + f"_seed{seed}.pt"), strict=True):
            m.load_state_dict(sd)
        return s


def fit_from_exports(export_dir: Path, out_prefix: Path, seed: int = 0, threads: int = 2, log=print) -> dict:
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
    s = EmbedScorer(seed=seed)
    info = s.fit(train, val, log=log)
    s.save(out_prefix)
    info.update(molecules=used, seed=seed, n_params=int(sum(p.numel() for p in s.params)))
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
    a = ap.parse_args()
    fit_from_exports(Path(a.export_dir), Path(a.out_prefix), a.seed, a.threads)
