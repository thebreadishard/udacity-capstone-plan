"""The registered simulation (pre-registration 26 September 2026, experiments E1 and E2): for every evaluation molecule, the recovery curve of the
deterministic order P0, the scorer order P1 (three seeds), and the oracle P3; K_off at ρ_off ≤ 0.3 and 0.1 and n₁₀ (in-band and all pairs); the median
ratios against P0 with the fraction of molecules improved, per evaluation set (layer-A parents; A2/B evaluation split).

    python run_simulation.py <exports> <scorer_prefix> <out_prefix> [--seeds 0,1,2] [--stride 8] [--noise-sigma 0] [--limit N] [--dry-run]
             [--pool band|all]      # E1 (the deck as it is) or E2 (two-mode patterns for every pair; the band stays the solver's prior)

Writes `<out_prefix>.json` (every curve) and `<out_prefix>.md` (the summary table). Nothing is judged here; the pass lines are read against the
pre-registration by hand."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pp import core as C  # noqa: E402
from pp import embed_scorer as E  # noqa: E402
from pp import scorer as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def widen_pool(e: dict) -> dict:
    """E2: add two-mode ± patterns for every pair outside the band (same amplitude, same construction as the probe), appended in a seeded shuffle after the
    existing patterns; none of them held out (the held-out set stays the registered one so ρ_off stays comparable). Returns a new export dict."""
    M, f = e["M"], np.asarray(e["freq_cm"])
    have = {tuple(m) for m, k in zip(e["modes"], e["kinds"], strict=True) if k == "two-mode"}
    extra = []
    for i in range(M):
        for j in range(i + 1, M):
            if (i, j) in have:
                continue
            for sgn in (1.0, -1.0):
                v = np.zeros(M)
                v[i] = C.PROBE.Q_S / np.sqrt(2)
                v[j] = sgn * C.PROBE.Q_S / np.sqrt(2)
                extra.append((v, [i, j]))
    rng = np.random.default_rng(C.PROBE.DECK_SEED + 11)
    rng.shuffle(extra)
    if not extra:
        return e
    A_new = np.vstack([e["A"], np.array([v for v, _ in extra])])
    rows_new = np.vstack([e["rows"], np.array([C.PROBE.design_row_E(v, e["pairs"]) for v, _ in extra])])
    out = dict(e)
    out.update(A=A_new, rows=rows_new, R=rows_new @ e["d_true"], kinds=np.concatenate([e["kinds"], np.array(["two-mode"] * len(extra))]),
               modes=list(e["modes"]) + [m for _, m in extra], holdout=np.concatenate([e["holdout"], np.zeros(len(extra), bool)]))
    return out


def evaluate(e: dict, orders: dict, checkpoints: int, noise_sigma: float, lam_grid) -> dict:
    res = {}
    f = np.asarray(e["freq_cm"])
    inband_pair = np.array([abs(f[i] - f[j]) <= C.W_BAND_CM and i != j for (i, j) in e["pairs"]])
    for name, order in orders.items():
        stride = max(2, int(np.ceil(len(order) / checkpoints)))                  # ≈ `checkpoints` solves per curve whatever the pool size
        curve = C.rho_curve(e, order, stride=stride, lam_grid=lam_grid, noise_sigma=noise_sigma, inband_mask=inband_pair)
        res[name] = dict(curve=curve, K_off_0p3=C.k_off_at(curve, 0.3, e["M"]), K_off_0p1=C.k_off_at(curve, 0.1, e["M"]),
                         n10_all=C.k_off_at(curve, 0.1, e["M"], key=3), n10_inband=C.k_off_at(curve, 0.1, e["M"], key=5))
    return res


def ratio_summary(per_mol: dict, base: str, other: str, key: str) -> dict:
    r, improved, n = [], 0, 0
    for m in per_mol.values():
        a, b = m[base][key], m[other][key]
        if a is None or b is None:
            continue
        n += 1
        r.append(b / max(a, 1))
        improved += b < a
    return dict(n=n, median_ratio=float(np.median(r)) if r else None, frac_improved=(improved / n) if n else None)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("exports")
    ap.add_argument("scorer_prefix")
    ap.add_argument("out_prefix")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--embed-prefix", default=None, help="P2 weights prefix (pp.embed_scorer); adds P2 and the P12 combination")
    ap.add_argument("--checkpoints", type=int, default=60, help="solves per curve (stride adapts to the pool size)")
    ap.add_argument("--lam-grid", default="1e-6,1e-5", help="λ grid of the banded-ℓ₁ prior, chosen per checkpoint on the held-out patterns")
    ap.add_argument("--noise-sigma", type=float, default=0.0)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--shard", default=None, help="k/n: this process takes every n-th evaluation molecule starting at k (0-based); merge with merge_shards.py")
    ap.add_argument("--pool", choices=["band", "all"], default="band")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(",")]
    index = json.load(open(Path(a.exports) / "index.json"))["molecules"]
    evals = [r for r in index if r["split"] in ("eval_parents", "eval")]
    if a.limit:
        evals = evals[: a.limit]
    if a.shard:
        k, n = (int(x) for x in a.shard.split("/"))
        evals = evals[k::n]
    lam_grid = tuple(float(x) for x in a.lam_grid.split(","))
    print(f"{len(evals)} evaluation molecules ({sum(r['split'] == 'eval_parents' for r in evals)} parents); pool {a.pool}; seeds {seeds}; checkpoints {a.checkpoints}; "
          f"λ {lam_grid}; noise σ {a.noise_sigma}; P2 {'yes' if a.embed_prefix else 'no'}" + (" (dry run)" if a.dry_run else ""))
    if a.dry_run:
        return 0
    scorers = {s: S.Scorer.load(Path(a.scorer_prefix), s) for s in seeds}
    embeds = {s: E.EmbedScorer.load(Path(a.embed_prefix), s) for s in seeds} if a.embed_prefix else {}
    per_mol, t0 = {}, time.time()
    for k, r in enumerate(evals):
        e = C.load_export(Path(a.exports) / f"{r['id']}.npz")
        if a.pool == "all":
            e = widen_pool(e)
        X, _, pairs = S.pair_features(e)
        orders = {"P0": C.order_p0(e), "P3_oracle": C.order_oracle(e)}
        for s, sc in scorers.items():
            p1 = sc.predict(X)
            orders[f"P1_seed{s}"] = C.order_by_scores(e, S.scores_matrix(e, p1, pairs))
            if s in embeds:
                p2 = embeds[s].predict(e)
                orders[f"P2_seed{s}"] = C.order_by_scores(e, S.scores_matrix(e, p2, pairs))
                z1, z2 = (p1 - p1.mean()) / (p1.std() + 1e-9), (p2 - p2.mean()) / (p2.std() + 1e-9)
                orders[f"P12_seed{s}"] = C.order_by_scores(e, S.scores_matrix(e, 0.5 * (z1 + z2) * p1.std() + p1.mean(), pairs))
        per_mol[r["id"]] = dict(split=r["split"], M=e["M"], **evaluate(e, orders, a.checkpoints, a.noise_sigma, lam_grid))
        print(f"  {k + 1}/{len(evals)} {r['id']} M {e['M']}: K_off(0.3) P0 {per_mol[r['id']]['P0']['K_off_0p3']} P1 {per_mol[r['id']]['P1_seed0']['K_off_0p3']} "
              f"oracle {per_mol[r['id']]['P3_oracle']['K_off_0p3']}; {time.time() - t0:.0f} s", flush=True)
    summary = {}
    for split in ("eval_parents", "eval"):
        sub = {i: m for i, m in per_mol.items() if m["split"] == split}
        summary[split] = {key: {name: ratio_summary(sub, "P0", name, key) for name in per_mol[next(iter(per_mol))] if name.startswith(("P1", "P2", "P3"))}
                          for key in ("K_off_0p3", "K_off_0p1", "n10_inband", "n10_all")} if sub else {}
        if sub:
            summary[split]["n_molecules"] = len(sub)
            summary[split]["P0_reached_0p3"] = sum(m["P0"]["K_off_0p3"] is not None for m in sub.values())
    out = dict(date=time.strftime("%Y-%m-%d %H:%M"), pool=a.pool, seeds=seeds, checkpoints=a.checkpoints, lam_grid=lam_grid, noise_sigma=a.noise_sigma,
               exports=str(a.exports), scorer_prefix=str(a.scorer_prefix), embed_prefix=a.embed_prefix, summary=summary, per_molecule=per_mol,
               seconds=round(time.time() - t0, 1))
    json.dump(out, open(a.out_prefix + ".json", "w"), indent=1)
    lines = [f"# Pattern-proposer simulation — pool {a.pool}, {out['date']}", "",
             f"seeds {seeds}, {a.checkpoints} checkpoints per curve, λ {lam_grid}, noise σ {a.noise_sigma}; {len(per_mol)} evaluation molecules.", ""]
    for split, tab in summary.items():
        if not tab:
            continue
        lines += [f"## {split} (n {tab['n_molecules']}; P0 reaches ρ_off ≤ 0.3 on {tab['P0_reached_0p3']})", "", "| read-out | ordering | n | median ratio vs P0 | improved |", "|---|---|---|---|---|"]
        for key in ("K_off_0p3", "K_off_0p1", "n10_inband", "n10_all"):
            for name, v in tab[key].items():
                mr = "—" if v["median_ratio"] is None else f"{v['median_ratio']:.2f}"
                fi = "—" if v["frac_improved"] is None else f"{100 * v['frac_improved']:.0f} %"
                lines.append(f"| {key} | {name} | {v['n']} | {mr} | {fi} |")
        lines.append("")
    Path(a.out_prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {a.out_prefix}.json / .md in {out['seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
