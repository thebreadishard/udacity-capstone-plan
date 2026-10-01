"""Rung C, hybrid head — rank 3 of the external reviews (30 September 2026): the equivariant encoder of `rungC_equivariant` supplies per-atom
features; the head predicts one scalar per pair of internal primitives on the pair model's pattern (diagonal, shared-atom pairs, same-ring bond–bond
pairs; `e7_rungB_pairs.molecule_pairs`), from the pooled features of the atoms of the two primitives, the pair class and the low-level force constants
F_low,pq, F_low,pp, F_low,qq — the object rung B is anchored on. The Cartesian correction is ΔH = Bᵀ ΔF B (exactly symmetric; translations and
rotations annihilated by the Wilson B matrix), so every read-out and loss of `rungC_train` applies unchanged.

Invariance: the head sees only O(3)-invariant quantities (scalar channels, the norms of the vector channels, F_low elements), ΔF is invariant, and
B transforms with the frame, so ΔH is equivariant by construction (tested in `tests/test_rungC_hybrid.py` with B rebuilt for the rotated geometry).

Options: `tensor_input` (the rank-2 input of the encoder, rank 1), `sqm_scale` (Gemini's suggestion: ΔF_pq = α_c F_low,pq + residual, one α per
pair class, initialised at 0 so the default is the pure residual). Class scales (one per pair class, the RMS of the true internal ΔF over the fit
molecules) and input scales (RMS of the three F_low inputs over the fit molecules) are set by the trainer from the fit ids only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rungC_equivariant import AGGREGATION, N_S, DeltaHessianModel  # noqa: E402

N_PAIR_CLASSES = 7          # e7_rungB_pairs: diag bond, diag angle, diag dihedral, diag other, off bond–bond, off other, off two-bonds-apart (pattern d, 1 Oct 2026)
N_CLASS_EMB = 8
N_FLOW = 16
HIDDEN = 128


def primitive_pool_matrix(prim_atoms: list[set[int]], n_atoms: int, dtype=torch.float32) -> torch.Tensor:
    """(K, N) mean-pooling matrix: row p averages the features of the atoms of primitive p."""
    M = torch.zeros(len(prim_atoms), n_atoms, dtype=dtype)
    for p, atoms in enumerate(prim_atoms):
        for a in atoms:
            M[p, a] = 1.0 / len(atoms)
    return M


def hybrid_inputs(t: dict) -> torch.Tensor:
    """(P, 3) the three low-level force constants of every pattern pair: F_pq, F_pp, F_qq (internal coordinates, a.u.)."""
    F, pairs = t["F_int"], t["pairs"]
    p, q = pairs[:, 0], pairs[:, 1]
    return torch.stack([F[p, q], F[p, p], F[q, q]], -1)


def pair_feature_stats(tensors: dict, ids: list) -> tuple[torch.Tensor, torch.Tensor]:
    """Mean and standard deviation of rung B's pair features over the pattern pairs of the fit molecules (never the hold-outs); zero spread → 1."""
    X = torch.cat([tensors[i]["pfeat"].double() for i in ids], 0)
    mu, sd = X.mean(0), X.std(0, unbiased=False)
    sd[sd < 1e-12] = 1.0
    return mu.float(), sd.float()


def input_scales(tensors: dict, ids: list) -> torch.Tensor:
    """RMS of the three F_low inputs over the pattern pairs of the fit molecules (never the hold-outs); a zero RMS becomes 1."""
    sq = torch.zeros(3, dtype=torch.float64)
    cnt = 0
    for i in ids:
        x = hybrid_inputs(tensors[i]).double()
        sq += (x ** 2).sum(0)
        cnt += x.shape[0]
    s = torch.sqrt(sq / max(cnt, 1))
    s[s == 0] = 1.0
    return s.float()


