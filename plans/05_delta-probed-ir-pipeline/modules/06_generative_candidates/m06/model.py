"""Module 06 — a small decoder-only Transformer over SMILES tokens (PRE_REGISTRATION.md, "Model"). Own PyTorch code, no pretrained weights."""
import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class Block(nn.Module):
    def __init__(self, d, heads, ff, dropout):
        super().__init__()
        self.ln1 = nn.LayerNorm(d); self.attn = nn.MultiheadAttention(d, heads, dropout=dropout, batch_first=True)
        self.ln2 = nn.LayerNorm(d); self.ff = nn.Sequential(nn.Linear(d, ff), nn.GELU(), nn.Dropout(dropout), nn.Linear(ff, d), nn.Dropout(dropout))

    def forward(self, x, causal):
        h = self.ln1(x); a, _ = self.attn(h, h, h, attn_mask=causal, need_weights=False); x = x + a
        return x + self.ff(self.ln2(x))


class SmilesTransformer(nn.Module):
    def __init__(self, vocab_size, max_len=96, d=256, heads=4, layers=4, ff=1024, dropout=0.1):
        super().__init__()
        self.tok = nn.Embedding(vocab_size, d); self.pos = nn.Embedding(max_len, d); self.drop = nn.Dropout(dropout)
        self.blocks = nn.ModuleList([Block(d, heads, ff, dropout) for _ in range(layers)]); self.ln = nn.LayerNorm(d)
        self.head = nn.Linear(d, vocab_size, bias=False); self.max_len = max_len
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, std=0.02)
        if isinstance(m, nn.Linear) and m.bias is not None:
            nn.init.zeros_(m.bias)

    def forward(self, ids):
        B, L = ids.shape; pos = torch.arange(L, device=ids.device)
        x = self.drop(self.tok(ids) + self.pos(pos)[None])
        causal = torch.triu(torch.ones(L, L, dtype=torch.bool, device=ids.device), 1)
        for b in self.blocks:
            x = b(x, causal)
        return self.head(self.ln(x))

    def loss(self, ids):
        logits = self(ids[:, :-1]); target = ids[:, 1:]
        return F.cross_entropy(logits.reshape(-1, logits.size(-1)), target.reshape(-1), ignore_index=0)

    @torch.no_grad()
    def sample(self, n, bos, eos, prefix=(), temperature=1.0, max_len=None, device="cpu", seed=None):
        g = torch.Generator(device=device).manual_seed(seed) if seed is not None else None
        max_len = max_len or self.max_len
        ids = torch.full((n, 1 + len(prefix)), bos, dtype=torch.long, device=device)
        for k, p in enumerate(prefix):
            ids[:, 1 + k] = p
        done = torch.zeros(n, dtype=torch.bool, device=device)
        while ids.size(1) < max_len and not bool(done.all()):
            logits = self(ids)[:, -1] / max(temperature, 1e-6)
            nxt = torch.multinomial(F.softmax(logits, -1), 1, generator=g).squeeze(1)
            nxt = torch.where(done, torch.zeros_like(nxt), nxt)
            ids = torch.cat([ids, nxt[:, None]], 1); done |= nxt == eos
        return ids

    def n_params(self):
        return sum(p.numel() for p in self.parameters())
