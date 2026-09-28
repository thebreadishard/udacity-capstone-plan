"""The registered simulation (pre-registration 26 September 2026, experiments E1 and E2): for every evaluation molecule, the recovery curve of the
deterministic order P0, the scorer order P1 (three seeds), and the oracle P3; K_off at ρ_off ≤ 0.3 and 0.1 and n₁₀ (in-band and all pairs); the median
ratios against P0 with the fraction of molecules improved, per evaluation set (layer-A parents; A2/B evaluation split).

    python run_simulation.py <exports> <scorer_prefix> <out_prefix> [--seeds 0,1,2] [--stride 8] [--noise-sigma 0] [--limit N] [--dry-run]
             [--pool band|all]      # E1 (the deck as it is) or E2 (two-mode patterns for every pair; the band stays the solver's prior)
             [--w-cm W]             # the solver's prior width (28 Sep 2026 amendment: 0 = band-free ℓ₁ on every off-diagonal pair; default = the band)
             [--only P0,P12,P3_oracle]  # curves only for these orderings (prefix match); the scorers still run

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
    M = e["M"]
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


def evaluate(e: dict, orders: dict, checkpoints: int, noise_sigma: float, lam_grid, priors: dict | None = None, w_cm: float = C.W_BAND_CM) -> dict:
    """`orders`: name → fixed pattern order. `priors` (26 Sep 2026 18:4x, the adaptive variants): name → a score per pattern; the pool is P0's set and
    the order is built checkpoint by checkpoint from the reconstruction (core.adaptive_pick). `w_cm` (28 Sep 2026 amendment): the solver's prior width;
    the in-band read-out column keeps the registered 200 cm⁻¹ whatever the solver uses."""
    res = {}
    f = np.asarray(e["freq_cm"])
    inband_pair = np.array([abs(f[i] - f[j]) <= C.W_BAND_CM and i != j for (i, j) in e["pairs"]])
    for name, order in orders.items():
        stride = max(2, int(np.ceil(len(order) / checkpoints)))                  # ≈ `checkpoints` solves per curve whatever the pool size
        curve = C.rho_curve(e, order, stride=stride, lam_grid=lam_grid, w_cm=w_cm, noise_sigma=noise_sigma, inband_mask=inband_pair)
        res[name] = dict(curve=curve, K_off_0p3=C.k_off_at(curve, 0.3, e["M"]), K_off_0p1=C.k_off_at(curve, 0.1, e["M"]),
                         n10_all=C.k_off_at(curve, 0.1, e["M"], key=3), n10_inband=C.k_off_at(curve, 0.1, e["M"], key=5))
    pool = C.order_p0(e)
    for name, prior in (priors or {}).items():
        stride = max(2, int(np.ceil(len(pool) / checkpoints)))
        curve = C.rho_curve(e, pool, stride=stride, lam_grid=lam_grid, w_cm=w_cm, noise_sigma=noise_sigma, inband_mask=inband_pair, adapt_prior=prior)
        res[name] = dict(curve=curve, K_off_0p3=C.k_off_at(curve, 0.3, e["M"]), K_off_0p1=C.k_off_at(curve, 0.1, e["M"]),
                         n10_all=C.k_off_at(curve, 0.1, e["M"], key=3), n10_inband=C.k_off_at(curve, 0.1, e["M"], key=5), adaptive=True)
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


def select_orders(named: dict, only: str | None) -> dict:
    """`--only` (28 Sep 2026): keep the orderings whose name starts with one of the comma-separated prefixes; P0 is always kept (the control column).
    None keeps everything."""
    if not only:
        return named
    prefixes = tuple(p.strip() for p in only.split(",") if p.strip())
    return {k: v for k, v in named.items() if k == "P0" or k.startswith(prefixes)}


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
    ap.add_argument("--adaptive", action="store_true", help="add P0A, P1A_seed*, P2A_seed* (re-rank after every checkpoint; registered 26 Sep 2026 18:4x)")
    ap.add_argument("--w-cm", type=float, default=C.W_BAND_CM, help="the solver's prior width in cm⁻¹; 0 = band-free ℓ₁ on every off-diagonal pair (28 Sep 2026 amendment)")
    ap.add_argument("--only", default=None, help="comma-separated ordering prefixes whose curves are computed (P0 always); e.g. P0,P12,P3_oracle")
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
          f"λ {lam_grid}; noise σ {a.noise_sigma}; P2 {'yes' if a.embed_prefix else 'no'}; adaptive {'yes' if a.adaptive else 'no'}; solver prior w {a.w_cm:g} cm⁻¹; "
          f"only {a.only or 'all'}" + (" (dry run)" if a.dry_run else ""))
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
        priors = {}
        if a.adaptive:
            prior0 = np.zeros(len(e["kinds"]))
            prior0[orders["P0"]] = -np.arange(len(orders["P0"]), dtype=float)                 # P0's rank as the prior score
            priors["P0A"] = prior0
        for s, sc in scorers.items():
            p1 = sc.predict(X)
            orders[f"P1_seed{s}"] = C.order_by_scores(e, S.scores_matrix(e, p1, pairs))
            if a.adaptive:
                priors[f"P1A_seed{s}"] = C.pair_scores_to_pattern_scores(e, S.scores_matrix(e, p1, pairs))
            if s in embeds:
                p2 = embeds[s].predict(e)
                orders[f"P2_seed{s}"] = C.order_by_scores(e, S.scores_matrix(e, p2, pairs))
                if a.adaptive:
                    priors[f"P2A_seed{s}"] = C.pair_scores_to_pattern_scores(e, S.scores_matrix(e, p2, pairs))
                z1, z2 = (p1 - p1.mean()) / (p1.std() + 1e-9), (p2 - p2.mean()) / (p2.std() + 1e-9)
                orders[f"P12_seed{s}"] = C.order_by_scores(e, S.scores_matrix(e, 0.5 * (z1 + z2) * p1.std() + p1.mean(), pairs))
        orders, priors = select_orders(orders, a.only), select_orders(priors, a.only)
        per_mol[r["id"]] = dict(split=r["split"], M=e["M"], **evaluate(e, orders, a.checkpoints, a.noise_sigma, lam_grid, priors, w_cm=a.w_cm))
        shown = [n for n in ("P1_seed0", "P12_seed0", "P3_oracle") if n in per_mol[r["id"]]]
        print(f"  {k + 1}/{len(evals)} {r['id']} M {e['M']}: K_off(0.3) P0 {per_mol[r['id']]['P0']['K_off_0p3']} "
              + " ".join(f"{n} {per_mol[r['id']][n]['K_off_0p3']}" for n in shown) + f"; {time.time() - t0:.0f} s", flush=True)
    summary = {}
    for split in ("eval_parents", "eval"):
        sub = {i: m for i, m in per_mol.items() if m["split"] == split}
        summary[split] = {key: {name: ratio_summary(sub, "P0", name, key) for name in per_mol[next(iter(per_mol))] if name.startswith(("P0A", "P1", "P2", "P3"))}
                          for key in ("K_off_0p3", "K_off_0p1", "n10_inband", "n10_all")} if sub else {}
        if sub:
            summary[split]["n_molecules"] = len(sub)
            summary[split]["P0_reached_0p3"] = sum(m["P0"]["K_off_0p3"] is not None for m in sub.values())
    out = dict(date=time.strftime("%Y-%m-%d %H:%M"), pool=a.pool, seeds=seeds, checkpoints=a.checkpoints, lam_grid=lam_grid, noise_sigma=a.noise_sigma,
               w_cm=a.w_cm, only=a.only, exports=str(a.exports), scorer_prefix=str(a.scorer_prefix), embed_prefix=a.embed_prefix, summary=summary,
               per_molecule=per_mol, seconds=round(time.time() - t0, 1))
    json.dump(out, open(a.out_prefix + ".json", "w"), indent=1)
    lines = [f"# Pattern-proposer simulation — pool {a.pool}, solver prior w {a.w_cm:g} cm⁻¹, {out['date']}", "",
             f"seeds {seeds}, {a.checkpoints} checkpoints per curve, λ {lam_grid}, noise σ {a.noise_sigma}; {len(per_mol)} evaluation molecules; orderings {a.only or 'all'}.", ""]
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
