#!/usr/bin/env python
"""Module 05 smoke test: proves the code path (corpus fixture -> tokens/labels -> SupportTransformer -> loss -> metrics)
on the dry-run fixture. NOT a result: one molecule, a few steps, no held-out set. Run:  python smoke_test.py"""
import json, time
from pathlib import Path
import numpy as np, torch
from model import SupportTransformer, implied_pattern_count

HERE = Path(__file__).resolve().parent
torch.manual_seed(0)
z = np.load(HERE.parent / "data" / "corpus_fixture.npz")
names = sorted({k.split("__")[0] for k in z.files})
tok = torch.tensor(z[f"{names[0]}__tokens"]).unsqueeze(0)
lab = torch.tensor(z[f"{names[0]}__labels"]).float().unsqueeze(0)
M = tok.shape[1]
model = SupportTransformer(d_in=tok.shape[-1])
n_par = sum(p.numel() for p in model.parameters())
pos = lab.sum().item(); neg = M * (M - 1) - pos
crit = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(neg / max(pos, 1.0)))
opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
offdiag = ~torch.eye(M, dtype=torch.bool)
t0 = time.time(); losses = []
for step in range(20):
    model.train(); opt.zero_grad()
    logits = model(tok)
    loss = crit(logits[0][offdiag], lab[0][offdiag]); loss.backward(); opt.step(); losses.append(loss.item())
model.eval()
with torch.no_grad():
    prob = torch.sigmoid(model(tok))[0]
K = implied_pattern_count(prob, lab[0], recall=0.9)
out = dict(molecule=names[0], M=M, params=n_par, positive_pairs=int(pos // 2), possible_pairs=M * (M - 1) // 2,
           loss_first=round(losses[0], 4), loss_last=round(losses[-1], 4), K_at_recall_0p9=K, seconds=round(time.time() - t0, 1),
           torch=torch.__version__, note="smoke test on one fixture molecule; not a result")
print(json.dumps(out, indent=1))
json.dump(out, open(HERE.parent / "data" / "smoke_test.json", "w"), indent=1)
