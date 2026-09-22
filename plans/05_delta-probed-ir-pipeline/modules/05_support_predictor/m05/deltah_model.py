# Verbatim copy (22 September 2026) of GoalGathering/architecture/51_deltaH_model_pytorch.py — the design sheet of the ΔH model.
# Module 05 imports it from here so that a clone of the module runs on its own; the sheet stays the source of truth and this copy
# is refreshed by `python m05/sync_model.py` (which also asserts the two files are identical). Promotion to src/dpir with tests
# follows the quality policy before the module is submitted.

"""51 — The ΔH model in PyTorch: the definition of the network (sheet 5b: sheet 5 in code).

This file defines only the network: input layer, hidden layers, output layers and what standardly
belongs around it (configuration, masking, initialisation, loss functions, ensemble, parameter count,
smoke test). Training (sheet 6) and test and licence (sheet 7) are not in it; they go into
`modules/05_support_predictor/` as soon as the labels are there.

Naming (agreement of 20 September 2026): the whole is **the ΔH model**; embedding + self-attention
form the **backbone**; **block head** and **pair head** are the heads; instances with different seeds
are the **members** of the **ensemble**; the simple rules (family median) are the **baseline**.

Numbers come from the desk note of 18 September (§1): two encoder layers, four attention heads,
width 64, dropout 0.1, order 10⁵ parameters; AdamW, lr 1e-3, batch 32 molecules. Since the RECIPE
change of 19 September the target object is the **family block** (diagonal and couplings), not the
separate shift per mode (E4).

Input per molecule (one row in the batch):
  tokens   (B, M, d_in)  one token per DFT normal mode: [ω/1000, family one-hot, irrep one-hot,
                          mass-weighted share of C/H/N/O, localisation index, environment classes]
  family   (B, M)        family index per mode (for the block mask)
  charge   (B,)          charge of the molecule (integer)
  mult     (B,)          spin multiplicity (1 = singlet, 2 = doublet, …)
  mask     (B, M)        True where a mode is real (molecules have 30–100 modes; the rest is padding)
Charge and multiplicity are molecule tokens placed in front of the mode tokens, so that cations can
flow in later without an architecture change (P26 §4).

Output:
  block        (B, M, M)  symmetric; ΔH block in the mode basis, filled only within a family:
                          diagonal K_ii (shift) and couplings K_ij (i ≠ j); unit cm⁻¹
  pair_logits  (B, M, M)  logit that the pair (i, j) belongs to the support of ΔH (support label, RECIPE)
On top of that the ensemble gives, per element, the mean and the spread over the members.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import torch
import torch.nn as nn
import torch.nn.functional as F


# ----------------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------------
@dataclass
class DeltaHConfig:
    # input
    n_families: int = 5          # C–H stretch, C–H oop, C–H in-plane / ring in-plane, ring breathing, other
    n_irreps: int = 8            # one-hot of the irrep within the point group (padded to 8)
    n_elements: int = 4          # mass-weighted share of C, H, N, O in the motion
    n_env: int = 0               # environment classes (H solo/duo/trio/quartet/substituent; C fused/edge/…); 0 = off
    max_charge: int = 2          # |charge| ≤ 2 → 5 classes (−2 … +2)
    max_mult: int = 4            # multiplicity 1 … 4
    # backbone
    d_model: int = 64
    n_heads: int = 4
    n_layers: int = 2
    d_ff: int = 256              # 4 × d_model, the usual ratio
    dropout: float = 0.1
    # heads
    d_pair: int = 64             # width of the pair network
    # training (only recorded here; the loop is in modules/05_support_predictor/)
    lr: float = 1e-3
    weight_decay: float = 1e-2
    batch_molecules: int = 32
    seeds: tuple[int, ...] = field(default_factory=lambda: (0, 1, 2))

    @property
    def d_in(self) -> int:
        # ω/1000 (1) + family + irrep + element shares + localisation (1) + environment classes
        return 1 + self.n_families + self.n_irreps + self.n_elements + 1 + self.n_env


# ----------------------------------------------------------------------------------------------
# Input layer: embedding of the mode tokens and the two molecule tokens
# ----------------------------------------------------------------------------------------------
class TokenEmbedding(nn.Module):
    """Mode token (d_in scalars) → vector in R^d_model; charge and multiplicity → one vector each.

    No positional encoding: the modes of a molecule are a set, not a sequence; the frequency is
    already in the token. The input is first normalised with a fixed scale (ω/1000, shares in [0, 1])
    and then passed through a two-layer MLP; a linear layer alone turned out to be too little in E0
    (ridge 17.6 cm⁻¹ on the ring family).
    """

    def __init__(self, cfg: DeltaHConfig):
        super().__init__()
        self.mode_mlp = nn.Sequential(
            nn.Linear(cfg.d_in, cfg.d_model), nn.GELU(), nn.Linear(cfg.d_model, cfg.d_model)
        )
        self.charge_emb = nn.Embedding(2 * cfg.max_charge + 1, cfg.d_model)   # index = charge + max_charge
        self.mult_emb = nn.Embedding(cfg.max_mult + 1, cfg.d_model)           # index = multiplicity
        self.type_emb = nn.Embedding(3, cfg.d_model)                          # 0 = mode, 1 = charge, 2 = multiplicity
        self.max_charge = cfg.max_charge
        self.norm = nn.LayerNorm(cfg.d_model)
        self.drop = nn.Dropout(cfg.dropout)

    def forward(self, tokens, charge, mult, mask):
        B, M, _ = tokens.shape
        h_modes = self.mode_mlp(tokens) + self.type_emb.weight[0]                       # (B, M, d)
        h_charge = (self.charge_emb(charge + self.max_charge) + self.type_emb.weight[1])[:, None]  # (B, 1, d)
        h_mult = (self.mult_emb(mult) + self.type_emb.weight[2])[:, None]              # (B, 1, d)
        h = torch.cat([h_charge, h_mult, h_modes], dim=1)                              # (B, 2 + M, d)
        full_mask = torch.cat([torch.ones(B, 2, dtype=torch.bool, device=mask.device), mask], dim=1)
        return self.drop(self.norm(h)), full_mask


# ----------------------------------------------------------------------------------------------
# Hidden layers: self-attention over the modes (the backbone)
# ----------------------------------------------------------------------------------------------
class Backbone(nn.Module):
    """Transformer encoder: n_layers × (multi-head self-attention → feed-forward), pre-LayerNorm.

    Every mode looks at every other mode of the same molecule (and at the two molecule tokens);
    so a ring mode can 'know' which other ring modes there are and how far apart they lie in
    frequency — exactly the information that determines the couplings in the family block.
    """

    def __init__(self, cfg: DeltaHConfig):
        super().__init__()
        layer = nn.TransformerEncoderLayer(
            d_model=cfg.d_model, nhead=cfg.n_heads, dim_feedforward=cfg.d_ff, dropout=cfg.dropout,
            activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=cfg.n_layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(cfg.d_model)

    def forward(self, h, full_mask):
        h = self.encoder(h, src_key_padding_mask=~full_mask)  # PyTorch masks True = ignore
        return self.norm(h)                                    # (B, 2 + M, d): context vectors


# ----------------------------------------------------------------------------------------------
# Output layers: block head and pair head
# ----------------------------------------------------------------------------------------------
def pair_features(h, omega):
    """Symmetric pair features [h_i + h_j, |h_i − h_j|, h_i ⊙ h_j, |ω_i − ω_j|/1000] → (B, M, M, 3d + 1)."""
    hi, hj = h[:, :, None, :], h[:, None, :, :]
    d_omega = (omega[:, :, None] - omega[:, None, :]).abs()[..., None]
    return torch.cat([hi + hj, (hi - hj).abs(), hi * hj, d_omega], dim=-1)


class BlockHead(nn.Module):
    """ΔH block per family in the mode basis: K_ii from the context vector of mode i, K_ij (i ≠ j) from
    the symmetric pair features; zero outside the family and outside the molecule.

    The symmetric pair features (h_i + h_j, |h_i − h_j|, h_i ⊙ h_j) make K_ij = K_ji in eval mode;
    with dropout on, the masks of (i, j) and (j, i) differ, so the block is symmetrised explicitly. The block is the target object of the RECIPE change of 19 September: the loss
    compares the whole block with the label, not only the diagonal (E4).
    """

    def __init__(self, cfg: DeltaHConfig):
        super().__init__()
        d = cfg.d_model
        self.diag = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Dropout(cfg.dropout), nn.Linear(d, 1))
        self.offdiag = nn.Sequential(nn.Linear(3 * d + 1, cfg.d_pair), nn.GELU(), nn.Dropout(cfg.dropout), nn.Linear(cfg.d_pair, 1))

    def forward(self, h, omega, family, mask):
        diag = self.diag(h).squeeze(-1)                                       # (B, M)
        off = self.offdiag(pair_features(h, omega)).squeeze(-1)               # (B, M, M)
        off = 0.5 * (off + off.transpose(1, 2))                               # exactly symmetric, also with dropout on
        same_family = family[:, :, None] == family[:, None, :]
        valid = mask[:, :, None] & mask[:, None, :]
        eye = torch.eye(h.shape[1], dtype=torch.bool, device=h.device)[None]
        block = torch.where(eye, torch.diag_embed(diag), off)
        return block * (same_family & valid)                                  # (B, M, M), symmetric


class PairHead(nn.Module):
    """Support label per mode pair: logit that (i, j) carries a coupling that moves the VPT2 band.
    Declared baseline (RECIPE): the resonance-denominator rule of P25, 1/|ω_i² − ω_j²| within an irrep."""

    def __init__(self, cfg: DeltaHConfig):
        super().__init__()
        d = cfg.d_model
        self.mlp = nn.Sequential(nn.Linear(3 * d + 1, cfg.d_pair), nn.GELU(), nn.Dropout(cfg.dropout), nn.Linear(cfg.d_pair, 1))

    def forward(self, h, omega, mask):
        logits = self.mlp(pair_features(h, omega)).squeeze(-1)                # (B, M, M)
        valid = mask[:, :, None] & mask[:, None, :]
        return logits.masked_fill(~valid, -1e4)


# ----------------------------------------------------------------------------------------------
# The ΔH model: input layer → backbone → two heads
# ----------------------------------------------------------------------------------------------
class DeltaHModel(nn.Module):
    def __init__(self, cfg: DeltaHConfig | None = None):
        super().__init__()
        self.cfg = cfg or DeltaHConfig()
        self.embed = TokenEmbedding(self.cfg)
        self.backbone = Backbone(self.cfg)
        self.block_head = BlockHead(self.cfg)
        self.pair_head = PairHead(self.cfg)
        self.apply(self._init)

    @staticmethod
    def _init(m):
        # standard: Xavier for linear layers, zero bias; embeddings small normal
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, std=0.02)

    def forward(self, tokens, family, charge, mult, mask):
        omega = tokens[..., 0]                                               # ω/1000 is first in the token
        h, full_mask = self.embed(tokens, charge, mult, mask)                # input layer
        ctx = self.backbone(h, full_mask)                                    # hidden layers
        ctx_modes = ctx[:, 2:]                                               # the molecule tokens have done their work
        return {
            "block": self.block_head(ctx_modes, omega, family, mask),        # output layer 1
            "pair_logits": self.pair_head(ctx_modes, omega, mask),           # output layer 2
            "context": ctx_modes,                                            # for diagnosis and E-series-like tests
        }

    def n_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ----------------------------------------------------------------------------------------------
# Loss functions (the form is fixed; the weights per family come from the error budget of sheet 4)
# ----------------------------------------------------------------------------------------------
def block_loss(pred_block, target_block, family, mask, family_weight=None):
    """Mean squared error over the filled block elements (within family, within molecule),
    optionally weighted per family with 1/margin² from the error budget. Diagonal and couplings
    both count: that is the block rule of 19 September."""
    same = (family[:, :, None] == family[:, None, :]) & mask[:, :, None] & mask[:, None, :]
    w = same.float()
    if family_weight is not None:                                            # (n_families,) → per element
        w = w * family_weight[family][:, :, None]
    return (w * (pred_block - target_block) ** 2).sum() / w.sum().clamp_min(1.0)


def pair_loss(pair_logits, support, mask, pos_weight):
    """Binary cross-entropy on the pairs, class-weighted to the prevalence in the training set
    (lesson of E5: unweighted, the network learns only the bias, because 98 % of the pairs are zero)."""
    valid = mask[:, :, None] & mask[:, None, :]
    loss = F.binary_cross_entropy_with_logits(pair_logits, support.float(), pos_weight=pos_weight, reduction="none")
    return (loss * valid).sum() / valid.sum().clamp_min(1.0)


# ----------------------------------------------------------------------------------------------
# Ensemble: members with different seeds; mean and spread per element
# ----------------------------------------------------------------------------------------------
class DeltaHEnsemble(nn.Module):
    """Bundle of trained members. Gives per block element the mean (the prediction) and the
    standard deviation over the members (the raw uncertainty; the calibration of sheet 7 scales it)."""

    def __init__(self, members: list[DeltaHModel]):
        super().__init__()
        self.members = nn.ModuleList(members)

    @torch.no_grad()
    def forward(self, tokens, family, charge, mult, mask):
        outs = [m(tokens, family, charge, mult, mask) for m in self.members]
        blocks = torch.stack([o["block"] for o in outs])                     # (E, B, M, M)
        probs = torch.stack([torch.sigmoid(o["pair_logits"]) for o in outs])
        return {
            "block_mean": blocks.mean(0), "block_std": blocks.std(0, unbiased=False),
            "pair_prob": probs.mean(0), "pair_prob_std": probs.std(0, unbiased=False),
        }


def make_ensemble(cfg: DeltaHConfig | None = None) -> DeltaHEnsemble:
    cfg = cfg or DeltaHConfig()
    members = []
    for s in cfg.seeds:
        torch.manual_seed(s)
        members.append(DeltaHModel(cfg))
    return DeltaHEnsemble(members)


# ----------------------------------------------------------------------------------------------
# Smoke test: shapes and parameter count on random input (no data, no training)
# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    torch.set_num_threads(1)
    cfg = DeltaHConfig()
    model = DeltaHModel(cfg)
    B, M = 2, 48                                                             # two molecules, padded to 48 modes (naphthalene)
    tokens = torch.rand(B, M, cfg.d_in); tokens[..., 0] = torch.rand(B, M) * 3.2  # ω/1000 in [0, 3.2]
    family = torch.randint(0, cfg.n_families, (B, M))
    charge = torch.tensor([0, 1]); mult = torch.tensor([1, 2])                # neutral singlet, cation doublet
    mask = torch.ones(B, M, dtype=torch.bool); mask[0, 30:] = False           # molecule 0 has 30 modes (benzene)
    out = model(tokens, family, charge, mult, mask)
    blk = out["block"]
    assert blk.shape == (B, M, M) and torch.allclose(blk, blk.transpose(1, 2), atol=1e-6), "block not symmetric"
    assert blk[0, 30:].abs().sum() == 0 and blk[0, :, 30:].abs().sum() == 0, "padding leaks into the block"
    same = family[:, :, None] == family[:, None, :]
    assert (blk * ~same).abs().sum() == 0, "coupling outside the family"
    target = torch.zeros_like(blk); support = torch.zeros(B, M, M, dtype=torch.bool)
    l1 = block_loss(blk, target, family, mask); l2 = pair_loss(out["pair_logits"], support, mask, pos_weight=torch.tensor(50.0))
    (l1 + l2).backward()
    ens = make_ensemble(cfg); eo = ens(tokens, family, charge, mult, mask)
    print(f"ΔH model: {model.n_parameters():,} parameters (d_in {cfg.d_in}, d_model {cfg.d_model}, "
          f"{cfg.n_layers} layers, {cfg.n_heads} heads); block {tuple(blk.shape)}, pair {tuple(out['pair_logits'].shape)}; "
          f"ensemble of {len(ens.members)}: block_mean {tuple(eo['block_mean'].shape)}, block_std mean {eo['block_std'].mean():.3f}; "
          f"loss block {l1.item():.3f}, pair {l2.item():.3f}; backward ok")
