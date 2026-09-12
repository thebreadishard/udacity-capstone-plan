"""Module 05 — the support Transformer (RECIPE.md baseline): self-attention over DFT-mode tokens, a pairwise head
that scores every (i, j) pair. PyTorch, CPU. Nothing here is tuned; the numbers are the RECIPE's."""
import torch
import torch.nn as nn


class SupportTransformer(nn.Module):
    def __init__(self, d_in: int, d_model: int = 64, n_heads: int = 4, n_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.embed = nn.Sequential(nn.Linear(d_in, d_model), nn.GELU(), nn.LayerNorm(d_model))
        layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=n_heads, dim_feedforward=4 * d_model, dropout=dropout, batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers, enable_nested_tensor=False)
        self.pair_head = nn.Sequential(nn.Linear(4 * d_model + 1, d_model), nn.GELU(), nn.Dropout(dropout), nn.Linear(d_model, 1))

    def forward(self, tokens: torch.Tensor, pad_mask: torch.Tensor | None = None) -> torch.Tensor:
        """tokens (B, M, d_in); pad_mask (B, M) True where padded. Returns pair logits (B, M, M), symmetric."""
        h = self.encoder(self.embed(tokens), src_key_padding_mask=pad_mask)          # (B, M, d)
        hi, hj = h.unsqueeze(2), h.unsqueeze(1)                                         # (B, M, 1, d), (B, 1, M, d)
        domega = (tokens[..., 0].unsqueeze(2) - tokens[..., 0].unsqueeze(1)).abs().unsqueeze(-1)   # |ω_i − ω_j| (token 0 = ω/1000)
        hi, hj = torch.broadcast_tensors(hi, hj)
        feat = torch.cat([hi, hj, (hi - hj).abs(), hi * hj, domega], dim=-1)
        logits = self.pair_head(feat).squeeze(-1)
        return 0.5 * (logits + logits.transpose(1, 2))


def implied_pattern_count(prob: torch.Tensor, labels: torch.Tensor, recall: float = 0.9) -> int:
    """K the prior implies: the number of off-diagonal pairs one must take, in descending predicted probability,
    to cover `recall` of the true support (upper triangle). Returns the count (diagonal patterns not included)."""
    iu = torch.triu_indices(prob.shape[-1], prob.shape[-1], offset=1)
    p, y = prob[iu[0], iu[1]], labels[iu[0], iu[1]]
    order = torch.argsort(p, descending=True)
    need = int(torch.ceil(recall * y.sum()).item())
    if need == 0:
        return 0
    cum = torch.cumsum(y[order], dim=0)
    return int((cum < need).sum().item()) + 1
