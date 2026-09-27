"""Rung C — train the equivariant Δ-Hessian model (`rungC_equivariant.py`) on the pair model's pool and read it out with the pair model's own read-outs
(pre-registration `PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md`, R1–R3 and R5 here; R4, the within-orbit spread, holds by construction
and is checked by `tests/test_rungC_equivariance.py`). Built 27 September 2026 as desk work; **nothing is run on the pool before the user's word**
(the Sunday-evening decision; `Decision_Memo_2026-09-27_RungC_Tonight.md`).

Same pool, sizes, seeds and hold-outs as `e7_rungB_pairs.py` (E6 splits, or `--split layerB`), same analytic-Hessian substitution, same read-out
functions (`readouts` of e7: E6 ratios per class, T2's basis-free corrected ω, the Cartesian residual ratio) — the equivariant model's Cartesian ΔH is
projected to the pair model's internal coordinates with the pseudo-inverse of the Wilson B, exactly the auxiliary term of the registered loss.
Fixed recipe (C1, from scratch): AdamW 1e-3, weight decay 1e-4, one molecule per step, `--epochs` passes over the training set (default 60 as the pair
model's fixed recipe), loss = mass-weighted MSE + 0.1 × internal ΔF term; no early stopping, no tuning (the fair-chance search applies to rung C as to
the pair model: a flat result under this one recipe licenses nothing). Output JSON mirrors e7's: zero rule, per size and seed the read-outs on (a) and (b)
(and (c) for the layer-B split), wall time; a markdown table beside it.

    python m05/rungC_train.py corpus/molecules out/E7_rungC_<date> --use-analytic [--sizes 45,100,all] [--seeds 0,1,2] [--epochs 60] [--threads 8]
    python m05/rungC_train.py corpus/molecules out/_smoke --smoke          # 5 molecules, 2 epochs, seed 0: mechanics only"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from e7_rungB_pairs import readouts  # noqa: E402
from rungC_equivariant import DeltaHessianModel, load_molecule, loss_terms, to_torch  # noqa: E402

AUX_WEIGHT = 0.1


class Scaled(torch.nn.Module):
    """The equivariant model with a fixed output scale: the training set's RMS ΔH (build note of 27 Sep — the pair model scales its targets per class the
    same way; without it the head starts four orders of magnitude above the targets and spends its epochs shrinking). Equivariance is untouched."""

    def __init__(self, model: DeltaHessianModel, scale: float):
        super().__init__()
        self.model, self.scale = model, float(scale)

    def forward(self, Z, pos, H_low):
        return self.model(Z, pos, H_low) * self.scale


def train_one(train_ids: list, tensors: dict, seed: int, epochs: int, lr: float = 1e-3, log=print) -> tuple[torch.nn.Module, list]:
    torch.manual_seed(seed)
    scale = float(np.sqrt(np.mean([float((tensors[i]["dH_true"] ** 2).mean()) for i in train_ids])))
    model = Scaled(DeltaHessianModel(), scale)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    rng = np.random.default_rng(seed)
    hist, t0 = [], time.time()
    for ep in range(epochs):
        model.train()
        tot_main = tot_aux = 0.0
        for k in rng.permutation(len(train_ids)):
            t = tensors[train_ids[k]]
            opt.zero_grad()
            main, _zero, pred = loss_terms(model, t)
            dF_p = t["Bp"].T @ pred @ t["Bp"]
            aux = ((dF_p - t["dF_true"]) ** 2).mean() / t["dF_norm"]        # relative internal-ΔF term (build note of 27 Sep: the raw term is ~1e9 in a.u.)
            (main + AUX_WEIGHT * aux).backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot_main += float(main.detach())
            tot_aux += float(aux.detach())
        hist.append(dict(epoch=ep + 1, main=tot_main / len(train_ids), aux=tot_aux / len(train_ids)))
        if (ep + 1) % 10 == 0 or ep == 0 or ep + 1 == epochs:
            log(f"    seed {seed} epoch {ep + 1}/{epochs}: loss main {hist[-1]['main']:.4g} aux {hist[-1]['aux']:.4g} ({time.time() - t0:.0f} s)")
    return model, hist


def predictor(model: torch.nn.Module, tensors: dict, mols: dict):
    """dF_of(i): the model's Cartesian ΔH projected to the pair model's internal coordinates (B⁺ᵀ ΔH B⁺), as `readouts` expects."""
    cache = {}

    def dF_of(i):
        if i not in cache:
            t = tensors[i]
            model.eval()
            with torch.no_grad():
                dH = model(t["Z"], t["pos"], t["H_low"]).numpy().astype(float)
            Bp = np.linalg.pinv(mols[i]["B"])
            cache[i] = Bp.T @ dH @ Bp
        return cache[i]
    return dF_of


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--sizes", default="45,100,175", help="the pair model's registered sizes; 'all' = the whole pool")
    ap.add_argument("--pool-layers", default="A,A2", help="split e6: keep only these layers in the pool (the registered floor's pool was layer A + A2; layer B entered the corpus later)")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--epochs", type=int, default=None, help="default 60 (2 under --smoke unless given)")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--split", default="e6", help="e6 (default) or layerB, as in e7_rungB_pairs.py")
    ap.add_argument("--use-analytic", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="5 pool molecules, 2 epochs, seed 0, hold-outs cut to 3 each: mechanics only, never a result")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    t_start = time.time()
    log = lambda s: print(s, flush=True)  # noqa: E731

    mols = T2.load(a.molecules)
    test_a, test_b, cores, pool = E6.splits(mols)
    substituted = []
    if a.use_analytic:
        import e7_rungB_reread_analytic as RR
        for i, m in mols.items():
            d = Path(a.molecules) / i
            if (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists():
                RR.substitute(m, d)
                substituted.append(i)
        log(f"analytic second-route Hessians substituted for {len(substituted)} molecules")
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    test_a = [i for i in test_a if i in mols]
    test_b = [i for i in test_b if i in mols]
    pool = [i for i in pool if i in mols]
    nat = {i: len(m["masses"]) for i, m in mols.items()}
    if a.split == "e6" and a.pool_layers:
        keep = set(a.pool_layers.split(","))
        pool = [i for i in pool if mols[i]["layer"] in keep]
    if a.split == "layerB":
        pool = sorted((i for i, m in mols.items() if m["layer"] == "B"), key=E6.sha)
        test_a = sorted(i for i, m in mols.items() if m["layer"] == "A")
        assert pool, "no admitted layer-B molecules under the molecules directory"
    sizes = sorted({min(int(s) if s != "all" else len(pool), len(pool)) for s in a.sizes.split(",")})
    seeds = [int(s) for s in a.seeds.split(",")]
    if a.smoke:
        sizes, seeds, a.epochs = [min(5, len(pool))], [0], (a.epochs or 2)
        test_a, test_b = test_a[:3], test_b[:3]
    a.epochs = a.epochs or 60

    # tensors for the equivariant model (Cartesian; the registered inputs), plus B⁺ for the auxiliary term and the read-out projection
    needed = set(pool[: sizes[-1]]) | set(test_a) | set(test_b)
    if a.split == "layerB":
        needed |= {i for i, m in mols.items() if m["layer"] == "A2"}
    tensors = {}
    for i in sorted(needed):
        m = load_molecule(Path(a.molecules) / i, use_analytic=a.use_analytic)
        t = to_torch(m)
        t["Bp"] = torch.as_tensor(np.linalg.pinv(mols[i]["B"]), dtype=torch.float32)
        t["dF_true"] = t["Bp"].T @ t["dH_true"] @ t["Bp"]
        t["dF_norm"] = (t["dF_true"] ** 2).mean().clamp_min(1e-30)
        tensors[i] = t
    log(f"{len(mols)} molecules; pool {len(pool)}; hold-out (a) {len(test_a)}, (b) {len(test_b)} ({cores}); sizes {sizes}; seeds {seeds}; epochs {a.epochs}; "
        f"threads {a.threads}; model {sum(p.numel() for p in DeltaHessianModel().parameters()):,} parameters" + (" — SMOKE" if a.smoke else ""))

    tests = {"a": test_a, "b": test_b}
    res = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), smoke=a.smoke, model="rungC_equivariant C1 (from scratch; output scaled by the training set's RMS ΔH)", n_molecules=len(mols), holdout_a=test_a,
               holdout_b=test_b, scaffold_cores=cores, pool=len(pool), pool_ids=pool, pool_layers=a.pool_layers, sizes=sizes, seeds=seeds, epochs=a.epochs, lr=a.lr, aux_weight=AUX_WEIGHT,
               substituted_analytic=substituted, curve={})
    res["zero_rule"] = {h: readouts(mols, ids, pool, lambda i: np.zeros_like(mols[i]["F_low"])) for h, ids in tests.items() if ids}
    lines = [f"# Rung C (equivariant ΔH, C1 from scratch) — {a.out_prefix} ({res['date']}){' — SMOKE, not a result' if a.smoke else ''}", "",
             "| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |", "|---|---|---|---|---|---|---|---|---|---|"]
    for n in sizes:
        tr = pool[:n]
        if a.split == "layerB":
            nmax = max(nat[i] for i in tr)
            tests["c"] = sorted(i for i, m in mols.items() if m["layer"] == "A2" and nat[i] > nmax and i not in set(test_b))
            res.setdefault("holdout_c", {})[str(n)] = dict(n_atoms_above=nmax, ids=tests["c"])
            if tests["c"]:
                res.setdefault("zero_rule_c", {})[str(n)] = readouts(mols, tests["c"], tr, lambda i: np.zeros_like(mols[i]["F_low"]))
        row = {"n": n, "per_seed": []}
        for seed in seeds:
            t1 = time.time()
            model, hist = train_one(tr, tensors, seed, a.epochs, a.lr, log)
            dF_of = predictor(model, tensors, mols)
            out = {"seed": seed, "train_history": hist, "output_scale": model.scale, "seconds": round(time.time() - t1, 1)}
            for h, ids in tests.items():
                if not ids:
                    continue
                r = readouts(mols, ids, tr, dF_of)
                out[h] = r
                z = res["zero_rule"][h] if h in res["zero_rule"] else res["zero_rule_c"][str(n)]
                lines.append(f"| {n} | {seed} | ({h}) | {r['coupling_rms']:.2f} | {r['coupling_zero_rms']:.2f} | {r['coupling_ratio']:.2f} | {r['corrected_freq_rms']:.2f} | "
                             f"{r['corrected_freq_rms_zero_rule']:.2f} | {r['dH_residual_ratio']:.3f} | {out['seconds']:.0f} |")
                log(f"  n={n} seed {seed} ({h}): ring couplings {r['coupling_rms']:.2f} vs zero {r['coupling_zero_rms']:.2f} (ratio {r['coupling_ratio']:.2f}) | corrected ω "
                    f"{r['corrected_freq_rms']:.2f} (zero {r['corrected_freq_rms_zero_rule']:.2f}) | ΔH residual ratio {r['dH_residual_ratio']:.3f}")
                del z
            row["per_seed"].append(out)
        res["curve"][str(n)] = row
    res["seconds"] = round(time.time() - t_start, 1)
    lines += ["", f"wall {res['seconds']:.0f} s; read-out keys: {sorted(k for k in next(iter(res['zero_rule'].values())).keys())}", ""]
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    Path(a.out_prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    log(f"wrote {a.out_prefix}.json/.md in {res['seconds']:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
