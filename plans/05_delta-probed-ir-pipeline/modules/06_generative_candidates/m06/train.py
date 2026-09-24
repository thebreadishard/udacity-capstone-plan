"""Module 06 — training and sampling by the pre-registered protocol (PRE_REGISTRATION.md, "Model"). Writes a JSON log per epoch with loss and
the validity of 200 samples; the notebook calls train_model() and reads the log. Usage (script): python train.py <dataset.csv> <out dir> [--seed 0]
[--epochs 20] [--conditioning] [--quick]."""
import argparse
import json
import math
import os
import random
import time

import numpy as np
import torch

from data import Vocab, assign_splits, prefix_for, read_dataset
from evaluate import canonical
from model import SmilesTransformer


def make_tensors(rows, vocab, max_len, conditioning):
    enc = [vocab.encode(r["smiles"], max_len, prefix_for(r) if conditioning else ()) for r in rows]
    kept = [e for e in enc if e is not None]
    return torch.tensor(kept, dtype=torch.long), len(rows) - len(kept)


def train_model(rows, out_dir, seed=0, epochs=20, batch=128, lr=3e-4, warmup=500, patience=3, conditioning=False, max_len=96, quick=False, log=print):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    os.makedirs(out_dir, exist_ok=True)
    tr = [r for r in rows if r["split"] == "train"]; va = [r for r in rows if r["split"] == "val"]
    if quick:
        tr, va, epochs = tr[:2000], va[:300], min(epochs, 2)
    vocab = Vocab.build([r["smiles"] for r in rows], conditioning)
    Xtr, drop_tr = make_tensors(tr, vocab, max_len, conditioning); Xva, drop_va = make_tensors(va, vocab, max_len, conditioning)
    model = SmilesTransformer(len(vocab.itos), max_len=max_len)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    steps_total = max(1, epochs * math.ceil(len(Xtr) / batch)); step = 0
    def lr_at(s):
        return lr * min(1.0, (s + 1) / warmup) * 0.5 * (1 + math.cos(math.pi * min(1.0, s / steps_total)))
    hist = []; best = float("inf"); bad = 0; bos, eos = vocab.stoi["<bos>"], vocab.stoi["<eos>"]
    log(f"train {len(Xtr)} (dropped {drop_tr} > {max_len} tokens), val {len(Xva)} (dropped {drop_va}); vocab {len(vocab.itos)}; params {model.n_params():,}; seed {seed}")
    for ep in range(epochs):
        model.train(); perm = torch.randperm(len(Xtr)); t0 = time.time(); tot = 0.0; nb = 0
        for i in range(0, len(Xtr), batch):
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            loss = model.loss(Xtr[perm[i:i + batch]]); opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); step += 1; tot += float(loss); nb += 1
        model.eval()
        with torch.no_grad():
            vl = float(np.mean([float(model.loss(Xva[i:i + batch])) for i in range(0, len(Xva), batch)])) if len(Xva) else float("nan")
            ids = model.sample(200, bos, eos, temperature=1.0, seed=seed * 1000 + ep)
            val200 = sum(1 for row in ids.tolist() if canonical(vocab.decode(row))) / 200
        hist.append(dict(epoch=ep + 1, train_loss=tot / max(nb, 1), val_loss=vl, validity_200=val200, seconds=round(time.time() - t0, 1)))
        log(f"epoch {ep + 1}: train {tot / max(nb, 1):.3f} val {vl:.3f} validity(200) {val200:.2f} {time.time() - t0:.0f} s")
        if vl < best - 1e-4:
            best = vl; bad = 0; torch.save(model.state_dict(), os.path.join(out_dir, f"model_seed{seed}.pt"))
        else:
            bad += 1
            if bad >= patience:
                log("early stop"); break
    json.dump(dict(seed=seed, history=hist, vocab=vocab.itos, conditioning=conditioning, max_len=max_len, n_train=len(Xtr), n_val=len(Xva), params=model.n_params()),
              open(os.path.join(out_dir, f"train_log_seed{seed}.json"), "w"), indent=1)
    model.load_state_dict(torch.load(os.path.join(out_dir, f"model_seed{seed}.pt")))
    return model, vocab, hist


def generate(model, vocab, n=10000, temperature=1.0, prefix=(), seed=0, chunk=500):
    bos, eos = vocab.stoi["<bos>"], vocab.stoi["<eos>"]; out = []
    pre = tuple(vocab.stoi[p] for p in prefix)
    for k in range(0, n, chunk):
        ids = model.sample(min(chunk, n - k), bos, eos, prefix=pre, temperature=temperature, seed=seed * 7919 + k)
        out += [vocab.decode(row) for row in ids.tolist()]
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dataset"); ap.add_argument("out"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=20); ap.add_argument("--conditioning", action="store_true"); ap.add_argument("--quick", action="store_true")
    a = ap.parse_args(); rows = assign_splits(read_dataset(a.dataset))
    train_model(rows, a.out, seed=a.seed, epochs=a.epochs, conditioning=a.conditioning, quick=a.quick)
