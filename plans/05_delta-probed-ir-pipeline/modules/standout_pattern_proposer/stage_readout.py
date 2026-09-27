"""Validation read-out of scorer recipes for the registered P2 search (pre-registration of 26 September 2026, amendment 12:1x and the stage-2 rule of
18:2x): per validation molecule, the predicted against the true log10|Delta_ij| over all pairs i < j gives

  mse        — mean squared error in log10 units (the training target's own metric);
  spearman   — Spearman rank correlation (the stage-2 selection metric: the read-out of the simulation is an ordering);
  p10_all    — precision of the top decile: the fraction of the 10 % largest true |Delta| pairs that the recipe puts in its own top 10 %;
  p10_in / p10_out — the same restricted to pairs within / beyond the 200 cm-1 band (the out-of-band pairs are the ones a hand recipe cannot reach).

Means over molecules per seed, then the seed mean and spread per recipe. P1 (the hand-feature scorer) is read the same way for scale.
Analysis-scale: a few seconds per recipe on one thread; the evaluation molecules are never loaded.

    python stage_readout.py out/exports out/stage2_readout_2026-09-26.md p2s1_lr1e-3_w128 p2s2_huber p2s2_rank [--p1 out/p1] [--seeds 0,1,2]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):   # not inside a notebook kernel
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pp import core as C  # noqa: E402
from pp import embed_scorer as E  # noqa: E402
from pp import scorer as S  # noqa: E402


def ranks(x: np.ndarray) -> np.ndarray:
    r = np.empty(len(x), float)
    r[np.argsort(x, kind="stable")] = np.arange(len(x), dtype=float)
    return r


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra, rb = ranks(a), ranks(b)
    ra -= ra.mean()
    rb -= rb.mean()
    d = float(np.sqrt((ra ** 2).sum() * (rb ** 2).sum()))
    return float((ra * rb).sum() / d) if d > 0 else 0.0


def precision_top(pred: np.ndarray, y: np.ndarray, frac: float = 0.1) -> float | None:
    k = max(int(round(frac * len(y))), 1)
    if len(y) < 10:
        return None
    top_true = set(np.argsort(-y)[:k].tolist())
    top_pred = set(np.argsort(-pred)[:k].tolist())
    return len(top_true & top_pred) / k


def metrics(pred: np.ndarray, y: np.ndarray, inband: np.ndarray) -> dict:
    out = dict(mse=float(((pred - y) ** 2).mean()), spearman=spearman(pred, y), p10_all=precision_top(pred, y))
    out["p10_in"] = precision_top(pred[inband], y[inband])
    out["p10_out"] = precision_top(pred[~inband], y[~inband])
    return out


def validation_molecules(export_dir: Path) -> list[tuple[str, dict]]:
    mols = []
    for p in sorted(Path(export_dir).glob("*.npz")):
        mid = p.stem
        layer = "A" if mid.startswith("A_") else ("A2" if mid.startswith("A2_") else "B")
        if C.split_of(mid, layer) == "val":
            mols.append((mid, C.load_export(p)))
    return mols


def targets(e: dict) -> tuple[np.ndarray, np.ndarray]:
    M = e["M"]
    iu = np.triu_indices(M, 1)
    y = np.log10(np.abs(np.asarray(e["D2"]))[iu] + 1e-8)
    f = np.asarray(e["freq_cm"])
    inband = np.abs(f[iu[0]] - f[iu[1]]) <= S.BAND_CM
    return y, inband


def read_recipe(name: str, predict, mols, seeds) -> dict:
    per_seed = {}
    for s in seeds:
        model = predict(s)
        rows = []
        for mid, e in mols:
            y, inband = targets(e)
            rows.append(metrics(model(e), y, inband))
        per_seed[s] = {k: float(np.mean([r[k] for r in rows if r[k] is not None])) for k in rows[0]}
    keys = list(next(iter(per_seed.values())).keys())
    summary = {k: dict(mean=float(np.mean([v[k] for v in per_seed.values()])), min=float(np.min([v[k] for v in per_seed.values()])),
                       max=float(np.max([v[k] for v in per_seed.values()]))) for k in keys}
    return dict(per_seed=per_seed, summary=summary)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("export_dir")
    ap.add_argument("out_md")
    ap.add_argument("recipes", nargs="+", help="P2 weight prefixes under out/ (e.g. p2s1_lr1e-3_w128)")
    ap.add_argument("--p1", default="out/p1")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(a.threads)
    seeds = [int(s) for s in a.seeds.split(",")]
    mols = validation_molecules(Path(a.export_dir))
    print(f"{len(mols)} validation molecules: {[m for m, _ in mols]}")
    results = {}
    if a.p1:
        def p1_model(s):
            sc = S.Scorer.load(Path(a.p1), s)
            return lambda e: sc.predict(S.pair_features(e)[0])
        results["P1"] = read_recipe("P1", p1_model, mols, seeds)
    for r in a.recipes:
        results[r] = read_recipe(r, lambda s, r=r: E.EmbedScorer.load(Path("out") / r, s).predict, mols, seeds)
    lines = [f"# Validation read-out — {len(mols)} molecules, seeds {seeds}", "",
             "| recipe | MSE(log10) | Spearman | P@10 % all | P@10 % in band | P@10 % out of band |", "|---|---|---|---|---|---|"]
    for name, res in results.items():
        cell = lambda k: f"{res['summary'][k]['mean']:.4f} [{res['summary'][k]['min']:.4f}, {res['summary'][k]['max']:.4f}]"  # noqa: E731
        lines.append(f"| {name} | {cell('mse')} | {cell('spearman')} | {cell('p10_all')} | {cell('p10_in')} | {cell('p10_out')} |")
    lines += ["", "seed mean [min, max] over seeds; every entry is a mean over the validation molecules.", ""]
    text = chr(10).join(lines)
    print(text)
    Path(a.out_md).write_text(text, encoding="utf-8")
    json.dump(dict(molecules=[m for m, _ in mols], seeds=seeds, results=results), open(a.out_md.replace(".md", ".json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
