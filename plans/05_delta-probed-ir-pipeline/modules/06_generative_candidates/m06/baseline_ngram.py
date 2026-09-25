"""Token-level n-gram (Markov) baseline for module 06 — the control the Transformer must beat (dated amendment of 25 September 2026 to the
pre-registration; secondary, the primary metrics and their predictions are unchanged).

A 5-gram model over the same SMILES tokens as the Transformer, with stupid back-off to shorter contexts, trained on the train split only, sampled
10,000 times at temperature 1.0 (plain sampling from the empirical conditional) and evaluated with exactly `evaluate.evaluate_samples`. Seconds of
compute; no learning beyond counting. Usage: python m06/baseline_ngram.py <dataset.csv> <out.json> [--order 5] [--n 10000] [--seed 0]"""
import argparse
import collections
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from m06.data import assign_splits, murcko, read_dataset, tokenize
from m06.evaluate import evaluate_samples

BOS, EOS = "<bos>", "<eos>"


def fit(smiles_list, order):
    counts = [collections.defaultdict(collections.Counter) for _ in range(order)]   # counts[k][context of length k][next token]
    for s in smiles_list:
        toks = [BOS] * (order - 1) + tokenize(s) + [EOS]
        for i in range(order - 1, len(toks)):
            for k in range(order):
                ctx = tuple(toks[i - k:i]) if k else ()
                counts[k][ctx][toks[i]] += 1
    return counts


def sample_one(counts, order, rng, max_len=96):
    toks = [BOS] * (order - 1); out = []
    while len(out) < max_len:
        nxt = None
        for k in range(order - 1, -1, -1):                       # longest context seen in training wins (stupid back-off)
            ctx = tuple(toks[len(toks) - k:]) if k else ()
            c = counts[k].get(ctx)
            if c:
                items, weights = zip(*c.items()); nxt = rng.choices(items, weights=weights)[0]; break
        if nxt is None or nxt == EOS:
            break
        out.append(nxt); toks.append(nxt)
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dataset"); ap.add_argument("out"); ap.add_argument("--order", type=int, default=5)
    ap.add_argument("--n", type=int, default=10000); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(); t0 = time.time()
    rows = assign_splits(read_dataset(a.dataset))
    train = [r for r in rows if r["split"] == "train"]; test_rows = [r for r in rows if r["split"] == "test"]
    counts = fit([r["smiles"] for r in train], a.order); t1 = time.time()
    rng = random.Random(a.seed); samples = [sample_one(counts, a.order, rng) for _ in range(a.n)]; t2 = time.time()
    res, extra = evaluate_samples(samples, [r["smiles"] for r in train], [r["scaffold"] for r in train], test_rows, murcko)
    out = dict(model=f"{a.order}-gram token Markov baseline with stupid back-off", n_train=len(train), n_contexts=[len(c) for c in counts], seed=a.seed, temperature=1.0,
               metrics=res, examples_valid_novel=extra["novel"][:10], examples_invalid=extra["invalid_examples"][:10],
               seconds=dict(fit=round(t1 - t0, 1), sample=round(t2 - t1, 1), evaluate=round(time.time() - t2, 1)))
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()}), "| seconds", out["seconds"])


if __name__ == "__main__":
    main()