class HybridDeltaFModel(nn.Module):
    def __init__(self, aggregation: str = AGGREGATION, tensor_input: bool = False, sqm_scale: bool = False,
                 class_scale: torch.Tensor | None = None, n_s: int = N_S, hidden: int = HIDDEN, n_pair_features: int = 0):
        super().__init__()
        self.body = DeltaHessianModel(aggregation=aggregation, tensor_input=tensor_input)      # encode() only; its Cartesian head is unused
        self.cls_emb = nn.Embedding(N_PAIR_CLASSES, N_CLASS_EMB)
        self.flow_in = nn.Linear(3, N_FLOW)
        self.n_pair_features = int(n_pair_features)                                            # 1 Oct 2026: rung B's pair vector, 0 = off
        self.pfeat_in = nn.Linear(self.n_pair_features, 32) if self.n_pair_features else None
        self.register_buffer("pfeat_mu", torch.zeros(max(self.n_pair_features, 1)))
        self.register_buffer("pfeat_sd", torch.ones(max(self.n_pair_features, 1)))
        n_in = 2 * n_s + self.body.n_v + N_CLASS_EMB + N_FLOW + (32 if self.n_pair_features else 0)
        self.head = nn.Sequential(nn.Linear(n_in, hidden), nn.SiLU(), nn.Linear(hidden, hidden), nn.SiLU(), nn.Linear(hidden, 1))
        self.alpha = nn.Parameter(torch.zeros(N_PAIR_CLASSES)) if sqm_scale else None
        self.register_buffer("class_scale", torch.ones(N_PAIR_CLASSES) if class_scale is None else torch.as_tensor(class_scale, dtype=torch.float32))
        self.register_buffer("flow_scale", torch.ones(3))
        self.tensor_input, self.sqm_scale = bool(tensor_input), bool(sqm_scale)

    def set_input_scales(self, s: torch.Tensor) -> None:
        self.flow_scale.copy_(s.to(self.flow_scale.dtype))

    def set_pair_feature_stats(self, mu: torch.Tensor, sd: torch.Tensor) -> None:
        self.pfeat_mu.copy_(mu.to(self.pfeat_mu.dtype))
        self.pfeat_sd.copy_(sd.to(self.pfeat_sd.dtype))

    def delta_f(self, Z, pos, H_low, t: dict) -> torch.Tensor:
        """(P,) the predicted internal correction on the pattern pairs, in a.u."""
        s, v, *_ = self.body.encode(Z, pos, H_low)
        vnorm = torch.sqrt((v ** 2).sum(1) + 1e-8)                                     # (N, n_v) invariant
        M = t["prim_pool"].to(s.dtype)
        hs, hv = M @ s, M @ vnorm                                                     # (K, n_s), (K, n_v)
        p, q = t["pairs"][:, 0], t["pairs"][:, 1]
        x_low = hybrid_inputs(t).to(s.dtype) / self.flow_scale.to(s.dtype)
        parts = [hs[p] + hs[q], hs[p] * hs[q], hv[p] + hv[q], self.cls_emb(t["pcls"]).to(s.dtype), self.flow_in(x_low)]
        if self.pfeat_in is not None:
            z = (t["pfeat"].to(s.dtype) - self.pfeat_mu.to(s.dtype)) / self.pfeat_sd.to(s.dtype)
            parts.append(self.pfeat_in(z))
        x = torch.cat(parts, -1)
        r = self.head(x).squeeze(-1) * self.class_scale.to(s.dtype)[t["pcls"]]
        if self.alpha is not None:
            r = r + self.alpha.to(s.dtype)[t["pcls"]] * t["F_int"][p, q].to(s.dtype)
        return r

    def forward(self, Z, pos, H_low, t: dict) -> torch.Tensor:
        """Cartesian ΔH = Bᵀ ΔF B with ΔF symmetric on the pattern and zero elsewhere."""
        r = self.delta_f(Z, pos, H_low, t)
        K = t["B"].shape[0]
        dF = torch.zeros(K, K, dtype=r.dtype, device=r.device)
        p, q = t["pairs"][:, 0], t["pairs"][:, 1]
        dF = dF.index_put((p, q), r).index_put((q, p), r)                               # symmetric; the diagonal is written twice with the same value
        B = t["B"].to(r.dtype)
        return B.T @ dF @ B
